import numpy as np
from datetime import datetime, timezone
from services.buffer import buffers
from services.prediction import predict_risk
from db.database import get_connection
from backend.app.services.transport_model import run_r_analytics
import pandas as pd
from db.database import get_connection

def export_latest_windows(device_id):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT *
        FROM window_features
        WHERE device_id = %s
        ORDER BY timestamp DESC
        LIMIT 5
    """, conn, params=(device_id,))
    conn.close()

    df.to_csv("analytics/latest_windows.csv", index=False)



SAFE_TEMP_MIN = 2
SAFE_TEMP_MAX = 8

def aggregate_and_store(device_id):
    if device_id not in buffers:
        return

    data = list(buffers[device_id])
    if len(data) < 30:
        return  # not enough data yet

    temps = np.array([d["temperature"] for d in data])
    hums  = np.array([d["humidity"] for d in data])
    doors = np.array([d["door"] for d in data])

    # -------- FEATURE EXTRACTION --------
    temp_avg = float(temps.mean())
    temp_max = float(temps.max())
    temp_min = float(temps.min())
    temp_rate = float((temp_max - temp_min) / 2)  # per minute
    time_outside = int(np.sum((temps < SAFE_TEMP_MIN) | (temps > SAFE_TEMP_MAX)))

    humidity_avg = float(hums.mean())
    humidity_variance = float(hums.var())
    humidity_spikes = int(np.sum(np.abs(np.diff(hums)) > 3))

    door_open_count = int(np.sum((doors[1:] == 1) & (doors[:-1] == 0)))
    door_open_duration = int(doors.sum())

    max_open = 0
    current = 0
    for d in doors:
        if d == 1:
            current += 1
            max_open = max(max_open, current)
        else:
            current = 0

    features = [
        temp_avg,
        temp_max,
        temp_min,
        temp_rate,
        time_outside,
        humidity_avg,
        humidity_variance,
        humidity_spikes,
        door_open_count,
        door_open_duration,
        int(max_open)
    ]

    # -------- PREDICTION --------
    # TAKE RISK FROM ESP32 (last sample)
    risk_prob = data[-1]["risk_probability"]
    risk_class = data[-1]["risk_class"]


    # -------- STORE WINDOW --------
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO window_features (
            device_id, timestamp,
            temp_avg, temp_max, temp_min, temp_rate,
            time_outside_range_sec, humidity_avg,
            humidity_variance, humidity_spike_count,
            door_open_count, door_open_duration_sec,
            max_door_open_time_sec,
            risk_probability, risk_class
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        device_id,
        datetime.now(timezone.utc),
        *features,
        risk_prob,
        risk_class
    ))
    from services.buffer import live_cache

    if device_id in live_cache:
        live_cache[device_id]["risk"] = risk_class

    conn.commit()
    export_latest_windows(device_id)
    run_r_analytics(device_id)

    run_r_analytics(device_id)
    cur.close()
    conn.close()

    print(f"[WINDOW] {device_id} → {risk_class} ({risk_prob:.2f})")
  
    
