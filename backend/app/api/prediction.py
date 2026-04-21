from fastapi import APIRouter
from sqlalchemy import text
from db.database import SessionLocal
from services.buffer import live_cache

router = APIRouter()

@router.get("/latest-prediction")
def latest_prediction(device_id: str):
    db = SessionLocal()

    try:
        result = db.execute(text("""
            SELECT final_risk, status
            FROM predictions
            WHERE device_id = :device_id
            ORDER BY timestamp DESC
            LIMIT 1
        """), {"device_id": device_id})

        row = result.fetchone()

        if not row:
            return {"risk": "UNKNOWN", "value": 0}

        risk_value = float(row[0])
        risk_status = row[1]

        # 🔥 Sync with live cache
        if device_id in live_cache:
            live_cache[device_id]["risk"] = risk_status
            live_cache[device_id]["risk_value"] = risk_value

        return {
            "device_id": device_id,
            "risk": risk_status,
            "risk_value": risk_value
        }

    except Exception as e:
        print("Prediction API Error:", e)
        return {"error": "failed"}

    finally:
        db.close()



from services.models import explain_prediction

@router.get("/prediction/explain")
def explain(device_id: str):
    db = SessionLocal()

    try:
        row = db.execute(text("""
            SELECT temp_avg, temp_max, temp_min, temp_variance,
                   humidity_avg, door_open_count,
                   excursion_time, thermal_stress
            FROM window_features
            WHERE device_id = :device_id
            ORDER BY timestamp DESC
            LIMIT 1
        """), {"device_id": device_id}).fetchone()

        if not row:
            return {"error": "no data"}

        features = [list(row)]

        explanation = explain_prediction(features)

        return {
            "device_id": device_id,
            "explanation": explanation
        }

    finally:
        db.close()


@router.get("/prediction/trend")
def trend(device_id: str):
    db = SessionLocal()

    rows = db.execute(text("""
        SELECT temperature
        FROM raw_sensor_data
        WHERE device_id = :device_id
        ORDER BY timestamp DESC
        LIMIT 30
    """), {"device_id": device_id}).fetchall()

    db.close()

    if not rows:
        return {"actual": [], "predicted": []}

    temps = [r[0] for r in rows][::-1]

    # 🔥 TEMP (until LSTM sequence implemented)
    predicted = temps[-10:]

    return {
        "actual": temps,
        "predicted": predicted
    }



@router.get("/prediction/lstm-trend")
def lstm_trend(device_id: str):
    db = SessionLocal()

    rows = db.execute(text("""
        SELECT temperature
        FROM raw_sensor_data
        WHERE device_id = :device_id
        ORDER BY timestamp DESC
        LIMIT 30
    """), {"device_id": device_id}).fetchall()

    db.close()

    if not rows:
        return {"trend": []}

    temps = [r[0] for r in rows][::-1]

    # 🔥 Example LSTM output (replace with real model)
    trend = [1 if t > 8 else 0 for t in temps]

    return {"trend": trend}

def estimate_spoil_time(temp_avg, excursion_time, stress):
    
    base_time = 120  # safe storage time (minutes)

    penalty = (
        excursion_time * 2 +
        stress * 3 +
        max(0, temp_avg - 8) * 5
    )

    remaining = max(0, base_time - penalty)

    return remaining

    
@router.get("/prediction/spoil-time")
def spoil_time(device_id: str):
    db = SessionLocal()

    row = db.execute(text("""
        SELECT temp_avg, excursion_time, thermal_stress
        FROM window_features
        WHERE device_id = :device_id
        ORDER BY timestamp DESC
        LIMIT 1
    """), {"device_id": device_id}).fetchone()

    db.close()

    if not row:
        return {"time_left": None}

    temp_avg, excursion, stress = row

    time_left = estimate_spoil_time(temp_avg, excursion, stress)

    return {
        "time_left": time_left
    }