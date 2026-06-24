# SPRINT LOG — Active Sprint Tracking

**Purpose:** Living document of what's happening RIGHT NOW. Agent updates this continuously during work.

> Agent updates this file at the start and end of EVERY work session, and after each completed item.

---

## Current Sprint

**Sprint:** Sprint 2 — Auth + Profile
**Started:** 2026-06-22
**Target completion:** 2026-06-22
**Spec reference:** ADDENDUM §23 Sprint 2, §14, §15

---

## Active TODO

- [x] Backend: `auth_service.py`, `schemas/auth.py`, `/auth` router (login/logout/refresh/me/change-password)
- [x] Backend: `schemas/profile.py`, `/profile` router (get/update/assignments/requests/change-password)
- [x] Frontend: shadcn UI components (button, input, label, card, separator, badge, avatar, dropdown-menu, dialog, sheet)
- [x] Frontend: `RequireAuth` component + `useAuth` hook
- [x] Frontend: `LoginPage` per ADDENDUM §14.1
- [x] Frontend: Topbar avatar dropdown (logout)
- [x] Frontend: `ProfilePage` (read-only + edit modal + change password modal)
- [x] Frontend: App routing wired (login redirect, RequireAuth gates, profile route)
- [ ] Smoke test: login → profile → logout flow

---

## Session Log

*(Append-only log of work sessions, newest at top)*

### [2026-06-22 09:00] Session Start
**Goal:** Build Sprint 1 Foundation — infrastructure, backend skeleton + all models, Alembic seed, frontend scaffold, AppShell.
**Plan:**
- Create docker-compose.yml, nginx.conf
- Backend: config.py, database.py, dependencies.py, main.py
- Backend: all 11 SQLAlchemy model files
- Backend: Alembic setup + initial migration with seed data
- Frontend: package.json, vite.config.ts, tailwind.config.ts, components.json
- Frontend: AppShell, Sidebar, Topbar stubs + root pages

### [2026-06-23 09:00] Session Start
**Goal:** Implement Sprint 2 — full auth flow (login/logout/refresh/me) + profile page (read + edit + change password).
**Plan:**
- Backend: redis_client.py, schemas/auth.py, services/auth_service.py, routers/auth.py
- Backend: schemas/profile.py, routers/profile.py, update main.py + dependencies.py
- Frontend: 10 shadcn UI components, RequireAuth, useAuth hook
- Frontend: LoginPage, ProfilePage, Topbar dropdown, App routing

### [2026-06-22 11:00] Session End
**Completed:**
- docker-compose.yml, nginx.conf, frontend/Dockerfile, backend/Dockerfile
- backend/app/config.py, database.py, dependencies.py, main.py
- All 11 SQLAlchemy model files (department, member, account, project, facility, room, seat, assignment, seat_request, notification, audit_log)
- backend/alembic/env.py (async), alembic/versions/001_initial_schema_and_seed.py (schema + seed: admin, facilities, dev departments)
- frontend: package.json, vite.config.ts, tailwind.config.ts, postcss.config.js, components.json, index.html
- frontend/src: main.tsx, App.tsx, index.css, lib/{utils,queryClient,auth-storage,axios}.ts
- frontend/src/store/authStore.ts, types/{auth,common}.ts
- frontend/src/components/layout: AppShell.tsx, Sidebar.tsx, Topbar.tsx, PageHeader.tsx
- frontend/src/pages/errors: NotFoundPage.tsx, ForbiddenPage.tsx
**Blocked:**
- None
**Carried to next session:**
- User must run: cp .env.example .env (fill DB_PASSWORD + JWT_SECRET_KEY), docker compose up -d db redis, cd backend && pip install -r requirements.txt && alembic upgrade head
- Verify: psql seat_mgmt and check admin account + facilities seeded
**New backlog items:**
- None

### [2026-06-22 14:00] Session End
**Completed:**
- backend/app/redis_client.py (fail-open Redis wrapper)
- backend/app/schemas/auth.py, schemas/profile.py
- backend/app/services/auth_service.py (authenticate, blacklist, refresh, change-password)
- backend/app/routers/auth.py (login, logout, refresh, me, change-password)
- backend/app/routers/profile.py (get, update, assignments, change-password)
- backend/app/main.py updated (router includes)
- backend/app/dependencies.py updated (JWT blacklist check, fail-open)
- frontend/src/components/ui: button, input, label, card, separator, badge, avatar, dropdown-menu, dialog, sheet
- frontend/src/store/authStore.ts updated (setHydrated, setAccount sets isHydrated)
- frontend/src/hooks/useAuth.ts (useMe, useLogin, useLogout, useChangePassword)
- frontend/src/components/auth/RequireAuth.tsx
- frontend/src/pages/auth/LoginPage.tsx
- frontend/src/pages/profile/ProfilePage.tsx
- frontend/src/components/layout/Topbar.tsx updated (avatar dropdown with My Profile + Sign out)
- frontend/src/App.tsx updated (full routing + auth hydration on mount)
**Blocked:**
- Smoke test deferred — requires running DB + Redis (Docker or manual setup)
**Carried to next session:**
- User must run `docker compose up -d db redis && alembic upgrade head` to enable smoke test
- Smoke test: login → profile → logout flow
**New backlog items:**
- None

---

## Verification Checklist (Sprint-End)

Before marking sprint complete, agent verifies:

- [ ] All TODO items above checked
- [ ] All commits pushed to feature branch (NOT main without approval)
- [ ] No linter errors (`ruff check`, `eslint`)
- [ ] No type errors (`mypy`, `tsc --noEmit`)
- [ ] Tests pass if any exist for this sprint
- [ ] Dev server starts cleanly
- [ ] Manual smoke test of the new feature works
- [ ] ROADMAP.md progress table updated
- [ ] BACKLOG.md items surfaced for user review
- [ ] DECISIONS.md updated with any technical choices

---

## Scope Guard

**Before doing any work, agent asks itself:**

1. Is this item in the current sprint's TODO list above? → Yes, proceed.
2. Is it a small fix discovered during this work (typo, obvious bug)? → Fix it, note in session log.
3. Is it a new feature/scope expansion? → STOP. Add to BACKLOG.md. Do not implement.
4. Is it a deviation from spec? → STOP. Add to BACKLOG.md with rationale. Ask user.

**Red flags that mean "stop and re-read this file":**
- Spending more than 30 min on something not in TODO above
- Editing files outside the modules the current sprint touches
- Installing new dependencies not in SPEC §2
- "While I'm here, let me also..." → that thought is the trigger to STOP and log to BACKLOG
