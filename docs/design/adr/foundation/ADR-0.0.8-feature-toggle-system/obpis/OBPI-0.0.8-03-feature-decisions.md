---
id: OBPI-0.0.8-03-feature-decisions
parent: ADR-0.0.8-feature-toggle-system
item: 3
lane: Heavy
status: Pending
---

# OBPI-0.0.8-03: Feature Decisions

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #5 — "Named decision methods (FeatureDecisions)"

**Status:** Pending

## Objective

Implement the FeatureDecisions class — the architectural keystone that maps
raw flag keys to named, typed decision methods. This is the single place in
the codebase where flag key strings appear outside the registry. Commands and
workflows consume named decisions, never flag keys.

Initial decisions: `product_proof_enforced()` for the GHI #49 use case.

## Lane

**Heavy** — New API surface consumed by command functions. The FeatureDecisions
contract is the boundary between toggle infrastructure and business logic.

## Dependencies

- **Upstream:** OBPI-02 (FlagService with `is_enabled`).
- **Downstream:** OBPI-06 (closeout migration consumes decisions).
- **Parallel:** OBPI-04 (diagnostics — no dependency in either direction).

## Allowed Paths

- `src/gzkit/flags/decisions.py` — FeatureDecisions class
- `src/gzkit/flags/__init__.py` — Public API updates (get_decisions)
- `tests/test_feature_decisions.py` — Decision method unit tests

## Denied Paths

- `src/gzkit/flags/service.py` — Read-only; belongs to OBPI-02
- `src/gzkit/commands/` — Integration belongs to OBPI-06
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: FeatureDecisions MUST accept a FlagService instance at construction.
1. REQUIREMENT: Each decision method MUST return `bool` and call `self._svc.is_enabled(key)` internally.
1. REQUIREMENT: Flag key strings MUST appear ONLY in FeatureDecisions methods — nowhere else in the codebase.
1. REQUIREMENT: Initial decision methods MUST include: `product_proof_enforced()`.
1. REQUIREMENT: A `get_decisions()` module-level function MUST return a lazily-initialized FeatureDecisions singleton.
1. REQUIREMENT: Every decision method MUST have a docstring explaining the behavioral effect of True vs False.
1. NEVER: Expose flag key strings through public API.
1. ALWAYS: Decision methods named as questions or capabilities (e.g., `product_proof_enforced`, `use_new_init_scaffold`).

> STOP-on-BLOCKERS: OBPI-02 must be complete (FlagService available).

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #5 referenced

### Gate 2: TDD

- [ ] Unit tests validate `product_proof_enforced()` returns True when flag ON
- [ ] Unit tests validate `product_proof_enforced()` returns False when flag OFF
- [ ] Unit tests validate each decision method with flag ON and OFF
- [ ] Unit tests validate `get_decisions()` returns same instance (singleton)
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Module docstring and method docstrings in decisions.py

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.0.8-03-01: Given `ops.product_proof` is enabled, when `decisions.product_proof_enforced()` is called, then returns `True`.
- [ ] REQ-0.0.8-03-02: Given `ops.product_proof` is disabled via test override, when `decisions.product_proof_enforced()` is called, then returns `False`.
- [ ] REQ-0.0.8-03-03: Given a grep for flag key strings outside `flags/decisions.py` and `data/flags.json`, when run, then no matches found.
- [ ] REQ-0.0.8-03-04: Given two calls to `get_decisions()`, when compared, then they return the same object.

## Verification Commands

```bash
# Decision method tests
uv run -m unittest tests.test_feature_decisions -v

# Verify flag key containment — keys must only appear in decisions.py and flags.json
grep -rn "ops.product_proof" src/gzkit/ --include="*.py" | grep -v "flags/decisions.py" | grep -v "__pycache__"
# Expected: no matches

# Full suite regression
uv run gz test

# Code quality
uv run gz lint
uv run gz typecheck
```

## Evidence

### Implementation Summary

- Files created/modified: (to be filled on completion)
- Validation commands run: (to be filled on completion)
- Date completed: (to be filled on completion)

### Key Proof

(to be filled on completion)

---

**Brief Status:** Pending
