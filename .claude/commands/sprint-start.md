---
description: Start or resume the current sprint
---

You are about to begin a work session. Follow this exact sequence:

1. **Read tracking files in order:**
   - `docs/ROADMAP.md` — to know which sprint is active
   - `docs/SPRINT_LOG.md` — to see current TODO and last session state
   - `docs/BACKLOG.md` — to recall any pending items
   - `docs/DECISIONS.md` — to recall past technical decisions

2. **State the plan:**
   - Which sprint are we on
   - What's the next unchecked TODO item
   - What files will be touched

3. **Append a session entry to SPRINT_LOG.md:**
   ```
   ### [current timestamp] Session Start
   **Goal:** <one sentence>
   **Plan:**
   - <bullets>
   ```

4. **Execute the TODO items in order.** Update checkboxes in SPRINT_LOG.md as you complete each.

5. **If you encounter scope creep, new ideas, or spec deviations:** STOP and add an entry to `docs/BACKLOG.md`. Do NOT implement them.

6. **At end of session:** Run `/sprint-end`.
