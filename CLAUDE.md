# CLAUDE.md — Seat Management System

This file is the entry point for the Claude Code agent. Read it first, then read the spec files and tracking files before writing any code.

---

## Project Overview
Internal workplace seat management web app with visual floor plan editor, RBAC, member search, and IT asset tracking.

## Authoritative Specs
- **`SEAT_MANAGEMENT_SPEC.md`** — Architecture, data model, RBAC, API, design system, floor plan editor
- **`SEAT_MANAGEMENT_SPEC_ADDENDUM.md`** — Auth flow, profile, CSV import, wireframes, API examples, validation, error format, seed data, bootstrap commands

## Tracking Files (READ AT EVERY SESSION START)
- **`docs/ROADMAP.md`** — Master sprint plan (immutable without approval)
- **`docs/SPRINT_LOG.md`** — Current sprint TODO + session history
- **`docs/BACKLOG.md`** — New ideas and deferred work
- **`docs/DECISIONS.md`** — Technical decision log

Do not deviate from the specs without explicit user approval. Use `BACKLOG.md` to capture deviations.

---

## Tech Stack (Locked)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind + shadcn/ui + Konva
- **Backend:** FastAPI + SQLAlchemy 2.0 async + Alembic + PostgreSQL 15 + Redis
- **State:** Zustand (UI) + TanStack Query (server)
- **Auth:** JWT (access + refresh) + bcrypt
- **Deploy:** Docker Compose

---

## Hard Rules

### Code Quality
1. **No inline CSS.** Tailwind utility classes only. No `style={}` except for dynamic Konva positions.
2. **No emojis in UI.** Use `lucide-react` icons only.
3. **No "TMA" mentions** in code, copy, comments, or docs.
4. **Dark theme first.** All pages render correctly with `class="dark"` on `<html>`.
5. **shadcn/ui components only.** Do not write custom button/input/dialog from scratch.

### Architecture
6. **Pydantic is source of truth for validation.** Zod on frontend mirrors but does not replace.
7. **Every mutation logs to audit_logs.** Use the audit decorator/dependency.
8. **Every protected route checks role.** Use `RequireAuth` (frontend) and role dependency (backend).
9. **TanStack Query for all API calls.** No raw axios in components.
10. **Zustand only for UI state.** Server state belongs in TanStack Query.

### Tracking Discipline
11. **Every work session starts with `/sprint-start`** — reads tracking files, plans the session.
12. **Every work session ends with `/sprint-end`** — verifies, commits, updates tracking.
13. **Scope expansion goes to BACKLOG**, never silently into current sprint. Use `/backlog-add`.
14. **Technical decisions get logged** via `/decision` when non-trivial.
15. **At any time, `/status` shows the current state** — use it whenever context feels lost.

---

## Autonomous Behavior Rules

The user has configured `.claude/settings.json` with broad permissions to run with minimal interruption. Honor that trust — be decisive and self-sufficient, but respect scope boundaries.

### Auto-Proceed Without Asking
- Read/write/edit any file inside the project root
- Run dev servers (`uvicorn`, `vite dev`, `npm run dev`)
- Database operations (`alembic upgrade head`, `psql` queries)
- Install dependencies listed in SPEC §2
- Tests, linters, type checkers, formatters
- Docker Compose operations
- All git operations except `push` and destructive history rewrites
- Modify files inside `/backend`, `/frontend`, `/alembic`, `/docs`
- Add shadcn/ui components
- HTTP requests to localhost for testing
- Read documentation from whitelisted domains

### Ask Before
- Adding dependencies NOT in SPEC §2
- Changing the database schema in a way that contradicts SPEC §4
- Changing the file structure defined in SPEC §3
- Modifying `.env`
- `git push` or `git reset --hard`
- **Deviating from ROADMAP.md** — log to BACKLOG, ask before implementing
- **Implementing anything not in current sprint TODO** — add to BACKLOG first

### Never Do
- Read or write secrets (`.env`, `*.pem`, SSH keys, AWS credentials)
- Run `sudo`, `rm -rf /`, pipe network input to a shell
- Commit secrets, even by accident
- Push to remotes without approval
- Disable tests to make CI green
- Suppress errors to silence linters

---

## Session Workflow

### Starting a session
```
/sprint-start
```
Agent reads ROADMAP, SPRINT_LOG, BACKLOG, DECISIONS, and announces:
- Which sprint is active
- What the next TODO is
- What files will be touched

### Mid-session: scope creep detected
Agent thinks "while I'm here, let me also..." → STOP.
```
/backlog-add "title of the new idea"
```
Agent adds entry and continues current sprint work.

### Mid-session: making a non-trivial choice
Agent picks one approach over another or deviates slightly from spec.
```
/decision "title of the decision"
```
Agent logs to DECISIONS.md. If deviation is significant, asks user first.

### Mid-session: checking where we are
```
/status
```
Read-only summary of current state.

### Ending a session
```
/sprint-end
```
Agent verifies, commits, updates tracking. Surfaces backlog items for user triage.

---

## Decision-Making Heuristics

When facing ambiguity:

1. **Check the specs.** If answer is in SPEC.md or ADDENDUM.md, use it.
2. **Check ROADMAP.md.** Is this item part of the current sprint?
3. **Check DECISIONS.md.** Has a similar decision been made before?
4. **Check existing code patterns.** Mirror what's already there.
5. **Pick the idiomatic option.** FastAPI conventions, React conventions, Tailwind conventions.
6. **Choose the simpler implementation.**
7. **If still ambiguous, ask with a concrete recommendation** — not an open question.

Bad: "How should I structure auth?"
Good: "I'll structure auth as `routers/auth.py` + `services/auth_service.py` + `dependencies.py`, mirroring the FastAPI tutorial pattern. Logging this as DEC-001. OK to proceed?"

---

## Error Recovery Protocol

1. Read the error fully.
2. Reproduce with a minimal command.
3. Check recent diffs: `git diff HEAD~1`.
4. Try one fix at a time.
5. After 3 failed attempts: STOP, log to SPRINT_LOG.md "Blocked", summarize for user.
6. Never delete tests or suppress errors to make the immediate problem go away.

---

## Communication Style

- Be brief. Status updates: one or two sentences.
- Lead with the result, then explain only if asked.
- Don't narrate every file you read; narrate decisions.
- Use checklists for multi-step plans; execute silently unless something deviates.
- At sprint end, give a one-paragraph summary plus what's verified working.

---

## File Structure
See **SEAT_MANAGEMENT_SPEC.md § 3** for the canonical directory layout, plus:

```
/docs
  ├── ROADMAP.md          # immutable sprint plan
  ├── SPRINT_LOG.md       # active sprint TODO + session log
  ├── BACKLOG.md          # new ideas / deferred work
  └── DECISIONS.md        # technical decision records

/.claude/commands
  ├── sprint-start.md     # /sprint-start command
  ├── sprint-end.md       # /sprint-end command
  ├── backlog-add.md      # /backlog-add command
  ├── decision.md         # /decision command
  └── status.md           # /status command
```

## Bootstrap
See **SEAT_MANAGEMENT_SPEC_ADDENDUM.md § 22** for exact commands.

## Initial Credentials
- Username: `admin`
- Password: `ChangeMe@2026`
- Forced password change on first login.

## Quick Start

```bash
# Initial bootstrap (see ADDENDUM §22)
cp .env.example .env
docker compose up -d db redis
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# In Claude Code session:
/sprint-start
# ... work happens ...
/sprint-end
```
