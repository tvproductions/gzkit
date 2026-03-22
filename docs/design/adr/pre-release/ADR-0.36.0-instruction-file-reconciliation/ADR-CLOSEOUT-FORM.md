# ADR Closeout Form: ADR-0.36.0-instruction-file-reconciliation

**Status**: Not Started

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass (`uv run gz test`)
- [ ] Gate 3 (Docs): Docs build passes (`uv run mkdocs build --strict`)
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 5 (Attestation) | Human sign-off | Closeout ceremony |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| OBPI-0.36.0-01 | Reconcile `cli.instructions.md` vs `cli.md` | Pending |
| OBPI-0.36.0-02 | Reconcile `tests.instructions.md` vs `tests.md` | Pending |
| OBPI-0.36.0-03 | Reconcile `cross-platform.instructions.md` vs `cross-platform.md` | Pending |
| OBPI-0.36.0-04 | Reconcile `models.instructions.md` vs `models.md` | Pending |
| OBPI-0.36.0-05 | Reconcile `pythonic.instructions.md` vs `pythonic.md` | Pending |
| OBPI-0.36.0-06 | Reconcile `gate5_runbook_code_covenant.instructions.md` vs `gate5-runbook-code-covenant.md` | Pending |
| OBPI-0.36.0-07 | Reconcile `adr_audit.instructions.md` vs `adr-audit.md` | Pending |
| OBPI-0.36.0-08 | Reconcile `arb.instructions.md` vs `arb.md` | Pending |
| OBPI-0.36.0-09 | Reconcile `chores.instructions.md` vs `chores.md` | Pending |
| OBPI-0.36.0-10 | Reconcile `gh_cli.instructions.md` vs `gh-cli.md` | Pending |
| OBPI-0.36.0-11 | Evaluate `sql_hygiene.instructions.md` for generic patterns | Pending |
| OBPI-0.36.0-12 | Evaluate `warehouse.instructions.md` for generic patterns | Pending |
| OBPI-0.36.0-13 | Evaluate `calendars.instructions.md` for generic patterns | Pending |

## Attestation

**Human Approver:** ___________________________

**Date:** ___________________________

**Decision:** Accept | Request Changes
