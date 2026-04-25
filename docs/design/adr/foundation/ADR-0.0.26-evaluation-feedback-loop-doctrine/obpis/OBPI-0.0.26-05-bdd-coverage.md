---
id: OBPI-0.0.26-05-bdd-coverage
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.26-05-bdd-coverage: BDD scenarios for the full evaluation-feedback loop

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md`
- **Checklist Item:** #5 — "BDD coverage — heavy-lane `@REQ-…`-tagged scenarios for the full loop (low-score → justify-required → clustering → proposal GHI → human-approved rule edit)"

**Status:** Draft

## Objective

Author behave scenarios that exercise the full evaluation-feedback loop end-to-end against real `gz adr-evaluate`, `gz validate --evaluation-justify-binding`, the chore, and `gz chores propose-ghi` invocations.

## Lane

**Heavy** — Heavy OBPIs require Gate 4 BDD coverage.

## Allowed Paths

- `features/evaluation_feedback_loop.feature`
- `features/steps/evaluation_feedback_loop_steps.py` (or extend existing)
- `data/behave_coverage_waivers.json` — read-only (no edits expected unless waiver needed)
- `tests/fixtures/evaluation/` — fixture artifacts (justify scaffolds, evaluation events) for the scenarios
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/**`

## Denied Paths

- `src/**`, `tests/**` (unit tier) — coverage in OBPI-01..04
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `features/evaluation_feedback_loop.feature` exists with at least one `@REQ-0.0.26-NN-MM` scenario tag per REQ from OBPI-01..04.
2. REQUIREMENT: At least one scenario walks the full loop: synthesize a low-score `adr-evaluation` event → run the binding gate → fail-closed → author a `gz-justify` artifact → re-run gate → pass → run the chore → produce a proposal → run `propose-ghi` (mocked GitHub) → file GHI.
3. REQUIREMENT: At least one scenario covers the trailer-validator path: simulated commit closing an `eval-feedback`-labeled GHI without trailer → exit 3.
4. REQUIREMENT: Scenarios mock the `gh` subprocess boundary; NEVER hit the real GitHub API.
5. REQUIREMENT: `gz validate --behave-req-tags` exits 0 — every REQ in OBPI-01..04 covered or waived.
6. REQUIREMENT: `uv run -m behave features/evaluation_feedback_loop.feature` exits 0.
7. REQUIREMENT: NEVER include the operator's personal email.

> STOP-on-BLOCKERS: if OBPI-01..04 have not landed, STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision (all items)
- [ ] OBPI-0.0.26-01..04 evidence — confirm all gates and chore landed
- [ ] `.claude/rules/tests.md` § Behave scenario tagging
- [ ] `features/` — read existing scenarios for tagging shape

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] behave passes
### Code Quality
- [ ] Lint clean
### Gate 4: BDD (Heavy)
- [ ] All scenarios pass; req-tags clean
### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run -m behave features/evaluation_feedback_loop.feature
uv run gz validate --behave-req-tags
```

## Acceptance Criteria

- [ ] REQ-0.0.26-05-01: Given the loop is fully wired (OBPI-01..04 landed), when `behave features/evaluation_feedback_loop.feature` runs, then every REQ from those OBPIs has at least one passing scenario tag.
- [ ] REQ-0.0.26-05-02: Given the full-loop scenario, when behave runs it, then synthesized low score → blocked → justified → unblocked → clustered → proposed → filed all transitions in one scenario.
- [ ] REQ-0.0.26-05-03: Given the trailer-validator scenario, when behave runs it, then a simulated rule-edit commit without trailer fails the gate; with trailer passes.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** behave passes
- [ ] **Code Quality:** clean
- [ ] **Gate 4 (BDD):** scenarios pass
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 4 (BDD)
```text
# behave + req-tags output
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- BDD scenarios added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
