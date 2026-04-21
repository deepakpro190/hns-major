from fastapi import APIRouter
from database import SessionLocal

router = APIRouter()

@router.get("/prediction/latest")
def latest_prediction():
    db = SessionLocal()

    row = db.execute("""
        SELECT * FROM window_features
        ORDER BY timestamp DESC LIMIT 1
    """).fetchone()

    db.close()

    if not row:
        return {}

    return {
        "temp_avg": row[2],
        "status": "SAFE"  # placeholder
    }