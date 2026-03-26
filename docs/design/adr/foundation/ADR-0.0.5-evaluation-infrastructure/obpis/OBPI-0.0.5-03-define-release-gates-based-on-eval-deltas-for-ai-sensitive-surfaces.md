---
id: OBPI-0.0.5-03-define-release-gates-based-on-eval-deltas-for-ai-sensitive-surfaces
parent: ADR-0.0.5-evaluation-infrastructure
item: 3
lane: lite
status: Draft
---

# OBPI-0.0.5-03: Eval-Delta Release Gates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
- **Checklist Item:** #3 - "Eval-delta release gates for AI-sensitive surfaces"

**Status:** Draft

## Objective

Integrate eval harness scores into the Gate 2 (TDD) pipeline so that eval
regressions beyond a configurable threshold block the release gate, giving
operators a signal before non-deterministic behavior degrades.

## Lane

**Lite** - Internal gate integration. Gate 2 already exists; this adds eval
results as an additional signal within the existing gate, not a new gate.

## Allowed Paths

- `src/gzkit/commands/gates.py` - Gate 2 integration
- `src/gzkit/quality.py` - wire `run_eval()` into quality pipeline
- `src/gzkit/eval/` - threshold configuration and delta comparison
- `config/` - eval threshold configuration
- `tests/commands/` - gate integration tests
- `tests/eval/` - delta comparison tests

## Denied Paths

- `data/eval/` - dataset creation is OBPI-01
- `src/gzkit/eval/runner.py` - harness internals are OBPI-02
- `src/gzkit/cli/` - no new CLI commands
- `docs/user/` - no operator docs changes

## Requirements (FAIL-CLOSED)

1. Gate 2 MUST include eval results when eval datasets exist.
2. Gate 2 MUST NOT fail when eval datasets are absent (graceful skip).
3. Eval thresholds MUST be configurable via `config/` -- not hardcoded.
4. A regression MUST be defined as: any dimension score dropping by more than
   the configured threshold compared to the stored baseline.
5. Gate failure output MUST include which surface and dimension regressed, the
   baseline score, and the current score.
6. Eval gate results MUST be recorded in the ledger via `gate_checked_event()`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `src/gzkit/commands/gates.py` lines 57-82 - Gate 2 implementation
- [ ] `src/gzkit/quality.py` - quality runner pattern
- [ ] `src/gzkit/eval/runner.py` - eval suite output structure (from OBPI-02)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/eval/runner.py` exists with `run_eval_suite()` (OBPI-02)
- [ ] `src/gzkit/quality.py` has `run_eval()` function (OBPI-02)

**Existing Code (understand current state):**

- [ ] `tests/commands/test_gates.py` - existing gate test patterns
- [ ] `config/` - existing configuration patterns

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
uv run gz gates --adr ADR-0.0.5
uv run -m unittest tests/eval/test_delta_gates.py -v
```

## Acceptance Criteria

- [ ] **REQ-0.0.5-03-01:** Gate 2 in `gates.py` includes eval results when
  `data/eval/` contains datasets, and skips gracefully when absent.
- [ ] **REQ-0.0.5-03-02:** Eval thresholds are configurable in `config/` with
  sensible defaults (suggested: 0.5 score drop per dimension).
- [ ] **REQ-0.0.5-03-03:** Gate failure output names the regressed surface,
  dimension, baseline score, and current score.
- [ ] **REQ-0.0.5-03-04:** Gate results are persisted to the ledger via
  `gate_checked_event()`.

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
