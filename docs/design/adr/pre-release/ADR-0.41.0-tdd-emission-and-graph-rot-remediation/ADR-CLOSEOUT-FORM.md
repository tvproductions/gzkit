# ADR Closeout Form: ADR-0.41.0-tdd-emission-and-graph-rot-remediation

**Status**: Draft — In Progress

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass, with `tdd_red_observed`/`tdd_green_observed` events emitted per REQ
- [ ] Gate 3 (Docs): Docs build passes, manpage for `gz tdd` present
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed
- [ ] GHI-160 Phases 1-7 retroactively housed and linked via OBPI-05

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-0.41.0-tdd-emission-and-graph-rot-remediation.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 2 (TDD events) | RED/GREEN chain | `uv run gz tdd chain REQ-0.41.0-NN-MM` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz attest ADR-0.41.0 --status completed` |

## OBPI Status

| OBPI | Title | Status |
|------|-------|--------|
| OBPI-0.41.0-01 | Ledger event types for TDD (tdd_red_observed / tdd_green_observed + schema) | Draft |
| OBPI-0.41.0-02 | `gz tdd` CLI with verified emission semantics | Draft |
| OBPI-0.41.0-03 | Attestation-enrichment rule integration for TDD event citations | Draft |
| OBPI-0.41.0-04 | Runbook, manpage, and docs for `gz tdd` + tests.md update | Draft |
| OBPI-0.41.0-05 | Retroactive governance housing for GHI-160 Phases 1-7 | Draft |

## GHI-160 Remediation Program Summary

This ADR is the formal governance home for the GHI-160 remedy program. At
closeout, the following prior-commit evidence is linked via OBPI-05:

| Phase | Commit    | Summary                                                  |
|-------|-----------|----------------------------------------------------------|
| 1     | `70cdcdb8` | Governance graph rot audit                              |
| 2     | `d3bdb60b` | `gz covers --include-doc` flag                          |
| 3     | `c481673a` | REQ-ID backfill across 260 briefs                       |
| 4a    | `00bfea05` | Retroactive `@covers` for orphan ceremony tests         |
| 4b    | `9ba8e802` | Phase 4 residual `@covers` for OBPI-01/02/03 orphans    |
| 6/7   | _this commit series_ | `gz validate` checks + TASK backfill           |
| 5     | _OBPI-01 through 04_ | TDD emission implementation                    |

## Attestation

**Attestor:**
**Date:**
**Decision:**
**Notes:**
