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

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Unit tests verify coverage section and advisory findings in audit output
- [ ] Tests pass: `uv run -m unittest tests.test_traceability -v`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [ ] `docs/user/commands/adr-audit-check.md` updated with coverage section
- [ ] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [ ] `features/test_traceability.feature` covers audit-check coverage behavior
- [ ] `uv run -m behave features/test_traceability.feature` passes

### Gate 5: Human

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.21.0-04-01: Given `gz adr audit-check ADR-0.20.0`, then output includes coverage section.
- [ ] REQ-0.21.0-04-02: Given uncovered REQs, then audit output lists them as advisory findings.
- [ ] REQ-0.21.0-04-03: Given `gz adr audit-check --json`, then coverage data is in JSON output.

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

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Docs updated
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
