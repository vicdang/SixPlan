---
description: Wrap up the current work session
---

Wrap up this work session. Follow this exact sequence:

1. **Run the verification checklist from SPRINT_LOG.md:**
   - All in-progress TODO items checked or carried forward
   - Linter clean: `ruff check backend/` and `cd frontend && npm run lint`
   - Type check clean: `cd backend && mypy app/` and `cd frontend && npx tsc --noEmit`
   - Tests pass if any: `pytest backend/tests/` and `cd frontend && npm test`
   - Dev servers start cleanly (backend on :8000, frontend on :3000)
   - Manual smoke test of the new feature

2. **Append session-end entry to SPRINT_LOG.md:**
   ```
   ### [current timestamp] Session End
   **Completed:**
   - <list of finished items>
   **Blocked:**
   - <items stuck and why>
   **Carried to next session:**
   - <unfinished items>
   **New backlog items:**
   - <references to BL-XXX entries added>
   ```

3. **Commit the work:**
   ```
   git add .
   git commit -m "feat(sprint-N): <summary of what was done>"
   ```
   Do NOT push without user approval.

4. **If the entire sprint is complete:**
   - Update `docs/ROADMAP.md` progress table for this sprint to `Completed`
   - Update `docs/SPRINT_LOG.md` "Current Sprint" pointer to next sprint
   - Move all sprint TODOs to a history section in SPRINT_LOG.md

5. **Surface to user:**
   - Print a 5-line summary: sprint, items done, items blocked, new backlog items, next step
   - Wait for user direction (proceed to next sprint, triage backlog, fix something)
