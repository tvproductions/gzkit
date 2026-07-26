---
id: OBPI-0.0.52-09-bdd-coverage-staleness-propagation
parent: ADR-0.0.52-artifact-staleness-propagation
item: 9
lane: Heavy
status: Draft
allowlist:
- features/staleness_propagation.feature
- features/staleness_resolution.feature
- features/staleness_validators.feature
- features/tier2_review.feature
- features/staleness_tripwire.feature
- features/steps/staleness_steps.py
- features/steps/staleness_fixtures.py
- tests/governance/test_bdd_staleness_coverage.py
- docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md
reqs:
- REQ-0.0.52-09-01
- REQ-0.0.52-09-02
- REQ-0.0.52-09-03
- REQ-0.0.52-09-04
- REQ-0.0.52-09-05
- REQ-0.0.52-09-06
- REQ-0.0.52-09-07
- REQ-0.0.52-09-08
- REQ-0.0.52-09-09
verification:
- uv run gz lint
- uv run gz typecheck
- uv run -m behave features/staleness_propagation.feature features/staleness_resolution.feature features/staleness_validators.feature features/tier2_review.feature features/staleness_tripwire.feature
- uv run -m unittest tests.governance.test_bdd_staleness_coverage -v
---

# OBPI-0.0.52-09-bdd-coverage-staleness-propagation: BDD coverage for staleness propagation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #9 — "BDD coverage — heavy-lane `@REQ`-tagged scenarios for fast-path fire, Tier 1 mechanical detection, Tier 2 advisory candidate promotion, clearance ceremony, validator fail-close, anti-theatre defenses, `tx_id` recovery"

**Status:** Draft

## Objective

Author the heavy-lane BDD coverage for the propagation pipeline — `@REQ`-tagged Gherkin scenarios spanning fast-path fire, Tier 1 mechanical detection, Tier 2 advisory candidate promotion, the clearance ceremony, validator fail-close behavior, anti-theatre defenses, and `tx_id` crash-recovery semantics. Each REQ from OBPIs 01-08 gets at least one covering scenario.

## Lane

**Heavy** — Gate 4 BDD coverage is required; this OBPI delivers it.

## Allowed Paths

- `features/staleness_propagation.feature` — **PRIMARY:** main BDD feature file with `@REQ`-tagged scenarios
- `features/staleness_resolution.feature` — clearance ceremony scenarios
- `features/staleness_validators.feature` — validator fail-close scenarios
- `features/tier2_review.feature` — Tier 2 batch-table promotion scenarios
- `features/staleness_tripwire.feature` — tripwire analytical-receipt scenarios
- `features/steps/staleness_steps.py` — step definitions for the above features
- `features/steps/staleness_fixtures.py` — shared fixtures (synthetic ADR/OBPI corpora, ledger setup)
- `tests/governance/test_bdd_staleness_coverage.py` — meta-test: every REQ-0.0.52-NN-MM has at least one BDD scenario covering it
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Source implementations (owned by OBPIs 01-08)
- Docs/runbook (OBPI-10)

## Creates These Files

- `features/staleness_propagation.feature` — **CREATE** main BDD feature file
- `features/staleness_resolution.feature` — **CREATE** clearance ceremony scenarios
- `features/staleness_validators.feature` — **CREATE** validator fail-close scenarios
- `features/tier2_review.feature` — **CREATE** Tier 2 batch-table promotion scenarios
- `features/staleness_tripwire.feature` — **CREATE** tripwire analytical-receipt scenarios
- `features/steps/staleness_steps.py` — **CREATE** step definitions
- `features/steps/staleness_fixtures.py` — **CREATE** shared fixtures
- `tests/governance/test_bdd_staleness_coverage.py` — **CREATE** meta-test for REQ-to-scenario coverage

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every REQ-0.0.52-NN-MM defined across OBPIs 01-08 MUST have at least one `@REQ-0.0.52-NN-MM`-tagged Gherkin scenario.
2. REQUIREMENT: Scenarios MUST cover the canonical happy paths: fast-path fire on no-change closeout; Tier 1 declared-edge match; Tier 1 path-overlap match (with fan-in downweight exclusion); Tier 2 candidate promotion via batch table; clearance with `confirmed_unchanged`; clearance with `amended`.
3. REQUIREMENT: Scenarios MUST cover failure modes: validator fail-close (`--adr-eval-fresh`) on flagged-artifact advance; coherence drift (`--staleness-coherence`) on orphan ledger event; anti-theatre defense (identical reason strings rejected); operator attestation missing rejected.
4. REQUIREMENT: Scenarios MUST cover `tx_id` atomic semantics: crash-between-ledger-and-frontmatter recovery via `--staleness-coherence`; LLM-judge-unreachable graceful degradation.
5. REQUIREMENT: Scenarios MUST exercise the orthogonal composition with ADR-0.0.26: after clearance, when fresh evaluation < 3.0, `--evaluation-justify-binding` fires naturally on next validation.
6. REQUIREMENT: Scenarios MUST cover read-only surfaces NOT firing fail-close: `gz status`, `gz state --json`, `explain-stale` against a flagged artifact all exit 0.
7. REQUIREMENT: `behave` MUST exit 0 on `uv run -m behave features/` for all new feature files.
8. REQUIREMENT: The meta-test `test_bdd_staleness_coverage.py` MUST fail if any REQ-0.0.52-NN-MM lacks a covering scenario (mechanical coverage gate, per Gate 4 discipline).

> STOP-on-BLOCKERS: ALL of OBPI-01 through OBPI-08 MUST have landed before this OBPI starts — BDD scenarios test the integrated surface. If OBPI-07 is still HARD-BLOCKED on ADR-0.0.39, its Tier 2 scenarios use the degraded-path fixture (judge-unreachable simulation) and the full happy-path Tier 2 scenarios stay in a `@skip-until-adr-039-proposed` tag until 0.0.39 advances.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"BDD coverage — heavy-lane `@REQ`-tagged scenarios for fast-path fire, Tier 1 mechanical detection, Tier 2 advisory candidate promotion, clearance ceremony, validator fail-close, anti-theatre defenses, `tx_id` recovery"*.
- [ ] Parent ADR § Decision (all subsections) — scenarios derive from Decision items.
- [ ] OBPIs 01-08 § Acceptance Criteria — each REQ becomes at least one scenario.

**Governance:**

- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — heavy-lane Gate 4 requirement.
- [ ] Existing `features/` directory reviewed for canonical Gherkin style.

**Prerequisites:**

- [ ] OBPI-0.0.52-01 through OBPI-0.0.52-08 ALL have landed.

**Existing Code:**

- [ ] An existing heavy-lane feature file (e.g., `features/evaluation_feedback_loop.feature`) reviewed for scenario structure, fixture patterns, and tag conventions.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from brief acceptance criteria
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/staleness_propagation.feature features/staleness_resolution.feature features/staleness_validators.feature features/tier2_review.feature features/staleness_tripwire.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m behave features/staleness_propagation.feature features/staleness_resolution.feature features/staleness_validators.feature features/tier2_review.feature features/staleness_tripwire.feature
uv run -m unittest tests.governance.test_bdd_staleness_coverage -v
```

## Demo

```bash
# Run all 5 feature files; expect 0 failures
uv run -m behave features/staleness_propagation.feature features/staleness_resolution.feature features/staleness_validators.feature features/tier2_review.feature features/staleness_tripwire.feature

# Meta-test: every REQ has a covering scenario
uv run -m unittest tests.governance.test_bdd_staleness_coverage -v

# Sample @REQ-tagged scenario inspection
grep -E "^\s*@REQ-0\.0\.52" features/*.feature | head -20
```

## Acceptance Criteria

- [ ] REQ-0.0.52-09-01: Given every REQ-0.0.52-NN-MM defined across OBPIs 01-08, when the meta-test runs, then each REQ has at least one `@REQ-0.0.52-NN-MM`-tagged scenario (mechanical coverage gate).
- [ ] REQ-0.0.52-09-02: Given the fast-path happy-path scenario, when an ADR closes with all 6 conditions met, then `behave` confirms `propagation_evaluated` is emitted with `affected_set: []` and `fast_path_fired: true`.
- [ ] REQ-0.0.52-09-03: Given the Tier 1 declared-edge scenario, when ADR-A closes and ADR-B cites ADR-A, then `behave` confirms ADR-B receives `evaluation_stale: ADR-A` with `source: mechanical` and `detection_signal: declared_edge:cites`.
- [ ] REQ-0.0.52-09-04: Given the Tier 1 path-overlap scenario with fan-in downweight, when ADR-A closes touching `src/gzkit/foo.py` (touched by 2 ADRs total, below threshold 5), then `behave` confirms downstream gets `path_overlap:src/gzkit/foo.py`; with fan-in-saturated `src/gzkit/validate.py`, no flag is raised.
- [ ] REQ-0.0.52-09-05: Given the validator fail-close scenario, when a flagged artifact attempts `gz closeout`, then `behave` confirms `--adr-eval-fresh` exits 3 with the copy-paste resolution command.
- [ ] REQ-0.0.52-09-06: Given the Tier 2 anti-theatre scenarios, when an operator submits identical reason strings or generic reasons, then `behave` confirms the commit is refused.
- [ ] REQ-0.0.52-09-07: Given the `tx_id` crash-recovery scenario, when an orphan ledger event exists without matching frontmatter, then `behave` confirms `--staleness-coherence` exits 3 with the prescriptive recovery message.
- [ ] REQ-0.0.52-09-08: Given the read-only surfaces scenarios, when `gz status`, `gz state --json`, or `explain-stale` runs against a flagged artifact, then `behave` confirms all exit 0 (no fail-close on read).
- [ ] REQ-0.0.52-09-09: Given `uv run -m behave features/`, when all 5 new feature files run, then `behave` exits 0.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: the integrated propagation surface had no behavioral coverage — unit tests proved each module worked in isolation, but the full closeout → flag → resolve → re-evaluate cycle had no executable scenario. Now: heavy-lane Gate 4 is satisfied with `@REQ`-tagged Gherkin scenarios that exercise the integrated pipeline end-to-end, and the meta-test enforces complete REQ-to-scenario coverage as a mechanical gate.

### Key Proof

```text
$ uv run -m behave features/staleness_propagation.feature
Feature: Cross-artifact staleness propagation
  ...
  Scenario: Fast-path fires on closeout with no semantic change  # @REQ-0.0.52-03-04
    Given an ADR ADR-0.0.A authored at 2026-05-01
    And no new REQ has been added to ADR-0.0.A since adr_created
    And no REQ body has been amended
    ...
    When gz closeout ADR-0.0.A runs
    Then a propagation_evaluated event is emitted with affected_set=[]
    And fast_path_fired is true

42 scenarios passed, 0 failed
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
