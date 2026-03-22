---
id: OBPI-0.22.0-04-gz-task-cli
parent: ADR-0.22.0-task-level-governance
item: 4
lane: Heavy
status: Accepted
---

# OBPI-0.22.0-04: gz task CLI

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- **Checklist Item:** #4 — "`gz task` CLI: list, start, complete, block lifecycle commands"

**Status:** Accepted

## Objective

Build the `gz task` CLI surface with subcommands for task lifecycle
management: `list` (show tasks for an OBPI), `start` (transition to
in_progress, including resume from blocked), `complete` (transition to
completed), `block` (transition to blocked with reason), and `escalate`
(transition to escalated with reason).

## Lane

**Heavy** — New CLI commands (external contract). Requires docs, BDD, and
human attestation.

## Allowed Paths

- `src/gzkit/commands/task.py` — CLI implementation
- `src/gzkit/cli.py` — register task subcommand
- `tests/test_tasks.py` — CLI smoke tests
- `docs/user/commands/task.md` — command documentation
- `features/task_governance.feature` — BDD scenarios
- `features/steps/task_governance_steps.py` — BDD steps

## Denied Paths

- `src/gzkit/tasks.py` — entity model belongs to OBPI-01 (read-only consumer)
- `src/gzkit/events.py` — event model belongs to OBPI-02 (consumer)
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz task list OBPI-X.Y.Z-NN` MUST show all tasks for that OBPI with status.
1. REQUIREMENT: `gz task start TASK-X.Y.Z-NN-MM-SS` MUST transition to `in_progress` and emit `task_started` event.
1. REQUIREMENT: `gz task start` on a blocked TASK MUST resume it to `in_progress` and reuse `task_started` event semantics.
1. REQUIREMENT: `gz task complete TASK-X.Y.Z-NN-MM-SS` MUST transition to completed and emit `task_completed` event.
1. REQUIREMENT: `gz task block TASK-X.Y.Z-NN-MM-SS --reason "..."` MUST transition to blocked and emit `task_blocked` event.
1. REQUIREMENT: `gz task escalate TASK-X.Y.Z-NN-MM-SS --reason "..."` MUST transition to escalated and emit `task_escalated` event.
1. REQUIREMENT: All subcommands support `--json` output.
1. REQUIREMENT: Invalid transitions MUST fail with exit code 1 and clear error message.
1. REQUIREMENT: `-h`/`--help` for each subcommand.

> STOP-on-BLOCKERS: OBPIs 01-02 must be complete.

## Acceptance Criteria

- [ ] REQ-0.22.0-04-01: Given `gz task list OBPI-0.20.0-01`, then shows tasks with status in table format.
- [ ] REQ-0.22.0-04-02: Given `gz task start TASK-0.20.0-01-01-01`, then status changes and ledger event emitted.
- [ ] REQ-0.22.0-04-03: Given `gz task complete` on a pending task, then exit code 1 with error.
- [ ] REQ-0.22.0-04-04: Given `gz task block --reason "Missing API"`, then blocked status and reason in ledger.
- [ ] REQ-0.22.0-04-05: Given `gz task list --json`, then valid JSON output.
- [ ] REQ-0.22.0-04-06: Given `gz task escalate --reason "Needs human decision"`, then escalated status and escalation reason are recorded.
- [ ] REQ-0.22.0-04-07: Given a blocked task, when `gz task start` is run, then the task resumes to `in_progress` and reuses `task_started` semantics.

## Verification Commands (Concrete)

```bash
uv run gz task --help
# Expected: task subcommands include list, start, complete, block, escalate

uv run gz task list OBPI-0.20.0-01 --json
# Expected: valid JSON task list for the target OBPI

uv run -m unittest tests.test_tasks -v
# Expected: CLI smoke tests pass for lifecycle transitions and invalid transitions

uv run -m behave features/task_governance.feature
# Expected: task CLI BDD scenarios pass

uv run mkdocs build --strict
# Expected: task command docs render cleanly

uv run gz lint
uv run gz typecheck
# Expected: CLI surface remains lint/type clean
```

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Command docs created, docs build passes
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **Code Quality:** Clean

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
