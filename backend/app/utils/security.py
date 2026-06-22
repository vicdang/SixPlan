from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(account_id: str, member_id: str, role: str, username: str) -> str:
    payload = {
        "sub": account_id,
        "member_id": member_id,
        "role": role,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(account_id: str) -> str:
    payload = {
        "sub": account_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days),
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
