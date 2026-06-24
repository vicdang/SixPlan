# SixPlan — Seat Management System

Internal workplace seat management web app with visual floor plan editor, RBAC, member search, and IT asset tracking.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS v3 + shadcn/ui + Konva.js |
| Backend | FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL 15 + Redis |
| State | Zustand (UI) + TanStack Query v5 (server) |
| Auth | JWT (access 60min + refresh 30d) + bcrypt + Redis blacklist |
| Deploy | Docker Compose + Nginx |

## Quick Start

### Prerequisites

- Docker + Docker Compose
- Python 3.11+ (for local backend dev)
- Node.js 20+ (for local frontend dev)

### 1. Environment setup

```bash
cp .env.example .env
# Edit .env — set DB_PASSWORD and JWT_SECRET_KEY at minimum
```

### 2. Start infrastructure

```bash
docker compose up -d db redis
```

### 3. Run database migrations + seed

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

This creates all tables and seeds:
- Admin account (`admin` / `ChangeMe@2026`)
- 10 default facilities (Monitor, Keyboard, Mouse, etc.)
- 6 development departments (IT, DEV, QA, HR, BA, PM)

### 4. Start the app

```bash
# Option A — full stack via Docker
docker compose up

# Option B — local dev servers
# Terminal 1 (backend):
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 (frontend):
cd frontend && npm install && npm run dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- API docs: http://localhost:8000/docs

### Initial credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `ChangeMe@2026` |

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (14 tables)
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Security, pagination, constants
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # Async engine + session
│   │   ├── dependencies.py  # Auth + role dependencies
│   │   └── main.py          # FastAPI app entry point
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── auth/        # RequireAuth guard
│       │   ├── layout/      # AppShell, Sidebar, Topbar, PageHeader
│       │   └── ui/          # shadcn/ui components
│       ├── hooks/           # useAuth (login/logout/me)
│       ├── lib/             # axios, queryClient, auth-storage, utils
│       ├── pages/           # LoginPage, ProfilePage, error pages
│       ├── store/           # Zustand authStore
│       └── types/           # TypeScript interfaces
├── docs/
│   ├── ROADMAP.md           # Sprint plan
│   ├── SPRINT_LOG.md        # Active sprint TODO + session log
│   ├── BACKLOG.md           # Deferred work
│   └── DECISIONS.md         # Technical decision records
├── SEAT_MANAGEMENT_SPEC.md        # Architecture + data model + API spec
├── SEAT_MANAGEMENT_SPEC_ADDENDUM.md  # Auth, profile, CSV import, wireframes
├── docker-compose.yml
└── nginx.conf
```

## Sprint Progress

| Sprint | Status | Description |
|---|---|---|
| Sprint 1 | Completed | Foundation: Docker, models, migrations, frontend scaffold |
| Sprint 2 | Completed | Auth flow, profile page, routing, shadcn/ui components |
| Sprint 3 | Not started | Member management (CRUD + CSV import) |
| Sprint 4 | Not started | Projects + Facilities |
| Sprint 5 | Not started | Rooms + Seats (basic) |
| Sprint 6 | Not started | Floor plan editor (Konva) |
| Sprint 7 | Not started | Viewer + search |
| Sprint 8 | Not started | Seat requests + assignments |
| Sprint 9 | Not started | Notifications + audit log |
| Sprint 10 | Not started | Polish + mobile responsive |

## RBAC

| Role | Access |
|---|---|
| `viewer` | Read-only: rooms, seats, floor maps |
| `user` | Viewer + submit seat requests, manage own profile |
| `manager` | User + approve/reject requests, manage team seats |
| `admin` | Full access including member/account management |

## API Overview

All endpoints prefixed `/api/v1`.

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Returns access + refresh tokens |
| POST | `/auth/logout` | Blacklists current token |
| POST | `/auth/refresh` | Rotates access token |
| GET | `/auth/me` | Returns current user info |
| GET | `/profile` | Full profile detail |
| PUT | `/profile` | Update phone / avatar |
| GET | `/profile/assignments` | Primary + secondary seat assignments |
| POST | `/profile/change-password` | Change own password |
