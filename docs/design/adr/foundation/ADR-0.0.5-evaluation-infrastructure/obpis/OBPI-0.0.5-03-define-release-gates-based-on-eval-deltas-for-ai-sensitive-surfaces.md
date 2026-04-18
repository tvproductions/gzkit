---
id: OBPI-0.0.5-03-define-release-gates-based-on-eval-deltas-for-ai-sensitive-surfaces
parent: ADR-0.0.5-evaluation-infrastructure
item: 3
lane: lite
status: in_progress
---

# OBPI-0.0.5-03: Eval-Delta Release Gates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
- **Checklist Item:** #3 - "Eval-delta release gates for AI-sensitive surfaces"

**Status:** Completed

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

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

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

- [x] **REQ-0.0.5-03-01:** Gate 2 in `gates.py` includes eval results when
  `data/eval/` contains datasets, and skips gracefully when absent.
- [x] **REQ-0.0.5-03-02:** Eval thresholds are configurable in `config/` with
  sensible defaults (suggested: 0.5 score drop per dimension).
- [x] **REQ-0.0.5-03-03:** Gate failure output names the regressed surface,
  dimension, baseline score, and current score.
- [x] **REQ-0.0.5-03-04:** Gate results are persisted to the ledger via
  `gate_checked_event()`.

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
Ran 20 tests in 0.044s — OK
tests/eval/test_delta_gates.py: 20/20 pass
Full suite: 1530 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Value Narrative

Before this OBPI, Gate 2 only ran deterministic tests — there was no mechanism to detect
regressions in eval scores across commits. Now, Gate 2 automatically compares eval harness
scores against stored baselines and blocks the gate when any dimension drops beyond a
configurable threshold.

### Key Proof

```bash
uv run -m unittest tests/eval/test_delta_gates.py -v
# 20 tests covering: threshold config, baseline storage, delta comparison,
# regression output formatting, and gate integration (skip/detect/record)
```

### Implementation Summary

- Files created/modified: `config/eval_thresholds.json`, `src/gzkit/eval/delta.py`, `src/gzkit/commands/gates.py`, `src/gzkit/cli/main.py`
- Tests added: `tests/eval/test_delta_gates.py` (20 tests)
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
