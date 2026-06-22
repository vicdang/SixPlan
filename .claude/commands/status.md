---
description: Show current sprint status
---

Print a status summary by reading the tracking files. Format:

```
================================================
SEAT MANAGEMENT — PROJECT STATUS
================================================

ROADMAP (docs/ROADMAP.md)
- Active sprint: Sprint N — <name>
- Completed: <count>/10 sprints
- Next up: Sprint N+1 — <name>

CURRENT SPRINT (docs/SPRINT_LOG.md)
- Started: <date>
- Items done: <X>/<Y>
- Last activity: <session timestamp>
- Blocked items: <count>

BACKLOG (docs/BACKLOG.md)
- New (awaiting triage): <count>
- Approved (scheduled): <count>
- Rejected: <count>

DECISIONS (docs/DECISIONS.md)
- Total decisions logged: <count>
- Recent decisions:
  - DEC-XXX: <title>
  - DEC-XXX: <title>

GIT
- Current branch: <branch>
- Uncommitted changes: <count> files
- Last commit: <hash> <message>
================================================
```

Do not make any changes — this is a read-only status report.
