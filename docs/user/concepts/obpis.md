# OBPIs

**OBPI = One Brief Per Item**

OBPIs are the atomic unit of work in gzkit. Each OBPI maps to exactly one checklist item in an ADR.

---

## Why OBPIs?

ADRs capture intent, but they're too coarse for tracking progress. An ADR might have 15 checklist items. Without OBPIs, you lose visibility into which items are done.

OBPIs solve this:

- Each checklist item gets its own brief
- Progress is observable at the item level
- Claude knows exactly what scope it's working on
- You can attest incrementally

---

## OBPI Anatomy

Each OBPI brief contains:

| Section | Purpose |
|---------|---------|
| **Parent ADR** | Links to the ADR this implements |
| **Checklist Item** | Which specific item this brief covers |
| **Objective** | One-sentence goal |
| **Lane** | Lite or Heavy |
| **Allowed Paths** | What's in scope |
| **Denied Paths** | What's explicitly out of scope |
| **Requirements** | Must-have constraints (fail-closed) |
| **Acceptance Criteria** | How to know it's done |
| **Gate Evidence** | Commands/artifacts that prove completion |

---

## Numbering Discipline

OBPI numbering is **sequential and zero-gap**:

```
OBPI-0.1.0-01-setup-database.md
OBPI-0.1.0-02-create-models.md
OBPI-0.1.0-03-add-api-endpoints.md
OBPI-0.1.0-04-write-tests.md
```

Rules:

- Start at `01`, not `00`
- No gaps (if you have 5 items, you have 01-05)
- No categorical grouping (don't skip numbers for "phases")
- Matches ADR checklist order

---

## OBPI vs GHI

| Type | What it is | When created |
|------|------------|--------------|
| **OBPI** | Planned work | Before implementation, from ADR checklist |
| **GHI** | Emergent work | During implementation, when you discover issues |

GHIs (GitHub Issues) are bugs, surprises, or asides discovered while working on an OBPI. They're not part of the original plan—they're work that surfaces during execution.

Example:
- OBPI-0.1.0-03 is "add API endpoints"
- While implementing, you discover the auth middleware is broken
- That's a GHI, not a new OBPI

---

## Creating OBPIs

From an ADR with a checklist:

```markdown
## Checklist

- [ ] Set up database schema
- [ ] Create user model
- [ ] Add authentication endpoints
- [ ] Write integration tests
```

Create corresponding OBPIs:

```bash
gz obpi ADR-0.1.0 --item 1 --title "Set up database schema"
gz obpi ADR-0.1.0 --item 2 --title "Create user model"
gz obpi ADR-0.1.0 --item 3 --title "Add authentication endpoints"
gz obpi ADR-0.1.0 --item 4 --title "Write integration tests"
```

---

## Directory Structure

OBPIs live with their parent ADR:

```
design/adr/ADR-0.1.0-feature-name/
├── ADR-0.1.0-feature-name.md
├── ADR-CLOSEOUT-FORM.md
└── briefs/
    ├── OBPI-0.1.0-01-setup-database.md
    ├── OBPI-0.1.0-02-create-models.md
    ├── OBPI-0.1.0-03-add-api-endpoints.md
    └── OBPI-0.1.0-04-write-tests.md
```

---

## Working with OBPIs

Typical workflow:

1. Create ADR with checklist (`gz plan`)
2. Generate OBPIs for each item (`gz obpi`)
3. Work through OBPIs sequentially
4. Check progress (`gz status`)
5. When all OBPIs complete, run closeout ceremony
6. Attest (`gz attest`)

---

## The Alignment Chain

OBPIs enforce the alignment chain:

```
Intent (ADR/OBPI) ↔ Code (behavior) ↔ Docs (claims)
```

All three must align. If your OBPI says "add auth endpoints" but the code doesn't have them, or the docs don't describe them—the work isn't done.

---

## Related

- [Lifecycle](lifecycle.md) — ADR states and pool system
- [Gates](gates.md) — What gets verified
- [Lanes](lanes.md) — Lite vs Heavy requirements
- [Closeout](closeout.md) — Completing an ADR
