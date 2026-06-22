import enum
from datetime import datetime, date
from uuid import UUID

from sqlalchemy import String, Text, Boolean, Date, ForeignKey, Enum as SAEnum, Index, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, INET, MACADDR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AssignmentType(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"


class SeatAssignment(Base):
    __tablename__ = "seat_assignments"
    __table_args__ = (
        # Partial unique index: at most one active primary assignment per seat
        Index(
            "uq_active_primary_seat",
            "seat_id",
            unique=True,
            postgresql_where=text("assignment_type = 'primary' AND is_active = TRUE"),
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    seat_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    member_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    assignment_type: Mapped[AssignmentType] = mapped_column(SAEnum(AssignmentType, name="assignment_type"), nullable=False, default=AssignmentType.primary)
    hostname: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    mac_address: Mapped[str | None] = mapped_column(MACADDR, nullable=True)
    device_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    assigned_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    seat: Mapped["Seat"] = relationship("Seat", back_populates="assignments")
    member: Mapped["Member"] = relationship("Member", back_populates="assignments")
