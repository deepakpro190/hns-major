from fastapi import APIRouter
from datetime import datetime, timedelta
import random
from fastapi import APIRouter
from sqlalchemy import text
from db.database import SessionLocal

router = APIRouter()

@router.get("/storage/history")
def history(device_id: str):
    db = SessionLocal()

    rows = db.execute(text("""
        SELECT temperature, humidity, timestamp
        FROM raw_sensor_data
        WHERE device_id = :device_id
        ORDER BY timestamp DESC
        LIMIT 30
    """), {"device_id": device_id}).fetchall()

    db.close()

    data = [
        {
            "temperature": float(r[0]),
            "humidity": float(r[1]),
            "time": str(r[2])
        }
        for r in rows
    ][::-1]

    return {"data": data}