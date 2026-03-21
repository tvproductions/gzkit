---
id: OBPI-0.18.0-05-pipeline-runtime-integration
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.18.0-05: Pipeline Runtime and Skill Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #5 — "Pipeline runtime and skill integration: dispatch tracking, result aggregation, model routing"

**Status:** Accepted

## Objective

Integrate all subagent dispatch patterns (OBPI-02 implementer, OBPI-03 reviewer, OBPI-04
REQ verification) into the pipeline runtime and update the pipeline skill documentation.
Add `gz roles` CLI surface for querying the role taxonomy. Add dispatch state tracking,
result aggregation, and model-aware routing configuration to `pipeline_runtime.py`.

This is the integration OBPI that wires everything together and updates external-facing
documentation.

## Lane

**Heavy** — Changes the pipeline skill documentation (external contract), adds `gz roles` CLI
surface, and modifies runtime behavior.

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` — dispatch state tracking, result aggregation, model routing
- `src/gzkit/roles.py` — integration with dispatch (if needed beyond OBPI-01)
- `src/gzkit/commands/roles.py` — `gz roles` CLI command
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — controller/worker architecture documentation
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — canonical skill (if separate from vendor mirror)
- `tests/test_pipeline_dispatch.py` — integration tests
- `tests/test_roles_cli.py` — CLI tests for `gz roles`
- `features/subagent_pipeline.feature` — BDD scenarios
- `features/steps/subagent_pipeline_steps.py` — BDD step implementations
- `docs/user/concepts/subagent-pipeline.md` — concept documentation
- `docs/user/runbook.md` — runbook updates

- `.claude/agents/implementer.md` — integration validation of agent file
- `.claude/agents/spec-reviewer.md` — integration validation of agent file
- `.claude/agents/quality-reviewer.md` — integration validation of agent file
- `.claude/agents/narrator.md` — integration validation of agent file

## Denied Paths

- Core dispatch logic already implemented in OBPI-02/03/04 (this OBPI integrates, not reimplements)
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Pipeline runtime MUST track subagent dispatch state: `{task_id, role, agent_file, model, isolation, background, dispatched_at, completed_at, status, result}`.
1. REQUIREMENT: Dispatch state MUST be persisted in the pipeline active marker (`.claude/plans/.pipeline-active-{OBPI-ID}.json`) so status is queryable.
1. REQUIREMENT: Result aggregation MUST compute: total tasks, completed, blocked, fix cycles, review findings by severity, model usage per role.
1. REQUIREMENT: Model routing configuration MUST be declarative (not hardcoded): task complexity heuristics → model ID mappings (`haiku`/`sonnet`/`opus`) defined in pipeline runtime config.
1. REQUIREMENT: `gz roles` CLI MUST list the four roles with their handoff contracts and corresponding `.claude/agents/` file paths.
1. REQUIREMENT: `gz roles --pipeline {OBPI-ID}` MUST show which roles were dispatched, their model overrides, isolation mode, and results for a completed or active pipeline run.
1. REQUIREMENT: Pipeline SKILL.md MUST document the controller/worker architecture including: dispatch sequence, agent file references, model routing, worktree isolation for parallel verification, and review protocol.
1. REQUIREMENT: BDD scenarios MUST cover the full dispatch lifecycle: plan → dispatch → review → verify → ceremony → sync.
1. REQUIREMENT: The four agent files (`.claude/agents/implementer.md`, `spec-reviewer.md`, `quality-reviewer.md`, `narrator.md`) MUST be validated as part of OBPI-05 integration — verifying tool restrictions, model defaults, maxTurns, and hooks are correctly wired.
1. NEVER: Break the Iron Law — all 5 stages must still run to completion.
1. ALWAYS: Subagent dispatch is opt-in per pipeline invocation (default: enabled). A `--no-subagents` flag allows fallback to inline execution for debugging.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Model Routing (Design Input)

Agent files define `model: inherit` by default. The controller overrides this per-dispatch via the Agent tool's `model` parameter, which takes precedence over the agent file's frontmatter.

```text
Task Complexity Heuristics → Claude Code Model IDs:
  SIMPLE (haiku — fast, economical):
    - 1-2 files modified
    - Mechanical changes (rename, move, delete, format)
    - Test-only changes
    - Documentation updates
  STANDARD (sonnet — balanced):
    - 3-5 files modified
    - Feature implementation within existing patterns
    - Integration with existing modules
  COMPLEX (opus — most capable):
    - 6+ files modified
    - New architectural patterns
    - Cross-module refactoring

Role-Specific Overrides (not complexity-dependent):
  Spec Compliance Reviewer: sonnet minimum, opus for complex briefs
  Code Quality Reviewer: sonnet minimum, opus for architectural review
  Narrator: sonnet (ceremony presentation requires coherent synthesis)
```

The mapping is declarative in pipeline runtime config, not hardcoded. Agent files use `model: inherit` so the controller has full routing authority.

## Edge Cases

- `--no-subagents` flag — entire pipeline runs inline (current behavior, preserved as fallback); no agent files loaded
- Pipeline resumes from handoff — dispatch state recovered from active marker, continue from last incomplete task; agent files re-loaded from `.claude/agents/`
- Model routing miscategorizes a task — reviewer catches quality issue, fix cycle dispatches at higher model tier (controller adjusts `model` parameter)
- `gz roles --pipeline` for a pipeline that used `--no-subagents` — shows "inline execution (no subagent dispatch)"
- Agent file missing or malformed — controller falls back to inline execution for that role with warning
- Agent file `maxTurns` exceeded — controller logs turn count, treats as BLOCKED, records in dispatch state

### Implementation Summary

- Files created: src/gzkit/commands/roles.py, tests/test_pipeline_integration.py, tests/test_roles_cli.py, docs/user/commands/roles.md, docs/user/concepts/subagent-pipeline.md
- Files modified: src/gzkit/pipeline_runtime.py, src/gzkit/cli.py, src/gzkit/commands/common.py, .claude/skills/gz-obpi-pipeline/SKILL.md, features/subagent_pipeline.feature, features/steps/subagent_pipeline_steps.py, docs/user/runbook.md
- Tests added: 27 unit tests (test_pipeline_integration.py, test_roles_cli.py), 5 BDD scenarios
- Date completed: 2026-03-21

### Key Proof

```bash
$ uv run gz roles --json | python -m json.tool | head -8
[
  {
    "role": "Planner",
    "description": "Creates ADR documents...",
    "stages": "pre-pipeline, stage-1",
    "agent_file": "",
    "tools": "Read, Glob, Grep, Bash, Agent",
    "can_write": false
  }
]

$ uv run -m unittest tests.test_pipeline_integration tests.test_roles_cli -q
..........................
----------------------------------------------------------------------
Ran 27 tests in 0.007s
OK
```

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [x] Gate 1 (ADR): Intent recorded in brief
- [x] Gate 2 (TDD): Unit tests for dispatch state tracking, result aggregation, model routing, `gz roles` CLI
- [x] Gate 3 (Docs): SKILL.md updated, concept doc written, runbook updated, mkdocs build clean
- [x] Gate 4 (BDD): Full dispatch lifecycle scenario passes (19 scenarios, 73 steps)
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
