---
id: OBPI-0.0.5-04-add-regression-detection-for-model-prompt-changes-before-high-agency-rollout
parent: ADR-0.0.5-evaluation-infrastructure
item: 4
lane: lite
status: Completed
---

# OBPI-0.0.5-04: Regression Detection for Model/Prompt Changes

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
- **Checklist Item:** #4 - "Regression detection for model/prompt changes before high-agency rollout"

**Status:** Completed

## Objective

Add a baseline tracker that stores eval scores per commit and a comparison
engine that detects when model, prompt, or instruction changes cause
regressions, producing structured reports suitable for ARB receipt integration.

## Lane

**Lite** - Internal detection tooling. No CLI contracts, API changes, or
operator-facing behavior changes.

## Allowed Paths

- `src/gzkit/eval/` - baseline storage, comparison engine, report models
- `tests/eval/` - regression detection tests
- `artifacts/baselines/` - stored eval baselines (JSON)
- `data/schemas/` - baseline schema

## Denied Paths

- `data/eval/` - dataset creation is OBPI-01
- `src/gzkit/eval/runner.py` - harness internals are OBPI-02
- `src/gzkit/commands/gates.py` - gate integration is OBPI-03
- `src/gzkit/cli/` - no new CLI commands
- `docs/user/` - no operator docs changes

## Requirements (FAIL-CLOSED)

1. Baselines MUST be stored as versioned JSON in `artifacts/baselines/`.
2. Each baseline MUST record: commit hash, timestamp, surface scores, and the
   eval dataset version used.
3. The comparison engine MUST produce a structured `RegressionReport` (Pydantic,
   `frozen=True, extra="forbid"`) listing each regressed dimension with before
   and after scores.
4. Regression reports MUST be compatible with ARB receipt format for ledger
   integration.
5. The comparison MUST handle missing baselines gracefully (first run creates
   the baseline, does not fail).
6. Baseline updates MUST be explicit (not automatic) to prevent silently
   accepting regressions.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `src/gzkit/eval/runner.py` - eval suite output structure (from OBPI-02)
- [ ] `src/gzkit/commands/arb_cmd.py` - ARB receipt format and integration
- [ ] `data/schemas/arb_lint_receipt.schema.json` - existing receipt schema pattern
- [ ] `artifacts/receipts/` - existing receipt storage pattern

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/eval/runner.py` exists with `run_eval_suite()` (OBPI-02)

**Existing Code (understand current state):**

- [ ] `src/gzkit/core/scoring.py` - `DecompositionScorecard` and `to_markdown()`
- [ ] `tests/test_adr_eval.py` - scoring test patterns

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
uv run -m unittest tests/eval/test_regression.py -v
python -c "from gzkit.eval.regression import RegressionReport; print(RegressionReport.model_fields.keys())"
```

## Acceptance Criteria

- [x] **REQ-0.0.5-04-01:** A baseline store in `artifacts/baselines/` persists
  eval scores keyed by commit hash and surface name.
- [x] **REQ-0.0.5-04-02:** A comparison engine produces a `RegressionReport`
  listing each regressed dimension with baseline and current scores.
- [x] **REQ-0.0.5-04-03:** The first eval run against a surface with no
  baseline creates the baseline and reports "no prior baseline" (not a failure).
- [x] **REQ-0.0.5-04-04:** Regression reports are serializable to ARB-compatible
  JSON for receipt integration.
- [x] **REQ-0.0.5-04-05:** Baseline updates require explicit invocation (e.g.,
  `--update-baseline` flag), not implicit acceptance.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 23 tests in 0.099s — OK
  TestBaselineStore (5 tests): save/load round-trip, JSON structure, missing returns None, frozen, extra forbid
  TestComparisonEngine (8 tests): regression detected, within threshold, exact threshold, improvement, multiple surfaces, frozen, extra forbid, all deltas
  TestFirstRunHandling (4 tests): no prior baseline, no auto-create, create initial, skip existing
  TestArbReceiptCompatibility (4 tests): JSON serialization, pass case, baselines created, frozen
  TestExplicitUpdateControl (2 tests): explicit overwrite, comparison never updates
```

### Code Quality

```text
uv run gz lint       → All checks passed
uv run gz typecheck  → All checks passed
uv run gz test       → 1553 tests OK
```

### Value Narrative

Before this OBPI, gzkit had no standalone regression detection with commit-tracked baselines. The delta module (OBPI-03) provided gate-level regression checking but lacked commit provenance, dataset version tracking, and ARB receipt integration. Now there is a complete regression detection module storing baselines with full provenance in `artifacts/baselines/`, producing frozen `RegressionReport` models, and serializing to ARB-compatible receipts — all with explicit-only baseline updates.

### Key Proof

```bash
uv run -m unittest tests/eval/test_regression.py -v
# 23/23 pass

python -c "from gzkit.eval.regression import RegressionReport; print(list(RegressionReport.model_fields.keys()))"
# ['timestamp', 'commit_hash', 'surfaces_checked', 'deltas', 'regressions', 'passed', 'baseline_created', 'no_prior_baseline']
```

### Implementation Summary

- Files created: `src/gzkit/eval/regression.py`, `tests/eval/test_regression.py`, `data/schemas/eval_baseline.schema.json`
- Tests added: 23
- Date completed: 2026-03-26
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `attest completed`
- Date: `2026-03-26`

---

**Brief Status:** Completed
**Date Completed:** 2026-03-26
**Evidence Hash:** -
