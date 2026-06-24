from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, get_current_account
from app.models.account import Account
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshRequest, RefreshResponse,
    ChangePasswordRequest, UserInfo, DepartmentSummary,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_user_info(account: Account) -> UserInfo:
    member = account.member
    dept = member.department if member else None
    return UserInfo(
        account_id=account.id,
        member_id=account.member_id,
        username=member.username if member else "",
        full_name=member.full_name if member else "",
        email=member.email if member else "",
        role=account.role,
        department=DepartmentSummary(id=dept.id, code=dept.code, name=dept.name) if dept else None,
        avatar_url=member.avatar_url if member else None,
    )


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    account = await auth_service.authenticate(body.identifier, body.password, db)
    access_token, refresh_token = auth_service.build_tokens(account)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=_build_user_info(account),
    )


@router.post("/logout", status_code=200)
async def logout(
    request: Request,
    account: Account = Depends(get_current_account),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        jti = payload.get("jti")
        exp = payload.get("exp", 0)
        if jti:
            ttl = max(0, exp - int(datetime.now(timezone.utc).timestamp()))
            await auth_service.blacklist_token(jti, ttl)
    except JWTError:
        pass
    return {"message": "Signed out"}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    access_token = await auth_service.refresh_access_token(body.refresh_token, db)
    return RefreshResponse(access_token=access_token)


@router.get("/me", response_model=UserInfo)
async def me(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    full_account = await auth_service.get_account_with_member(str(account.id), db)
    return _build_user_info(full_account)


@router.post("/change-password", status_code=200)
async def change_password(
    body: ChangePasswordRequest,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.change_password(account, body.current_password, body.new_password, db)
    return {"message": "Password updated"}
