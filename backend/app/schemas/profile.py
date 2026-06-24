from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.account import UserRole
from app.schemas.auth import DepartmentSummary


class ProfileDetail(BaseModel):
    account_id: UUID
    member_id: UUID
    username: str
    employee_id: str
    full_name: str
    email: str
    phone: str | None
    gender: str | None
    title: str | None
    department: DepartmentSummary | None
    role: UserRole
    avatar_url: str | None
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    phone: str | None = None
    avatar_url: str | None = None


class AssignmentSummary(BaseModel):
    id: UUID
    seat_id: UUID
    seat_code: str
    room_code: str
    room_name: str
    assignment_type: str
    hostname: str | None
    ip_address: str | None
    mac_address: str | None
    start_date: str | None

    model_config = {"from_attributes": True}


class ProfileAssignments(BaseModel):
    primary: AssignmentSummary | None
    secondary: list[AssignmentSummary]
