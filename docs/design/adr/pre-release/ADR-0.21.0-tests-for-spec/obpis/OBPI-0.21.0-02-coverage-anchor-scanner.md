---
id: OBPI-0.21.0-02-coverage-anchor-scanner
parent: ADR-0.21.0-tests-for-spec
item: 2
lane: Lite
status: Accepted
---

# OBPI-0.21.0-02: Coverage Anchor Scanner

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #2 — "Coverage anchor scanner: walk test tree, discover annotations, produce LinkageRecords"

**Status:** Accepted

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

- [ ] REQ-0.21.0-02-01: Given a test tree with 10 `@covers` annotations across 5 files, when scanned, then 10 LinkageRecords are produced with correct file paths.
- [ ] REQ-0.21.0-02-02: Given 8 REQs in briefs and 5 `@covers` annotations, when coverage is computed, then report shows 5/8 covered (62.5%).
- [ ] REQ-0.21.0-02-03: Given coverage data, when rolled up by ADR, then shows per-ADR coverage percentage.

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
