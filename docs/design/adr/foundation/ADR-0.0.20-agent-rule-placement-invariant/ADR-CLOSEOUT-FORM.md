# ADR Closeout Form: ADR-0.0.20

**Status**: Phase 0 — Draft (pre-implementation)

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Foundation-kind closeout walkthrough executed (per ADR-0.0.18 § Foundation-kind rigor, applies across lanes)
- [ ] Three downstream-impact GHIs filed (ADR-0.36.0 WBS refresh, ADR-0.38.0 baseline note, ADR-0.0.19 reference refresh)
- [ ] `gz validate --unscoped-rules` exits 0 against final state
- [ ] `gz validate --all` exits 0 against final state
- [ ] Vendor mirrors regenerated cleanly via `gz agent sync control-surfaces`

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Quality (Validator) | `--unscoped-rules` exits 0 | `uv run gz validate --unscoped-rules` |
| Quality (Aggregate) | `--all` exits 0 | `uv run gz validate --all` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 5 | Human attests (foundation walkthrough) | `uv run gz closeout ADR-0.0.20` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| OBPI-0.0.20-01-validator-and-allowlist | Validator + allow-list foundation | Pending |
| OBPI-0.0.20-02-fold-agent-contract | Fold `agent-contract.md` into AGENTS.md + CLAUDE.md + docs/governance/ | Pending |
| OBPI-0.0.20-03-fold-attestation-enrichment | Fold `attestation-enrichment.md` into AGENTS.md + docs/governance/arb-middleware.md | Pending |
| OBPI-0.0.20-04-fold-defect-fix-routing | Fold `defect-fix-routing.md` into AGENTS.md + docs/governance/defect-fix-routing.md | Pending |
| OBPI-0.0.20-05-closeout-and-downstream | Closeout sweep + downstream GHIs + foundation walkthrough | Pending |

## Defense Brief

### Closing Arguments

*Populated at closeout.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.20-01-validator-and-allowlist | test_evidence + command_doc + scorecard_row | PENDING |
| OBPI-0.0.20-02-fold-agent-contract | agents_md_diff + sync_evidence + reference_sweep | PENDING |
| OBPI-0.0.20-03-fold-attestation-enrichment | agents_md_diff + governance_doc + python_docstring_sweep | PENDING |
| OBPI-0.0.20-04-fold-defect-fix-routing | agents_md_diff + governance_doc + reference_sweep | PENDING |
| OBPI-0.0.20-05-closeout-and-downstream | grep_clean + validator_clean + downstream_ghis + foundation_walkthrough | PENDING |

### Reviewer Assessment

*Populated at closeout.*
