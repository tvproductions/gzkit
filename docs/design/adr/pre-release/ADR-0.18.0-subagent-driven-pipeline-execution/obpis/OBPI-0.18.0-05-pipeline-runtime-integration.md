---
id: OBPI-0.18.0-05-pipeline-runtime-integration
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 5
lane: Heavy
status: Accepted
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

## Denied Paths

- Core dispatch logic already implemented in OBPI-02/03/04 (this OBPI integrates, not reimplements)
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Pipeline runtime MUST track subagent dispatch state: `{task_id, role, model, dispatched_at, completed_at, status, result}`.
1. REQUIREMENT: Dispatch state MUST be persisted in the pipeline active marker (`.claude/plans/.pipeline-active-{OBPI-ID}.json`) so status is queryable.
1. REQUIREMENT: Result aggregation MUST compute: total tasks, completed, blocked, fix cycles, review findings by severity.
1. REQUIREMENT: Model routing configuration MUST be declarative (not hardcoded): task complexity heuristics and model mappings defined in pipeline runtime config.
1. REQUIREMENT: `gz roles` CLI MUST list the four roles with their handoff contracts.
1. REQUIREMENT: `gz roles --pipeline {OBPI-ID}` MUST show which roles were dispatched and their results for a completed or active pipeline run.
1. REQUIREMENT: Pipeline SKILL.md MUST document the controller/worker architecture including: dispatch sequence, result handling, review protocol, and REQ verification dispatch.
1. REQUIREMENT: BDD scenarios MUST cover the full dispatch lifecycle: plan → dispatch → review → verify → ceremony → sync.
1. NEVER: Break the Iron Law — all 5 stages must still run to completion.
1. ALWAYS: Subagent dispatch is opt-in per pipeline invocation (default: enabled). A `--no-subagents` flag allows fallback to inline execution for debugging.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Model Routing (Design Input)

```text
Task Complexity Heuristics:
  SIMPLE (economical model):
    - 1-2 files modified
    - Mechanical changes (rename, move, delete, format)
    - Test-only changes
    - Documentation updates
  STANDARD (default model):
    - 3-5 files modified
    - Feature implementation within existing patterns
    - Integration with existing modules
  COMPLEX (most capable model):
    - 6+ files modified
    - New architectural patterns
    - Cross-module refactoring
    - Review tasks (always complex — requires judgment)
```

## Edge Cases

- `--no-subagents` flag — entire pipeline runs inline (current behavior, preserved as fallback)
- Pipeline resumes from handoff — dispatch state recovered from active marker, continue from last incomplete task
- Model routing miscategorizes a task — reviewer catches quality issue, fix cycle dispatches at higher model tier
- `gz roles --pipeline` for a pipeline that used `--no-subagents` — shows "inline execution (no subagent dispatch)"

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [ ] Gate 1 (ADR): Intent recorded in brief
- [ ] Gate 2 (TDD): Unit tests for dispatch state tracking, result aggregation, model routing, `gz roles` CLI
- [ ] Gate 3 (Docs): SKILL.md updated, concept doc written, runbook updated, mkdocs build clean
- [ ] Gate 4 (BDD): Full dispatch lifecycle scenario passes
- [ ] Code Quality: Lint, format, type checks clean

### Gate 5: Human Attestation (MANDATORY)

**Attestation Commands:**

```bash
# Verify gz roles CLI
uv run gz roles

# Verify pipeline with subagent dispatch
uv run gz obpi pipeline OBPI-0.18.0-XX

# Verify fallback mode
uv run gz obpi pipeline OBPI-0.18.0-XX --no-subagents

# Verify dispatch state in active marker
cat .claude/plans/.pipeline-active-OBPI-0.18.0-XX.json | python -m json.tool
```

1. [ ] Agent presents CLI commands for verification
1. [ ] **STOP** — Agent waits for human to verify
1. [ ] **STOP** — Agent waits for human attestation response
1. [ ] Agent records attestation in brief

## Completion Checklist (Heavy)

- [ ] Gates 1-4 pass
- [ ] Gate 5 attestation commands presented
- [ ] Gate 5 attestation RECEIVED from human
- [ ] Attestation recorded in brief
- [ ] OBPI marked completed ONLY AFTER attestation
