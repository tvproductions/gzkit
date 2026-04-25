# ADR Closeout Form: ADR-0.0.22-security-sensitivity-doctrine

**Status**: Phase 0 — Proposed (closeout pending OBPI completion)

---

## Pre-Attestation Checklist

Closeout evidence to be verified after OBPI completion:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed
- [ ] Foundation-kind closeout walkthrough per ADR-0.0.18 (heavy lane + foundation kind + sensitivity:security)

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | Behave suite passes | `uv run behave features/` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.22-security-sensitivity-doctrine` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.22-01-schema-frontmatter-field](obpis/OBPI-0.0.22-01-schema-frontmatter-field.md) | Schema + frontmatter field for sensitivity axis | Pending |
| [OBPI-0.0.22-02-security-surface-registry](obpis/OBPI-0.0.22-02-security-surface-registry.md) | Security-surface registry data file | Pending |
| [OBPI-0.0.22-03-validate-sensitivity-scope](obpis/OBPI-0.0.22-03-validate-sensitivity-scope.md) | gz validate --sensitivity scope with --explain subform | Pending |
| [OBPI-0.0.22-04-requires-security-review-attestation](obpis/OBPI-0.0.22-04-requires-security-review-attestation.md) | _requires_security_review_attestation audit OR | Pending |
| [OBPI-0.0.22-05-gate5-walkthrough-arb-slot](obpis/OBPI-0.0.22-05-gate5-walkthrough-arb-slot.md) | Gate 5 walkthrough extension and ARB canonical command slot | Pending |
| [OBPI-0.0.22-06-rule-file-matrix-scorecard](obpis/OBPI-0.0.22-06-rule-file-matrix-scorecard.md) | Rule file plus AGENTS.md matrix plus advisory scorecard entry | Pending |

## Parallelism

`{OBPI-01, OBPI-02} → OBPI-03 → {OBPI-04 → OBPI-05} → OBPI-06`

## Defense Brief

*To be authored at closeout — populated by `gz closeout` ceremony from OBPI Closing Arguments.*

## Human Attestation

*Pending OBPI completion. Foundation-kind + heavy-lane + sensitivity:security stacks attestation rigor — TTY + ATTEST gate required.*
