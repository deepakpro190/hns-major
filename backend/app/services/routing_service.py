# services/routing_service.py

from services.osrm import get_routes
from services.transport_prediction import predict_transport_risk
from services.route_scoring import score_route


def suggest_route(device_id, origin_lat, origin_lon, dest_lat, dest_lon):
    """
    User-triggered intelligent routing
    """

    # 1️⃣ Get OSRM routes
    routes = get_routes(origin_lat, origin_lon, dest_lat, dest_lon)
    if not routes:
        return {"error": "No routes found"}

    # 2️⃣ Predict transport spoilage risk
    transport_risk = predict_transport_risk(device_id)
    if transport_risk is None:
        transport_risk = 0.3  # safe fallback

    scored_routes = []

    # 3️⃣ Score routes
    for r in routes:
        cost = score_route(r, transport_risk)

        scored_routes.append({
            "eta": round(r["duration"] / 60, 1),   # minutes
            "distance_km": round(r["distance_km"], 2),
            "risk": round(transport_risk, 3),
            "cost": cost,
            "geometry": r["geometry"]
        })

    # 4️⃣ Choose best route
    best = min(scored_routes, key=lambda x: x["cost"])

    return {
        "best_route": best,
        "alternatives": [r for r in scored_routes if r != best]
    }
