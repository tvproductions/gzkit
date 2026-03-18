---
id: OBPI-0.18.0-03-two-stage-review-protocol
parent: ADR-0.18.0-subagent-driven-pipeline-execution
item: 3
lane: Lite
status: Accepted
---

# OBPI-0.18.0-03: Two-Stage Review Protocol

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/ADR-0.18.0-subagent-driven-pipeline-execution.md`
- **Checklist Item:** #3 — "Two-stage review protocol: spec compliance + code quality reviewer subagents"

**Status:** Accepted

## Objective

After each implementer subagent completes a task, dispatch two independent reviewer subagents
in sequence: a spec compliance reviewer and a code quality reviewer. The spec compliance reviewer
verifies that what was built matches what was requested. The code quality reviewer evaluates
architecture, SOLID principles, test coverage, and maintainability.

This is the superpowers two-stage review pattern adapted for gzkit's governance model.

## Lane

**Lite** — Internal review protocol; no external CLI/API/schema contract changes. The review
protocol is consumed by the pipeline skill, not exposed as a user-facing surface.

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` — review dispatch logic and result handling
- `src/gzkit/roles.py` — reviewer role sub-types (if not already covered by OBPI-01)
- `tests/test_review_protocol.py` — review dispatch and verdict handling tests

## Denied Paths

- `.claude/skills/gz-obpi-pipeline/SKILL.md` — skill documentation belongs to OBPI-05
- `src/gzkit/commands/` — CLI surface belongs to OBPI-05
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: After each implementer task with status `DONE` or `DONE_WITH_CONCERNS`, dispatch spec compliance reviewer first, then code quality reviewer.
1. REQUIREMENT: Spec compliance reviewer MUST independently read the actual code changes — never trust the implementer's self-report. Prompt MUST include: "The implementer may be optimistic. Verify everything independently."
1. REQUIREMENT: Spec compliance reviewer receives: the plan task description, brief requirements relevant to this task, and the list of files changed by the implementer.
1. REQUIREMENT: Code quality reviewer dispatches ONLY after spec compliance passes. If spec compliance fails, dispatch a fix cycle (new implementer subagent with review feedback) before quality review.
1. REQUIREMENT: Code quality reviewer receives: files changed, test files, and evaluates against SOLID principles, file organization, test coverage, and maintainability.
1. REQUIREMENT: Review verdicts use structured format: `{verdict: PASS|FAIL|CONCERNS, findings: [{severity: critical|important|minor, description, file, line}]}`.
1. REQUIREMENT: Critical findings from either reviewer MUST block task advancement. Important findings are logged. Minor findings are noted but do not block.
1. REQUIREMENT: Both reviewer subagents MUST be dispatched using their respective `.claude/agents/` files (`spec-reviewer.md`, `quality-reviewer.md`) which enforce read-only access via `tools: Read, Glob, Grep` — no Edit, Write, or Bash. This is structural independence: the reviewer literally cannot modify the code it reviews.
1. REQUIREMENT: Reviewer subagents MUST use capable models (`sonnet` minimum, `opus` for complex reviews). Reviews always require judgment — never route to `haiku`.
1. NEVER: Skip the spec compliance review — even for "simple" tasks.
1. ALWAYS: Review cycle limit: max 2 fix cycles per task before escalating to BLOCKED.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Review Dispatch Sequence (Design Input)

```text
After implementer returns DONE/DONE_WITH_CONCERNS:
  1. Dispatch spec compliance reviewer subagent:
     - subagent_type: "spec-reviewer" (.claude/agents/spec-reviewer.md)
     - model: "sonnet" (minimum — "opus" for complex tasks)
     - Tools enforced: Read, Glob, Grep only (no write access)
     - maxTurns: 15
     Input: task description, brief requirements, files_changed
     Output: {verdict, findings}
  2. If verdict == FAIL with critical findings:
     a. Dispatch new implementer subagent with review feedback
     b. On return, re-dispatch spec compliance reviewer
     c. If still FAIL after 2 cycles → BLOCKED
  3. If verdict == PASS or CONCERNS-only:
     Dispatch code quality reviewer subagent:
     - subagent_type: "quality-reviewer" (.claude/agents/quality-reviewer.md)
     - model: "sonnet" (minimum)
     - Tools enforced: Read, Glob, Grep only (no write access)
     - maxTurns: 15
     Input: files_changed, test files, quality criteria
     Output: {verdict, findings}
  4. If quality verdict has critical findings:
     Dispatch implementer fix cycle (same pattern as step 2)
  5. Log all findings to pipeline evidence
  6. Advance to next task
```

### Why Read-Only is Structural, Not Prompt-Based

Reviewer independence is enforced by the Claude Code `tools` allowlist in the agent file, not by prompt instruction. The reviewer subagent literally cannot call Edit or Write — the Agent tool rejects unauthorized tool calls before execution. This makes "reviewer modifies what it reviews" impossible at the platform level, not just discouraged by convention.

## Edge Cases

- Implementer returns `BLOCKED` — skip review entirely (nothing to review)
- Spec reviewer finds task was not attempted (no meaningful changes) — treat as implementer FAIL
- Quality reviewer disagrees with spec reviewer on same code — spec compliance takes precedence for correctness; quality takes precedence for architecture
- All review verdicts have only minor findings — advance without fix cycle

## Quality Gates (Lite)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR OBPI entry referenced

### Gate 2: TDD

- [ ] Unit tests for review dispatch sequence
- [ ] Unit tests for verdict handling (PASS/FAIL/CONCERNS)
- [ ] Unit tests for fix cycle logic and escalation
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
