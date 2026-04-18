---
id: OBPI-0.18.0-06-wire-implementer-dispatch
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 6
lane: Heavy
status: attested_completed
---

# OBPI-0.18.0-06: Wire Implementer Dispatch into Stage 2

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #6 — "Wire implementer dispatch into Stage 2 of the pipeline skill"

**Status:** Pending

## Objective

Update the pipeline skill (`SKILL.md`) Stage 2 instructions to actually dispatch fresh
implementer subagents per plan task using the dispatch machinery built in OBPIs 01-05.
Currently Stage 2 executes all implementation inline in the main session. After this OBPI,
Stage 2 iterates plan tasks and dispatches each to a fresh implementer subagent via the
Agent tool, collecting structured results (`DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`,
`BLOCKED`) and recording dispatch state in the pipeline marker.

## Lane

**Heavy** — Changes the pipeline skill external contract (SKILL.md Stage 2 behavior).

## Allowed Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` — Stage 2 dispatch wiring
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — canonical skill mirror
- `.github/skills/gz-obpi-pipeline/SKILL.md` — GitHub mirror
- `.agents/skills/gz-obpi-pipeline/SKILL.md` — agents mirror
- `src/gzkit/pipeline_runtime.py` — any runtime helpers needed for dispatch wiring
- `tests/test_pipeline_dispatch.py` — dispatch wiring tests
- `features/subagent_pipeline.feature` — BDD scenarios for dispatch
- `features/steps/subagent_pipeline_steps.py` — BDD step implementations
- `docs/user/runbook.md` — runbook updates for subagent dispatch operation

## Denied Paths

- Core dispatch models/functions already built in OBPI-02 (this OBPI wires, not reimplements)
- Role taxonomy (OBPI-01), review protocol (OBPI-03), verification dispatch (OBPI-04)
- Stages 1, 3, 4, 5 logic (Stage 3 wiring is OBPI-08)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: SKILL.md Stage 2 MUST dispatch a fresh implementer subagent per plan task using the Agent tool with `subagent_type` referencing the implementer agent file.
1. REQUIREMENT: Each dispatch MUST pass scoped context: task description, allowed files, test expectations, brief requirements.
1. REQUIREMENT: Each dispatch MUST use model-aware routing from `ModelRoutingConfig` (OBPI-05) based on task complexity heuristics.
1. REQUIREMENT: Dispatch results MUST be recorded as `SubagentDispatchRecord` entries in the pipeline active marker.
1. REQUIREMENT: The controller MUST handle all four result statuses: `DONE` (advance), `DONE_WITH_CONCERNS` (log and advance), `NEEDS_CONTEXT` (provide context and retry once), `BLOCKED` (halt and report).
1. REQUIREMENT: `--no-subagents` flag MUST bypass dispatch and execute inline (preserving current behavior as fallback).
1. REQUIREMENT: Dispatch MUST be sequential (not parallel) per superpowers methodology — one implementer at a time.
1. NEVER: Skip remaining stages after all tasks dispatch. The Iron Law holds.
1. ALWAYS: Record dispatch timing for model routing optimization.

> STOP-on-BLOCKERS: if OBPI-02 or OBPI-05 dispatch machinery is missing, print a BLOCKERS list and halt.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.18.0-06-01: REQUIREMENT: SKILL.md Stage 2 MUST dispatch a fresh implementer subagent per plan task using the Agent tool with `subagent_type` referencing the implementer agent file.
- [x] REQ-0.18.0-06-02: REQUIREMENT: Each dispatch MUST pass scoped context: task description, allowed files, test expectations, brief requirements.
- [x] REQ-0.18.0-06-03: REQUIREMENT: Each dispatch MUST use model-aware routing from `ModelRoutingConfig` (OBPI-05) based on task complexity heuristics.
- [x] REQ-0.18.0-06-04: REQUIREMENT: Dispatch results MUST be recorded as `SubagentDispatchRecord` entries in the pipeline active marker.
- [x] REQ-0.18.0-06-05: REQUIREMENT: The controller MUST handle all four result statuses: `DONE` (advance), `DONE_WITH_CONCERNS` (log and advance), `NEEDS_CONTEXT` (provide context and retry once), `BLOCKED` (halt and report).
- [x] REQ-0.18.0-06-06: REQUIREMENT: `--no-subagents` flag MUST bypass dispatch and execute inline (preserving current behavior as fallback).
- [x] REQ-0.18.0-06-07: REQUIREMENT: Dispatch MUST be sequential (not parallel) per superpowers methodology — one implementer at a time.
- [x] REQ-0.18.0-06-08: NEVER: Skip remaining stages after all tasks dispatch. The Iron Law holds.
- [x] REQ-0.18.0-06-09: ALWAYS: Record dispatch timing for model routing optimization.


## Edge Cases

- `--no-subagents` — Stage 2 runs inline as today; no Agent tool calls
- Implementer returns `BLOCKED` — controller halts Stage 2, records blocker, presents to user
- Implementer returns `NEEDS_CONTEXT` — controller adds context from brief and retries once; second `NEEDS_CONTEXT` treated as `BLOCKED`
- Agent file missing — falls back to inline execution with warning
- Task modifies files outside allowed paths — implementer agent's hook enforcement prevents it; controller records violation

### Implementation Summary

- Files modified: .gzkit/skills/gz-obpi-pipeline/SKILL.md (Stage 2 rewritten), .claude/skills/gz-obpi-pipeline/SKILL.md, .github/skills/gz-obpi-pipeline/SKILL.md, .agents/skills/gz-obpi-pipeline/SKILL.md, tests/test_pipeline_dispatch.py, features/subagent_pipeline.feature, features/steps/subagent_pipeline_steps.py, docs/user/runbook.md
- Tests added: tests/test_pipeline_dispatch.py::TestStage2DispatchLoopContract (7 tests), 2 BDD scenarios (19 steps)
- Date completed: 2026-03-21

### Key Proof

```bash
$ uv run -m unittest tests.test_pipeline_dispatch.TestStage2DispatchLoopContract -v
test_blocked_task_halts_loop ... ok
test_done_with_concerns_logs_and_advances ... ok
test_empty_plan_produces_empty_state ... ok
test_full_loop_creates_state_and_composes_prompts ... ok
test_model_routing_per_task_complexity ... ok
test_needs_context_redispatches_once_then_blocks ... ok
test_sequential_advance_and_result_handling ... ok
Ran 7 tests in 0.001s — OK

$ uv run -m behave features/subagent_pipeline.feature --tags=@stage2
2 scenarios passed, 0 failed — 19 steps passed
```

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [x] Gate 1 (ADR): Intent recorded in brief
- [x] Gate 2 (TDD): Unit tests for dispatch wiring
- [x] Gate 3 (Docs): SKILL.md updated, runbook updated
- [x] Gate 4 (BDD): Dispatch lifecycle scenario passes
- [x] Code Quality: Lint, format, type checks clean

### Gate 5: Human Attestation (MANDATORY)

1. [x] Agent presents CLI commands for verification
1. [x] **STOP** — Agent waits for human to verify
1. [x] **STOP** — Agent waits for human attestation response — "attest completed"
1. [x] Agent records attestation in brief

## Completion Checklist (Heavy)

- [x] Gates 1-4 pass
- [x] Gate 5 attestation commands presented
- [x] Gate 5 attestation RECEIVED from human
- [x] Attestation recorded in brief
- [x] OBPI marked completed ONLY AFTER attestation
