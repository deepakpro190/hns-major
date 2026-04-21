from fastapi import APIRouter
from sqlalchemy import text
from db.database import SessionLocal
from datetime import datetime

router = APIRouter()

@router.post("/ingest/raw")
def ingest_raw(data: dict):
    db = SessionLocal()

    try:
        # ✅ Validate fields
        device_id = data.get("device_id")
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        door = data.get("door")

        if None in [device_id, temperature, humidity, door]:
            return {"error": "Missing fields"}

        # ✅ Insert
        db.execute(text("""
            INSERT INTO raw_sensor_data (
                device_id, temperature, humidity, door, timestamp
            )
            VALUES (
                :device_id, :temperature, :humidity, :door, :timestamp
            )
        """), {
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity,
            "door": door,
            "timestamp": datetime.now()
        })

        db.commit()

        return {"status": "stored"}

    except Exception as e:
        print("INGEST ERROR:", e)   # 🔥 print real error
        return {"error": str(e)}

    finally:
        db.close()


from fastapi import APIRouter
from pydantic import BaseModel


class TransportIngest(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    timestamp: str


@router.post("/ingest/transport")
def ingest_transport(data: TransportIngest):
    print("TRANSPORT DATA:", data)
    return {"status": "transport stored"}