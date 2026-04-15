---
id: OBPI-0.18.0-04-req-verification-dispatch
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 4
lane: Lite
status: Completed
---

# OBPI-0.18.0-04: REQ-Level Parallel Verification Dispatch

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #4 — "REQ-level parallel verification dispatch in Stage 3"

**Status:** Completed

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
1. REQUIREMENT: Parallel verification subagents MUST be dispatched with `isolation: "worktree"` — each subagent operates on an isolated git worktree copy. This eliminates file-conflict risk and makes path-overlap analysis a performance optimization rather than a safety requirement.
1. REQUIREMENT: Parallel verification subagents MUST be dispatched with `run_in_background: true` to enable concurrent execution. The controller is notified when each completes.
1. REQUIREMENT: Verification subagents MUST use read-only tools (`Read, Glob, Grep, Bash`) — Bash is needed for running test commands but Edit/Write are denied since verification should not modify code.
1. NEVER: Dispatch parallel verification subagents without worktree isolation.
1. ALWAYS: Fall back to sequential inline verification if requirement test paths cannot be determined or worktree creation fails.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.18.0-04-01: REQUIREMENT: Stage 3 MUST identify which requirements have non-overlapping test paths before dispatching parallel subagents.
- [x] REQ-0.18.0-04-02: REQUIREMENT: Requirements with overlapping test paths MUST be verified sequentially (same subagent or inline) to avoid test interference.
- [x] REQ-0.18.0-04-03: REQUIREMENT: Each verification subagent receives: the requirement text, the specific test files/commands to run, and the expected pass criteria.
- [x] REQ-0.18.0-04-04: REQUIREMENT: Verification results are aggregated by the controller: all REQs must PASS for Stage 3 to succeed.
- [x] REQ-0.18.0-04-05: REQUIREMENT: If any verification subagent returns FAIL, the controller attempts one fix cycle (dispatch implementer with failure details), then re-verifies. If still failing after 1 retry, Stage 3 fails with handoff.
- [x] REQ-0.18.0-04-06: REQUIREMENT: Baseline quality checks (`gz lint`, `gz typecheck`, `gz test`) always run inline in the controller — they are not dispatched to subagents. Only brief-specific requirement verification is parallelized.
- [x] REQ-0.18.0-04-07: REQUIREMENT: Parallel verification subagents MUST be dispatched with `isolation: "worktree"` — each subagent operates on an isolated git worktree copy. This eliminates file-conflict risk and makes path-overlap analysis a performance optimization rather than a safety requirement.
- [x] REQ-0.18.0-04-08: REQUIREMENT: Parallel verification subagents MUST be dispatched with `run_in_background: true` to enable concurrent execution. The controller is notified when each completes.
- [x] REQ-0.18.0-04-09: REQUIREMENT: Verification subagents MUST use read-only tools (`Read, Glob, Grep, Bash`) — Bash is needed for running test commands but Edit/Write are denied since verification should not modify code.
- [x] REQ-0.18.0-04-10: NEVER: Dispatch parallel verification subagents without worktree isolation.
- [x] REQ-0.18.0-04-11: ALWAYS: Fall back to sequential inline verification if requirement test paths cannot be determined or worktree creation fails.


## Dispatch Decision Logic (Design Input)

```text
Stage 3 entry:
  1. Run baseline checks inline (gz lint, gz typecheck, gz test)
  2. If baseline fails → attempt fix, retry once, fail with handoff
  3. Parse brief requirements into verification scopes:
     - For each REQ: identify test files, verification commands, expected outputs
     - Compute path overlap matrix between REQs (performance optimization)
  4. Partition REQs into independent groups (no path overlap within group)
  5. For each independent group:
     - Dispatch verification subagents with:
       - isolation: "worktree" (each gets isolated repo copy)
       - run_in_background: true (concurrent execution)
       - tools: Read, Glob, Grep, Bash (read-only + test execution)
     - If group has 1 REQ: dispatch single background subagent
     - If group has 2+ REQs with no overlap: dispatch parallel background subagents
     - If overlap detected: dispatch single subagent for the group (sequential within worktree)
  6. Controller awaits completion notifications from all background subagents
  7. Aggregate results: all PASS → Stage 3 succeeds → proceed to Stage 4
```

### Worktree Isolation Rationale

Claude Code's `isolation: "worktree"` creates a temporary git worktree for each subagent, giving it an isolated copy of the repository. This has two effects:

1. **Safety** — Parallel verification subagents cannot interfere with each other's test state, even if they run overlapping test suites. The path-overlap analysis becomes a *performance optimization* (avoid redundant test runs) rather than a *safety requirement* (prevent conflicts).

2. **Cleanup** — Worktrees are automatically cleaned up if the subagent makes no changes. Since verification subagents are read-only (no Edit/Write tools), worktrees are always cleaned up.

### Background Execution

Parallel subagents are dispatched with `run_in_background: true`. The controller does not poll — it is automatically notified when each subagent completes. This is more efficient than sequential dispatch and avoids busy-waiting.

## Edge Cases

- Brief has zero explicit requirements — skip parallel dispatch, run only baseline checks
- Brief has 1 requirement — dispatch single verification subagent in worktree (isolated context still beneficial)
- All requirements overlap on the same test files — single worktree subagent runs all sequentially (overlap analysis triggers consolidation)
- Verification subagent times out — treat as FAIL, attempt retry in fresh worktree
- REQ-level entities exist (future: task-level-governance) — use REQ IDs as natural dispatch boundaries
- Worktree creation fails (e.g., disk space, git state) — fall back to sequential inline verification with warning
- Background subagent completes with error — controller receives notification, logs error, treats as FAIL

## Quality Gates (Lite)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR OBPI entry referenced

### Gate 2: TDD

- [x] Unit tests for path overlap detection
- [x] Unit tests for REQ partitioning into independent groups
- [x] Unit tests for parallel dispatch and result aggregation
- [x] Unit tests for sequential fallback
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Coverage:** Coverage >= 40% maintained
- [x] **OBPI Completion:** Record evidence in brief

### Implementation Summary

- Models: VerificationScope, VerificationOutcome, VerificationResult, VerificationPlan added to pipeline_runtime.py
- Extraction: extract_verification_scopes() parses brief REQUIREMENT lines into scopes with test paths
- Overlap: compute_path_overlap() detects shared test paths between REQ pairs
- Partitioning: partition_independent_groups() uses union-find to merge overlapping scopes into connected components
- Planning: build_verification_plan() produces parallel/sequential/mixed strategy based on overlap analysis
- Prompts: compose_verification_prompt() builds read-only subagent prompts with REQ text, test files, commands
- Parsing: parse_verification_results() extracts structured results from subagent JSON output
- Aggregation: aggregate_verification_results() requires all expected REQs to PASS; missing = FAIL
- Fallback: should_fallback_to_sequential() triggers when strategy is sequential (no test paths or single group)

### Key Proof

```
$ uv run -m unittest tests.test_verification_dispatch -v
Ran 63 tests in 0.001s — OK

$ uv run gz test
Ran 906 tests — OK

$ uv run gz lint
All checks passed!

$ uv run gz typecheck
All checks passed!

$ uv run coverage report --include='src/gzkit/pipeline_runtime.py'
src/gzkit/pipeline_runtime.py     588    111    81%
```
