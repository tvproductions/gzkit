---
id: OBPI-0.21.0-01-covers-decorator-and-registration
parent: ADR-0.21.0-tests-for-spec
item: 1
lane: Lite
status: Accepted
---

# OBPI-0.21.0-01: @covers Decorator and Registration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #1 — "`@covers` decorator with REQ validation and linkage registration"

**Status:** Accepted

## Objective

Formalize the `@covers` decorator as a typed, validating mechanism that test methods use to declare which governance requirement they prove. The decorator registers linkage at import time and validates the REQ identifier format.

## Lane

**Lite** — Internal decorator; no CLI/API changes.

## Allowed Paths

- `src/gzkit/traceability.py` — decorator implementation, linkage registry
- `tests/test_traceability.py` — decorator unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI belongs to OBPI-03
- `src/gzkit/triangle.py` — read-only consumer of REQ model from ADR-0.20.0
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `@covers("REQ-X.Y.Z-NN-MM")` decorator MUST validate the REQ identifier format at decoration time.
1. REQUIREMENT: Decorator MUST register a LinkageRecord (from ADR-0.20.0 triangle model) mapping the test function to the REQ.
1. REQUIREMENT: Multiple `@covers` on the same test MUST register multiple linkages.
1. REQUIREMENT: `@covers` with an invalid REQ format MUST raise ValueError at import time, not silently pass.
1. REQUIREMENT: A global registry MUST collect all registered linkages for scanner consumption.
1. NEVER: Modify the decorated test function's behavior — `@covers` is metadata-only.
1. ALWAYS: Decorator MUST work with both `unittest.TestCase` methods and standalone test functions.

> STOP-on-BLOCKERS: ADR-0.20.0 OBPI-01 must be complete (REQ entity model).

## Acceptance Criteria

- [ ] REQ-0.21.0-01-01: Given `@covers("REQ-0.15.0-03-02")` on a test method, when the module is imported, then a LinkageRecord is registered.
- [ ] REQ-0.21.0-01-02: Given `@covers("INVALID")` on a test method, when the module is imported, then ValueError is raised.
- [ ] REQ-0.21.0-01-03: Given two `@covers` decorators on one test, when imported, then two LinkageRecords are registered.
- [ ] REQ-0.21.0-01-04: Given `@covers("REQ-0.15.0-03-02")` on a test, when the test runs, then test behavior is unchanged.

## Completion Checklist (Lite)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Unit tests pass
- [ ] **Code Quality:** Lint, format, type checks clean

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
