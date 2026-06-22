# SEAT MANAGEMENT SYSTEM — TECHNICAL SPECIFICATION
**Version:** 1.0 | **Status:** Ready for Claude Code Implementation

---

## TABLE OF CONTENTS
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Repository Structure](#3-repository-structure)
4. [Database Schema](#4-database-schema)
5. [RBAC Matrix](#5-rbac-matrix)
6. [API Specification](#6-api-specification)
7. [UI Design System](#7-ui-design-system)
8. [Floor Plan Editor](#8-floor-plan-editor)
9. [Feature Modules](#9-feature-modules)
10. [Notification Architecture](#10-notification-architecture)
11. [Deployment](#11-deployment)
12. [Implementation Phases](#12-implementation-phases)
13. [Estimation](#13-estimation)

---

## 1. PROJECT OVERVIEW

### Purpose
An internal **Workplace Seat Management System** that enables employees to locate, register, and manage seat assignments across office rooms. Secondary purpose: IT Helpdesk asset tracking (hostname/IP/MAC) and quick member location lookup.

### Core Concepts
| Concept | Description |
|---|---|
| **Room** | Physical office space identified by code (e.g., `C703` = Block C, Floor 7, Room 03). Has a visual floor plan layout. |
| **Seat** | A physical desk/workstation inside a Room. Has one primary occupant and zero-to-many secondary device slots. |
| **Primary Assignment** | One member "owns" the seat as their main workstation. |
| **Secondary Slot** | Additional members place a device at a seat without occupying it physically (hostname/IP/MAC tracked). |
| **Project** | A managed entity (name + color) used to group/label seats on the floor plan. |
| **Floor Plan** | Admin-designed visual layout of a room using a grid-based drag-drop canvas editor. Versioned. |

### Key Differentiators
- Visual floor plan editor with room elements (doors, pillars, AC units, etc.)
- Seat color-coding by Project assignment
- Member search → navigate to seat on floor plan
- IT asset tracking on secondary device slots
- Full audit log on all assignment changes

---

## 2. TECH STACK

### Frontend
| Layer | Choice | Rationale |
|---|---|---|
| Framework | **React 18 + TypeScript + Vite** | Fast DX, strong typing, ecosystem |
| Styling | **Tailwind CSS v3** | Utility-first, consistent dark theme, no inline CSS |
| Component Library | **shadcn/ui** | Accessible, Tailwind-native, dark mode first, copy-paste model |
| Floor Plan Canvas | **Konva.js + react-konva** | Canvas-based, drag/drop, transforms, performant at scale |
| State Management | **Zustand** | Lightweight, minimal boilerplate |
| Server State | **TanStack Query v5** | Caching, background refetch, optimistic updates |
| Routing | **React Router v6** | Nested layouts, protected routes |
| Forms | **React Hook Form + Zod** | Type-safe validation |
| HTTP Client | **Axios** | Interceptors for auth token injection |
| Icons | **Lucide React** | Consistent, tree-shakable — no emojis in UI |
| Notifications (UI) | **Sonner** | Toast notifications, minimal |

### Backend
| Layer | Choice | Rationale |
|---|---|---|
| Framework | **FastAPI + Python 3.11** | Async, auto OpenAPI docs, fast |
| ORM | **SQLAlchemy 2.0 (async)** | Modern async support, typed models |
| Migrations | **Alembic** | Schema versioning |
| Database | **PostgreSQL 15** | JSONB for seat layout data, robust |
| Cache / Session | **Redis 7** | JWT blacklist, notification queue |
| Auth | **JWT (python-jose) + bcrypt** | Stateless, Google OAuth2 ready |
| Background Tasks | **FastAPI BackgroundTasks** (MVP) → Celery (Phase 2) | Notification dispatch |
| File Import | **pandas + openpyxl** | CSV/Excel member import |
| Validation | **Pydantic v2** | Schema validation |

### Infrastructure
| Layer | Choice |
|---|---|
| Containerization | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| Database | PostgreSQL (Docker volume) |
| Cache | Redis (Docker volume) |
| Future VPS deploy | Docker Compose (same config, env swap) |

---

## 3. REPOSITORY STRUCTURE

```
seat-management/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── README.md
├── CLAUDE.md                          # This spec file (abridged for agent)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings (pydantic BaseSettings)
│   │   ├── database.py                # Async SQLAlchemy engine + session
│   │   ├── dependencies.py            # get_db, get_current_user, role guards
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   ├── member.py
│   │   │   ├── department.py
│   │   │   ├── room.py
│   │   │   ├── seat.py
│   │   │   ├── project.py
│   │   │   ├── facility.py
│   │   │   ├── assignment.py
│   │   │   ├── seat_request.py
│   │   │   ├── notification.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── account.py
│   │   │   ├── member.py
│   │   │   ├── room.py
│   │   │   ├── seat.py
│   │   │   ├── project.py
│   │   │   ├── facility.py
│   │   │   ├── assignment.py
│   │   │   ├── seat_request.py
│   │   │   └── notification.py
│   │   │
│   │   ├── routers/                   # FastAPI routers
│   │   │   ├── auth.py
│   │   │   ├── accounts.py
│   │   │   ├── members.py
│   │   │   ├── departments.py
│   │   │   ├── rooms.py
│   │   │   ├── seats.py
│   │   │   ├── projects.py
│   │   │   ├── facilities.py
│   │   │   ├── assignments.py
│   │   │   ├── seat_requests.py
│   │   │   ├── notifications.py
│   │   │   ├── search.py
│   │   │   └── audit_logs.py
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── member_service.py
│   │   │   ├── room_service.py
│   │   │   ├── seat_service.py
│   │   │   ├── assignment_service.py
│   │   │   ├── request_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── import_service.py
│   │   │   └── audit_service.py
│   │   │
│   │   └── utils/
│   │       ├── security.py            # JWT, bcrypt helpers
│   │       ├── pagination.py
│   │       └── constants.py
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── components.json                # shadcn/ui config
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        │
        ├── lib/
        │   ├── axios.ts               # Axios instance + interceptors
        │   ├── queryClient.ts         # TanStack Query config
        │   └── utils.ts               # cn(), formatDate(), etc.
        │
        ├── store/                     # Zustand stores
        │   ├── authStore.ts
        │   ├── editorStore.ts         # Floor plan editor state
        │   └── notificationStore.ts
        │
        ├── types/                     # TypeScript interfaces
        │   ├── auth.ts
        │   ├── member.ts
        │   ├── room.ts
        │   ├── seat.ts
        │   ├── project.ts
        │   └── common.ts
        │
        ├── hooks/                     # TanStack Query hooks
        │   ├── useAuth.ts
        │   ├── useRooms.ts
        │   ├── useSeats.ts
        │   ├── useMembers.ts
        │   ├── useProjects.ts
        │   ├── useAssignments.ts
        │   └── useNotifications.ts
        │
        ├── components/
        │   ├── ui/                    # shadcn/ui primitives (auto-generated)
        │   ├── layout/
        │   │   ├── AppShell.tsx       # Sidebar + topbar wrapper
        │   │   ├── Sidebar.tsx
        │   │   ├── Topbar.tsx
        │   │   └── PageHeader.tsx
        │   ├── common/
        │   │   ├── DataTable.tsx      # Reusable table with sort/filter/pagination
        │   │   ├── StatusBadge.tsx    # Seat/request status badge
        │   │   ├── RoleBadge.tsx
        │   │   ├── ConfirmDialog.tsx
        │   │   ├── EmptyState.tsx
        │   │   └── LoadingSpinner.tsx
        │   ├── seat/
        │   │   ├── SeatCard.tsx       # Seat info panel (popup on map click)
        │   │   ├── SeatStatusIcon.tsx
        │   │   └── SeatMetaForm.tsx   # Edit seat metadata form
        │   ├── floor-plan/
        │   │   ├── FloorPlanViewer.tsx   # Read-only viewer (Konva)
        │   │   ├── FloorPlanEditor.tsx   # Admin editor (Konva)
        │   │   ├── EditorToolbar.tsx
        │   │   ├── EditorSidebar.tsx
        │   │   ├── shapes/
        │   │   │   ├── SeatShape.tsx
        │   │   │   ├── RoomElement.tsx   # Door, window, pillar, etc.
        │   │   │   └── SelectionBox.tsx
        │   │   └── PropertiesPanel.tsx
        │   └── notifications/
        │       ├── NotificationBell.tsx
        │       └── NotificationDropdown.tsx
        │
        └── pages/
            ├── auth/
            │   └── LoginPage.tsx
            ├── dashboard/
            │   └── DashboardPage.tsx
            ├── rooms/
            │   ├── RoomListPage.tsx
            │   ├── RoomViewPage.tsx      # Floor plan viewer
            │   └── RoomEditorPage.tsx    # Floor plan editor (admin)
            ├── seats/
            │   └── SeatDetailPage.tsx
            ├── members/
            │   ├── MemberListPage.tsx
            │   └── MemberDetailPage.tsx
            ├── search/
            │   └── SearchPage.tsx
            ├── requests/
            │   └── RequestsPage.tsx
            ├── projects/
            │   └── ProjectsPage.tsx
            ├── admin/
            │   ├── AccountsPage.tsx
            │   ├── DepartmentsPage.tsx
            │   ├── FacilitiesPage.tsx
            │   └── AuditLogPage.tsx
            └── errors/
                ├── NotFoundPage.tsx
                └── ForbiddenPage.tsx
```

---

## 4. DATABASE SCHEMA

### 4.1 Enums

```sql
CREATE TYPE user_role AS ENUM ('viewer', 'user', 'manager', 'admin');
CREATE TYPE seat_status AS ENUM ('available', 'occupied', 'reserved', 'disabled', 'maintenance');
CREATE TYPE room_status AS ENUM ('draft', 'pending_approval', 'warehouse', 'published', 'locked');
CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');
CREATE TYPE request_type AS ENUM ('register', 'unregister');
CREATE TYPE assignment_type AS ENUM ('primary', 'secondary');
CREATE TYPE notification_type AS ENUM ('request_submitted', 'request_approved', 'request_rejected', 'seat_assigned', 'seat_unassigned', 'room_comment');
```

### 4.2 Core Tables

```sql
-- DEPARTMENTS (flat list)
CREATE TABLE departments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(20) UNIQUE NOT NULL,   -- e.g., "IT", "HR", "C703-ADMIN"
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- MEMBERS
CREATE TABLE members (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     VARCHAR(50) UNIQUE NOT NULL,  -- from HRM
    username        VARCHAR(100) UNIQUE NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    email           VARCHAR(200) UNIQUE NOT NULL,
    gender          VARCHAR(10),                  -- 'male', 'female', 'other'
    phone           VARCHAR(30),
    title           VARCHAR(100),
    avatar_url      VARCHAR(500),
    department_id   UUID REFERENCES departments(id) ON DELETE SET NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ACCOUNTS (auth)
CREATE TABLE accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id       UUID UNIQUE REFERENCES members(id) ON DELETE CASCADE,
    password_hash   VARCHAR(255),               -- NULL if Google-only
    google_id       VARCHAR(255) UNIQUE,        -- for future Google OAuth
    role            user_role NOT NULL DEFAULT 'user',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- PROJECTS
CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    code        VARCHAR(50) UNIQUE NOT NULL,
    color       VARCHAR(7) NOT NULL DEFAULT '#6366f1',  -- hex color
    description TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- FACILITIES (admin-managed list)
CREATE TABLE facilities (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    icon        VARCHAR(50),          -- Lucide icon name
    is_default  BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Default facilities seed data:
-- Monitor, Standing Desk, Near Window, Near AC, Near Door,
-- Power Outlet, LAN Port, Locker, Whiteboard, Phone

-- ROOMS
CREATE TABLE rooms (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "C703"
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    capacity        INTEGER NOT NULL DEFAULT 0,   -- total physical seats
    status          room_status NOT NULL DEFAULT 'draft',
    version         INTEGER NOT NULL DEFAULT 0,
    -- Layout stored as JSONB (Konva stage JSON)
    layout_data     JSONB,
    -- Lock state
    locked_at       TIMESTAMPTZ,
    locked_by       UUID REFERENCES accounts(id),
    -- Approval
    submitted_by    UUID REFERENCES accounts(id),
    submitted_at    TIMESTAMPTZ,
    approved_by     UUID REFERENCES accounts(id),
    approved_at     TIMESTAMPTZ,
    published_at    TIMESTAMPTZ,
    created_by      UUID REFERENCES accounts(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ROOM VERSIONS (snapshot on each publish)
CREATE TABLE room_versions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id     UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    version     INTEGER NOT NULL,
    layout_data JSONB NOT NULL,
    published_by UUID REFERENCES accounts(id),
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    note        TEXT
);

-- ROOM COMMENTS (manager feedback on floor plan)
CREATE TABLE room_comments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id     UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    account_id  UUID NOT NULL REFERENCES accounts(id),
    content     TEXT NOT NULL,
    position_x  FLOAT,    -- optional: pin comment to a location on canvas
    position_y  FLOAT,
    resolved    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- SEATS
CREATE TABLE seats (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id         UUID NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    code            VARCHAR(50) NOT NULL,          -- e.g., "C703-A01"
    label           VARCHAR(100),                  -- display label on map
    seat_type       VARCHAR(50) NOT NULL DEFAULT 'single',
    -- seat_type: single | double | double_facing | meeting_round | executive
    status          seat_status NOT NULL DEFAULT 'available',
    project_id      UUID REFERENCES projects(id) ON DELETE SET NULL,
    description     TEXT,
    -- Canvas position/size (mirrored from layout_data for query purposes)
    pos_x           FLOAT NOT NULL DEFAULT 0,
    pos_y           FLOAT NOT NULL DEFAULT 0,
    width           FLOAT NOT NULL DEFAULT 60,
    height          FLOAT NOT NULL DEFAULT 60,
    rotation        FLOAT NOT NULL DEFAULT 0,
    max_secondary   INTEGER,                      -- NULL = unlimited
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (room_id, code)
);

-- SEAT FACILITIES (M:N)
CREATE TABLE seat_facilities (
    seat_id         UUID NOT NULL REFERENCES seats(id) ON DELETE CASCADE,
    facility_id     UUID NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    PRIMARY KEY (seat_id, facility_id)
);

-- SEAT ASSIGNMENTS (primary + secondary)
CREATE TABLE seat_assignments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seat_id         UUID NOT NULL REFERENCES seats(id) ON DELETE CASCADE,
    member_id       UUID NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    assignment_type assignment_type NOT NULL DEFAULT 'primary',
    -- Device info (secondary only)
    hostname        VARCHAR(200),
    ip_address      INET,
    mac_address     MACADDR,
    device_note     TEXT,
    -- Time range (optional)
    start_date      DATE,
    end_date        DATE,
    -- Assignment meta
    assigned_by     UUID NOT NULL REFERENCES accounts(id),
    note            TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Only one active primary assignment per seat
    CONSTRAINT uq_primary_assignment EXCLUDE USING btree (
        seat_id WITH =,
        assignment_type WITH =,
        is_active WITH =
    ) WHERE (assignment_type = 'primary' AND is_active = TRUE)
);

-- SEAT REQUESTS (member self-registration queue)
CREATE TABLE seat_requests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seat_id         UUID NOT NULL REFERENCES seats(id) ON DELETE CASCADE,
    member_id       UUID NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    request_type    request_type NOT NULL DEFAULT 'register',
    status          request_status NOT NULL DEFAULT 'pending',
    requester_note  TEXT,
    reviewer_note   TEXT,
    reviewed_by     UUID REFERENCES accounts(id),
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- NOTIFICATIONS
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id    UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    type            notification_type NOT NULL,
    title           VARCHAR(200) NOT NULL,
    body            TEXT,
    reference_type  VARCHAR(50),    -- 'seat_request', 'assignment', 'room_comment'
    reference_id    UUID,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- AUDIT LOGS
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID REFERENCES accounts(id) ON DELETE SET NULL,
    action          VARCHAR(100) NOT NULL,  -- e.g., 'seat.assign', 'room.publish'
    entity_type     VARCHAR(50) NOT NULL,   -- 'seat', 'room', 'assignment', etc.
    entity_id       UUID,
    before_data     JSONB,
    after_data      JSONB,
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- INDEXES
CREATE INDEX idx_members_department ON members(department_id);
CREATE INDEX idx_members_employee_id ON members(employee_id);
CREATE INDEX idx_seats_room ON seats(room_id);
CREATE INDEX idx_seats_project ON seats(project_id);
CREATE INDEX idx_seats_status ON seats(status);
CREATE INDEX idx_assignments_seat ON seat_assignments(seat_id) WHERE is_active = TRUE;
CREATE INDEX idx_assignments_member ON seat_assignments(member_id) WHERE is_active = TRUE;
CREATE INDEX idx_requests_status ON seat_requests(status);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_id) WHERE is_read = FALSE;
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
```

### 4.3 Layout Data Structure (JSONB)

`rooms.layout_data` stores the Konva stage JSON. Structure:

```json
{
  "canvas": {
    "width": 1200,
    "height": 800,
    "background": "#1e1e2e"
  },
  "elements": [
    {
      "id": "elem_uuid",
      "type": "door",
      "x": 100, "y": 0, "width": 60, "height": 10,
      "rotation": 0,
      "label": "Main Entrance"
    },
    {
      "id": "elem_uuid2",
      "type": "pillar",
      "x": 200, "y": 150, "width": 30, "height": 30,
      "rotation": 0
    }
  ],
  "seats": [
    {
      "id": "seat_db_uuid",
      "type": "single",
      "x": 300, "y": 200,
      "width": 60, "height": 60,
      "rotation": 0,
      "label": "C703-A01"
    }
  ]
}
```

---

## 5. RBAC MATRIX

### 5.1 Roles

| Role | Code | Description |
|---|---|---|
| Viewer | `viewer` | Read-only: view published rooms, seat info, member locations |
| User | `user` | Viewer + submit seat registration requests |
| Manager | `manager` | User + approve requests, assign seats, comment on floor plans, view warehouse |
| Admin | `admin` | Full access: CRUD all entities, manage floor plans, publish rooms |

### 5.2 Permission Matrix

| Feature | Viewer | User | Manager | Admin |
|---|:---:|:---:|:---:|:---:|
| View published floor plan | ✓ | ✓ | ✓ | ✓ |
| View seat details & occupant | ✓ | ✓ | ✓ | ✓ |
| Search member → locate seat | ✓ | ✓ | ✓ | ✓ |
| Submit seat registration request | — | ✓ | ✓ | ✓ |
| Cancel own pending request | — | ✓ | ✓ | ✓ |
| View own assignments | — | ✓ | ✓ | ✓ |
| View all seat requests | — | — | ✓ | ✓ |
| Approve / reject requests | — | — | ✓ | ✓ |
| Assign member to seat (direct) | — | — | ✓ | ✓ |
| Add secondary slot | — | — | ✓ | ✓ |
| View warehouse (pending-approval rooms) | — | — | ✓ | ✓ |
| Comment on floor plan | — | — | ✓ | ✓ |
| View all members | — | — | ✓ | ✓ |
| CRUD rooms (create, design, lock, publish) | — | — | — | ✓ |
| CRUD seats (metadata, facilities) | — | — | — | ✓ |
| CRUD members | — | — | — | ✓ |
| CRUD accounts (roles, activation) | — | — | — | ✓ |
| CRUD departments | — | — | — | ✓ |
| CRUD projects | — | — | — | ✓ |
| CRUD facilities | — | — | — | ✓ |
| Import members via CSV | — | — | — | ✓ |
| View audit logs | — | — | — | ✓ |

### 5.3 Room Status Transition

```
draft → pending_approval → warehouse → published → locked → published
                                           ↑
                                    (manager comment → admin re-edits → back to warehouse)
```

| Status | Who can view | Who can edit |
|---|---|---|
| `draft` | Admin only | Admin (creator) |
| `pending_approval` | Admin + Manager | Read-only (awaiting approval) |
| `warehouse` | Admin + Manager | Admin (with comments from Manager) |
| `published` | Everyone | Admin (must lock first) |
| `locked` | Everyone (banner shown) | Admin (editor unlocked for them) |

---

## 6. API SPECIFICATION

**Base URL:** `/api/v1`  
**Auth header:** `Authorization: Bearer <JWT>`  
**Content-Type:** `application/json`

### 6.1 Auth

```
POST   /auth/login              → { access_token, token_type, expires_in, user }
POST   /auth/logout             → 200 (blacklist token)
POST   /auth/refresh            → { access_token }
GET    /auth/me                 → AccountWithMember
POST   /auth/change-password    → 200
```

### 6.2 Members

```
GET    /members                 → PaginatedList[MemberSummary]  (manager/admin)
GET    /members/{id}            → MemberDetail
POST   /members                 → MemberDetail  (admin)
PUT    /members/{id}            → MemberDetail  (admin)
DELETE /members/{id}            → 204  (admin, soft delete)
POST   /members/import          → ImportResult  (admin, CSV/Excel)
GET    /members/{id}/seats      → List[SeatAssignmentSummary]
```

### 6.3 Accounts

```
GET    /accounts                → PaginatedList[Account]  (admin)
POST   /accounts                → Account  (admin)
PUT    /accounts/{id}           → Account  (admin)
PUT    /accounts/{id}/role      → Account  (admin)
PUT    /accounts/{id}/activate  → Account  (admin)
DELETE /accounts/{id}           → 204  (admin)
```

### 6.4 Departments

```
GET    /departments             → List[Department]
POST   /departments             → Department  (admin)
PUT    /departments/{id}        → Department  (admin)
DELETE /departments/{id}        → 204  (admin)
```

### 6.5 Rooms

```
GET    /rooms                   → PaginatedList[RoomSummary]  (status filter by role)
GET    /rooms/{id}              → RoomDetail (with layout_data)
POST   /rooms                   → RoomDetail  (admin)
PUT    /rooms/{id}              → RoomDetail  (admin, not-locked)
DELETE /rooms/{id}              → 204  (admin, draft only)

PUT    /rooms/{id}/layout       → RoomDetail  (admin, saves layout_data)
POST   /rooms/{id}/submit       → RoomDetail  (admin → pending_approval)
POST   /rooms/{id}/approve      → RoomDetail  (admin/manager → warehouse)
POST   /rooms/{id}/publish      → RoomDetail  (admin → published, version++)
POST   /rooms/{id}/lock         → RoomDetail  (admin → locked)
POST   /rooms/{id}/unlock       → RoomDetail  (admin → published)

GET    /rooms/{id}/comments     → List[RoomComment]
POST   /rooms/{id}/comments     → RoomComment  (manager/admin)
PUT    /rooms/{id}/comments/{cid} → RoomComment  (admin, resolve)
DELETE /rooms/{id}/comments/{cid} → 204  (admin)

GET    /rooms/{id}/versions     → List[RoomVersionSummary]  (admin)
GET    /rooms/{id}/versions/{v} → RoomVersion  (admin)
```

### 6.6 Seats

```
GET    /rooms/{room_id}/seats         → List[SeatWithAssignment]
GET    /seats/{id}                    → SeatDetail
POST   /rooms/{room_id}/seats         → SeatDetail  (admin)
PUT    /seats/{id}                    → SeatDetail  (admin)
DELETE /seats/{id}                    → 204  (admin)
PUT    /seats/{id}/facilities         → SeatDetail  (admin)
GET    /seats/{id}/assignments        → List[AssignmentRecord]
GET    /seats/{id}/history           → List[AuditLog]
```

### 6.7 Projects

```
GET    /projects                → List[Project]
POST   /projects                → Project  (admin)
PUT    /projects/{id}           → Project  (admin)
DELETE /projects/{id}           → 204  (admin)
```

### 6.8 Facilities

```
GET    /facilities              → List[Facility]
POST   /facilities              → Facility  (admin)
PUT    /facilities/{id}         → Facility  (admin)
DELETE /facilities/{id}         → 204  (admin)
```

### 6.9 Assignments

```
GET    /assignments                           → PaginatedList (manager/admin, filterable)
POST   /assignments                           → Assignment  (manager/admin — direct assign)
PUT    /assignments/{id}                      → Assignment  (manager/admin)
DELETE /assignments/{id}                      → 204  (manager/admin, deactivate)
POST   /seats/{id}/assign-primary             → Assignment  (manager/admin shortcut)
POST   /seats/{id}/assign-secondary           → Assignment  (manager/admin, with device info)
```

### 6.10 Seat Requests

```
GET    /seat-requests                         → PaginatedList[SeatRequest]  (filtered by role)
POST   /seat-requests                         → SeatRequest  (user+ self-register)
GET    /seat-requests/{id}                    → SeatRequest
PUT    /seat-requests/{id}/approve            → SeatRequest  (manager/admin)
PUT    /seat-requests/{id}/reject             → SeatRequest  (manager/admin)
DELETE /seat-requests/{id}                    → 204  (requester cancel own, or admin)
```

### 6.11 Search

```
GET    /search/members?q=&department_id=&project_id=&seat_code=&email=
       → List[MemberSearchResult]  (includes seat assignments)

GET    /search/seats?q=&room_id=&status=&project_id=&facility_id=
       → List[SeatSearchResult]
```

### 6.12 Notifications

```
GET    /notifications           → PaginatedList[Notification]
PUT    /notifications/{id}/read → Notification
PUT    /notifications/read-all  → 204
GET    /notifications/unread-count → { count: int }
```

### 6.13 Audit Logs

```
GET    /audit-logs?entity_type=&entity_id=&account_id=&from=&to=
       → PaginatedList[AuditLog]  (admin only)
```

---

## 7. UI DESIGN SYSTEM

### 7.1 Design Philosophy
- **Dark-first** workspace tool. Clean, high information density, no decorative flourishes.
- No emojis in the UI. Use Lucide icons exclusively.
- Every component reused from a shared library — no one-off inline styles.
- Spacing via Tailwind scale only (`p-4`, `gap-6`, etc.).

### 7.2 Color Tokens (Tailwind config extension)

```typescript
// tailwind.config.ts
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Surfaces
        surface: {
          base: '#09090b',      // zinc-950 — app background
          raised: '#18181b',    // zinc-900 — cards, panels
          overlay: '#27272a',   // zinc-800 — modals, dropdowns
          border: '#3f3f46',    // zinc-700 — borders
          muted: '#52525b',     // zinc-600 — disabled, placeholders
        },
        // Text
        text: {
          primary: '#fafafa',   // zinc-50
          secondary: '#a1a1aa', // zinc-400
          muted: '#71717a',     // zinc-500
        },
        // Brand accent
        accent: {
          DEFAULT: '#6366f1',   // indigo-500
          hover: '#4f46e5',     // indigo-600
          muted: '#312e81',     // indigo-900 — subtle bg
          foreground: '#ffffff',
        },
        // Seat status colors
        status: {
          available: '#22c55e',   // green-500
          occupied: '#ef4444',    // red-500
          reserved: '#f59e0b',    // amber-500
          disabled: '#52525b',    // zinc-600
          maintenance: '#f97316', // orange-500
        },
      },
    },
  },
}
```

### 7.3 Typography

```typescript
// Font stack via Google Fonts (self-hosted in prod)
// Display + headings: "Inter" (weights: 400, 500, 600, 700)
// Mono (code, seat codes, IDs): "JetBrains Mono"

// Type scale (Tailwind classes only)
// h1: text-2xl font-semibold tracking-tight text-text-primary
// h2: text-xl font-semibold text-text-primary
// h3: text-base font-medium text-text-primary
// Body: text-sm text-text-secondary
// Caption: text-xs text-text-muted
// Code/ID: font-mono text-xs text-accent
```

### 7.4 Core Component Specs

#### StatusBadge
```tsx
// Variants derived from seat_status enum
// Usage: <StatusBadge status="available" />
// Renders: small rounded pill with dot indicator + label
// available   → bg-green-500/10  text-green-400  border-green-500/20
// occupied    → bg-red-500/10    text-red-400    border-red-500/20
// reserved    → bg-amber-500/10  text-amber-400  border-amber-500/20
// disabled    → bg-zinc-700/30   text-zinc-500   border-zinc-700/50
// maintenance → bg-orange-500/10 text-orange-400 border-orange-500/20
```

#### DataTable
```tsx
// Props: columns[], data[], loading, pagination, onSort, onFilter
// Features: sticky header, row hover highlight, column sort indicators
// Header: bg-surface-raised, border-b border-surface-border
// Rows: bg-surface-base, hover:bg-surface-raised/50
// Pagination: bottom bar with page size select + page nav
```

#### AppShell Layout
```
┌─────────────────────────────────────────────────────┐
│ Topbar: Logo | Breadcrumb          Notif | Avatar   │  h-14 bg-surface-raised border-b
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ Sidebar  │  Page Content Area                       │
│ w-60     │  p-6                                     │
│ bg-      │  overflow-y-auto                         │
│ surface- │                                          │
│ raised   │                                          │
│          │                                          │
└──────────┴──────────────────────────────────────────┘
```

#### Sidebar Navigation Groups
```
Navigation:
  - Dashboard         (all roles)
  - Floor Plans       (all roles — published rooms)
  - Search            (all roles)
  - My Assignments    (user+)

Management:
  - Seat Requests     (manager+)
  - Members           (manager+)
  - Projects          (admin)

Administration:
  - Rooms             (admin)
  - Accounts          (admin)
  - Departments       (admin)
  - Facilities        (admin)
  - Audit Logs        (admin)
```

### 7.5 Page-Level Designs

#### Room View Page (Floor Plan Viewer)
```
┌──────────────────────────────────────────────────────────┐
│ PageHeader: "C703 — Block C Floor 7 Room 03"             │
│ [Status badge] [Version badge]  [Search member in room]  │
├────────────────────────────────┬─────────────────────────┤
│                                │  Seat Info Panel         │
│  Konva Canvas (flex-1)         │  (slides in on click)   │
│  Seats colored by project      │                          │
│  Hover tooltip: seat code +    │  Code: C703-A01          │
│  occupant name                 │  Status: Occupied        │
│                                │  Project: Team Alpha     │
│  Legend bar (bottom):          │  Occupant: Nguyen Van A  │
│  ● Available  ● Occupied       │  Facilities: [Monitor]   │
│  ● Reserved   ● Maintenance    │  [LAN Port]              │
│                                │  [Register] / [Assign]   │
└────────────────────────────────┴─────────────────────────┘
```

#### Search Page
```
┌──────────────────────────────────────────────────────────┐
│ Search Members                                           │
│ ┌─────────────────────────┐ [Dept ▼] [Project ▼]       │
│ │ Search by name, email,  │                              │
│ │ employee ID, seat code  │                              │
│ └─────────────────────────┘                              │
├──────────────────────────────────────────────────────────┤
│ Results (list)                                           │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ [Avatar] Nguyen Van A              IT Dept           │ │
│ │ Employee: EMP001 | email@co.com                      │ │
│ │ Primary Seat: C703-A01  [View on Map →]              │ │
│ │ Secondary: C302-B05     [View on Map →]              │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## 8. FLOOR PLAN EDITOR

### 8.1 Library: react-konva

**Why Konva.js:**
- Canvas-based (not DOM/SVG) → handles 200+ seats without lag
- Built-in drag, resize (Transformer), hit detection
- Serializes to JSON natively (save/load layout_data)
- `react-konva` provides React component wrappers

### 8.2 Element Types

#### Room Elements (non-seat, informational)
| Type | Icon | Color | Description |
|---|---|---|---|
| `door` | Rectangle (thin) | `#4ade80` green | Entrance/exit doors |
| `emergency_exit` | Rectangle | `#f87171` red | Fire exits |
| `window` | Rectangle (thin) | `#60a5fa` blue | Windows |
| `pillar` | Square (filled) | `#78716c` stone | Structural columns |
| `ac_unit` | Square | `#38bdf8` sky | Air conditioning units |
| `elevator` | Rectangle | `#a78bfa` violet | Elevator shafts |
| `restroom` | Rectangle | `#fb923c` orange | Bathrooms |
| `corridor` | Rectangle (outlined) | `#374151` gray | Hallway zones |
| `meeting_room` | Rectangle (dashed outline) | `#fbbf24` amber | Internal meeting rooms |
| `label` | Text only | white | Free text annotation |

#### Seat Types
| Type | Shape | Description |
|---|---|---|
| `single` | 60×60 square | Standard single desk |
| `double` | 120×60 | Two seats side by side (one unit) |
| `double_facing` | 120×120 | Two seats facing each other |
| `meeting_round` | Circle r=60 | Round meeting table |
| `executive` | 100×80 | Larger executive desk |

**Note:** Each seat in the editor corresponds to one `seats` record. `double` and `double_facing` types are cosmetic representations — they still map to individual seat records.

### 8.3 Editor Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ TOOLBAR (top)                                                        │
│ [Select]  [Room Elements ▼]  [Seat Types ▼]  │  [Undo][Redo]        │
│                               [Grid: ON/OFF]  │  [Save Draft][Lock?]│
├──────────────┬───────────────────────────────┬─────────────────────┤
│ LEFT PANEL   │  CANVAS                        │ RIGHT PANEL         │
│ w-48         │  (flex-1, overflow scroll)     │ w-64                │
│              │                                │                     │
│ Elements:    │  Grid overlay (optional)       │ Properties:         │
│ [Door]       │                                │ (selected element)  │
│ [Window]     │  Konva Stage                   │                     │
│ [Pillar]     │  ↳ Layer: room_elements        │ Seat Code: C703-A01 │
│ [AC Unit]    │  ↳ Layer: seats                │ Type: single        │
│ [Elevator]   │  ↳ Layer: ui (selection box)   │ Status: [dropdown]  │
│ [Restroom]   │                                │ Project: [dropdown] │
│ [Meeting Rm] │                                │ Facilities:         │
│ [Label]      │                                │  ☑ Monitor          │
│              │                                │  ☑ LAN Port         │
│ Seat Types:  │                                │ Description: [text] │
│ [Single]     │                                │ Max Secondary: [n]  │
│ [Double]     │                                │                     │
│ [Facing]     │                                │ Position: x=300 y=200│
│ [Round]      │                                │ Size: 60×60         │
│ [Executive]  │                                │ Rotation: 0°        │
│              │                                │                     │
└──────────────┴───────────────────────────────┴─────────────────────┘
```

### 8.4 Editor State (Zustand — editorStore.ts)

```typescript
interface EditorStore {
  roomId: string | null;
  stageData: StageData;           // canvas + elements + seats
  selectedId: string | null;
  tool: 'select' | 'add_element' | 'add_seat';
  elementTypeToAdd: ElementType | null;
  seatTypeToAdd: SeatType | null;
  isDirty: boolean;
  history: StageData[];           // undo stack
  historyIndex: number;

  // Actions
  setStage: (data: StageData) => void;
  addElement: (element: RoomElement) => void;
  addSeat: (seat: SeatNode) => void;
  updateNode: (id: string, updates: Partial<SeatNode | RoomElement>) => void;
  deleteNode: (id: string) => void;
  selectNode: (id: string | null) => void;
  undo: () => void;
  redo: () => void;
  markDirty: () => void;
  markClean: () => void;
}
```

### 8.5 Save Strategy

1. **Auto-save (draft):** Every 30s if `isDirty`, PUT `/rooms/{id}/layout` silently.
2. **Manual save:** Toolbar "Save Draft" button — force save + toast confirmation.
3. **Publish:** Admin confirms publish → POST `/rooms/{id}/publish` → version incremented → status = `published`.
4. **Seat sync:** On save, backend diffs `layout_data.seats` vs DB seats table → creates missing, updates positions, soft-deletes removed.

---

## 9. FEATURE MODULES

### 9.1 Dashboard

**Cards (summary metrics):**
- Total rooms (published)
- Total seats / available / occupied
- Pending seat requests
- Recent assignments (last 7 days)

**Quick links:** View rooms, Pending requests, Search member

### 9.2 Room List Page

- Filter: status, code search
- Grid view: Room cards showing code, name, capacity, status badge, occupancy %
- Admin: "Create Room" button
- Manager: see warehouse rooms with comment indicator

### 9.3 Room View Page (Viewer)

- Konva canvas, read-only
- Seat click → slide-in panel with full seat info
- Seat hover → tooltip (seat code + primary occupant)
- Project color legend
- Room element labels visible (door names, etc.)
- Banner if `room.status === 'locked'`
- Filter overlay: by project, by status, by facilities

### 9.4 Room Editor Page (Admin)

- Full editor as described in Section 8
- Room is auto-locked on edit entry; auto-unlocked on save/cancel
- Version badge in header
- Comment thread panel (collapsible, right side)

### 9.5 Seat Requests Page

**For Managers/Admin:**
- Table: requester name, seat code, room, type, status, submitted date
- Filter: status, room, date range
- Bulk approve/reject
- Approve action → triggers assignment creation + notification

**For Users:**
- "My Requests" tab showing own requests with status

### 9.6 Member Management Page (Admin)

- DataTable with search, department filter
- Import CSV button → modal with column mapping + preview + confirm
- CSV expected columns: `employee_id, username, full_name, email, gender, phone, title, department_code`
- Edit member → slide-over form
- View member → `/members/{id}` detail page with seat assignments

### 9.7 Member Detail Page

- Profile card (avatar, info)
- Primary seat card + navigate to map button
- Secondary slots list (seat code, room, device info)
- Assignment history

### 9.8 Search Page

- Debounced search input (300ms)
- Multi-field search: name, email, employee_id, username, seat_code, room_code
- Filters: department, project
- Results: MemberSearchResult cards
- Click "View on Map" → navigate to `/rooms/{id}?highlight={seat_id}` → canvas auto-pans and highlights seat

### 9.9 Notification Center

- Bell icon in topbar with unread badge count
- Dropdown: last 10 notifications with mark-read
- Click notification → navigate to relevant page (request detail, seat, etc.)
- "View all" link → full notifications page

**In-App Notification Triggers:**
| Event | Recipients |
|---|---|
| Seat request submitted | All managers + admins |
| Seat request approved | Requester |
| Seat request rejected | Requester |
| Member directly assigned to seat | Assigned member |
| Member unassigned from seat | Member |
| Comment added to room | Admin (room creator) |

### 9.10 Notification Interface (Future-ready)

```python
# app/services/notification_service.py

class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, recipient: Account, event: NotificationEvent) -> None:
        pass

class InAppNotificationChannel(NotificationChannel):
    async def send(self, recipient, event):
        # INSERT into notifications table
        pass

class EmailNotificationChannel(NotificationChannel):
    async def send(self, recipient, event):
        # PLACEHOLDER — implement SMTP/SendGrid later
        pass

class TeamsNotificationChannel(NotificationChannel):
    async def send(self, recipient, event):
        # PLACEHOLDER — implement MS Teams webhook later
        pass

class NotificationService:
    def __init__(self, channels: list[NotificationChannel]):
        self.channels = channels

    async def dispatch(self, recipients, event):
        for channel in self.channels:
            await channel.send(recipients, event)

# Registration (main.py):
notification_service = NotificationService(channels=[
    InAppNotificationChannel(),
    # EmailNotificationChannel(),    # uncomment when ready
    # TeamsNotificationChannel(),    # uncomment when ready
])
```

---

## 10. DEPLOYMENT

### 10.1 docker-compose.yml (local dev)

```yaml
version: '3.9'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: seat_mgmt
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    env_file: .env
    environment:
      DATABASE_URL: postgresql+asyncpg://admin:${DB_PASSWORD}@db:5432/seat_mgmt
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend

volumes:
  pgdata:
```

### 10.2 .env.example

```bash
# Database
DB_PASSWORD=changeme

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Redis
REDIS_URL=redis://redis:6379/0

# App
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80

# Future: Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Future: Email
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Future: MS Teams
TEAMS_WEBHOOK_URL=
```

### 10.3 Nginx Config

```nginx
server {
    listen 80;

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 11. IMPLEMENTATION PHASES

### Phase 1 — MVP Core (Functional system)
- [ ] Project scaffolding (Vite + FastAPI + Docker Compose)
- [ ] DB schema + Alembic migrations + seed data
- [ ] Auth (login, JWT, RBAC middleware)
- [ ] Member CRUD + CSV import
- [ ] Department, Project, Facility CRUD
- [ ] Room CRUD (no editor yet — basic layout_data stub)
- [ ] Seat CRUD + facility assignment
- [ ] Primary seat assignment (manager/admin direct)
- [ ] User seat registration request flow + approval
- [ ] In-app notifications
- [ ] Search page (member → seats)
- [ ] Audit log

### Phase 2 — Floor Plan Editor
- [ ] Konva editor scaffolding (canvas, layers, grid)
- [ ] Room element drag-drop (door, window, pillar, etc.)
- [ ] Seat type shapes (single, double, facing, round, executive)
- [ ] Properties panel (seat metadata editing)
- [ ] Auto-save draft
- [ ] Room status workflow (submit → approve → publish)
- [ ] Room versioning
- [ ] Manager comment system
- [ ] Room lock/unlock
- [ ] Floor plan viewer (read-only, seat click panel)
- [ ] Map-aware search (navigate to seat on map)

### Phase 3 — Polish & Extensions
- [ ] Dashboard with metrics
- [ ] Secondary device slot tracking (hostname/IP/MAC)
- [ ] Seat time-bound assignments
- [ ] Mobile-responsive layout
- [ ] Google OAuth integration
- [ ] Email notification channel
- [ ] MS Teams notification channel
- [ ] Room floor plan export (PNG/PDF)
- [ ] Advanced reporting

---

## 12. ESTIMATION

### Human Work (Traditional)
| Phase | Scope | Man-days | USD | VND |
|---|---|---|---|---|
| Phase 1 — MVP Core | Backend + Frontend + DB | 30 md | $3,000 | 75M |
| Phase 2 — Floor Plan Editor | Konva editor + viewer + workflows | 25 md | $2,500 | 62.5M |
| Phase 3 — Polish | OAuth, notifications, mobile, reporting | 15 md | $1,500 | 37.5M |
| **Total** | | **70 man-days** | **$7,000** | **175M VND** |

### AI-Assisted Work (Claude Code)
| Phase | Scope | Man-days | USD | VND |
|---|---|---|---|---|
| Phase 1 — MVP Core | Backend + Frontend + DB | 8 md | $800 | 20M |
| Phase 2 — Floor Plan Editor | Konva editor + viewer + workflows | 10 md | $1,000 | 25M |
| Phase 3 — Polish | OAuth, notifications, mobile, reporting | 5 md | $500 | 12.5M |
| **Total** | | **23 man-days** | **$2,300** | **57.5M VND** |

*Rate basis: ~$100/day blended developer rate. AI ratio assumes 1 developer with Claude Code generating 60-70% of boilerplate, API endpoints, schema, and component scaffolding.*

---

## 13. CLAUDE CODE AGENT INSTRUCTIONS

When implementing this project, follow this order:

1. **Read this spec fully before writing any code.**
2. Start with `docker-compose.yml` and `.env.example`.
3. Implement backend first: models → schemas → services → routers.
4. Run `alembic upgrade head` after each model group.
5. Implement frontend shell: Vite setup → Tailwind config → shadcn/ui init → AppShell → routing.
6. Implement pages in Phase 1 order from Section 11.
7. **Never use inline styles.** All styling via Tailwind utility classes.
8. **No emoji in UI.** Use `lucide-react` icons only.
9. All components go in `/src/components/`. No logic in page files beyond hooks + layout.
10. Every API call goes through a TanStack Query hook in `/src/hooks/`.
11. Zustand stores handle UI state only — server state belongs in TanStack Query.
12. Every protected route checks role via `authStore.account.role` — redirect to `/forbidden` if insufficient.
13. Floor plan editor (Phase 2) — use `react-konva`. Canvas state lives in `editorStore`. Save to API on explicit save action only (not on every drag).
```
