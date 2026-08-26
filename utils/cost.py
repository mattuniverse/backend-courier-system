BASE_RATES = {
    "document": 50,
    "box": 100,
    "fragile": 150,
    "electronics": 200,
    "other": 100,
}

PER_KG_RATE = 25
PER_KM_RATE = 15


def calculate_cost(weight_kg: float, parcel_type: str, distance_km: float | None = None) -> float:
    base = BASE_RATES.get(parcel_type, 100)
    weight_cost = weight_kg * PER_KG_RATE
    distance_cost = (distance_km * PER_KM_RATE) if distance_km else 0
    return round(base + weight_cost + distance_cost, 2)
