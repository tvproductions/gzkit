---
id: OBPI-0.22.0-01-task-entity-model
parent: ADR-0.22.0-task-level-governance
item: 1
lane: Lite
status: Accepted
---

# OBPI-0.22.0-01: TASK Entity Model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #1 — "TASK entity model: Pydantic model, identifier scheme, lifecycle states"

**Status:** Accepted

## Objective

Define the TASK entity as a Pydantic BaseModel with identifier scheme `TASK-<semver>-<obpi>-<req>-<seq>`, lifecycle states {pending, in_progress, completed, blocked, escalated}, and valid state transitions. This completes the fourth tier of gzkit's governance hierarchy.

## Lane

**Lite** — Internal data model; no CLI/API changes.

## Allowed Paths

- `src/gzkit/tasks.py` — TASK entity model, identifier parsing, lifecycle states
- `tests/test_tasks.py` — TASK model unit tests

## Denied Paths

- `src/gzkit/events.py` — ledger events belong to OBPI-02
- `src/gzkit/commands/` — CLI belongs to OBPI-04
- `src/gzkit/pipeline_runtime.py` — pipeline integration belongs to ADR-0.18.0
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: TASK identifier scheme MUST be `TASK-<semver>-<obpi_item>-<req_index>-<seq>` (e.g., `TASK-0.20.0-01-01-01`).
1. REQUIREMENT: TASK model MUST include: id, description, status, parent_req (REQ identifier), parent_obpi (OBPI identifier).
1. REQUIREMENT: Lifecycle states MUST be exactly: {pending, in_progress, completed, blocked, escalated}.
1. REQUIREMENT: Valid transitions MUST be defined and enforced: pending→in_progress, in_progress→completed, in_progress→blocked, blocked→in_progress, in_progress→escalated.
1. REQUIREMENT: Invalid transitions (e.g., pending→completed) MUST raise an error.
1. REQUIREMENT: TASK identifier MUST be parseable from a string using a classmethod.
1. REQUIREMENT: Model MUST use `ConfigDict(frozen=True, extra="forbid")` for immutable snapshots.
1. REQUIREMENT: TASKs MUST be derivable from plan-file steps — include a factory function that creates TASKs from plan text + parent context.
1. NEVER: Encode vendor-specific details in the TASK model.
1. ALWAYS: Type hints use modern syntax.

> STOP-on-BLOCKERS: ADR-0.20.0 OBPI-01 should be complete (REQ entity model for parent linkage), but TASK model can be built with string-based REQ references if needed.

## Acceptance Criteria

- [ ] REQ-0.22.0-01-01: Given a valid TASK string `TASK-0.20.0-01-01-01`, when parsed, then returns a TASK entity with correct semver, obpi_item, req_index, and seq components.
- [ ] REQ-0.22.0-01-02: Given a TASK in `pending` state, when transitioned to `in_progress`, then status updates successfully.
- [ ] REQ-0.22.0-01-03: Given a TASK in `pending` state, when transitioned directly to `completed`, then an error is raised.
- [ ] REQ-0.22.0-01-04: Given plan text "Implement the REQ model" with parent context OBPI-0.20.0-01/REQ-0.20.0-01-01, when factory is called, then a TASK entity is created with auto-generated seq number.
- [ ] REQ-0.22.0-01-05: Given all 5 lifecycle states, when enumerated, then exactly {pending, in_progress, completed, blocked, escalated} are present.
- [ ] REQ-0.22.0-01-06: Given a TASK in `blocked` state, when transitioned to `in_progress`, then the model allows resume as a valid transition.

## Verification Commands (Concrete)

```bash
uv run -m unittest tests.test_tasks -v
# Expected: TASK parsing, transitions, and plan-derivation tests pass

uv run gz lint
# Expected: lint passes after task model edits

uv run gz typecheck
# Expected: task model types remain clean
```

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Coverage:** Coverage >= 40% maintained

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
