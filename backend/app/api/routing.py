from fastapi import APIRouter
from services.routing_service import suggest_route

router = APIRouter()

@router.get("/transport/route")
def route_suggestion(
    device_id: str,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float
):
    result = suggest_route(
        device_id,
        origin=(origin_lon, origin_lat),
        destination=(dest_lon, dest_lat)
    )

    if not result:
        return {"error": "Insufficient data"}

    return result
