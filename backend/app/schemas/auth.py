from uuid import UUID
from pydantic import BaseModel, Field
from app.models.account import UserRole


class DepartmentSummary(BaseModel):
    id: UUID
    code: str
    name: str

    model_config = {"from_attributes": True}


class UserInfo(BaseModel):
    account_id: UUID
    member_id: UUID
    username: str
    full_name: str
    email: str
    role: UserRole
    department: DepartmentSummary | None
    avatar_url: str | None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)
