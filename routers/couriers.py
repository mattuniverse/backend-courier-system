import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from database import get_conn
from schemas import CourierIn
from utils.auth import get_current_user

router = APIRouter(prefix="/couriers", tags=["Couriers"])


@router.get("/")
async def list_couriers(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("""
        SELECT co.*, b.name AS branch_name
        FROM couriers co
        LEFT JOIN branches b ON b.id = co.branch_id
        ORDER BY co.created_at DESC
    """)
    return [dict(r) for r in rows]


@router.post("/")
async def create_courier(
    data: CourierIn,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow(
        """INSERT INTO couriers (name, phone, email, vehicle_no, branch_id)
           VALUES ($1, $2, $3, $4, $5) RETURNING *""",
        data.name, data.phone, data.email, data.vehicle_no, data.branch_id,
    )
    return dict(row)


@router.patch("/{courier_id}/toggle")
async def toggle_courier(
    courier_id: int,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow(
        """UPDATE couriers SET status = CASE WHEN status='available' THEN 'busy' ELSE 'available' END
           WHERE id=$1 RETURNING *""",
        courier_id,
    )
    if not row:
        raise HTTPException(404, detail="Courier not found")
    return dict(row)


@router.delete("/{courier_id}")
async def delete_courier(
    courier_id: int,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    result = await conn.execute("DELETE FROM couriers WHERE id=$1", courier_id)
    if result == "DELETE 0":
        raise HTTPException(404, detail="Courier not found")
    return {"detail": "Courier deleted"}
