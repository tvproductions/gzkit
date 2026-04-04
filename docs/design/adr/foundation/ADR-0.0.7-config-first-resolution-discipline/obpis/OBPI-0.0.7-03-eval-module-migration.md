---
id: OBPI-0.0.7-03-eval-module-migration
parent: ADR-0.0.7-config-first-resolution-discipline
item: 3
lane: Lite
status: Completed
---

# OBPI-0.0.7-03-eval-module-migration: Eval module migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #3 - "Eval module migration — remove `_PROJECT_ROOT` from `eval/datasets.py`, `eval/delta.py`, `eval/regression.py`; thread manifest paths"

**Status:** Completed

## Objective

Remove all 3 `_PROJECT_ROOT = Path(__file__).resolve().parents[3]` constants and
their 5 dependent path constants from `eval/datasets.py`, `eval/delta.py`, and
`eval/regression.py`. Replace with manifest-threaded parameters using the
`manifest_path()` helper from OBPI-02.

## Lane

**Lite** - Internal refactoring; no CLI/API contract change.

## Allowed Paths

- `src/gzkit/eval/datasets.py` — remove `_PROJECT_ROOT`, `_DATA_DIR`, `_SCHEMA_PATH`; thread manifest
- `src/gzkit/eval/delta.py` — remove `_PROJECT_ROOT`, `_CONFIG_PATH`, `_BASELINES_DIR`; thread manifest
- `src/gzkit/eval/regression.py` — remove `_PROJECT_ROOT`, `_BASELINES_DIR`; thread manifest
- `tests/test_eval_*.py` — update tests to pass manifest parameter

## Denied Paths

- `src/gzkit/hooks/` — that is OBPI-04
- `src/gzkit/commands/common.py` — helper already exists from OBPI-02
- New dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `grep -rn "_PROJECT_ROOT" src/gzkit/eval/` MUST return zero matches after migration
2. REQUIREMENT: `grep -rn "Path(__file__)" src/gzkit/eval/` MUST return zero matches after migration
3. NEVER: Add a fallback that reads from the old constant when no manifest is provided
4. ALWAYS: Every function that previously used `_PROJECT_ROOT` must accept the path as a parameter
5. REQUIREMENT: All existing eval tests MUST pass after migration

> STOP-on-BLOCKERS: if OBPI-01 or OBPI-02 are not yet implemented, halt.

## Discovery Checklist

**Context:**

- [x] Parent ADR — understand anti-pattern warning about "fallback" constants
- [x] OBPI-01 complete (v2 manifest with `data` section)
- [x] OBPI-02 complete (`manifest_path()` helper available)

**Existing Code (understand current state):**

- [x] `src/gzkit/eval/datasets.py:18` — `_PROJECT_ROOT` and dependents
- [x] `src/gzkit/eval/delta.py:21` — `_PROJECT_ROOT` and dependents
- [x] `src/gzkit/eval/regression.py:26` — `_PROJECT_ROOT` and dependents
- [x] Callers of functions in these modules (to update parameter passing)

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Tests pass: `uv run gz test`
- [x] Zero `_PROJECT_ROOT` in eval modules: `grep -rn "_PROJECT_ROOT" src/gzkit/eval/`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Verification

```bash
grep -rn "_PROJECT_ROOT" src/gzkit/eval/     # expect: no output
grep -rn "Path(__file__)" src/gzkit/eval/    # expect: no output
uv run gz lint
uv run gz typecheck
uv run -m unittest -q
```

## Acceptance Criteria

- [x] REQ-0.0.7-03-01: Given the eval modules, when `grep -rn "_PROJECT_ROOT" src/gzkit/eval/` runs, then zero matches are returned
- [x] REQ-0.0.7-03-02: Given `eval/datasets.py`, when a caller invokes dataset functions, then paths resolve from manifest parameter, not module constants
- [x] REQ-0.0.7-03-03: Given existing eval tests, when `uv run -m unittest -q` runs, then all tests pass with zero failures

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, grep proof clean
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Implementation Summary

- Removed: `_PROJECT_ROOT`, `_DATA_DIR`, `_SCHEMA_PATH` from `datasets.py`
- Removed: `_PROJECT_ROOT`, `_CONFIG_PATH`, `_BASELINES_DIR` from `delta.py`
- Removed: `_PROJECT_ROOT`, `_BASELINES_DIR` from `regression.py`
- Changed: All path parameters from `Path | None = None` to required `Path`
- Updated: `runner.py` and `quality.py` to thread `data_dir` from callers
- Updated: 4 test files to pass explicit path parameters

### Key Proof

```text
$ grep -rn "_PROJECT_ROOT" src/gzkit/eval/
(no output — zero matches)

$ grep -rn "Path(__file__)" src/gzkit/eval/
(no output — zero matches)

$ uv run -m unittest tests/eval/test_datasets.py tests/eval/test_delta_gates.py tests/eval/test_regression.py tests/eval/test_harness.py -v
Ran 73 tests in 0.141s — OK

$ uv run gz test
Ran 2015 tests in 17.001s — OK

$ uv run gz lint
All checks passed!

$ uv run gz typecheck
All checks passed!
```

### Gate 2 (TDD)

```text
grep -rn "_PROJECT_ROOT" src/gzkit/eval/  →  zero matches
grep -rn "Path(__file__)" src/gzkit/eval/  →  zero matches
73/73 eval tests pass; 2015/2015 full suite pass
```

### Code Quality

```text
uv run gz lint  →  All checks passed!
uv run gz typecheck  →  All checks passed!
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff` (Foundation ADR — human attestation required)
- Attestation: `attest completed`
- Date: `2026-03-30`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-30

**Evidence Hash:** -
