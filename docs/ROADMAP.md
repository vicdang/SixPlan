# ROADMAP — Seat Management System

**Master plan.** This file is the source of truth for sprint structure and scope. Do not modify without explicit user approval.

> If a sprint deviates from this roadmap, log the deviation in `BACKLOG.md` and `DECISIONS.md`, do not silently edit this file.

---

## Phase 1 — MVP Core

### Sprint 1 — Foundation
- [x] `docker-compose.yml`, `nginx.conf`, `.env.example`
- [x] Backend skeleton: `main.py`, `config.py`, `database.py`, `dependencies.py`
- [x] All SQLAlchemy models per SPEC §4
- [x] Initial Alembic migration + seed data (admin + facilities)
- [x] Verify DB up, admin seeded
- [x] Frontend scaffold: Vite + Tailwind config + shadcn init
- [x] Tailwind config with design tokens per SPEC §7.2
- [x] AppShell layout (Sidebar + Topbar stubs)

### Sprint 2 — Auth + Profile
- [x] Backend: `auth_service.py`, `/auth` router (login/logout/refresh/me)
- [x] Frontend: `LoginPage`, `authStore`, axios interceptor, `RequireAuth`
- [x] Frontend: Topbar with avatar dropdown (logout)
- [x] Profile page (read-only first, then edit + change password)
- [ ] E2E test: login → see profile → logout (requires running DB)

### Sprint 3 — Member Management
- [ ] Backend: `/departments` CRUD, `/members` CRUD, `/accounts` CRUD
- [ ] Backend: `/members/import` (preview + execute)
- [ ] Frontend: `DepartmentsPage`, `MemberListPage`, member add/edit Sheet
- [ ] Frontend: CSV import modal (3-step flow)
- [ ] Frontend: `AccountsPage` (role management)

### Sprint 4 — Projects + Facilities
- [ ] Backend: `/projects` CRUD, `/facilities` CRUD
- [ ] Frontend: `ProjectsPage`, `FacilitiesPage`

### Sprint 5 — Rooms + Seats (basic)
- [ ] Backend: `/rooms` CRUD (no layout yet), `/seats` CRUD
- [ ] Backend: Room status workflow (`/submit`, `/approve`, `/publish`, `/lock`)
- [ ] Frontend: `RoomListPage` with status tabs
- [ ] Frontend: Room create modal
- [ ] Frontend: `RoomEditorPage` stub
- [ ] Frontend: `RoomViewPage` stub

## Phase 2 — Floor Plan Editor

### Sprint 6 — Floor Plan Editor
- [ ] Editor canvas: react-konva Stage + Layers
- [ ] Drag-drop room elements (door, window, pillar, etc.)
- [ ] Drag-drop seat shapes (all 5 types)
- [ ] Transformer for resize/rotate
- [ ] Properties panel binding
- [ ] Undo/redo via Zustand history
- [ ] Auto-save layout to API
- [ ] Seat sync logic (backend diff on save)

### Sprint 7 — Viewer + Search
- [ ] `RoomViewPage` with read-only Konva
- [ ] Seat click → slide-in info panel
- [ ] Project color rendering on seats
- [ ] Search page (member → list)
- [ ] Map navigation: `?highlight=seat_id` → pan + glow seat

### Sprint 8 — Requests + Assignments
- [ ] Backend: `/seat-requests` flow + `/assignments`
- [ ] Frontend: `RequestsPage` (manager view + user view)
- [ ] Frontend: "Register" button on seat panel
- [ ] Frontend: Direct assign modal
- [ ] Secondary assignment form (hostname/IP/MAC/note)

## Phase 3 — Polish

### Sprint 9 — Notifications + Audit
- [ ] Backend: notification service with InApp channel
- [ ] Backend: audit log decorator on all mutation endpoints
- [ ] Frontend: notification bell in topbar
- [ ] Frontend: `AuditLogPage` (admin)

### Sprint 10 — Polish
- [ ] Dashboard with metrics
- [ ] Empty states across all pages
- [ ] Loading skeletons
- [ ] Mobile responsive pass
- [ ] Final E2E smoke test

---

## Progress Tracking

| Sprint | Status | Started | Completed | Notes |
|---|---|---|---|---|
| Sprint 1 | Completed | 2026-06-22 | 2026-06-22 | — |
| Sprint 2 | Completed | 2026-06-22 | 2026-06-22 | Smoke test deferred (needs DB) |
| Sprint 3 | Not started | — | — | — |
| Sprint 4 | Not started | — | — | — |
| Sprint 5 | Not started | — | — | — |
| Sprint 6 | Not started | — | — | — |
| Sprint 7 | Not started | — | — | — |
| Sprint 8 | Not started | — | — | — |
| Sprint 9 | Not started | — | — | — |
| Sprint 10 | Not started | — | — | — |

**Status values:** `Not started` / `In progress` / `Blocked` / `Completed` / `Skipped`
