# services/osrm.py
import requests
import polyline

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

def get_routes(origin_lat, origin_lon, dest_lat, dest_lon):
    """
    Returns multiple routes with:
    - duration (seconds)
    - distance_km
    - geometry [(lat, lon), ...]
    """

    url = f"{OSRM_URL}/{origin_lon},{origin_lat};{dest_lon},{dest_lat}"

    params = {
        "alternatives": "true",
        "overview": "full",
        "geometries": "polyline"
    }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    routes = []

    for rt in data.get("routes", []):
        routes.append({
            "duration": rt["duration"],            # ✅ seconds
            "distance_km": rt["distance"] / 1000,  # km
            "geometry": polyline.decode(rt["geometry"])  # [(lat, lon)]
        })

    return routes
