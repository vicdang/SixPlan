# DECISIONS — Technical Decision Log

**Purpose:** Capture significant technical decisions made during implementation. Lightweight ADR (Architecture Decision Record) format.

> Agent logs here when making a decision that:
> - Deviates from spec
> - Picks one approach over another non-trivially
> - Affects future work or other modules
> - Resolves ambiguity in the spec

---

## Format

```
### DEC-NNN — [Title]
- **Date:** YYYY-MM-DD
- **Sprint:** Sprint N
- **Status:** Proposed / Accepted / Superseded by DEC-XXX
- **Context:** What problem are we solving?
- **Options considered:**
  1. Option A — pros/cons
  2. Option B — pros/cons
- **Decision:** What we chose and why
- **Consequences:** What this means for future work
```

---

## Active Decisions

### DEC-000 — [Template — do not delete]
- **Date:** 2026-06-22
- **Sprint:** —
- **Status:** Template
- **Context:** Reference format
- **Options considered:** —
- **Decision:** —
- **Consequences:** —

---

## When to write a decision

**Write one when:**
- Spec is ambiguous and agent picks an interpretation
- Library has multiple usage patterns, agent picks one
- A small deviation from spec is justified (e.g., simpler approach works the same)
- A trade-off affects performance, security, or maintainability
- A workaround is needed (e.g., library bug)

**Skip when:**
- Following spec exactly
- Trivial choices (variable names, file ordering)
- Standard idiomatic code with one obvious way

---

## When to ask user vs log decision

| Situation | Action |
|---|---|
| Spec is clear, follow it | Just do it, no log needed |
| Spec is ambiguous, agent has a reasonable choice | Log decision, proceed |
| Spec is ambiguous, agent unsure | Ask user with concrete recommendation |
| Deviating from spec for good reason | Log decision, ASK user before proceeding |
| Major architectural change | ASK user, then log decision after agreement |
