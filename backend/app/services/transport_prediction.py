import joblib
import numpy as np
from db.database import get_connection

model = joblib.load("models/transport_risk.pkl")

def predict_transport_risk(device_id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT temp_drift, excursion_time, temp_variance,
               door_rate, handling_index, delay_risk,
               heat_stress, thermal_buffer
        FROM transport_features
        WHERE device_id=%s
        ORDER BY timestamp DESC LIMIT 1
    """, (device_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    x = np.array(row).reshape(1,-1)
    p = float(model.predict_proba(x)[0][1])
    return p
