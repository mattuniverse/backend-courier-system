import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from database import get_conn

router = APIRouter(tags=["Tracking"])


@router.get("/track/{tracking_no}")
async def track_parcel(tracking_no: str, conn: asyncpg.Connection = Depends(get_conn)):
    row = await conn.fetchrow("""
        SELECT p.*, c.name AS sender_name
        FROM parcels p
        JOIN customers c ON c.id = p.sender_id
        WHERE p.tracking_no=$1
    """, tracking_no)
    if not row:
        raise HTTPException(404, detail="Parcel not found")

    history = await conn.fetch("""
        SELECT * FROM parcel_tracking WHERE parcel_id=$1 ORDER BY updated_at DESC
    """, row["id"])

    return {"parcel": dict(row), "tracking_history": [dict(h) for h in history]}
