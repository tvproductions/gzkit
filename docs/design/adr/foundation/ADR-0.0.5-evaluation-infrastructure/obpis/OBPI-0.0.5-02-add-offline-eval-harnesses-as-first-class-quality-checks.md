---
id: OBPI-0.0.5-02-add-offline-eval-harnesses-as-first-class-quality-checks
parent: ADR-0.0.5-evaluation-infrastructure
item: 2
lane: lite
status: attested_completed
---

# OBPI-0.0.5-02: Offline Eval Harnesses

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.5-evaluation-infrastructure/ADR-0.0.5-evaluation-infrastructure.md`
- **Checklist Item:** #2 - "Offline eval harnesses as first-class quality checks"

**Status:** Completed

## Objective

Build unittest-based eval harnesses that load reference datasets, execute
deterministic scoring against AI-sensitive surfaces, and produce structured
score results compatible with the existing `QualityResult` pipeline.

## Lane

**Lite** - Internal test infrastructure. No CLI, API, or operator-facing changes.

## Allowed Paths

- `src/gzkit/eval/` - eval harness modules (scorer, runner, models)
- `tests/eval/` - harness unit tests
- `src/gzkit/quality.py` - add `run_eval()` runner

## Denied Paths

- `data/eval/` - dataset creation is OBPI-01
- `src/gzkit/commands/gates.py` - gate integration is OBPI-03
- `src/gzkit/cli/` - no CLI changes
- `docs/user/` - no operator docs changes

## Requirements (FAIL-CLOSED)

1. Eval harnesses MUST use stdlib `unittest` -- no pytest or custom frameworks.
2. Harnesses MUST NOT make network calls or invoke LLMs.
3. Harnesses MUST produce a numeric score per dimension per surface.
4. Score results MUST be Pydantic `BaseModel` with `frozen=True, extra="forbid"`.
5. A `run_eval()` function MUST be added to `quality.py` returning `QualityResult`.
6. The full eval suite MUST complete within 60 seconds.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `src/gzkit/instruction_eval.py` - existing eval pattern (4-dimension scoring)
- [ ] `src/gzkit/adr_eval.py` - dimension scoring with Pydantic models
- [ ] `src/gzkit/quality.py` - `QualityResult` model and runner pattern
- [ ] `src/gzkit/core/scoring.py` - `DecompositionScorecard` pattern

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/eval/` directory exists (or create it)
- [ ] Dataset loader from OBPI-01 exists, OR use test fixtures for development

**Existing Code (understand current state):**

- [ ] `tests/test_instruction_eval.py` - test scaffold pattern
- [ ] `tests/test_adr_eval.py` - `_STRONG_ADR` fixture and scoring tests

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
uv run -m unittest tests/eval/test_harness.py -v
python -c "from gzkit.eval.runner import run_eval_suite; print(run_eval_suite.__doc__)"
```

## Acceptance Criteria

- [x] **REQ-0.0.5-02-01:** An eval runner in `src/gzkit/eval/runner.py` loads
  datasets by surface name, executes scoring, and returns typed `EvalSuiteScore`
  results.
- [x] **REQ-0.0.5-02-02:** `quality.py` exposes `run_eval()` that returns
  `QualityResult` with structured eval output.
- [x] **REQ-0.0.5-02-03:** Scoring dimensions are defined per surface with
  numeric (0-4) scores, matching the pattern in `adr_eval.py`.
- [x] **REQ-0.0.5-02-04:** Unit tests verify scoring logic against known-good
  and known-bad fixture inputs.

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
Ran 13 tests in 0.008s — OK
Coverage: 99% (scorer.py + runner.py)
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Value Narrative

Reference datasets from OBPI-01 had no scoring engine to consume them. Now per-surface
scorers evaluate fixture inputs structurally (0-4 per dimension), a runner aggregates
results into typed EvalSuiteScore models, and quality.py exposes run_eval() for
integration with the existing quality pipeline.

### Key Proof

```python
from gzkit.eval.runner import run_eval_suite
r = run_eval_suite()
# 5 surfaces, overall=2.7/4.0, success=True
```

### Implementation Summary

- Files created: src/gzkit/eval/scorer.py, src/gzkit/eval/runner.py, tests/eval/test_harness.py
- Files modified: src/gzkit/quality.py (added run_eval())
- Tests added: 13 (6 test classes — scoring, golden/edge, runner, quality integration, determinism)
- Date completed: 2026-03-26
- Attestation status: Human attested (Completed)
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Jeff
- Attestation: Completed — eval harnesses with per-surface scoring, runner, and quality.py integration.
- Date: 2026-03-26

---

**Brief Status:** Completed
**Date Completed:** 2026-03-26
**Evidence Hash:** -
