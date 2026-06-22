import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import Text, ForeignKey, Enum as SAEnum, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RequestType(str, enum.Enum):
    register = "register"
    unregister = "unregister"


class RequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class SeatRequest(Base):
    __tablename__ = "seat_requests"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    seat_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    member_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    request_type: Mapped[RequestType] = mapped_column(SAEnum(RequestType, name="request_type"), nullable=False, default=RequestType.register)
    status: Mapped[RequestStatus] = mapped_column(SAEnum(RequestStatus, name="request_status"), nullable=False, default=RequestStatus.pending)
    requester_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    seat: Mapped["Seat"] = relationship("Seat", back_populates="seat_requests")
    member: Mapped["Member"] = relationship("Member", back_populates="seat_requests")
