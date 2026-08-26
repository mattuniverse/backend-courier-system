import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_conn
from schemas import UserIn, UserOut
from utils.auth import get_current_user, require_admin, hash_password
from limiter import limiter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def list_users(
    current: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_conn),
):
    rows = await conn.fetch("SELECT id, username, full_name, role, status, created_at FROM users ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@router.post("/")
async def create_user(
    data: UserIn,
    current: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_conn),
):
    existing = await conn.fetchval("SELECT id FROM users WHERE username=$1", data.username.lower())
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    row = await conn.fetchrow(
        """INSERT INTO users (username, password, full_name, role)
           VALUES ($1, $2, $3, $4) RETURNING id, username, full_name, role, status, created_at""",
        data.username.lower(), hash_password(data.password), data.full_name, data.role,
    )
    return dict(row)


@router.patch("/{user_id}/toggle")
async def toggle_user(
    user_id: int,
    current: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_conn),
):
    if current["id"] == user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot toggle your own account")
    row = await conn.fetchrow(
        """UPDATE users SET status = CASE WHEN status='active' THEN 'inactive' ELSE 'active' END
           WHERE id=$1 RETURNING id, username, full_name, role, status""",
        user_id,
    )
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return dict(row)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current: dict = Depends(require_admin),
    conn: asyncpg.Connection = Depends(get_conn),
):
    if current["id"] == user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    result = await conn.execute("DELETE FROM users WHERE id=$1", user_id)
    if result == "DELETE 0":
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"detail": "User deleted"}
