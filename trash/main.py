from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import psycopg2

app = FastAPI(title="Cold Chain Backend")

conn = psycopg2.connect(
    host="localhost",
    database="coldchain",
    user="postgres",
    password="rakesh1972"
)
cursor = conn.cursor()

class WindowPayload(BaseModel):
    device_id: str
    timestamp: str
    features: Dict[str, float]
    risk_probability: float
    risk_class: str

@app.post("/ingest/window")
def ingest_window(data: WindowPayload):
    cursor.execute("""
        INSERT INTO window_features (
            device_id, timestamp,
            temp_avg, temp_max, temp_min, temp_rate,
            time_outside_range_sec, humidity_avg,
            humidity_variance, humidity_spike_count,
            door_open_count, door_open_duration_sec,
            max_door_open_time_sec,
            risk_probability, risk_class
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data.device_id,
        data.timestamp,
        *data.features.values(),
        data.risk_probability,
        data.risk_class
    ))
    conn.commit()
    return {"status": "ok"}
