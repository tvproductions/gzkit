---
id: OBPI-0.18.0-04-req-verification-dispatch
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 4
lane: Lite
status: Accepted
---

# OBPI-0.18.0-04: REQ-Level Parallel Verification Dispatch

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #4 — "REQ-level parallel verification dispatch in Stage 3"

**Status:** Accepted

## Objective

Enable Stage 3 (Verify) to dispatch parallel verification subagents scoped to individual
requirements when those requirements have non-overlapping test paths. Each REQ verification
subagent runs the tests and checks relevant to its requirement independently, reducing
verification wall-clock time for OBPIs with many requirements.

This OBPI does not depend on the formal REQ entity from `ADR-pool.task-level-governance`.
It works with the existing brief requirements section — each numbered requirement in the brief
becomes a verification scope. When formal REQ entities land, they become the natural dispatch
unit.

## Lane

**Lite** — Internal verification optimization; no external CLI/API/schema contract changes.
Stage 3 already runs verification; this changes how (parallel subagents vs sequential inline).

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` — verification dispatch logic
- `tests/test_verification_dispatch.py` — parallel dispatch and result aggregation tests

## Denied Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` — skill documentation belongs to OBPI-05
- `src/gzkit/commands/` — CLI surface belongs to OBPI-05
- Stage 2 logic — implementer dispatch belongs to OBPI-02
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Stage 3 MUST identify which requirements have non-overlapping test paths before dispatching parallel subagents.
1. REQUIREMENT: Requirements with overlapping test paths MUST be verified sequentially (same subagent or inline) to avoid test interference.
1. REQUIREMENT: Each verification subagent receives: the requirement text, the specific test files/commands to run, and the expected pass criteria.
1. REQUIREMENT: Verification results are aggregated by the controller: all REQs must PASS for Stage 3 to succeed.
1. REQUIREMENT: If any verification subagent returns FAIL, the controller attempts one fix cycle (dispatch implementer with failure details), then re-verifies. If still failing after 1 retry, Stage 3 fails with handoff.
1. REQUIREMENT: Baseline quality checks (`gz lint`, `gz typecheck`, `gz test`) always run inline in the controller — they are not dispatched to subagents. Only brief-specific requirement verification is parallelized.
1. NEVER: Dispatch parallel verification subagents that would run overlapping test suites.
1. ALWAYS: Fall back to sequential inline verification if requirement test paths cannot be determined.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Dispatch Decision Logic (Design Input)

```text
Stage 3 entry:
  1. Run baseline checks inline (gz lint, gz typecheck, gz test)
  2. If baseline fails → attempt fix, retry once, fail with handoff
  3. Parse brief requirements into verification scopes:
     - For each REQ: identify test files, verification commands, expected outputs
     - Compute path overlap matrix between REQs
  4. Partition REQs into independent groups (no path overlap within group)
  5. For each independent group:
     - If group has 1 REQ: dispatch single verification subagent
     - If group has 2+ REQs with no overlap: dispatch parallel subagents
     - If overlap detected: run sequentially in one subagent
  6. Aggregate results: all PASS → Stage 3 succeeds → proceed to Stage 4
```

## Edge Cases

- Brief has zero explicit requirements — skip parallel dispatch, run only baseline checks
- Brief has 1 requirement — dispatch single verification subagent (no parallelization benefit, but still isolated context)
- All requirements overlap on the same test files — sequential fallback (no parallel dispatch)
- Verification subagent times out — treat as FAIL, attempt retry
- REQ-level entities exist (future: task-level-governance) — use REQ IDs as natural dispatch boundaries

## Quality Gates (Lite)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 2: TDD

- [ ] Unit tests for path overlap detection
- [ ] Unit tests for REQ partitioning into independent groups
- [ ] Unit tests for parallel dispatch and result aggregation
- [ ] Unit tests for sequential fallback
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Coverage:** Coverage >= 40% maintained
- [ ] **OBPI Completion:** Record evidence in brief
