---
id: OBPI-0.22.0-01-task-entity-model
parent: ADR-0.22.0-task-level-governance
item: 1
lane: Lite
status: attested_completed
---

# OBPI-0.22.0-01: TASK Entity Model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #1 — "TASK entity model: Pydantic model, identifier scheme, lifecycle states"

**Status:** Completed

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

- [x] REQ-0.22.0-01-01: Given a valid TASK string `TASK-0.20.0-01-01-01`, when parsed, then returns a TASK entity with correct semver, obpi_item, req_index, and seq components.
- [x] REQ-0.22.0-01-02: Given a TASK in `pending` state, when transitioned to `in_progress`, then status updates successfully.
- [x] REQ-0.22.0-01-03: Given a TASK in `pending` state, when transitioned directly to `completed`, then an error is raised.
- [x] REQ-0.22.0-01-04: Given plan text "Implement the REQ model" with parent context OBPI-0.20.0-01/REQ-0.20.0-01-01, when factory is called, then a TASK entity is created with auto-generated seq number.
- [x] REQ-0.22.0-01-05: Given all 5 lifecycle states, when enumerated, then exactly {pending, in_progress, completed, blocked, escalated} are present.
- [x] REQ-0.22.0-01-06: Given a TASK in `blocked` state, when transitioned to `in_progress`, then the model allows resume as a valid transition.

## Verification Commands (Concrete)

```bash
uv run -m unittest tests.test_tasks -v
# Expected: TASK parsing, transitions, and plan-derivation tests pass

uv run gz lint
# Expected: lint passes after task model edits

uv run gz typecheck
# Expected: task model types remain clean
```

### Implementation Summary

- Created: `src/gzkit/tasks.py` — TaskId, TaskStatus, TaskEntity, create_task_from_plan_step
- Created: `tests/test_tasks.py` — 24 unit tests covering all 6 REQs
- Pattern: follows ReqId/ReqEntity in triangle.py (frozen ConfigDict, regex parse, __str__ roundtrip)
- Transitions: 5 valid transitions enforced via _VALID_TRANSITIONS dict, invalid raise ValueError
- Factory: create_task_from_plan_step derives TASKs from plan text with zero-padded seq

### Key Proof

```
$ uv run -m unittest tests.test_tasks -v
Ran 24 tests in 0.001s — OK
All 6 REQs verified: parsing, valid transitions, invalid rejection, plan derivation, 5 states, resume
$ uv run gz lint — pass
$ uv run gz typecheck — pass
$ uv run gz test — 1808 pass
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass (24/24)
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Coverage:** Coverage >= 40% maintained

---

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
