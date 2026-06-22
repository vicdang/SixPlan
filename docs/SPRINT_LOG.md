# SPRINT LOG — Active Sprint Tracking

**Purpose:** Living document of what's happening RIGHT NOW. Agent updates this continuously during work.

> Agent updates this file at the start and end of EVERY work session, and after each completed item.

---

## Current Sprint

**Sprint:** *(not started)*
**Started:** —
**Target completion:** —
**Spec reference:** ADDENDUM §23

---

## Active TODO

*(Agent populates this from ROADMAP at sprint start, and updates checkboxes as it goes)*

- [ ] Read ROADMAP.md and pick next sprint
- [ ] Read relevant spec sections for this sprint
- [ ] List files to create/modify
- [ ] Implement
- [ ] Verify (start server, hit endpoint, click UI)
- [ ] Commit
- [ ] Update SPRINT_LOG progress
- [ ] Surface BACKLOG items
- [ ] Update ROADMAP status table

---

## Session Log

*(Append-only log of work sessions, newest at top)*

### [YYYY-MM-DD HH:MM] Session Start
**Goal:** —
**Plan:**
- —

### [YYYY-MM-DD HH:MM] Session End
**Completed:**
- —
**Blocked:**
- —
**Carried to next session:**
- —
**New backlog items:**
- —

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
