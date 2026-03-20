---
id: OBPI-0.21.0-04-adr-audit-integration
parent: ADR-0.21.0-tests-for-spec
item: 4
lane: Heavy
status: Accepted
---

# OBPI-0.21.0-04: ADR Audit Integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #4 — "ADR audit integration: wire coverage into `gz adr audit-check`"

**Status:** Accepted

## Objective

Integrate requirement coverage data into `gz adr audit-check` so that auditors can verify REQ fulfillment as part of the standard audit pipeline. Uncovered REQs surface as audit findings.

## Lane

**Heavy** — Changes existing `gz adr audit-check` output.

## Allowed Paths

- `src/gzkit/commands/` — audit-check integration
- `tests/test_traceability.py` — audit integration tests
- `docs/user/commands/adr-audit-check.md` — updated docs

## Denied Paths

- `src/gzkit/traceability.py` — engine is read-only at this point
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz adr audit-check ADR-X.Y.Z` MUST include a coverage section showing REQ fulfillment.
1. REQUIREMENT: Uncovered REQs MUST appear as audit findings (advisory, not blocking).
1. REQUIREMENT: Coverage section in `--json` output MUST include per-OBPI coverage data.
1. NEVER: Make coverage a blocking audit gate in this OBPI.

> STOP-on-BLOCKERS: OBPI-03 must be complete (coverage data must be queryable).

## Acceptance Criteria

- [ ] REQ-0.21.0-04-01: Given `gz adr audit-check ADR-0.20.0`, then output includes coverage section.
- [ ] REQ-0.21.0-04-02: Given uncovered REQs, then audit output lists them as advisory findings.
- [ ] REQ-0.21.0-04-03: Given `gz adr audit-check --json`, then coverage data is in JSON output.

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Docs updated
- [ ] **Gate 5 (Human):** Attestation recorded

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
