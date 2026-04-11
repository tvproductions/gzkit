# GovZero Compliance Rules

## Versioning (Minor Odometer)

**ADRs propel MINOR versions only (0.y.z where y increments for each ADR).**

- During 0.y.z: Each ADR increments minor (y) -> 0.1.0, 0.2.0, 0.3.0
- Patch (z) is for corrections, not sub-minor work
- Format: `ADR-0.{minor}.{patch}` or `ADR-{major}.{minor}.{patch}`
- Agents work under ONE ADR at a time; cannot bump SemVer (human gate required)
- Post-1.0: ADRs still use minor increments for capability additions

## Lifecycle States (Canonical)

| State | Meaning |
|-------|---------|
| Pool | Planned, awaiting prioritization |
| Draft | Being authored, not ready for review |
| Proposed | Submitted for review |
| Accepted | Approved, implementation may begin |
| Completed | Implementation finished, Gate 5 attestation received |
| Superseded | Replaced by newer ADR |
| Abandoned | Work stopped, will not be completed |

**Deprecated terms:** "Deprecated", "Pending", "Retired" -- use canonical states above.

## Five Gates

| Gate | Applies | Artifact |
|------|---------|----------|
| Gate 1 (ADR) | All | Intent document with problem/decision/consequences |
| Gate 2 (TDD) | All | Red-Green-Refactor cycle followed, tests derived from brief, coverage >=40% |
| Gate 3 (Docs) | Heavy only | Markdown lint clean, mkdocs build passes |
| Gate 4 (BDD) | Heavy only | Behave scenarios pass (CLI/API/schema contracts) |
| Gate 5 (Attestation) | Heavy only | Human directly observes and attests |

**Lane doctrine:**

- Lite lane (default): Gates 1-2 only (internal changes)
- Heavy lane: Gates 1-5 (external contract changes: CLI, API, schema, errors)

## OBPI Discipline

**One Brief Per Item:** Each ADR checklist item maps to exactly one OBPI brief.

- Format: `OBPI-{version}-{nn}-{slug}.md`
- Briefs live in `obpis/` subfolder (canonical name; `briefs/` is legacy and MUST NOT be used)
- Each OBPI must reference parent ADR and specific checklist item
- OBPI frontmatter MUST use `parent:` (not `parent_adr:`) for the parent ADR field

## OBPI Co-Creation Rule (Mandatory)

**OBPIs are co-created with the ADR, not deferred.**

When creating an ADR:

1. Count the checklist items in the Feature Checklist
2. Create exactly that many OBPI brief files using `gz specify` (preferred) or manually in `obpis/`
3. Verify 1:1 mapping before marking ADR as Proposed

**Prohibited patterns:**

- ADR table showing "Pending" OBPIs with no actual brief files
- ADR marked Proposed/Accepted with missing briefs
- Creating briefs "later" as a separate task

**Rationale:** The WBS is a contract between intent and implementation.
Orphaned checklist items create scope ambiguity. Co-creation locks intent
with execution units at decision time.

**Canonical reference:** `docs/governance/GovZero/adr-lifecycle.md` OBPI Completeness Requirement

## ADR-Contained Layout (Preferred)

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md
  ADR-CLOSEOUT-FORM.md            # optional
  obpis/
    OBPI-X.Y.Z-01-*.md
    OBPI-X.Y.Z-02-*.md
  audit/
    AUDIT-ADR-X.Y.Z-COMPLETED.md
  logs/
    design-outcomes.jsonl         # optional
```
