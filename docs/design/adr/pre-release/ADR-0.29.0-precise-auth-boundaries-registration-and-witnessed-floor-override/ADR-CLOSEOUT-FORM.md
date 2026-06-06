# ADR Closeout Form: ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override

**Status**: Phase 1 — Proposed (authoring complete; implementation pending)

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes (n/a — surfaces covered by direct CLI/validator unit tests)
- [ ] Gate 5 (Human): brief-level attestation (universal; security sensitivity walkthrough)
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Fence | Drift-back validator | `uv run gz validate --auth-surface-coherence` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.29.0-01-precise-auth-boundaries-registration](obpis/OBPI-0.29.0-01-precise-auth-boundaries-registration.md) | Extract `obpi_security_gate.py`; re-point `auth_boundaries`; fail-close names surface+category; verify delegation. | Pending |
| [OBPI-0.29.0-02-security-floor-overridden-event](obpis/OBPI-0.29.0-02-security-floor-overridden-event.md) | `security_floor_overridden` ledger event across all five surfaces; emit on override; make queryable. | Pending |
| [OBPI-0.29.0-03-auth-surface-coherence-validator](obpis/OBPI-0.29.0-03-auth-surface-coherence-validator.md) | `gz validate --auth-surface-coherence` drift-back validator; manpage + runbook docs; advisory-rules-audit scorecard row. | Pending |

## Human Attestation

### Verbatim Attestation

*Pending — recorded at closeout.*

**Attested by**: _______________
**Timestamp (UTC)**: _______________
