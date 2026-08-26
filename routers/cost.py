from fastapi import APIRouter
from schemas import CostEstimateIn, CostEstimateOut
from utils.cost import BASE_RATES, PER_KG_RATE, PER_KM_RATE
from utils.auth import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/cost", tags=["Cost"])


@router.post("/estimate")
async def estimate_cost(
    data: CostEstimateIn,
    current: dict = Depends(get_current_user),
):
    base = BASE_RATES.get(data.parcel_type, 100)
    weight_cost = data.weight_kg * PER_KG_RATE
    distance_cost = (data.distance_km * PER_KM_RATE) if data.distance_km else 0
    total = round(base + weight_cost + distance_cost, 2)
    return CostEstimateOut(
        base_rate=base,
        weight_cost=round(weight_cost, 2),
        distance_cost=round(distance_cost, 2),
        total=total,
    )
