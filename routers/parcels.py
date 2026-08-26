import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_conn
from schemas import ParcelIn, StatusUpdateIn
from utils.auth import get_current_user
from utils.tracking import generate_tracking_no

router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.get("/")
async def list_parcels(
    q: str = Query("", description="Search by tracking_no, receiver, sender"),
    status_filter: str = Query("", alias="status"),
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    conditions = []
    params = []
    idx = 1

    if q:
        conditions.append(f"(p.tracking_no ILIKE ${idx} OR p.receiver_name ILIKE ${idx} OR c.name ILIKE ${idx})")
        params.append(f"%{q}%")
        idx += 1
    if status_filter:
        conditions.append(f"p.status = ${idx}")
        params.append(status_filter)
        idx += 1

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    rows = await conn.fetch(f"""
        SELECT p.*, c.name AS sender_name, co.name AS courier_name
        FROM parcels p
        JOIN customers c ON c.id = p.sender_id
        LEFT JOIN couriers co ON co.id = p.courier_id
        {where}
        ORDER BY p.created_at DESC
    """, *params)
    return [dict(r) for r in rows]


@router.post("/book")
async def book_parcel(
    data: ParcelIn,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    tracking_no = generate_tracking_no()
    async with conn.transaction():
        row = await conn.fetchrow(
            """INSERT INTO parcels
               (tracking_no, sender_id, receiver_name, receiver_phone, receiver_address,
                pickup_branch_id, delivery_branch_id, courier_id, parcel_type, weight_kg,
                cost, payment_status, status, booking_date, expected_delivery_date, created_by)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,'pending',$13,$14,$15)
               RETURNING *""",
            tracking_no, data.sender_id, data.receiver_name, data.receiver_phone,
            data.receiver_address, data.pickup_branch_id, data.delivery_branch_id,
            data.courier_id, data.parcel_type, data.weight_kg, data.cost,
            data.payment_status, data.booking_date, data.expected_delivery_date,
            current["id"],
        )
        await conn.execute(
            """INSERT INTO parcel_tracking (parcel_id, status, location, remarks, updated_by)
               VALUES ($1, 'pending', 'Origin', 'Parcel booked', $2)""",
            row["id"], current["id"],
        )
    return dict(row)


@router.get("/{parcel_id}")
async def get_parcel(
    parcel_id: int,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow("""
        SELECT p.*, c.name AS sender_name, c.phone AS sender_phone,
               co.name AS courier_name,
               pb.name AS pickup_branch_name, db.name AS delivery_branch_name
        FROM parcels p
        JOIN customers c ON c.id = p.sender_id
        LEFT JOIN couriers co ON co.id = p.courier_id
        LEFT JOIN branches pb ON pb.id = p.pickup_branch_id
        LEFT JOIN branches db ON db.id = p.delivery_branch_id
        WHERE p.id=$1
    """, parcel_id)
    if not row:
        raise HTTPException(404, detail="Parcel not found")

    history = await conn.fetch("""
        SELECT t.*, u.full_name AS updated_by_name
        FROM parcel_tracking t
        LEFT JOIN users u ON u.id = t.updated_by
        WHERE t.parcel_id=$1
        ORDER BY t.updated_at DESC
    """, parcel_id)

    return {"parcel": dict(row), "tracking_history": [dict(h) for h in history]}


@router.patch("/{parcel_id}/status")
async def update_parcel_status(
    parcel_id: int,
    data: StatusUpdateIn,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    parcel = await conn.fetchrow("SELECT id, status FROM parcels WHERE id=$1", parcel_id)
    if not parcel:
        raise HTTPException(404, detail="Parcel not found")

    async with conn.transaction():
        delivered_at_clause = ""
        params_extra = []
        if data.status == "delivered":
            delivered_at_clause = ", delivered_at = NOW()"

        await conn.execute(
            f"UPDATE parcels SET status=$1{delivered_at_clause} WHERE id=$2",
            data.status, parcel_id,
        )
        await conn.execute(
            """INSERT INTO parcel_tracking (parcel_id, status, location, remarks, updated_by)
               VALUES ($1, $2, $3, $4, $5)""",
            parcel_id, data.status, data.location, data.remarks, current["id"],
        )
    return {"detail": "Status updated"}
