# ADR Closeout Form: ADR-0.0.56-closeout-defect-accounting-invariant

**Status**: Phase 1 — Pending Implementation

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
| Gate 1 | ADR exists | `docs/design/adr/foundation/ADR-0.0.56-closeout-defect-accounting-invariant/ADR-0.0.56-closeout-defect-accounting-invariant.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build passes | `uv run mkdocs build --strict` |
| Gate 5 | Human attests | `uv run gz closeout ADR-0.0.56-closeout-defect-accounting-invariant` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.0.56-01-closeout-defect-baseline-snapshot](obpis/OBPI-0.0.56-01-closeout-defect-baseline-snapshot.md) | Closeout defect-baseline snapshot — `gz closeout` embeds a `gz check --json` defect fingerprint set in a `closeout_defect_snapshot` ledger event | Draft |
| [OBPI-0.0.56-02-closeout-defect-accounting-reconcile-scope](obpis/OBPI-0.0.56-02-closeout-defect-accounting-reconcile-scope.md) | `gz validate --closeout-defect-accounting` reconcile scope, joined into `gz check` | Draft |
| [OBPI-0.0.56-03-routing-receipt-model-completion-gate](obpis/OBPI-0.0.56-03-routing-receipt-model-completion-gate.md) | `RoutingReceipt` model + fail-closed `gz closeout` completion-gate wiring | Draft |
| [OBPI-0.0.56-04-obpi-complete-defect-accounting](obpis/OBPI-0.0.56-04-obpi-complete-defect-accounting.md) | Extend the snapshot-reconcile mechanism to `gz obpi complete` | Draft |
| [OBPI-0.0.56-05-ghi-close-defect-accounting-backstop](obpis/OBPI-0.0.56-05-ghi-close-defect-accounting-backstop.md) | Extend to ghi-close via a PreToolUse hook backstop on `gh issue close` | Draft |
| [OBPI-0.0.56-06-prime-directive-scorecard-reclassification](obpis/OBPI-0.0.56-06-prime-directive-scorecard-reclassification.md) | Reclassify PRIME DIRECTIVE #5/#6 Judgment → Mechanical + runbook/manpage docs | Draft |

## Defense Brief

### Closing Arguments

*To be populated during closeout ceremony.*

### Product Proof

| OBPI | Proof Type | Status |
|------|-----------|--------|
| OBPI-0.0.56-01-closeout-defect-baseline-snapshot | governance_artifact | PENDING |
| OBPI-0.0.56-02-closeout-defect-accounting-reconcile-scope | governance_artifact | PENDING |
| OBPI-0.0.56-03-routing-receipt-model-completion-gate | governance_artifact | PENDING |
| OBPI-0.0.56-04-obpi-complete-defect-accounting | governance_artifact | PENDING |
| OBPI-0.0.56-05-ghi-close-defect-accounting-backstop | governance_artifact | PENDING |
| OBPI-0.0.56-06-prime-directive-scorecard-reclassification | governance_artifact | PENDING |

### Reviewer Assessment

*To be populated during closeout ceremony.*

## Human Attestation

### Verbatim Attestation

*To be recorded at closeout per ADR-0.0.36 universal OBPI attestation.*

**Attested by**: _g0_
**Timestamp (UTC)**: _Pending_
