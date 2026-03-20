---
id: OBPI-0.22.0-05-status-and-state-integration
parent: ADR-0.22.0-task-level-governance
item: 5
lane: Heavy
status: Accepted
---

# OBPI-0.22.0-05: Status and State Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #5 — "Status and state integration: TASK data in `gz status` and `gz state`"

**Status:** Accepted

## Objective

Integrate TASK status data into existing `gz status` and `gz state` reporting commands so operators can see task-level progress alongside OBPI and ADR status.

## Lane

**Heavy** — Changes existing CLI output contracts.

## Allowed Paths

- `src/gzkit/commands/` — status and state command updates
- `src/gzkit/cli.py` — if needed for command registration
- `tests/test_tasks.py` — integration tests
- `docs/user/commands/status.md` — updated docs
- `docs/user/commands/state.md` — updated docs

## Denied Paths

- `src/gzkit/tasks.py` — entity model is read-only
- `src/gzkit/events.py` — event model is read-only
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz status` MUST show task-level summary when tasks exist for active OBPIs.
1. REQUIREMENT: `gz state --json` MUST include task data in its JSON output.
1. REQUIREMENT: Task summary MUST show: total tasks, pending, in_progress, completed, blocked.
1. REQUIREMENT: Task data MUST NOT appear when no tasks exist (backward compatible).
1. NEVER: Break existing `gz status` output format for consumers without tasks.

> STOP-on-BLOCKERS: OBPI-04 must be complete (`gz task` CLI must work first).

## Acceptance Criteria

- [ ] REQ-0.22.0-05-01: Given active tasks for OBPI-0.20.0-01, when `gz status` is run, then task summary row appears.
- [ ] REQ-0.22.0-05-02: Given no tasks exist, when `gz status` is run, then output is unchanged from current behavior.
- [ ] REQ-0.22.0-05-03: Given `gz state --json`, then JSON includes task counts per OBPI.

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Docs updated, docs build passes
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **Code Quality:** Clean

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
