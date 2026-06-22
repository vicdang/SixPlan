import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Text, Boolean, Integer, Float, ForeignKey, Enum as SAEnum, UniqueConstraint, Index, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeatStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"
    disabled = "disabled"
    maintenance = "maintenance"


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("room_id", "code", name="uq_seat_room_code"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    room_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seat_type: Mapped[str] = mapped_column(String(50), nullable=False, default="single")
    status: Mapped[SeatStatus] = mapped_column(SAEnum(SeatStatus, name="seat_status"), nullable=False, default=SeatStatus.available)
    project_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pos_x: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    pos_y: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    width: Mapped[float] = mapped_column(Float, nullable=False, default=60)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=60)
    rotation: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    max_secondary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    room: Mapped["Room"] = relationship("Room", back_populates="seats")
    project: Mapped["Project | None"] = relationship("Project", back_populates="seats")
    seat_facilities: Mapped[list["SeatFacility"]] = relationship("SeatFacility", back_populates="seat", cascade="all, delete-orphan")
    assignments: Mapped[list["SeatAssignment"]] = relationship("SeatAssignment", back_populates="seat")
    seat_requests: Mapped[list["SeatRequest"]] = relationship("SeatRequest", back_populates="seat")


class SeatFacility(Base):
    __tablename__ = "seat_facilities"

    seat_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("seats.id", ondelete="CASCADE"), primary_key=True)
    facility_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), primary_key=True)

    seat: Mapped["Seat"] = relationship("Seat", back_populates="seat_facilities")
    facility: Mapped["Facility"] = relationship("Facility", back_populates="seat_facilities")
