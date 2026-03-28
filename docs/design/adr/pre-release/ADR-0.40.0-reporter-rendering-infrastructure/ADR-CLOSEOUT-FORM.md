# ADR Closeout Form: ADR-0.40.0-reporter-rendering-infrastructure

**Status**: Phase 1 — In Progress

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.40.0-reporter-rendering-infrastructure/ADR-0.40.0-reporter-rendering-infrastructure.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz attest ADR-0.40.0 --status completed` |

## OBPI Status

| OBPI | Title | Status |
|------|-------|--------|
| OBPI-0.40.0-01 | Reporter module scaffold | Pending |
| OBPI-0.40.0-02 | Common rendering helpers | Pending |
| OBPI-0.40.0-03 | Status/report table migration | Pending |
| OBPI-0.40.0-04 | List table migration | Pending |
| OBPI-0.40.0-05 | Ceremony panel migration | Pending |

## Attestation

**Attestor:**
**Date:**
**Decision:**
**Notes:**
