---
id: OBPI-0.18.0-07-wire-two-stage-review
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 7
lane: Heavy
status: attested_completed
---

# OBPI-0.18.0-07: Wire Two-Stage Review into Pipeline Flow

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #7 — "Wire two-stage review into the pipeline flow after each implementation task"

**Status:** Completed

## Objective

Update the pipeline skill (`SKILL.md`) to dispatch two independent reviewer subagents after
each implementer task completes in Stage 2: a spec compliance reviewer and a code quality
reviewer. Uses the review protocol machinery built in OBPI-03 and the agent files defined in
OBPI-01. Reviews run after each task (not batched at end of Stage 2) per superpowers methodology.

## Lane

**Heavy** — Changes the pipeline skill external contract (SKILL.md review dispatch behavior).

## Allowed Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` — review dispatch wiring in Stage 2
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — canonical skill mirror
- `.github/skills/gz-obpi-pipeline/SKILL.md` — GitHub mirror
- `.agents/skills/gz-obpi-pipeline/SKILL.md` — agents mirror
- `src/gzkit/pipeline_runtime.py` — review dispatch helpers
- `tests/test_pipeline_dispatch.py` — review dispatch tests
- `features/subagent_pipeline.feature` — BDD scenarios for review dispatch
- `features/steps/subagent_pipeline_steps.py` — BDD step implementations
- `docs/user/runbook.md` — runbook updates for review operation

## Denied Paths

- Core review protocol functions already built in OBPI-03 (this OBPI wires, not reimplements)
- Role taxonomy (OBPI-01), implementer dispatch logic (OBPI-02/06), verification dispatch (OBPI-04/08)
- Stages 1, 3, 4, 5 logic

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: After each implementer task completes with `DONE` or `DONE_WITH_CONCERNS`, SKILL.md MUST dispatch two independent reviewer subagents: spec-reviewer and quality-reviewer.
1. REQUIREMENT: Both reviewers MUST be dispatched concurrently using `run_in_background: true` on the first, then foreground on the second (or both background with result collection).
1. REQUIREMENT: Spec reviewer MUST receive: the task description, brief requirements, and the diff produced by the implementer.
1. REQUIREMENT: Quality reviewer MUST receive: the changed files, test coverage context, and architectural constraints from the brief.
1. REQUIREMENT: Review findings MUST be recorded as structured data in the pipeline marker with severity levels (`critical`, `major`, `minor`, `info`).
1. REQUIREMENT: Critical findings MUST trigger a fix cycle — redispatch the implementer with the finding as context, then re-review.
1. REQUIREMENT: Fix cycles MUST be bounded — maximum 2 fix cycles per task before escalating to the user.
1. REQUIREMENT: `--no-subagents` flag MUST skip review dispatch (inline execution has no independent review).
1. NEVER: Allow the implementer subagent to also perform its own review. Separation of concerns is the point.
1. ALWAYS: Record review timing and finding counts for quality metrics.

> STOP-on-BLOCKERS: if OBPI-03 review protocol or OBPI-06 implementer wiring is incomplete, print a BLOCKERS list and halt.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.18.0-07-01: REQUIREMENT: After each implementer task completes with `DONE` or `DONE_WITH_CONCERNS`, SKILL.md MUST dispatch two independent reviewer subagents: spec-reviewer and quality-reviewer.
- [x] REQ-0.18.0-07-02: REQUIREMENT: Both reviewers MUST be dispatched concurrently using `run_in_background: true` on the first, then foreground on the second (or both background with result collection).
- [x] REQ-0.18.0-07-03: REQUIREMENT: Spec reviewer MUST receive: the task description, brief requirements, and the diff produced by the implementer.
- [x] REQ-0.18.0-07-04: REQUIREMENT: Quality reviewer MUST receive: the changed files, test coverage context, and architectural constraints from the brief.
- [x] REQ-0.18.0-07-05: REQUIREMENT: Review findings MUST be recorded as structured data in the pipeline marker with severity levels (`critical`, `major`, `minor`, `info`).
- [x] REQ-0.18.0-07-06: REQUIREMENT: Critical findings MUST trigger a fix cycle — redispatch the implementer with the finding as context, then re-review.
- [x] REQ-0.18.0-07-07: REQUIREMENT: Fix cycles MUST be bounded — maximum 2 fix cycles per task before escalating to the user.
- [x] REQ-0.18.0-07-08: REQUIREMENT: `--no-subagents` flag MUST skip review dispatch (inline execution has no independent review).
- [x] REQ-0.18.0-07-09: NEVER: Allow the implementer subagent to also perform its own review. Separation of concerns is the point.
- [x] REQ-0.18.0-07-10: ALWAYS: Record review timing and finding counts for quality metrics.


## Edge Cases

- `--no-subagents` — no review dispatch; Stage 2 runs inline as today
- Reviewer subagent times out — treat as no findings (conservative: do not block on reviewer failure)
- Both reviewers find critical issues — combine findings, dispatch single fix cycle addressing both
- Implementer returned `DONE_WITH_CONCERNS` — pass concerns as additional context to reviewers
- Review of a `BLOCKED` task — skip review (task didn't produce code changes)

### Implementation Summary

- Files modified: .gzkit/skills/gz-obpi-pipeline/SKILL.md (Stage 2 review dispatch wiring steps h.i-h.vii), .claude/skills/gz-obpi-pipeline/SKILL.md, .github/skills/gz-obpi-pipeline/SKILL.md, .agents/skills/gz-obpi-pipeline/SKILL.md, tests/test_pipeline_dispatch.py, features/subagent_pipeline.feature, features/steps/subagent_pipeline_steps.py, docs/user/runbook.md
- Tests added: tests/test_pipeline_dispatch.py::TestStage2ReviewDispatchContract (10 tests), 4 BDD scenarios (25 steps)
- Date completed: 2026-03-21

### Key Proof

```bash
$ uv run -m unittest tests.test_pipeline_dispatch.TestStage2ReviewDispatchContract -v
test_fix_cycle_redispatches_implementer_with_findings ... ok
test_full_loop_with_review_after_each_task ... ok
test_no_review_for_blocked_task ... ok
test_quality_review_prompt_includes_files_and_criteria ... ok
test_review_cycle_advance_when_both_pass ... ok
test_review_cycle_blocked_after_max_fix_cycles ... ok
test_review_cycle_fix_on_critical_spec_finding ... ok
test_review_dispatched_only_for_done_statuses ... ok
test_review_model_never_haiku ... ok
test_spec_review_prompt_includes_task_and_requirements ... ok
Ran 10 tests in 0.000s — OK

$ uv run -m behave features/subagent_pipeline.feature --tags=@review
4 scenarios passed, 0 failed — 25 steps passed
```

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [x] Gate 1 (ADR): Intent recorded in brief
- [x] Gate 2 (TDD): Unit tests for review dispatch wiring
- [x] Gate 3 (Docs): SKILL.md updated, runbook updated
- [x] Gate 4 (BDD): Review dispatch lifecycle scenario passes
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
