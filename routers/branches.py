import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from database import get_conn
from schemas import BranchIn
from utils.auth import get_current_user

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("/")
async def list_branches(
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("SELECT * FROM branches ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@router.post("/")
async def create_branch(
    data: BranchIn,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow(
        """INSERT INTO branches (name, city, address, phone)
           VALUES ($1, $2, $3, $4) RETURNING *""",
        data.name, data.city, data.address, data.phone,
    )
    return dict(row)


@router.delete("/{branch_id}")
async def delete_branch(
    branch_id: int,
    current: dict = Depends(get_current_user),
    conn: asyncpg.Connection = Depends(get_conn),
):
    result = await conn.execute("DELETE FROM branches WHERE id=$1", branch_id)
    if result == "DELETE 0":
        raise HTTPException(404, detail="Branch not found")
    return {"detail": "Branch deleted"}
