---
id: OBPI-0.18.0-07-wire-two-stage-review
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 7
lane: Heavy
status: Pending
---

# OBPI-0.18.0-07: Wire Two-Stage Review into Pipeline Flow

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #7 — "Wire two-stage review into the pipeline flow after each implementation task"

**Status:** Pending

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

## Edge Cases

- `--no-subagents` — no review dispatch; Stage 2 runs inline as today
- Reviewer subagent times out — treat as no findings (conservative: do not block on reviewer failure)
- Both reviewers find critical issues — combine findings, dispatch single fix cycle addressing both
- Implementer returned `DONE_WITH_CONCERNS` — pass concerns as additional context to reviewers
- Review of a `BLOCKED` task — skip review (task didn't produce code changes)

## Quality Gates (Heavy)

### Gates 1-4: Implementation

- [ ] Gate 1 (ADR): Intent recorded in brief
- [ ] Gate 2 (TDD): Unit tests for review dispatch wiring
- [ ] Gate 3 (Docs): SKILL.md updated, runbook updated
- [ ] Gate 4 (BDD): Review dispatch lifecycle scenario passes
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
