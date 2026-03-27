---
id: OBPI-0.21.0-02-coverage-anchor-scanner
parent: ADR-0.21.0-tests-for-spec
item: 2
lane: Lite
status: Completed
---

# OBPI-0.21.0-02: Coverage Anchor Scanner

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #2 — "Coverage anchor scanner: walk test tree, discover annotations, produce LinkageRecords"

**Status:** Completed

## Objective

Build a scanner that walks the test directory tree, discovers all `@covers` annotations (both via runtime registry and AST-based static analysis), and produces a complete set of LinkageRecords for coverage computation.

## Lane

**Lite** — Internal engine; no CLI changes.

## Allowed Paths

- `src/gzkit/traceability.py` — scanner functions (extend from OBPI-01)
- `tests/test_traceability.py` — scanner unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI belongs to OBPI-03
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Scanner MUST discover `@covers` annotations across all Python test files in a given directory tree.
1. REQUIREMENT: Scanner MUST produce LinkageRecords with source file path and line number for each annotation.
1. REQUIREMENT: Scanner MUST compute coverage rollup at three levels: ADR, OBPI, REQ.
1. REQUIREMENT: Coverage report MUST show: total REQs, covered REQs, uncovered REQs, coverage percentage per level.
1. REQUIREMENT: Scanner MUST be deterministic — same test tree always produces same results.
1. NEVER: Execute test files during scanning — analysis must be static or use the import-time registry.

> STOP-on-BLOCKERS: OBPI-01 must be complete (@covers decorator and registry).

## Acceptance Criteria

- [x] REQ-0.21.0-02-01: Given a test tree with 10 `@covers` annotations across 5 files, when scanned, then 10 LinkageRecords are produced with correct file paths.
- [x] REQ-0.21.0-02-02: Given 8 REQs in briefs and 5 `@covers` annotations, when coverage is computed, then report shows 5/8 covered (62.5%).
- [x] REQ-0.21.0-02-03: Given coverage data, when rolled up by ADR, then shows per-ADR coverage percentage.

## Verification Commands (Concrete)

```bash
uv run -m unittest tests.test_traceability -v
# Expected: scanner tests pass for discovery, line-number capture, and rollup math

uv run gz lint
# Expected: lint passes after scanner implementation

uv run gz typecheck
# Expected: scanner/linkage types remain clean
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean

---

### Implementation Summary

- Scanner: `scan_test_tree()` in `src/gzkit/traceability.py` — AST-based discovery of `@covers` annotations across Python test files, no execution
- Coverage: `compute_coverage()` produces `CoverageReport` with rollups at ADR, OBPI, and REQ levels
- Models: `CoverageEntry`, `CoverageRollup`, `CoverageReport` — frozen Pydantic models with JSON serialization
- Tests: 18 new tests in `tests/test_traceability.py` (9 scanner, 9 coverage rollup)
- Coverage: 83% on `src/gzkit/traceability.py` (threshold: 40%)

### Key Proof

```
$ uv run -m unittest tests.test_traceability -v
Ran 38 tests in 0.005s  OK
```

```
$ uv run gz lint && uv run gz typecheck
Lint passed. Type check passed.
```

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
