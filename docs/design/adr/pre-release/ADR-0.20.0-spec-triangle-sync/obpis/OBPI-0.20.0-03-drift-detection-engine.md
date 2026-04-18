---
id: OBPI-0.20.0-03-drift-detection-engine
parent: ADR-0.20.0-spec-triangle-sync
item: 3
lane: Lite
status: in_progress
---

# OBPI-0.20.0-03: Drift Detection Engine

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #3 — "Drift detection engine: compute unlinked specs, orphan tests, and unjustified code changes"

**Status:** Completed

## Objective

Build the core drift detection engine that, given extracted REQ entities, test
linkage data, and changed-code signals, computes three categories of drift:
unlinked specs (REQs with no test coverage), orphan tests (tests referencing
non-existent REQs), and unjustified code changes (changed code vertices with no
corresponding governance justification). The engine is pure computation — no
I/O, no CLI.

## Lane

**Lite** — Internal engine; no external contract changes.

## Allowed Paths

- `src/gzkit/triangle.py` — drift detection functions (extend the module from OBPI-01/02)
- `tests/test_triangle.py` — drift detection unit tests

## Denied Paths

- `src/gzkit/commands/` — CLI belongs to OBPI-04
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Detect unlinked specs — REQ entities that have no corresponding test linkage record.
1. REQUIREMENT: Detect orphan tests — test linkage records that reference REQ identifiers not found in any brief.
1. REQUIREMENT: Detect unjustified code changes — changed code vertices with no corresponding `justifies` edge to an in-scope REQ in the inspected scan window.
1. REQUIREMENT: Produce a DriftReport model containing: unlinked_specs, orphan_tests, unjustified_code_changes, summary counts, scan timestamp.
1. REQUIREMENT: DriftReport MUST be serializable to JSON for downstream consumption by CLI and gate integration.
1. REQUIREMENT: Engine MUST be deterministic — same inputs always produce same outputs.
1. REQUIREMENT: Engine accepts REQs, linkage data, and changed code vertices as input (not file I/O) — pure computation for testability.
1. NEVER: Use LLM inference for drift detection.
1. ALWAYS: Sort results by identifier for stable output.

> STOP-on-BLOCKERS: OBPI-0.20.0-01 must be complete (data model), OBPI-0.20.0-02 should be complete (REQ extraction) but engine can be tested with synthetic data.

## Quality Gates (Lite)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Unit tests with table-driven data: no drift, all drift, mixed drift, unjustified code change
- [x] Unit tests verify determinism (same input → same output)
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [x] REQ-0.20.0-03-01: Given 5 REQs and 5 matching test linkages, when drift is computed, then unlinked_specs and orphan_tests are both empty.
- [x] REQ-0.20.0-03-02: Given 5 REQs and 0 test linkages, when drift is computed, then unlinked_specs contains all 5 REQs.
- [x] REQ-0.20.0-03-03: Given 3 REQs and 5 test linkages (2 referencing non-existent REQs), when drift is computed, then orphan_tests contains the 2 orphaned linkages.
- [x] REQ-0.20.0-03-04: Given 2 changed code vertices and only 1 `justifies` edge to an in-scope REQ, when drift is computed, then unjustified_code_changes contains the remaining changed code vertex.
- [x] REQ-0.20.0-03-05: Given identical inputs run twice, when drift is computed, then both DriftReports are equal.

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Coverage:** Coverage >= 40% maintained

## Evidence

### Implementation Summary

- Engine: `detect_drift()` pure function in `src/gzkit/triangle.py`
- Models: `DriftSummary` and `DriftReport` Pydantic models with frozen/forbid config
- Inputs: REQ entities, linkage records, changed code vertices, scan timestamp
- Outputs: Deterministic DriftReport with unlinked_specs, orphan_tests, unjustified_code_changes
- Sorting: Semantic version order for REQ IDs via `_req_id_sort_key()`
- Tests: 18 new drift detection tests across 8 test classes in `tests/test_triangle.py`

### Key Proof

```text
$ uv run -m unittest tests.test_triangle -v 2>&1 | grep -E '(drift|Drift)'
test_identical_inputs_identical_outputs ... ok
test_all_drift_categories ... ok
test_empty_inputs ... ok
test_all_reqs_covered_no_drift ... ok
test_orphan_tests_detected ... ok
test_all_code_justified ... ok
test_no_changed_code ... ok
test_unjustified_code_changes ... ok
test_all_reqs_unlinked ... ok
test_partial_coverage ... ok
test_frozen_immutability ... ok
test_json_serialization_roundtrip ... ok
test_report_is_valid_json ... ok
test_results_sorted_semantically ... ok
test_summary_counts_correct ... ok
test_summary_extra_forbidden ... ok
test_summary_frozen ... ok

Ran 66 tests in 0.004s — OK

$ uv run coverage report --include='src/gzkit/triangle.py'
src/gzkit/triangle.py    159      6    96%
```

### Gate 2 (TDD)

```text
Ran 66 tests in 0.004s — OK
Coverage: 96% (threshold: 40%)
```

## Human Attestation

- Attestor: Jeff
- Attestation: attest completed
- Date: 2026-03-27

---

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
