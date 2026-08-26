import asyncpg
from fastapi import APIRouter, Depends
from database import get_conn
from utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_summary(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow("""
        SELECT
          (SELECT COUNT(*) FROM parcels) AS total_parcels,
          (SELECT COUNT(*) FROM parcels WHERE status='delivered') AS delivered_count,
          (SELECT COUNT(*) FROM parcels WHERE status='pending') AS pending_count,
          (SELECT COUNT(*) FROM parcels WHERE status='in_transit') AS in_transit_count,
          (SELECT COUNT(*) FROM parcels WHERE status='cancelled') AS cancelled_count,
          (SELECT COUNT(*) FROM parcels WHERE status='returned') AS returned_count,
          (SELECT COALESCE(SUM(cost),0) FROM parcels WHERE payment_status='paid') AS total_revenue,
          (SELECT COUNT(*) FROM parcels WHERE created_at >= NOW() - INTERVAL '7 days') AS parcels_this_week,
          (SELECT COUNT(*) FROM parcels WHERE created_at >= CURRENT_DATE) AS parcels_today,
          COALESCE(
            (SELECT AVG(EXTRACT(EPOCH FROM (delivered_at - created_at)) / 86400.0)
             FROM parcels WHERE delivered_at IS NOT NULL AND status='delivered'), 0
          ) AS avg_delivery_days
    """)
    return dict(row)


@router.get("/weekly")
async def get_weekly(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("""
        SELECT
          (CURRENT_DATE - s.i)::DATE AS date,
          (SELECT COUNT(*) FROM parcels p WHERE p.created_at::DATE = (CURRENT_DATE - s.i)::DATE) AS count
        FROM generate_series(0, 6) AS s(i)
        ORDER BY date ASC
    """)
    return [{"date": str(r["date"]), "count": r["count"]} for r in rows]


@router.get("/monthly")
async def get_monthly(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("""
        SELECT
          TO_CHAR(d, 'YYYY-MM') AS month,
          (SELECT COUNT(*) FROM parcels p WHERE TO_CHAR(p.created_at, 'YYYY-MM') = TO_CHAR(d, 'YYYY-MM')) AS count
        FROM generate_series(
          (CURRENT_DATE - INTERVAL '11 months')::DATE,
          CURRENT_DATE,
          '1 month'
        ) AS d
        ORDER BY d ASC
    """)
    return [{"month": r["month"], "count": r["count"]} for r in rows]


@router.get("/branch-performance")
async def get_branch_performance(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("""
        SELECT
          b.name AS branch_name,
          COUNT(p.id) AS parcels_handled,
          COUNT(p.id) FILTER (WHERE p.status = 'delivered') AS delivered
        FROM branches b
        LEFT JOIN parcels p ON p.pickup_branch_id = b.id OR p.delivery_branch_id = b.id
        GROUP BY b.id, b.name
        ORDER BY parcels_handled DESC
    """)
    return [dict(r) for r in rows]


@router.get("/revenue")
async def get_revenue(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("""
        SELECT
          (CURRENT_DATE - s.i)::DATE AS date,
          COALESCE(
            (SELECT SUM(cost) FROM parcels p
             WHERE p.payment_status = 'paid' AND p.created_at::DATE = (CURRENT_DATE - s.i)::DATE), 0
          ) AS revenue
        FROM generate_series(0, 29) AS s(i)
        ORDER BY date ASC
    """)
    return [{"date": str(r["date"]), "revenue": float(r["revenue"])} for r in rows]
