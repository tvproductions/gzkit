---
id: OBPI-0.22.0-02-task-ledger-events
parent: ADR-0.22.0-task-level-governance
item: 2
lane: Lite
status: Completed
---

# OBPI-0.22.0-02: TASK Ledger Events

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #2 — "TASK ledger events: started, completed, blocked, escalated"

**Status:** Completed

## Objective

Define four TASK-level ledger event types (`task_started`, `task_completed`,
`task_blocked`, `task_escalated`) following the existing event model patterns
in `events.py`. `task_started` covers both initial start and resume from
blocked state. Events are appended to the JSONL ledger for audit and
traceability.

## Lane

**Lite** — Internal ledger event types; no CLI changes.

## Allowed Paths

- `src/gzkit/events.py` — add TASK event models to existing event discriminated union
- `src/gzkit/tasks.py` — event emission helpers (if needed)
- `tests/test_tasks.py` — ledger event unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI belongs to OBPI-04
- `.gzkit/ledger.jsonl` — never edit manually
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Define four event types: `task_started`, `task_completed`, `task_blocked`, `task_escalated`.
1. REQUIREMENT: Each event MUST include: type, timestamp, task_id, obpi_id, adr_id, agent.
1. REQUIREMENT: `task_started` MUST be valid for both `pending -> in_progress` starts and `blocked -> in_progress` resumes; this ADR does not introduce a separate resume event type.
1. REQUIREMENT: `task_blocked` MUST include a `reason` field.
1. REQUIREMENT: `task_escalated` MUST include a `reason` field and optional `escalated_to` field.
1. REQUIREMENT: Events MUST follow existing Pydantic event model patterns in `events.py` (discriminated union).
1. REQUIREMENT: Events MUST be serializable to JSONL for ledger append.
1. NEVER: Edit the ledger file directly — use the existing ledger append API.

> STOP-on-BLOCKERS: OBPI-01 must be complete (TASK entity model with identifier scheme).

## Acceptance Criteria

- [x] REQ-0.22.0-02-01: Given a `task_started` event, when serialized to JSON, then includes type, timestamp, task_id, obpi_id, adr_id, agent.
- [x] REQ-0.22.0-02-02: Given a `task_blocked` event with reason "Missing dependency", when serialized, then reason field is present.
- [x] REQ-0.22.0-02-03: Given all four event types, when parsed via the discriminated union, then each resolves to the correct event model.
- [x] REQ-0.22.0-02-04: Given a blocked TASK resuming to `in_progress`, when the event is emitted, then `task_started` is reused rather than a new resume event type.

## Verification Commands (Concrete)

```bash
uv run -m unittest tests.test_tasks -v
# Expected: event serialization and discriminated-union tests pass

uv run gz lint
# Expected: lint passes after event-model edits

uv run gz typecheck
# Expected: event model types remain clean
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean

### Implementation Summary

- Events: Added `_TaskEventBase`, `TaskStartedEvent`, `TaskCompletedEvent`, `TaskBlockedEvent`, `TaskEscalatedEvent` to `src/gzkit/events.py`
- Union: Extended `TypedLedgerEvent` discriminated union with all four TASK event types
- Tests: 16 new event tests in `tests/test_tasks.py` covering serialization, reason fields, discriminated union parsing, and resume reuse
- Coverage: 76% on `events.py` (threshold 40%)

### Key Proof

```
$ uv run -m unittest tests.test_tasks -v
Ran 40 tests in 0.001s — OK
TestTaskStartedEvent: serialize, discriminated union, resume reuse, JSONL — all PASS
TestTaskBlockedEvent: reason field required and serialized — PASS
TestTaskEscalatedEvent: reason + optional escalated_to — PASS
TestAllFourEventTypes: 4 types defined, all roundtrip, common fields — PASS
```

---

**Brief Status:** Completed

**Date Completed:** 2026-03-28

**Evidence Hash:** -
