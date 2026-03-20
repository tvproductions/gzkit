---
id: OBPI-0.18.0-02-implementer-subagent-dispatch
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.18.0-02: Controller/Worker Stage 2 — Implementer Subagent Dispatch

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #2 — "Controller/worker Stage 2: dispatch fresh implementer subagents per plan task"

**Status:** Completed

## Objective

Refactor pipeline Stage 2 from single-session inline execution to a controller/worker pattern.
The main session (controller) parses the approved plan into individual tasks and dispatches a
fresh implementer subagent for each task. This prevents context pollution, enables model-aware
routing, and keeps the orchestrator lean for Stages 3-5.

## Lane

**Heavy** — Changes the pipeline execution model, an external behavioral contract consumed by
agents and documented in SKILL.md.

## Allowed Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` — Stage 2 architecture documentation
- `src/gzkit/pipeline_runtime.py` — dispatch loop, result handling, task state tracking
- `tests/test_pipeline_dispatch.py` — dispatch and result handling tests
- `features/subagent_pipeline.feature` — BDD scenarios for dispatch lifecycle
- `features/steps/subagent_pipeline_steps.py` — BDD step implementations

## Denied Paths

- Stage 3/4/5 logic — other OBPIs or existing behavior
- `src/gzkit/roles.py` — role data model belongs to OBPI-01
- `src/gzkit/commands/` — CLI surface belongs to OBPI-05
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Stage 2 MUST dispatch one fresh subagent per plan task. Tasks are never batched.
1. REQUIREMENT: Implementer subagents are dispatched sequentially, never in parallel. This prevents file conflicts and ensures each task builds on the previous one's changes.
1. REQUIREMENT: Each subagent receives scoped context: task description, allowed file paths (from brief), test expectations, and brief requirements relevant to this task.
1. REQUIREMENT: Each subagent MUST return a structured result: `{status, files_changed, tests_added, concerns}`.
1. REQUIREMENT: Controller handles all four result statuses:
   - `DONE` — advance to next task
   - `DONE_WITH_CONCERNS` — log concerns, advance
   - `NEEDS_CONTEXT` — provide requested context, re-dispatch
   - `BLOCKED` — log blocker, attempt fix (2 tries), then handoff
1. REQUIREMENT: Model-aware routing — simple tasks (1-2 files, mechanical changes) MAY use economical models (`haiku`); integration/architecture tasks MUST use capable models (`opus`). The controller overrides the agent file's `model: inherit` via the Agent tool's `model` parameter per-dispatch.
1. REQUIREMENT: Implementer subagent MUST be dispatched using the `.claude/agents/implementer.md` agent file, which enforces `permissionMode: acceptEdits` (non-blocking file writes) and `maxTurns: 25` (bounded loop).
1. REQUIREMENT: File path enforcement MUST use a `hooks.PreToolUse` hook on Edit/Write tools that validates against the brief's allowed paths — structural enforcement, not prompt-only instruction.
1. NEVER: Dispatch multiple implementer subagents in parallel for the same OBPI.
1. NEVER: Let the controller write implementation code directly — it orchestrates only.
1. ALWAYS: After all tasks complete, the controller MUST proceed to Stage 3 immediately (Iron Law).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Controller Loop (Design Input)

```text
For each task in approved_plan.tasks:
  1. Compose subagent prompt:
     - Task description and step-by-step instructions
     - Allowed file paths (intersection of brief allowlist and task scope)
     - Test expectations (what tests to write, what to verify)
     - TDD discipline: write failing test -> verify failure -> implement -> verify pass
  2. Select model based on task complexity:
     - SIMPLE (1-2 files, mechanical) → model: "haiku"
     - STANDARD (3-5 files, feature) → model: "sonnet"
     - COMPLEX (6+ files, cross-module) → model: "opus"
  3. Dispatch implementer subagent via Agent tool:
     - subagent_type: "implementer" (references .claude/agents/implementer.md)
     - model: override from step 2 (takes precedence over agent file's "inherit")
     - Agent file enforces: tools allowlist, permissionMode, maxTurns, hooks
  4. Receive structured result
  5. Handle result status (advance / re-dispatch / fix / handoff)
  6. Update task tracking (TaskUpdate)
  7. [If reviewer protocol enabled] Dispatch reviewer subagents (OBPI-03)
```

### File Path Enforcement Hook

The implementer agent file includes a `PreToolUse` hook that validates Edit/Write targets against the brief's allowed paths. The controller generates a task-scoped allowlist and injects it as an environment variable before dispatch:

```text
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/validate-allowed-paths.sh"
```

The validation script reads `$PIPELINE_ALLOWED_PATHS` and exits with code 2 (block) if the target file is outside scope. This is structural enforcement — the subagent cannot bypass it via prompt manipulation.

## Edge Cases

- Plan has zero tasks (degenerate case) — skip Stage 2, proceed to Stage 3
- Subagent returns `NEEDS_CONTEXT` repeatedly (circuit breaker after 2 re-dispatches) — treat as BLOCKED
- Subagent attempts to modify files outside allowed paths — `PreToolUse` hook blocks the tool call (exit code 2); subagent must work within scope or return `BLOCKED`
- Subagent crashes or times out — treat as BLOCKED, log error, attempt re-dispatch once
- `maxTurns` (25) exceeded before task completion — Agent tool terminates subagent; controller treats as BLOCKED
- Model override produces unexpected cost — controller logs model selection rationale for auditability

### Implementation Summary

- Runtime: Added dispatch data models (TaskComplexity, DispatchTask, DispatchRecord, DispatchState) and orchestration functions to `src/gzkit/pipeline_runtime.py`
- Extraction: `extract_plan_tasks()` parses heading-format and numbered-list plans into task dicts
- Classification: `classify_task_complexity()` assesses SIMPLE/STANDARD/COMPLEX based on file scope
- Routing: `select_dispatch_model()` maps SIMPLE→haiku, STANDARD→sonnet, COMPLEX→opus
- Prompt: `compose_implementer_prompt()` builds scoped context (allowed files, test expectations, brief requirements)
- Parsing: `parse_handoff_result()` extracts structured HandoffResult from subagent output JSON blocks
- State: `create_dispatch_state()`, `advance_dispatch()`, `handle_task_result()` manage dispatch lifecycle with circuit breakers
- Docs: SKILL.md Stage 2 updated with controller/worker architecture, controller loop, runtime function catalog

### Key Proof

```
$ uv run -m unittest tests.test_pipeline_dispatch -v
Ran 46 tests in 0.001s — OK

$ uv run -m behave features/subagent_pipeline.feature --tags=@dispatch
15 scenarios passed, 0 failed, 59 steps passed

$ uv run coverage report --include='src/gzkit/pipeline_runtime.py'
src/gzkit/pipeline_runtime.py  410  218  47%
```

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [x] Gate 1 (ADR): Intent recorded in brief
- [x] Gate 2 (TDD): Unit tests for dispatch loop, result handling, model routing
- [x] Gate 3 (Docs): SKILL.md updated, mkdocs build clean
- [x] Gate 4 (BDD): Dispatch lifecycle scenarios pass
- [x] Code Quality: Lint, format, type checks clean

### Gate 5: Human Attestation (MANDATORY)

1. [x] Agent presents CLI commands for pipeline dispatch verification
1. [x] **STOP** — Agent waits for human to verify dispatch behavior
1. [x] **STOP** — Agent waits for human attestation response
1. [x] Agent records attestation in brief

## Completion Checklist (Heavy)

- [x] Gates 1-4 pass
- [x] Gate 5 attestation commands presented
- [x] Gate 5 attestation RECEIVED from human
- [x] Attestation recorded in brief
- [x] OBPI marked completed ONLY AFTER attestation
