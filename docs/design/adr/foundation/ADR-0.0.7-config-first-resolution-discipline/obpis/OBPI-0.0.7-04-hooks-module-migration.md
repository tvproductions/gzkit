---
id: OBPI-0.0.7-04-hooks-module-migration
parent: ADR-0.0.7
item: 4
lane: Lite
status: Accepted
---

# OBPI-0.0.7-04-hooks-module-migration: Hooks module migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.7-config-first-resolution-discipline/ADR-0.0.7-config-first-resolution-discipline.md`
- **Checklist Item:** #4 - "Hooks module migration — remove `Path(__file__).parents[3]` from `hooks/guards.py`; thread manifest paths"

**Status:** Accepted

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

- [ ] Parent ADR — understand anti-pattern warning
- [ ] OBPI-02 complete (`manifest_path()` helper available)

**Existing Code:**

- [ ] `src/gzkit/hooks/guards.py:99` — the violation site
- [ ] Callers of the function containing the violation

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Tests pass: `uv run gz test`
- [ ] Zero `Path(__file__)` in guards: `grep -rn "Path(__file__)" src/gzkit/hooks/guards.py`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
grep -rn "Path(__file__)" src/gzkit/hooks/guards.py   # expect: no output
uv run gz lint
uv run gz typecheck
uv run -m unittest -q
```

## Acceptance Criteria

- [ ] REQ-0.0.7-04-01: Given `hooks/guards.py`, when `grep -rn "Path(__file__)" src/gzkit/hooks/guards.py` runs, then zero matches are returned
- [ ] REQ-0.0.7-04-02: Given the function that previously used `Path(__file__).parents[3]`, when called, then it receives project root as a parameter
- [ ] REQ-0.0.7-04-03: Given existing hooks tests, when `uv run -m unittest -q` runs, then all tests pass

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
