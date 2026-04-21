from fastapi import APIRouter
from sqlalchemy import text
from db.database import SessionLocal
import math
import random

router = APIRouter()


# =========================
# DISTANCE CALC
# =========================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# =========================
# 🚚 ROUTE API
# =========================
@router.get("/transport/route")
def get_route(
    device_id: str,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float
):

    distance = haversine(origin_lat, origin_lon, dest_lat, dest_lon)

    # 🔥 SIMULATED TRAFFIC
    traffic = random.uniform(0.4, 0.9)

    # ETA calculation
    speed = 60 * (1 - traffic)
    speed = max(20, speed)

    eta = distance / speed * 60  # minutes

    # Risk simulation (you can later plug model)
    risk = traffic

    best_route = {
        "geometry": [
            [origin_lat, origin_lon],
            [dest_lat, dest_lon]
        ],
        "distance_km": round(distance, 2),
        "eta": int(eta),
        "risk": risk,
        "cost": round(distance * 5, 2)
    }

    # 🔁 Alternative routes
    alternatives = []

    for i in range(2):
        alt_risk = min(1, risk + random.uniform(-0.1, 0.2))

        alternatives.append({
            "geometry": [
                [origin_lat, origin_lon],
                [dest_lat + random.uniform(-0.05, 0.05),
                 dest_lon + random.uniform(-0.05, 0.05)]
            ],
            "distance_km": round(distance * random.uniform(1.05, 1.2), 2),
            "eta": int(eta * random.uniform(1.1, 1.3)),
            "risk": alt_risk,
            "cost": round(distance * random.uniform(5, 7), 2)
        })

    return {
        "best_route": best_route,
        "alternatives": alternatives
    }