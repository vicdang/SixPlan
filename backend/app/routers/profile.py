from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.dependencies import get_db, get_current_account
from app.models.account import Account
from app.models.assignment import SeatAssignment, AssignmentType
from app.models.member import Member
from app.models.seat import Seat
from app.models.room import Room
from app.schemas.auth import DepartmentSummary, ChangePasswordRequest
from app.schemas.profile import ProfileDetail, ProfileUpdate, ProfileAssignments, AssignmentSummary
from app.services import auth_service

router = APIRouter(prefix="/profile", tags=["profile"])


async def _get_full_account(account: Account, db: AsyncSession) -> Account:
    return await auth_service.get_account_with_member(str(account.id), db)


def _build_profile(account: Account) -> ProfileDetail:
    member = account.member
    dept = member.department if member else None
    return ProfileDetail(
        account_id=account.id,
        member_id=account.member_id,
        username=member.username if member else "",
        employee_id=member.employee_id if member else "",
        full_name=member.full_name if member else "",
        email=member.email if member else "",
        phone=member.phone if member else None,
        gender=member.gender if member else None,
        title=member.title if member else None,
        department=DepartmentSummary(id=dept.id, code=dept.code, name=dept.name) if dept else None,
        role=account.role,
        avatar_url=member.avatar_url if member else None,
        last_login_at=account.last_login_at,
    )


@router.get("", response_model=ProfileDetail)
async def get_profile(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    full = await _get_full_account(account, db)
    return _build_profile(full)


@router.put("", response_model=ProfileDetail)
async def update_profile(
    body: ProfileUpdate,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    full = await _get_full_account(account, db)
    member = full.member
    if body.phone is not None:
        member.phone = body.phone or None
    if body.avatar_url is not None:
        member.avatar_url = body.avatar_url or None
    await db.commit()
    await db.refresh(full, ["member"])
    return _build_profile(full)


@router.get("/assignments", response_model=ProfileAssignments)
async def get_assignments(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SeatAssignment)
        .where(
            SeatAssignment.member_id == account.member_id,
            SeatAssignment.is_active == True,
        )
        .options(
            joinedload(SeatAssignment.seat).joinedload(Seat.room)
        )
    )
    assignments = result.scalars().all()

    def _to_summary(a: SeatAssignment) -> AssignmentSummary:
        seat: Seat = a.seat
        room: Room = seat.room
        return AssignmentSummary(
            id=a.id,
            seat_id=seat.id,
            seat_code=seat.code,
            room_code=room.code,
            room_name=room.name,
            assignment_type=a.assignment_type.value,
            hostname=a.hostname,
            ip_address=str(a.ip_address) if a.ip_address else None,
            mac_address=str(a.mac_address) if a.mac_address else None,
            start_date=str(a.start_date) if a.start_date else None,
        )

    primary = next(
        (a for a in assignments if a.assignment_type == AssignmentType.primary), None
    )
    secondary = [a for a in assignments if a.assignment_type == AssignmentType.secondary]

    return ProfileAssignments(
        primary=_to_summary(primary) if primary else None,
        secondary=[_to_summary(a) for a in secondary],
    )


@router.post("/change-password", status_code=200)
async def change_password(
    body: ChangePasswordRequest,
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.change_password(account, body.current_password, body.new_password, db)
    return {"message": "Password updated"}
