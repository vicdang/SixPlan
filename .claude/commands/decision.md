---
description: Log a technical decision
argument-hint: "<short title of the decision>"
---

Log a technical decision to `docs/DECISIONS.md`.

1. **Read `docs/DECISIONS.md`** to find the next available `DEC-NNN` ID.

2. **Append a new entry** with this format:

   ```markdown
   ### DEC-NNN — $ARGUMENTS
   - **Date:** <today's date>
   - **Sprint:** Sprint <current>
   - **Status:** Accepted
   - **Context:**
     - What problem are we solving?
   - **Options considered:**
     1. <Option A> — pros / cons
     2. <Option B> — pros / cons
   - **Decision:**
     - What we chose and why
   - **Consequences:**
     - What this means for future work
   ```

3. Fill in each field based on the current situation. Be concise — 1-3 lines per field is plenty.

4. **If this decision deviates from the spec or roadmap**, ALSO surface it to the user immediately and wait for confirmation before proceeding with the implementation that depends on this decision.
