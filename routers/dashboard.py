import asyncpg
from fastapi import APIRouter, Depends
from database import get_conn
from utils.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow("""
        SELECT
          (SELECT COUNT(*) FROM parcels) AS total_parcels,
          (SELECT COUNT(*) FROM parcels WHERE status='pending') AS pending,
          (SELECT COUNT(*) FROM parcels WHERE status='in_transit') AS in_transit,
          (SELECT COUNT(*) FROM parcels WHERE status='out_for_delivery') AS out_for_delivery,
          (SELECT COUNT(*) FROM parcels WHERE status='delivered') AS delivered,
          (SELECT COUNT(*) FROM customers) AS customers,
          (SELECT COUNT(*) FROM couriers) AS couriers,
          (SELECT COALESCE(SUM(cost),0) FROM parcels WHERE payment_status='paid') AS revenue
    """)
    return dict(row)


@router.get("/recent-parcels")
async def get_recent_parcels(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("""
        SELECT p.*, c.name AS sender_name
        FROM parcels p
        JOIN customers c ON c.id = p.sender_id
        ORDER BY p.created_at DESC
        LIMIT 8
    """)
    return [dict(r) for r in rows]
