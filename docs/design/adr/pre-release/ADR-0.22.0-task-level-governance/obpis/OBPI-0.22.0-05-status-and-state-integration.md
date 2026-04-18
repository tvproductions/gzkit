---
id: OBPI-0.22.0-05-status-and-state-integration
parent: ADR-0.22.0-task-level-governance
item: 5
lane: Heavy
status: attested_completed
---

# OBPI-0.22.0-05: Status and State Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #5 — "Status and state integration: TASK data in `gz status` and `gz state`"

**Status:** Completed

## Objective

Integrate TASK status data into existing `gz status` and `gz state` reporting
commands so operators can see task-level progress alongside OBPI and ADR
status, including escalated-task visibility and whether TASK tracing is
advisory or required for the active lane.

## Lane

**Heavy** — Changes existing CLI output contracts. Requires docs, BDD, and
human attestation.

## Allowed Paths

- `src/gzkit/commands/` — status and state command updates
- `src/gzkit/cli.py` — if needed for command registration
- `tests/test_tasks.py` — integration tests
- `docs/user/commands/status.md` — updated docs
- `docs/user/commands/state.md` — updated docs
- `features/task_governance.feature` — reporting acceptance scenarios
- `features/steps/task_governance_steps.py` — BDD step implementations

## Denied Paths

- `src/gzkit/tasks.py` — entity model is read-only
- `src/gzkit/events.py` — event model is read-only
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz status` MUST show task-level summary when tasks exist for active OBPIs.
1. REQUIREMENT: `gz state --json` MUST include task data in its JSON output.
1. REQUIREMENT: Task summary MUST show: total tasks, pending, in_progress, completed, blocked, escalated.
1. REQUIREMENT: Reporting MUST surface whether TASK tracing is advisory (Lite) or required (Heavy) for the active lane.
1. REQUIREMENT: Task data MUST NOT appear when no tasks exist (backward compatible).
1. NEVER: Break existing `gz status` output format for consumers without tasks.

> STOP-on-BLOCKERS: OBPI-04 must be complete (`gz task` CLI must work first).

## Acceptance Criteria

- [x] REQ-0.22.0-05-01: Given active tasks for OBPI-0.20.0-01, when `gz status` is run, then task summary row appears.
- [x] REQ-0.22.0-05-02: Given no tasks exist, when `gz status` is run, then output is unchanged from current behavior.
- [x] REQ-0.22.0-05-03: Given `gz state --json`, then JSON includes task counts per OBPI.
- [x] REQ-0.22.0-05-04: Given escalated tasks exist, when `gz status` is run, then escalated count is visible in the task summary.
- [x] REQ-0.22.0-05-05: Given an active Lite or Heavy OBPI, when task data is shown, then the output indicates whether tracing is advisory or required for that lane.

## Quality Gates (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Integration tests verify task summaries, escalated counts, and
  lane-policy surfacing
- [x] Tests pass: `uv run -m unittest tests.test_tasks -v`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [x] `docs/user/commands/status.md` updated with task summary examples
- [x] `docs/user/commands/state.md` updated with task JSON schema examples
- [x] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [x] `features/task_governance.feature` covers task-aware reporting behavior
- [x] `uv run -m behave features/task_governance.feature` passes

### Gate 5: Human

- [x] Human attestation recorded

## Verification Commands (Concrete)

```bash
uv run gz status
# Expected: task summary appears only when tasks exist and includes escalated count

uv run gz state --json
# Expected: task data and lane-policy fields are present in JSON output

uv run -m unittest tests.test_tasks -v
# Expected: reporting integration tests pass

uv run -m behave features/task_governance.feature
# Expected: reporting/CLI BDD scenarios pass

uv run mkdocs build --strict
# Expected: status/state docs build cleanly

uv run gz lint
uv run gz typecheck
# Expected: reporting integration remains lint/type clean
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass
- [x] **Gate 3 (Docs):** Docs updated, docs build passes
- [x] **Gate 4 (BDD):** Acceptance scenarios pass
- [x] **Gate 5 (Human):** Attestation recorded
- [x] **Code Quality:** Clean

### Implementation Summary

- Files modified: `src/gzkit/commands/status.py`, `src/gzkit/commands/state.py`
- Tests added: 11 integration tests in `tests/test_tasks.py` (TestStatusTaskSummary, TestStateTaskIntegration)
- BDD scenarios added: 4 new scenarios in `features/task_governance.feature`
- Docs updated: `docs/user/commands/status.md`, `docs/user/commands/state.md`
- Validation commands run: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`, `uv run mkdocs build --strict`, `uv run -m behave features/task_governance.feature`

### Key Proof

```
uv run -m unittest tests.test_tasks.TestStatusTaskSummary tests.test_tasks.TestStateTaskIntegration -v
test_status_json_includes_task_summary ... ok
test_status_json_includes_tracing_policy ... ok
test_status_json_no_task_summary_when_no_tasks ... ok
test_status_no_task_section_when_no_tasks ... ok
test_status_shows_escalated_count ... ok
test_status_shows_task_summary_when_tasks_exist ... ok
test_status_shows_tracing_policy ... ok
test_state_json_includes_task_data ... ok
test_state_json_no_task_data_when_no_tasks ... ok
test_state_json_task_summary_counts ... ok
test_state_json_task_tracing_policy ... ok
Ran 11 tests in 0.256s — OK
```

### Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: `2026-03-28`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-28

**Evidence Hash:** -
