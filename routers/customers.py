import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_conn
from schemas import CustomerIn
from utils.auth import get_current_user, require_admin

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/")
async def list_customers(
    q: str = Query("", description="Search by name or phone"),
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    if q:
        rows = await conn.fetch(
            "SELECT * FROM customers WHERE name ILIKE $1 OR phone ILIKE $1 ORDER BY created_at DESC",
            f"%{q}%",
        )
    else:
        rows = await conn.fetch("SELECT * FROM customers ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@router.post("/")
async def create_customer(
    data: CustomerIn,
    current: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow(
        """INSERT INTO customers (name, phone, email, address)
           VALUES ($1, $2, $3, $4) RETURNING *""",
        data.name, data.phone, data.email, data.address,
    )
    return dict(row)


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    current: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_conn),
):
    result = await conn.execute("DELETE FROM customers WHERE id=$1", customer_id)
    if result == "DELETE 0":
        raise HTTPException(404, detail="Customer not found")
    return {"detail": "Customer deleted"}
