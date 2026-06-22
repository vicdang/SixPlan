"""Initial schema and seed data

Revision ID: 001
Revises:
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    op.execute("CREATE TYPE user_role AS ENUM ('viewer', 'user', 'manager', 'admin')")
    op.execute("CREATE TYPE seat_status AS ENUM ('available', 'occupied', 'reserved', 'disabled', 'maintenance')")
    op.execute("CREATE TYPE room_status AS ENUM ('draft', 'pending_approval', 'warehouse', 'published', 'locked')")
    op.execute("CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled')")
    op.execute("CREATE TYPE request_type AS ENUM ('register', 'unregister')")
    op.execute("CREATE TYPE assignment_type AS ENUM ('primary', 'secondary')")
    op.execute("CREATE TYPE notification_type AS ENUM ('request_submitted', 'request_approved', 'request_rejected', 'seat_assigned', 'seat_unassigned', 'room_comment')")

    # departments
    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # members
    op.create_table(
        "members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("employee_id", sa.String(50), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_members_department", "members", ["department_id"])
    op.create_index("idx_members_employee_id", "members", ["employee_id"])

    # accounts
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE"), unique=True, nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("google_id", sa.String(255), unique=True, nullable=True),
        sa.Column("role", sa.Enum("viewer", "user", "manager", "admin", name="user_role", create_type=False), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # projects
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("color", sa.String(7), nullable=False, server_default="#6366f1"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # facilities
    op.create_table(
        "facilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # rooms
    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("draft", "pending_approval", "warehouse", "published", "locked", name="room_status", create_type=False), nullable=False, server_default="draft"),
        sa.Column("version", sa.Integer, nullable=False, server_default="0"),
        sa.Column("layout_data", postgresql.JSONB, nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # room_versions
    op.create_table(
        "room_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("layout_data", postgresql.JSONB, nullable=False),
        sa.Column("published_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("note", sa.Text, nullable=True),
    )

    # room_comments
    op.create_table(
        "room_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("position_x", sa.Float, nullable=True),
        sa.Column("position_y", sa.Float, nullable=True),
        sa.Column("resolved", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # seats
    op.create_table(
        "seats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("label", sa.String(100), nullable=True),
        sa.Column("seat_type", sa.String(50), nullable=False, server_default="single"),
        sa.Column("status", sa.Enum("available", "occupied", "reserved", "disabled", "maintenance", name="seat_status", create_type=False), nullable=False, server_default="available"),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("pos_x", sa.Float, nullable=False, server_default="0"),
        sa.Column("pos_y", sa.Float, nullable=False, server_default="0"),
        sa.Column("width", sa.Float, nullable=False, server_default="60"),
        sa.Column("height", sa.Float, nullable=False, server_default="60"),
        sa.Column("rotation", sa.Float, nullable=False, server_default="0"),
        sa.Column("max_secondary", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("room_id", "code", name="uq_seat_room_code"),
    )
    op.create_index("idx_seats_room", "seats", ["room_id"])
    op.create_index("idx_seats_project", "seats", ["project_id"])
    op.create_index("idx_seats_status", "seats", ["status"])

    # seat_facilities
    op.create_table(
        "seat_facilities",
        sa.Column("seat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("seats.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("facility_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("facilities.id", ondelete="CASCADE"), primary_key=True),
    )

    # seat_assignments
    op.create_table(
        "seat_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("seat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("seats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assignment_type", sa.Enum("primary", "secondary", name="assignment_type", create_type=False), nullable=False, server_default="primary"),
        sa.Column("hostname", sa.String(200), nullable=True),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("mac_address", postgresql.MACADDR, nullable=True),
        sa.Column("device_note", sa.Text, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_active_primary_seat ON seat_assignments (seat_id) "
        "WHERE assignment_type = 'primary' AND is_active = TRUE"
    )
    op.create_index("idx_assignments_member", "seat_assignments", ["member_id"], postgresql_where=sa.text("is_active = TRUE"))

    # seat_requests
    op.create_table(
        "seat_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("seat_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("seats.id", ondelete="CASCADE"), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("members.id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_type", sa.Enum("register", "unregister", name="request_type", create_type=False), nullable=False, server_default="register"),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", "cancelled", name="request_status", create_type=False), nullable=False, server_default="pending"),
        sa.Column("requester_note", sa.Text, nullable=True),
        sa.Column("reviewer_note", sa.Text, nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_requests_status", "seat_requests", ["status"])

    # notifications
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("recipient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("request_submitted", "request_approved", "request_rejected", "seat_assigned", "seat_unassigned", "room_comment", name="notification_type", create_type=False), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_notifications_recipient", "notifications", ["recipient_id"], postgresql_where=sa.text("is_read = FALSE"))

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("before_data", postgresql.JSONB, nullable=True),
        sa.Column("after_data", postgresql.JSONB, nullable=True),
        sa.Column("ip_address", postgresql.INET, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_audit_entity", "audit_logs", ["entity_type", "entity_id"])
    op.execute("CREATE INDEX idx_audit_created ON audit_logs (created_at DESC)")

    # ---- Seed data ----
    _seed_data()


def _seed_data() -> None:
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash("ChangeMe@2026")

    # System department
    op.execute(
        f"INSERT INTO departments (id, code, name, description) "
        f"VALUES (gen_random_uuid(), 'SYS', 'System', 'System default department')"
    )

    # Admin member
    op.execute(
        "INSERT INTO members (id, employee_id, username, full_name, email, gender, department_id, is_active) "
        "SELECT gen_random_uuid(), 'EMP00001', 'admin', 'System Administrator', "
        "'admin@company.local', 'other', id, TRUE "
        "FROM departments WHERE code = 'SYS'"
    )

    # Admin account
    op.execute(
        f"INSERT INTO accounts (id, member_id, password_hash, role, is_active) "
        f"SELECT gen_random_uuid(), m.id, '{password_hash}', 'admin', TRUE "
        f"FROM members m WHERE m.username = 'admin'"
    )

    # Dev departments
    dev_depts = [
        ("IT", "Information Technology"),
        ("DEV", "Development"),
        ("QA", "Quality Assurance"),
        ("HR", "Human Resources"),
        ("BA", "Business Analyst"),
        ("PM", "Project Management"),
    ]
    for code, name in dev_depts:
        op.execute(
            f"INSERT INTO departments (id, code, name) "
            f"VALUES (gen_random_uuid(), '{code}', '{name}')"
        )

    # Default facilities
    facilities = [
        ("Monitor", "monitor", 1),
        ("Standing Desk", "armchair", 2),
        ("Near Window", "panels-top-left", 3),
        ("Near AC", "snowflake", 4),
        ("Near Door", "door-open", 5),
        ("Power Outlet", "plug", 6),
        ("LAN Port", "ethernet-port", 7),
        ("Locker", "lock", 8),
        ("Whiteboard", "presentation", 9),
        ("Phone", "phone", 10),
    ]
    for name, icon, order in facilities:
        op.execute(
            f"INSERT INTO facilities (id, name, icon, is_default, sort_order, is_active) "
            f"VALUES (gen_random_uuid(), '{name}', '{icon}', TRUE, {order}, TRUE)"
        )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_table("seat_requests")
    op.drop_table("seat_assignments")
    op.drop_table("seat_facilities")
    op.drop_table("seats")
    op.drop_table("room_comments")
    op.drop_table("room_versions")
    op.drop_table("rooms")
    op.drop_table("facilities")
    op.drop_table("projects")
    op.drop_table("accounts")
    op.drop_table("members")
    op.drop_table("departments")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS assignment_type")
    op.execute("DROP TYPE IF EXISTS request_type")
    op.execute("DROP TYPE IF EXISTS request_status")
    op.execute("DROP TYPE IF EXISTS room_status")
    op.execute("DROP TYPE IF EXISTS seat_status")
    op.execute("DROP TYPE IF EXISTS user_role")
