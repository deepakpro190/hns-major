import numpy as np
from datetime import datetime, timedelta, timezone
from db.database import get_connection

SAFE_MIN, SAFE_MAX = 2, 8

def compute_transport_features(device_id: str, window_min=10):
    conn = get_connection()
    cur = conn.cursor()

    since = datetime.now(timezone.utc) - timedelta(minutes=window_min)

    # 1️⃣ Sensor data (from ESP32)
    cur.execute("""
        SELECT temperature, door, timestamp
        FROM raw_sensor_data
        WHERE device_id=%s AND timestamp >= %s
        ORDER BY timestamp
    """, (device_id, since))

    rows = cur.fetchall()
    if len(rows) < 5:
        cur.close()
        conn.close()
        return None

    temps = np.array([r[0] for r in rows])
    doors = np.array([r[1] for r in rows])

    # 2️⃣ Transport context (latest)
    cur.execute("""
        SELECT ambient_temp, traffic_index, speed
        FROM transport_context
        WHERE device_id=%s
        ORDER BY timestamp DESC
        LIMIT 1
    """, (device_id,))

    ctx = cur.fetchone()
    if not ctx:
        cur.close()
        conn.close()
        return None

    amb_temp, traffic, speed = ctx

    # -------- FEATURE ENGINEERING --------
    temp_drift = float(np.gradient(temps).mean())
    excursion_time = float(np.sum((temps < SAFE_MIN) | (temps > SAFE_MAX)))
    temp_variance = float(np.var(temps))

    door_open_events = np.sum((doors[1:] == 1) & (doors[:-1] == 0))
    door_rate = float(door_open_events / max(window_min / 60, 0.1))

    handling_index = float((door_rate + temp_variance) / 2)

    delay_risk = float(traffic * (1 / max(speed, 1)))
    heat_stress = float(amb_temp * window_min)
    thermal_buffer = float(1 / (heat_stress + 1e-3))

    # 3️⃣ Store features
    cur.execute("""
        INSERT INTO transport_features
        (device_id, timestamp,
         temp_drift, excursion_time, temp_variance,
         door_rate, handling_index, delay_risk,
         heat_stress, thermal_buffer)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        device_id, datetime.now(timezone.utc),
        temp_drift, excursion_time, temp_variance,
        door_rate, handling_index,
        delay_risk, heat_stress, thermal_buffer
    ))

    conn.commit()
    cur.close()
    conn.close()
