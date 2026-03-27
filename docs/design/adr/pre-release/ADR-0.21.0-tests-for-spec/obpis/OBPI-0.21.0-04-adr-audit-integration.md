---
id: OBPI-0.21.0-04-adr-audit-integration
parent: ADR-0.21.0-tests-for-spec
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.21.0-04: ADR Audit Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #4 — "ADR audit integration: wire coverage into `gz adr audit-check`"

**Status:** Completed

## Objective

Integrate requirement coverage data into `gz adr audit-check` so that auditors can verify REQ fulfillment as part of the standard audit pipeline. Uncovered REQs surface as audit findings.

## Lane

**Heavy** — Changes existing `gz adr audit-check` output. Requires docs,
BDD, and human attestation.

## Allowed Paths

- `src/gzkit/commands/` — audit-check integration
- `tests/test_traceability.py` — audit integration tests
- `docs/user/commands/adr-audit-check.md` — updated docs
- `features/test_traceability.feature` — audit/coverage acceptance scenarios
- `features/steps/test_traceability_steps.py` — BDD step implementations

## Denied Paths

- `src/gzkit/traceability.py` — engine is read-only at this point
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz adr audit-check ADR-X.Y.Z` MUST include a coverage section showing REQ fulfillment.
1. REQUIREMENT: Uncovered REQs MUST appear as audit findings (advisory, not blocking).
1. REQUIREMENT: Coverage section in `--json` output MUST include per-OBPI coverage data.
1. NEVER: Make coverage a blocking audit gate in this OBPI.

> STOP-on-BLOCKERS: OBPI-03 must be complete (coverage data must be queryable).

## Quality Gates (Heavy)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [x] Unit tests verify coverage section and advisory findings in audit output
- [x] Tests pass: `uv run -m unittest tests.test_traceability -v`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [x] `docs/user/commands/adr-audit-check.md` updated with coverage section
- [x] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [x] `features/test_traceability.feature` covers audit-check coverage behavior
- [x] `uv run -m behave features/test_traceability.feature` passes

### Gate 5: Human

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.21.0-04-01: Given `gz adr audit-check ADR-0.20.0`, then output includes coverage section.
- [x] REQ-0.21.0-04-02: Given uncovered REQs, then audit output lists them as advisory findings.
- [x] REQ-0.21.0-04-03: Given `gz adr audit-check --json`, then coverage data is in JSON output.

## Verification Commands (Concrete)

```bash
uv run gz adr audit-check ADR-0.20.0
# Expected: output includes coverage section and advisory uncovered-REQ findings

uv run gz adr audit-check ADR-0.20.0 --json
# Expected: JSON payload includes per-OBPI coverage data

uv run -m unittest tests.test_traceability -v
# Expected: audit integration tests pass

uv run -m behave features/test_traceability.feature
# Expected: audit/coverage BDD scenarios pass

uv run mkdocs build --strict
# Expected: updated audit-check docs build cleanly

uv run gz lint
uv run gz typecheck
# Expected: audit integration remains lint/type clean
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (60/60)
- [x] **Gate 3 (Docs):** Docs updated
- [x] **Gate 4 (BDD):** Acceptance scenarios pass (7/7)
- [x] **Gate 5 (Human):** Attestation recorded
- [x] **Code Quality:** Clean (lint, typecheck, 96% coverage)

---

### Implementation Summary

- Integration: `_compute_adr_coverage()` scans briefs and test tree, filters by ADR semver, groups by OBPI
- Output: coverage section in human (Rich console) and JSON modes with per-OBPI rollup
- Advisory: uncovered REQs listed with `severity: "advisory"`, never affect `passed` status
- Tests: 12 new tests (4 `TestExtractAdrSemver` + 8 `TestComputeAdrCoverage`)
- BDD: 2 new scenarios verifying JSON coverage section and advisory findings
- Docs: `docs/user/commands/adr-audit-check.md` coverage section documentation

### Key Proof

```bash
uv run gz adr audit-check ADR-0.20.0 --json
# JSON includes "coverage" key with total_reqs, covered_reqs, by_obpi array
# JSON includes "advisory_findings" for uncovered REQs
uv run -m behave features/test_traceability.feature
# 7/7 scenarios pass including audit-check coverage scenarios
```

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
