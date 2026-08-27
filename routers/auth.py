import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from database import get_conn
from schemas import TokenOut
from utils.auth import verify_password, create_access_token, get_current_user
from limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    conn: asyncpg.Connection = Depends(get_conn),
):
    row = await conn.fetchrow(
        "SELECT id, username, full_name, role, password, status FROM users WHERE username=$1",
        form.username.lower(),
    )
    if not row or not verify_password(form.password, row["password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if row["status"] != "active":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account disabled")

    token = create_access_token({"sub": str(row["id"]), "role": row["role"]})
    return TokenOut(
        access_token=token,
        user={
            "id": row["id"],
            "username": row["username"],
            "full_name": row["full_name"],
            "role": row["role"],
        },
    )


@router.post("/logout")
async def logout(current: dict = Depends(get_current_user)):
    return {"detail": "Logged out"}
