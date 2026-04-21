import joblib
import numpy as np
import math
import random
from datetime import datetime

# 🔥 LOAD MODEL
xgb_transport = joblib.load("models/xgb_transport.pkl")


# =========================
# DISTANCE (Haversine)
# =========================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# =========================
# FEATURE BUILDER (SMART)
# =========================
def build_features(origin, dest):
    lat1, lon1 = origin
    lat2, lon2 = dest

    distance = haversine(lat1, lon1, lat2, lon2)

    # 🧠 TRAFFIC (time-based)
    hour = datetime.now().hour
    if 8 <= hour <= 11 or 17 <= hour <= 20:
        traffic_index = 0.8
    else:
        traffic_index = 0.4

    # 🌡 TEMP (simple geo logic)
    ambient_temp = 30 if lat1 > 20 else 25

    # 🚗 SPEED (inverse traffic)
    speed = max(20, 60 * (1 - traffic_index))

    # ⏱ DELAY
    delay_hr = traffic_index * 1.5

    # 🧠 COMPLEXITY
    route_complexity = min(1, distance / 50)

    # ⚠ THERMAL STRESS
    thermal_stress_total = max(0, ambient_temp - 25)

    # 🔥 FINAL FEATURES (MUST MATCH TRAINING)
    features = np.array([[
        ambient_temp,
        ambient_temp + 2,         # max temp approx
        (ambient_temp - 2),       # variance approx
        1,                        # door count approx
        delay_hr,
        thermal_stress_total,
        delay_hr,
        route_complexity,
        traffic_index
    ]])

    return features


# =========================
# PREDICT
# =========================
def predict_transport(origin, dest):
    features = build_features(origin, dest)

    prob = xgb_transport.predict_proba(features)[0]
    risk_score = float(np.max(prob))

    status = (
        "CRITICAL" if risk_score > 0.7 else
        "WARNING" if risk_score > 0.4 else
        "SAFE"
    )

    return {
        "risk": status,
        "risk_score": risk_score
    }