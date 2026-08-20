# ADR Closeout Form: ADR-0.0.20-agent-rule-placement-invariant

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [x] All checklist items in ADR are complete
- [x] All OBPIs have passing acceptance criteria
- [x] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.20-agent-rule-placement-invariant/ADR-0.0.20-agent-rule-placement-invariant.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.20-agent-rule-placement-invariant` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.20-01-validator-and-allowlist](OBPI-0.0.20-01-validator-and-allowlist.md) | Validator and Allow-list Foundation | Completed |
| [OBPI-0.0.20-02-fold-agent-contract](OBPI-0.0.20-02-fold-agent-contract.md) | Fold agent-contract.md into AGENTS.md / CLAUDE.md / docs/governance/ | Completed |
| [OBPI-0.0.20-03-fold-attestation-enrichment](OBPI-0.0.20-03-fold-attestation-enrichment.md) | Fold attestation-enrichment.md into AGENTS.md / docs/governance/arb-middleware.md | Completed |
| [OBPI-0.0.20-04-fold-defect-fix-routing](OBPI-0.0.20-04-fold-defect-fix-routing.md) | Fold defect-fix-routing.md into AGENTS.md / docs/governance/defect-fix-routing.md | Completed |
| [OBPI-0.0.20-05-closeout-and-downstream](OBPI-0.0.20-05-closeout-and-downstream.md) | Closeout Sweep + Downstream GHIs + Foundation Walkthrough | Completed |

## Defense Brief

### Closing Arguments

*No closing arguments found.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.20-01-validator-and-allowlist | command_doc | FOUND |
| OBPI-0.0.20-02-fold-agent-contract | governance_artifact | FOUND |
| OBPI-0.0.20-03-fold-attestation-enrichment | docstring | FOUND |
| OBPI-0.0.20-04-fold-defect-fix-routing | governance_artifact | FOUND |
| OBPI-0.0.20-05-closeout-and-downstream | closeout_artifact | FOUND |

### Reviewer Assessment

*No reviewer assessments found.*


## Human Attestation

### Verbatim Attestation

- `completed`

**Attested by**: g0
**Timestamp (UTC)**: 2026-04-24T01:10:52Z
