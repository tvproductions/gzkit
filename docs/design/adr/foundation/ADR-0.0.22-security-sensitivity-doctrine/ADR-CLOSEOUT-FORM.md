# ADR Closeout Form: ADR-0.0.22-security-sensitivity-doctrine

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [x] Gate 3 (Docs): Docs build passes
- [x] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.22-security-sensitivity-doctrine` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.22-01-schema-frontmatter-field](OBPI-0.0.22-01-schema-frontmatter-field.md) | Schema + frontmatter field for sensitivity axis | Completed |
| [OBPI-0.0.22-02-security-surface-registry](OBPI-0.0.22-02-security-surface-registry.md) | Security-surface registry data file | Completed |
| [OBPI-0.0.22-03-validate-sensitivity-scope](OBPI-0.0.22-03-validate-sensitivity-scope.md) | gz validate --sensitivity scope with --explain subform | Completed |
| [OBPI-0.0.22-04-requires-security-review-attestation](OBPI-0.0.22-04-requires-security-review-attestation.md) | _requires_security_review_attestation audit OR | Completed |
| [OBPI-0.0.22-05-gate5-walkthrough-arb-slot](OBPI-0.0.22-05-gate5-walkthrough-arb-slot.md) | Gate 5 walkthrough extension and ARB canonical command slot | Completed |
| [OBPI-0.0.22-06-rule-file-matrix-scorecard](OBPI-0.0.22-06-rule-file-matrix-scorecard.md) | Rule file plus AGENTS.md matrix plus advisory scorecard entry | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.22-01-schema-frontmatter-field | docstring | FOUND |
| OBPI-0.0.22-02-security-surface-registry | docstring | FOUND |
| OBPI-0.0.22-03-validate-sensitivity-scope | docstring | FOUND |
| OBPI-0.0.22-04-requires-security-review-attestation | docstring | FOUND |
| OBPI-0.0.22-05-gate5-walkthrough-arb-slot | docstring | FOUND |
| OBPI-0.0.22-06-rule-file-matrix-scorecard | docstring | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `attest completed — Foundation-kind heavy-lane doctrine landed: sensitivity third axis canonized across schema (OBPI-01), surface registry data/security_surfaces.json (OBPI-02), gz validate --sensitivity scope with --explain subform (OBPI-03; 587 briefs scanned, no escapes, registry healthy), _requires_security_review_attestation OR'd into _requires_human_obpi_attestation (OBPI-04), Gate 5 walkthrough + reserved arb-step-security- canonical slot (OBPI-05), and .gzkit/rules/security-sensitivity.md + AGENTS.md matrix + Mechanical scorecard entry (OBPI-06). All 6 OBPIs attested_completed. Receipts: lint arb-ruff-c0a477b263e24d70ba3a4c12a6eb0c9b; types arb-step-typecheck-59a09b5cb3184fb89afc736ecf2cb008; tests arb-step-unittest-ffa18f3cf496467881a57e3bcf19524b (3803 passed, 1 skipped); docs arb-step-mkdocs-9bb99769aa4a49aa851cf4b4d8736e5d. Out-of-scope BOM table rendering defect tracked GHI #362.`

**Attested by**: Jeffry
**Timestamp (UTC)**: 2026-04-29T10:59:55Z
