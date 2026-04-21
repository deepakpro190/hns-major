from fastapi import APIRouter
from sqlalchemy import text
from db.database import SessionLocal

router = APIRouter()

@router.get("/live-status")
def get_live():
    db = SessionLocal()

    try:
        result = db.execute(text("""
            SELECT temperature, humidity, door, timestamp
            FROM raw_sensor_data
            ORDER BY timestamp DESC
            LIMIT 1
        """))

        row = result.fetchone()

        if not row:
            return {"message": "No data"}

        return {
            "temperature": row[0],
            "humidity": row[1],
            "door": row[2],
            "timestamp": str(row[3])
        }

    except Exception as e:
        print("LIVE ERROR:", e)
        return {"error": str(e)}

    finally:
        db.close()