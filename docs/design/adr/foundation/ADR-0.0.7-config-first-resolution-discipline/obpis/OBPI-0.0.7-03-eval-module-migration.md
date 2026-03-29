---
id: OBPI-0.0.7-03-eval-module-migration
parent: ADR-0.0.7
item: 3
lane: Lite
status: Accepted
---

# OBPI-0.0.7-03-eval-module-migration: Eval module migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #3 - "Eval module migration — remove `_PROJECT_ROOT` from `eval/datasets.py`, `eval/delta.py`, `eval/regression.py`; thread manifest paths"

**Status:** Accepted

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

- [ ] Parent ADR — understand anti-pattern warning about "fallback" constants
- [ ] OBPI-01 complete (v2 manifest with `data` section)
- [ ] OBPI-02 complete (`manifest_path()` helper available)

**Existing Code (understand current state):**

- [ ] `src/gzkit/eval/datasets.py:18` — `_PROJECT_ROOT` and dependents
- [ ] `src/gzkit/eval/delta.py:21` — `_PROJECT_ROOT` and dependents
- [ ] `src/gzkit/eval/regression.py:26` — `_PROJECT_ROOT` and dependents
- [ ] Callers of functions in these modules (to update parameter passing)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Tests pass: `uv run gz test`
- [ ] Zero `_PROJECT_ROOT` in eval modules: `grep -rn "_PROJECT_ROOT" src/gzkit/eval/`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
grep -rn "_PROJECT_ROOT" src/gzkit/eval/     # expect: no output
grep -rn "Path(__file__)" src/gzkit/eval/    # expect: no output
uv run gz lint
uv run gz typecheck
uv run -m unittest -q
```

## Acceptance Criteria

- [ ] REQ-0.0.7-03-01: Given the eval modules, when `grep -rn "_PROJECT_ROOT" src/gzkit/eval/` runs, then zero matches are returned
- [ ] REQ-0.0.7-03-02: Given `eval/datasets.py`, when a caller invokes dataset functions, then paths resolve from manifest parameter, not module constants
- [ ] REQ-0.0.7-03-03: Given existing eval tests, when `uv run -m unittest -q` runs, then all tests pass with zero failures

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, grep proof clean
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 2 (TDD)

```text
# Paste grep proof and test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a` (Lite lane, Lite parent)
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
