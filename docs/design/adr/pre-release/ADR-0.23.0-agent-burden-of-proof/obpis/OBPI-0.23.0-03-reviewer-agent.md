---
id: OBPI-0.23.0-03-reviewer-agent
parent: ADR-0.23.0-agent-burden-of-proof
item: 3
lane: Heavy
status: attested_completed
---
<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.23.0-03 — Reviewer Agent Role

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.23.0-03 — "Reviewer agent role — fresh-eyes verification of delivered work against OBPI promises"`

## ADR ALIGNMENT

1. **Critical Constraint:**
   > ADR states: "Implementations MUST ensure the burden of proof falls on the completing agent at the END of the run."
   >
   > In my own words: A separate agent — with no sunk-cost bias from doing the implementation work — must independently verify that what was delivered matches what the OBPI promised, and that operator documentation is substantive.

2. **Integration Points:**
   > This OBPI must integrate with: `src/gzkit/commands/pipeline.py` (subagent dispatch), `.claude/skills/gz-obpi-pipeline/SKILL.md` (pipeline stages), ADR-0.18.0 agent role taxonomy

3. **Anti-Pattern:**
   > A failed implementation would: have the same agent that implemented the OBPI also "review" it — that's self-certification, not independent review. The reviewer must be a distinct agent invocation with fresh context.

4. **Alignment Check:**
   > - [x] **YES** — Proceed. Reasoning: Independent review by a fresh agent directly supports the multi-agent approach and prevents self-certification of quality.

## OBJECTIVE

Add a "reviewer" agent role to the OBPI pipeline that is dispatched after implementation completion. The reviewer agent reads the OBPI brief's promises (objective, requirements, acceptance criteria) and the closing argument, then independently verifies: (a) the delivered code matches the promises, (b) operator documentation is substantive and accurate, (c) the closing argument is earned from evidence, not echoed from planning.

## ROLE

**Agent Identity:** Multi-agent pipeline architect

**Success Behavior:** Design a reviewer dispatch that gives a fresh agent the brief, the closing argument, and the delivered artifacts — then asks it to render a verdict.

**Failure Behavior:** Implementing review as a checkbox in the same agent's context, or making the review so shallow it always passes.

## ASSUMPTIONS

- ADR-0.18.0 subagent dispatch infrastructure is available
- The reviewer agent is a Claude Code subagent (Agent tool) with read-only access
- The reviewer produces a structured assessment that the ceremony skill can present to the human attestor

## NON-GOALS

- The reviewer does not fix problems — it identifies them
- The reviewer does not replace human attestation — it informs it
- No new CLI command for reviewer dispatch (it's internal to the pipeline)

## CHANGE IMPACT DECLARATION

- [x] **YES** — External contract changes: OBPI pipeline gains a new stage visible in pipeline output.

## LANE

Heavy — Pipeline contract change (new stage, new output).

## EXTERNAL CONTRACT

- Surface: OBPI pipeline stages, ceremony skill output
- Impacted audience: agents running pipeline, human attestors

## ALLOWED PATHS

- `src/gzkit/commands/pipeline.py`
- `.claude/skills/gz-obpi-pipeline/SKILL.md`
- `tests/test_reviewer_agent.py`
- `features/reviewer_agent.feature`
- `features/steps/reviewer_agent_steps.py`
- `docs/governance/governance_runbook.md`

## REQUIREMENTS (FAIL-CLOSED)

1. Define "reviewer" role in the agent role taxonomy (extends ADR-0.18.0)
1. Reviewer agent receives: OBPI brief, closing argument, list of changed files, and relevant doc files
1. Reviewer produces structured assessment: promises-met (yes/no per requirement), docs-quality (substantive/boilerplate/missing), closing-argument-quality (earned/echoed/missing)
1. Assessment is stored as a reviewable artifact alongside the brief
1. Ceremony skill presents reviewer assessment to human attestor before attestation prompt

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.23.0-03-01: Given the agent role taxonomy from ADR-0.18.0, when extended, then a `reviewer` role is defined with a distinct dispatch path that does not reuse the implementing agent's context.
- [x] REQ-0.23.0-03-02: Given the reviewer agent is dispatched for an OBPI, when prompted, then it receives the full OBPI brief.
- [x] REQ-0.23.0-03-03: Given the reviewer agent is dispatched for an OBPI, when prompted, then it receives the OBPI's authored Closing Argument.
- [x] REQ-0.23.0-03-04: Given the reviewer agent is dispatched for an OBPI, when prompted, then it receives the list of changed files for that OBPI.
- [x] REQ-0.23.0-03-05: Given the reviewer agent is dispatched for an OBPI, when prompted, then it receives the relevant operator documentation files for that OBPI.
- [x] REQ-0.23.0-03-06: Given the reviewer agent's assessment, when parsed, then it includes a `promises-met` field with a yes/no judgment per requirement.
- [x] REQ-0.23.0-03-07: Given the reviewer agent's assessment, when parsed, then it includes a `docs-quality` field valued one of {substantive, boilerplate, missing}.
- [x] REQ-0.23.0-03-08: Given the reviewer agent's assessment, when parsed, then it includes a `closing-argument-quality` field valued one of {earned, echoed, missing}.
- [x] REQ-0.23.0-03-09: Given the reviewer assessment for an OBPI, when produced, then it is stored as a reviewable artifact (`REVIEW-<obpi-id>.md`) alongside the brief.
- [x] REQ-0.23.0-03-10: Given a closeout ceremony run, when the human attestation prompt is reached, then the ceremony skill has presented the reviewer assessment to the attestor first.

## EDGE CASES

- Reviewer disagrees with implementer's closing argument: assessment flags the discrepancy, human decides
- OBPI has no operator-facing surface: reviewer still checks that docstrings and internal docs are substantive
- Reviewer agent fails or times out: closeout proceeds with warning, but human is informed no review was completed

## QUALITY GATES

### Gates 1-4: Implementation

- [x] Gate 1 (ADR): Intent recorded in brief
- [x] Gate 2 (TDD): Unit tests pass, coverage >= 40%
- [x] Gate 3 (Docs): Governance runbook updated
- [x] Gate 4 (BDD): Behave scenarios pass
- [x] Code Quality: Lint, type check clean

### Verification Commands (Concrete)

```bash
# Prove reviewer role exists in taxonomy
grep -r "reviewer" src/gzkit/commands/pipeline.py
# Expected: reviewer dispatch function or role constant

# Prove assessment artifact is written
ls docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/briefs/REVIEW-*.md
# Expected: one review artifact per OBPI

# Prove reviewer assessment has structured fields
grep -c "promises-met\|docs-quality\|closing-argument-quality" <assessment_artifact>
# Expected: >= 3 (one per field)

# Prove reviewer is dispatched as a separate agent (not inline)
grep -r "subagent_type\|Agent(" src/gzkit/commands/pipeline.py | grep -i review
# Expected: match showing distinct agent invocation
```

### Gate 5: Human Attestation

- [x] Agent presents reviewer assessment example output
- [x] **STOP** — Agent waits for human attestation

## Closing Argument

The pipeline previously had no independent verification of whether delivered work matched OBPI promises. The implementing agent self-certified its own output. This OBPI adds a reviewer agent dispatch (Stage 3.5) that receives the brief, closing argument, changed files, and doc files — then independently assesses promises-met, docs-quality, and closing-argument-quality. The assessment is stored as a `REVIEW-*.md` artifact and presented in the Stage 4 ceremony before human attestation. Evidence: 42 unit tests, 8 BDD scenarios (46 steps), lint/typecheck/docs all clean.

### Implementation Summary

- Created: `src/gzkit/commands/pipeline.py` — ReviewerAssessment model, prompt composer, JSON parser, artifact storage, ceremony formatter
- Created: `tests/test_reviewer_agent.py` — 42 unit tests covering all functions
- Created: `features/reviewer_agent.feature` — 8 BDD scenarios for dispatch, parse, artifact, ceremony
- Created: `features/steps/reviewer_agent_steps.py` — step definitions for all scenarios
- Updated: `.claude/skills/gz-obpi-pipeline/SKILL.md` — Stage 3.5 reviewer dispatch, Stage 4 template with reviewer assessment
- Updated: `docs/governance/governance_runbook.md` — reviewer agent protocol section

### Key Proof

```bash
$ uv run -m unittest tests.test_reviewer_agent -v
# 42 tests: models (frozen, extra=forbid), prompt composition (OBPI ID, brief, closing arg, files, JSON schema), parsing (PASS/FAIL/CONCERNS/invalid/missing), artifact storage (REVIEW-*.md in briefs/), ceremony formatting (table rows, verdict, pipe escaping)
# Result: 42/42 OK

$ uv run -m behave features/reviewer_agent.feature
# 8 scenarios: prompt with brief+closing, missing closing, PASS/FAIL/CONCERNS parse, invalid parse, artifact storage, ceremony formatting
# Result: 8/8 passed, 46/46 steps passed
```
