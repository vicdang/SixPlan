---
description: Add a new item to the backlog
argument-hint: "<title of the item>"
---

A new item has been identified that is OUT OF SCOPE for the current sprint. Do NOT implement it now.

1. **Read `docs/BACKLOG.md`** to find the next available `BL-XXX` ID.

2. **Append a new entry** under "Active Items" with this format:

   ```markdown
   ### BL-XXX — $ARGUMENTS
   - **Status:** New
   - **Priority:** (leave blank — user decides)
   - **Source:** Discovered during Sprint <N>, while working on <what>
   - **Sprint:** (leave blank — user decides)
   - **Description:**
     - What was found
     - Why it matters
     - Why it's out of current scope
   - **Decision:** (pending user triage)
   ```

3. **Continue the current sprint work.** Do not implement the new item.

4. **At sprint-end**, this item will be surfaced to the user for triage.
