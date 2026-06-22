import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import String, Text, Boolean, Integer, Float, ForeignKey, Enum as SAEnum, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoomStatus(str, enum.Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    warehouse = "warehouse"
    published = "published"
    locked = "locked"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[RoomStatus] = mapped_column(SAEnum(RoomStatus, name="room_status"), nullable=False, default=RoomStatus.draft)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    layout_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    locked_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    submitted_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    approved_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    seats: Mapped[list["Seat"]] = relationship("Seat", back_populates="room", cascade="all, delete-orphan")
    versions: Mapped[list["RoomVersion"]] = relationship("RoomVersion", back_populates="room", cascade="all, delete-orphan")
    comments: Mapped[list["RoomComment"]] = relationship("RoomComment", back_populates="room", cascade="all, delete-orphan")


class RoomVersion(Base):
    __tablename__ = "room_versions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    room_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    layout_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    published_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    published_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    room: Mapped["Room"] = relationship("Room", back_populates="versions")


class RoomComment(Base):
    __tablename__ = "room_comments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    room_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    position_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now(), onupdate=func.now())

    room: Mapped["Room"] = relationship("Room", back_populates="comments")
