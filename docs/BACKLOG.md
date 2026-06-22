# BACKLOG — Seat Management System

**Purpose:** Capture new ideas, deferred work, scope changes, and discovered tasks that arise during implementation. Items here are NOT part of the original roadmap.

> **Agent behavior:** When discovering something out of scope, ADD it here — do not silently expand the current sprint. Wait for user prioritization.

---

## Format

Each item has:
- **ID** — `BL-XXX` (sequential)
- **Title** — short summary
- **Status** — `New` / `Triaged` / `Approved` / `In sprint` / `Done` / `Rejected`
- **Priority** — `Critical` / `High` / `Medium` / `Low`
- **Source** — who/what surfaced it
- **Sprint** — target sprint (after triage)
- **Description** — what + why
- **Decision** — what user said (after triage)

---

## Active Items

### BL-001 — [Template]
- **Status:** New
- **Priority:** —
- **Source:** —
- **Sprint:** —
- **Description:** —
- **Decision:** —

---

## Triaged Items
*(Items moved here after user reviews them)*

---

## Done Items
*(Items completed and merged into a sprint)*

---

## Rejected Items
*(Items not proceeding — with reason)*

---

## Triage Process

1. **Agent finds something out-of-scope** during implementation.
2. **Agent adds entry** to "Active Items" with status `New`.
3. **Agent continues current sprint** — does NOT implement the new item.
4. **At sprint end**, agent surfaces all `New` items in the sprint report.
5. **User triages**: assigns priority, sprint, or rejects.
6. **Item moves** to Triaged / scheduled sprint / Rejected.

## Examples of what belongs here

- "While building Member CRUD, noticed we need bulk delete functionality"
- "Manager comment thread would be nicer with @mentions"
- "Konva editor could support keyboard shortcuts"
- "Spec says X but a simpler approach Y exists — request approval to deviate"
- "Bug found in unrelated module while implementing current sprint"

## What does NOT belong here

- Bugs in the current sprint's deliverables → fix immediately, don't log
- Spelling/typo fixes → fix immediately
- Refactors within already-touched files → do as part of current work
- Anything in the ROADMAP — those have a home already
