---
id: OBPI-0.18.0-08-wire-req-verification-dispatch
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 8
lane: Heavy
status: Pending
---

# OBPI-0.18.0-08: Wire REQ Verification Dispatch into Stage 3

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #8 — "Wire REQ verification dispatch into Stage 3"

**Status:** Pending

## Objective

Update the pipeline skill (`SKILL.md`) Stage 3 to dispatch parallel verification subagents
for REQ-level checks when requirements have non-overlapping test paths. Uses the verification
dispatch machinery built in OBPI-04 and worktree isolation for safe concurrent execution.
Currently Stage 3 runs all verification sequentially in the main session.

## Lane

**Heavy** — Changes the pipeline skill external contract (SKILL.md Stage 3 behavior).

## Allowed Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` — Stage 3 verification dispatch wiring
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — canonical skill mirror
- `.github/skills/gz-obpi-pipeline/SKILL.md` — GitHub mirror
- `.agents/skills/gz-obpi-pipeline/SKILL.md` — agents mirror
- `src/gzkit/pipeline_runtime.py` — verification dispatch helpers
- `tests/test_pipeline_dispatch.py` — verification dispatch tests
- `features/subagent_pipeline.feature` — BDD scenarios for parallel verification
- `features/steps/subagent_pipeline_steps.py` — BDD step implementations
- `docs/user/runbook.md` — runbook updates for parallel verification

## Denied Paths

- Core REQ verification dispatch functions already built in OBPI-04 (this OBPI wires, not reimplements)
- Role taxonomy (OBPI-01), implementer dispatch (OBPI-02/06), review protocol (OBPI-03/07)
- Stages 1, 2, 4, 5 logic

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: SKILL.md Stage 3 MUST analyze brief requirements for non-overlapping test paths before dispatching parallel verification.
1. REQUIREMENT: Requirements with non-overlapping paths MUST be dispatched as concurrent verification subagents using `isolation: worktree` and `run_in_background: true`.
1. REQUIREMENT: Requirements with overlapping paths MUST run sequentially (no concurrent modification risk).
1. REQUIREMENT: Each verification subagent MUST receive: the requirement text, test file paths, expected pass criteria, and the current branch state.
1. REQUIREMENT: Verification results MUST be aggregated using `DispatchAggregation` (OBPI-05) and recorded in the pipeline marker.
1. REQUIREMENT: All verification subagents MUST complete before Stage 3 advances to presenting results.
1. REQUIREMENT: `--no-subagents` flag MUST bypass parallel dispatch and run verification sequentially inline.
1. REQUIREMENT: Worktree cleanup MUST be automatic — no orphaned worktrees after verification completes or fails.
1. NEVER: Dispatch parallel verification for overlapping file paths — data corruption risk.
1. ALWAYS: Record wall-clock time savings from parallel vs sequential execution for metrics.

> STOP-on-BLOCKERS: if OBPI-04 verification dispatch machinery is missing, print a BLOCKERS list and halt.

## Edge Cases

- `--no-subagents` — Stage 3 runs verification sequentially inline as today
- All requirements overlap — no parallel dispatch; sequential execution only
- Single requirement — no parallelization benefit; dispatch one verification subagent (or inline)
- Verification subagent fails in worktree — record failure, worktree auto-cleaned, report to user
- Worktree creation fails (disk space, git state) — fall back to sequential inline verification with warning
- Mixed results (some pass, some fail) — aggregate all, present complete picture before advancing

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [ ] Gate 1 (ADR): Intent recorded in brief
- [ ] Gate 2 (TDD): Unit tests for verification dispatch wiring
- [ ] Gate 3 (Docs): SKILL.md updated, runbook updated
- [ ] Gate 4 (BDD): Parallel verification scenario passes
- [ ] Code Quality: Lint, format, type checks clean

### Gate 5: Human Attestation (MANDATORY)

1. [ ] Agent presents CLI commands for verification
1. [ ] **STOP** — Agent waits for human to verify
1. [ ] **STOP** — Agent waits for human attestation response — "attest completed"
1. [ ] Agent records attestation in brief

## Completion Checklist (Heavy)

- [ ] Gates 1-4 pass
- [ ] Gate 5 attestation commands presented
- [ ] Gate 5 attestation RECEIVED from human
- [ ] Attestation recorded in brief
- [ ] OBPI marked completed ONLY AFTER attestation
