---
id: OBPI-0.0.7-04-hooks-module-migration
parent: ADR-0.0.7-config-first-resolution-discipline
item: 4
lane: Lite
status: attested_completed
---

# OBPI-0.0.7-04-hooks-module-migration: Hooks module migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #4 - "Hooks module migration — remove `Path(__file__).parents[3]` from `hooks/guards.py`; thread manifest paths"

**Status:** Completed

## Objective

Remove the `root = Path(__file__).resolve().parents[3]` local variable from
`hooks/guards.py:99` and replace with a manifest-threaded path parameter.
Single-file migration targeting one violation site.

## Lane

**Lite** - Internal refactoring; no CLI/API contract change.

## Allowed Paths

- `src/gzkit/hooks/guards.py` — remove `Path(__file__).parents[3]`; thread manifest or project root
- `tests/` — update or add tests covering the guards function

## Denied Paths

- `src/gzkit/eval/` — that is OBPI-03
- Other hooks modules not containing the violation
- New dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `grep -rn "Path(__file__)" src/gzkit/hooks/guards.py` MUST return zero matches after migration
2. NEVER: Add a fallback that computes root from `__file__` when no parameter is provided
3. ALWAYS: The function containing this pattern must accept project root or manifest as a parameter
4. REQUIREMENT: All existing hooks tests MUST pass after migration

> STOP-on-BLOCKERS: if OBPI-02 is not yet implemented, halt.

## Discovery Checklist

**Context:**

- [x] Parent ADR — understand anti-pattern warning
- [x] OBPI-02 complete (`manifest_path()` helper available)

**Existing Code:**

- [x] `src/gzkit/hooks/guards.py:99` — the violation site
- [x] Callers of the function containing the violation

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Tests pass: `uv run gz test`
- [x] Zero `Path(__file__)` in guards: `grep -rn "Path(__file__)" src/gzkit/hooks/guards.py`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Verification

```bash
grep -rn "Path(__file__)" src/gzkit/hooks/guards.py   # expect: no output
uv run gz lint
uv run gz typecheck
uv run -m unittest -q
```

## Acceptance Criteria

- [x] REQ-0.0.7-04-01: Given `hooks/guards.py`, when `grep -rn "Path(__file__)" src/gzkit/hooks/guards.py` runs, then zero matches are returned
- [x] REQ-0.0.7-04-02: Given the function that previously used `Path(__file__).parents[3]`, when called, then it receives project root as a parameter
- [x] REQ-0.0.7-04-03: Given existing hooks tests, when `uv run -m unittest -q` runs, then all tests pass

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, grep proof clean
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Implementation Summary

- Removed: `root = Path(__file__).resolve().parents[3]` from `forbid_pytest()`
- Changed: `forbid_pytest()` signature to `forbid_pytest(root: Path)` — required parameter
- Updated: `main()` to pass `Path.cwd()` as root

### Key Proof

```text
$ grep -rn "Path(__file__)" src/gzkit/hooks/guards.py
(no output — zero matches)

$ uv run gz test
Ran 2015 tests in 17.206s — OK

$ uv run gz lint
All checks passed!

$ uv run gz typecheck
All checks passed!
```

### Gate 2 (TDD)

```text
grep -rn "Path(__file__)" src/gzkit/hooks/guards.py  →  zero matches
2015/2015 full suite pass
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
