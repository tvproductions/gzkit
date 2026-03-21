# Subagent Pipeline Execution

The gz-obpi-pipeline uses a controller/worker architecture for implementation
and verification stages. The main session orchestrates governance stages and
dispatches fresh subagents for task-level work.

## Controller/Worker Architecture

The pipeline controller (main session) manages the five governance stages. During
Stage 2 (Implement) and Stage 3 (Verify), it dispatches subagents — fresh
sessions scoped to individual tasks. Each subagent starts with clean context,
executes its task, and returns a structured result.

```text
Main Session (Controller)
  Stage 1: Load Context
  Stage 2: Implement
    ├─ dispatch Implementer subagent (task 1)
    │   └─ returns HandoffResult
    │   ├─ dispatch Spec Reviewer
    │   └─ dispatch Quality Reviewer
    ├─ dispatch Implementer subagent (task 2)
    │   └─ ...
  Stage 3: Verify
    ├─ dispatch Verification subagents (per REQ)
  Stage 4: Present Evidence (human gate)
  Stage 5: Sync and Account
```

## Four Agent Roles

| Role | Agent File | Stages | Write Access |
|------|-----------|--------|-------------|
| Planner | *(controller)* | pre-pipeline, 1 | No |
| Implementer | `.claude/agents/implementer.md` | 2 | Yes |
| Reviewer | `.claude/agents/spec-reviewer.md`, `.claude/agents/quality-reviewer.md` | 2, 3 | No |
| Narrator | `.claude/agents/narrator.md` | 4, 5 | No |

Query roles with `gz roles`. View dispatch history with `gz roles --pipeline OBPI-ID`.

## Model Routing

Task complexity determines which model handles each dispatch:

| Complexity | File Count | Implementer | Reviewer |
|-----------|-----------|-------------|---------|
| Simple | 1-2 files | haiku | sonnet |
| Standard | 3-5 files | sonnet | sonnet |
| Complex | 6+ files | opus | opus |

Routing is declarative via `.gzkit/pipeline-config.json` (optional). Defaults
match the table above.

## Dispatch State

Dispatch records are persisted in the pipeline active marker
(`.claude/plans/.pipeline-active-{OBPI-ID}.json`) during execution. On
completion, a dispatch summary is written for historical queries.

## Fallback Mode

Use `--no-subagents` on `gz obpi pipeline` to run the entire pipeline in a
single session (current inline behavior). Useful for debugging or environments
without subagent support.
