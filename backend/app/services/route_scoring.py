# services/route_scoring.py

def score_route(route, transport_risk):
    """
    Risk-aware cost function

    route fields:
      - duration (seconds)
      - distance_km
    transport_risk:
      - probability [0,1]
    """

    # --- Weights (tunable / explainable) ---
    alpha = 0.6   # time importance
    beta = 0.2    # distance importance
    gamma = 0.8   # spoilage risk importance

    # --- Normalize ---
    eta_min = route["duration"] / 60        # seconds → minutes
    dist_km = route["distance_km"]

    # --- Cost ---
    cost = (
        alpha * eta_min +
        beta * dist_km +
        gamma * (transport_risk * 100)  # amplify ML risk
    )

    return round(cost, 3)
