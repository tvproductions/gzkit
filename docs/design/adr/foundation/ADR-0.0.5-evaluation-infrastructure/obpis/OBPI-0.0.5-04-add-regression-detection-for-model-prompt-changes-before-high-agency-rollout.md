---
id: OBPI-0.0.5-04-add-regression-detection-for-model-prompt-changes-before-high-agency-rollout
parent: ADR-0.0.5-evaluation-infrastructure
item: 4
lane: lite
status: Draft
---

# OBPI-0.0.5-04: Regression Detection for Model/Prompt Changes

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
- **Checklist Item:** #4 - "Regression detection for model/prompt changes before high-agency rollout"

**Status:** Draft

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

- [ ] **REQ-0.0.5-04-01:** A baseline store in `artifacts/baselines/` persists
  eval scores keyed by commit hash and surface name.
- [ ] **REQ-0.0.5-04-02:** A comparison engine produces a `RegressionReport`
  listing each regressed dimension with baseline and current scores.
- [ ] **REQ-0.0.5-04-03:** The first eval run against a surface with no
  baseline creates the baseline and reports "no prior baseline" (not a failure).
- [ ] **REQ-0.0.5-04-04:** Regression reports are serializable to ARB-compatible
  JSON for receipt integration.
- [ ] **REQ-0.0.5-04-05:** Baseline updates require explicit invocation (e.g.,
  `--update-baseline` flag), not implicit acceptance.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Value Narrative
<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof
<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft
**Date Completed:** -
**Evidence Hash:** -
