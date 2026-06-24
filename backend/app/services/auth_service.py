from datetime import datetime, timezone

from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models.account import Account
from app.models.member import Member
from app.redis_client import get_redis
from app.utils.security import verify_password, hash_password, create_access_token, create_refresh_token

_INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Username or password is incorrect"}},
)


async def authenticate(identifier: str, password: str, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account)
        .join(Member, Account.member_id == Member.id)
        .where(
            (Member.username == identifier) | (Member.email == identifier),
            Account.is_active == True,
        )
        .options(joinedload(Account.member).joinedload(Member.department))
    )
    account = result.scalar_one_or_none()
    if not account or not account.password_hash:
        raise _INVALID_CREDENTIALS
    if not verify_password(password, account.password_hash):
        raise _INVALID_CREDENTIALS

    account.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(account, ["member"])
    return account


async def get_account_with_member(account_id: str, db: AsyncSession) -> Account:
    result = await db.execute(
        select(Account)
        .where(Account.id == account_id)
        .options(joinedload(Account.member).joinedload(Member.department))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Account not found"}})
    return account


async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    redis = await get_redis()
    if redis and ttl_seconds > 0:
        await redis.setex(f"jwt_blacklist:{jti}", ttl_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    redis = await get_redis()
    if not redis:
        return False
    try:
        return bool(await redis.exists(f"jwt_blacklist:{jti}"))
    except Exception:
        return False


def build_tokens(account: Account) -> tuple[str, str]:
    member = account.member
    access = create_access_token(
        account_id=str(account.id),
        member_id=str(account.member_id),
        role=account.role.value,
        username=member.username if member else "",
    )
    refresh = create_refresh_token(account_id=str(account.id))
    return access, refresh


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> str:
    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise ValueError
        account_id = payload.get("sub")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TOKEN_INVALID", "message": "Invalid refresh token"}},
        )

    account = await get_account_with_member(account_id, db)
    if not account.is_active:
        raise HTTPException(status_code=401, detail={"error": {"code": "TOKEN_INVALID", "message": "Account inactive"}})

    member = account.member
    return create_access_token(
        account_id=str(account.id),
        member_id=str(account.member_id),
        role=account.role.value,
        username=member.username if member else "",
    )


async def change_password(account: Account, current_password: str, new_password: str, db: AsyncSession) -> None:
    if not account.password_hash or not verify_password(current_password, account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Current password is incorrect"}},
        )
    account.password_hash = hash_password(new_password)
    await db.commit()
