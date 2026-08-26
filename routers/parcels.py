import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from database import get_conn
from schemas import ParcelIn, StatusUpdateIn, BulkStatusIn, DeliveryProofIn
from utils.auth import get_current_user
from utils.tracking import generate_tracking_no
from services.email import send_booking_confirmation, send_status_update
from services.pdf import generate_booking_receipt

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

    try:
        sender = await conn.fetchrow("SELECT email FROM customers WHERE id=$1", data.sender_id)
        if sender and sender["email"]:
            send_booking_confirmation(sender["email"], tracking_no, data.receiver_name, data.booking_date)
    except Exception:
        pass

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

    try:
        full_parcel = await conn.fetchrow("""
            SELECT p.tracking_no, p.receiver_name, c.email
            FROM parcels p
            JOIN customers c ON c.id = p.sender_id
            WHERE p.id=$1
        """, parcel_id)
        if full_parcel and full_parcel["email"]:
            send_status_update(full_parcel["email"], full_parcel["tracking_no"], data.status, data.location or "")
    except Exception:
        pass

    return {"detail": "Status updated"}


@router.post("/bulk-status")
async def bulk_update_status(
    data: BulkStatusIn,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    if not data.parcel_ids:
        raise HTTPException(400, detail="No parcel IDs provided")

    async with conn.transaction():
        placeholders = ",".join(f"${i+1}" for i in range(len(data.parcel_ids)))
        await conn.execute(
            f"UPDATE parcels SET status=$1, updated_at=NOW() WHERE id IN ({placeholders})",
            data.status, *data.parcel_ids,
        )
        for pid in data.parcel_ids:
            await conn.execute(
                """INSERT INTO parcel_tracking (parcel_id, status, location, remarks, updated_by)
                   VALUES ($1, $2, $3, $4, $5)""",
                pid, data.status, data.location, data.remarks, current["id"],
            )

    return {"detail": f"Updated {len(data.parcel_ids)} parcels"}


@router.post("/{parcel_id}/delivery-proof")
async def add_delivery_proof(
    parcel_id: int,
    data: DeliveryProofIn,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    parcel = await conn.fetchrow("SELECT id FROM parcels WHERE id=$1", parcel_id)
    if not parcel:
        raise HTTPException(404, detail="Parcel not found")

    await conn.execute(
        """UPDATE parcels SET
           status='delivered', delivered_at=NOW(), updated_at=NOW()
           WHERE id=$1""",
        parcel_id,
    )
    await conn.execute(
        """INSERT INTO parcel_tracking (parcel_id, status, location, remarks, updated_by)
           VALUES ($1, 'delivered', 'Delivered', $2, $3)""",
        parcel_id, f"Delivered to {data.recipient_name}", current["id"],
    )

    return {
        "parcel_id": parcel_id,
        "recipient_name": data.recipient_name,
        "delivered_at": None,
        "created_at": None,
    }


@router.post("/{parcel_id}/resend-email")
async def resend_status_email(
    parcel_id: int,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow("""
        SELECT p.tracking_no, p.status, p.receiver_name, c.email
        FROM parcels p
        JOIN customers c ON c.id = p.sender_id
        WHERE p.id=$1
    """, parcel_id)
    if not row:
        raise HTTPException(404, detail="Parcel not found")
    if not row["email"]:
        raise HTTPException(400, detail="No email on file for sender")

    sent = send_status_update(row["email"], row["tracking_no"], row["status"], "")
    if not sent:
        raise HTTPException(500, detail="Failed to send email")

    return {"detail": "Email resent"}


@router.post("/{parcel_id}/receipt")
async def generate_receipt(
    parcel_id: int,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow("""
        SELECT p.*, c.name AS sender_name, c.phone AS sender_phone,
               pb.name AS pickup_branch_name, db.name AS delivery_branch_name
        FROM parcels p
        JOIN customers c ON c.id = p.sender_id
        LEFT JOIN branches pb ON pb.id = p.pickup_branch_id
        LEFT JOIN branches db ON db.id = p.delivery_branch_id
        WHERE p.id=$1
    """, parcel_id)
    if not row:
        raise HTTPException(404, detail="Parcel not found")

    pdf_bytes = generate_booking_receipt(
        tracking_no=row["tracking_no"],
        sender_name=row["sender_name"],
        sender_phone=row["sender_phone"],
        receiver_name=row["receiver_name"],
        receiver_phone=row["receiver_phone"],
        receiver_address=row["receiver_address"],
        parcel_type=row["parcel_type"],
        weight_kg=float(row["weight_kg"]),
        cost=float(row["cost"]),
        booking_date=str(row["booking_date"]),
        pickup_branch=row["pickup_branch_name"] or "",
        delivery_branch=row["delivery_branch_name"] or "",
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="receipt_{row["tracking_no"]}.pdf"'},
    )
