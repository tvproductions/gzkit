---
id: ADR-0.7.0-obpi-first-operations
status: Proposed
semver: 0.7.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-02-21
promoted_from: ADR-pool.obpi-first-operations
---

# ADR-0.7.0-obpi-first-operations: OBPI-First Operations

## Intent

Align gzkit's OBPI lifecycle handling with AirlineOps so OBPI completion is enforced as the atomic unit of execution, evidence, and human authority.

Current gaps are runtime enforcement gaps: OBPI completion can still be represented without an explicit validator/recorder lifecycle, and ledger consumption is not yet fully OBPI-proof-first.

## Decision

Adopt an OBPI-first runtime lifecycle contract with four implementation tracks:

1. Pre-completion validator gate for OBPI `Completed` transitions.
2. Post-completion recorder flow with optional git anchor capture.
3. Ledger-first OBPI audit consumption for closeout readiness.
4. OBPI drift/status reconciliation surfaces in runtime reporting.

Execution is decomposed into OBPI briefs under this ADR package.

## Consequences

### Positive

- OBPI completion is treated as a governed transition, not a documentation-only edit.
- Human attestation authority is enforced where required (Heavy/Foundation inheritance).
- Status and audit surfaces become evidence-driven at OBPI scope.

### Negative

- Additional runtime and documentation surfaces increase implementation complexity.
- Existing operator habits that are ADR-only or gate-centric require migration.

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] Implement OBPI completion validator gate parity (`OBPI-0.7.0-01`)
- [ ] Implement OBPI completion recorder + anchor parity (`OBPI-0.7.0-02`)
- [ ] Move audit readiness to ledger-first OBPI consumption (`OBPI-0.7.0-03`)
- [ ] Add OBPI drift/status reconciliation reporting (`OBPI-0.7.0-04`)

## OBPIs

1. [`OBPI-0.7.0-01-obpi-completion-validator-gate`](obpis/OBPI-0.7.0-01-obpi-completion-validator-gate.md)
2. [`OBPI-0.7.0-02-obpi-completion-recorder-and-anchor`](obpis/OBPI-0.7.0-02-obpi-completion-recorder-and-anchor.md)
3. [`OBPI-0.7.0-03-ledger-first-obpi-audit-consumption`](obpis/OBPI-0.7.0-03-ledger-first-obpi-audit-consumption.md)
4. [`OBPI-0.7.0-04-obpi-drift-and-status-reconciliation`](obpis/OBPI-0.7.0-04-obpi-drift-and-status-reconciliation.md)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion seeded via `gz adr promote`, then scope aligned from AirlineOps parity study of:

- `AGENTS.md` OBPI Acceptance Protocol
- `.claude/hooks/obpi-completion-validator.py`
- `.claude/hooks/obpi-completion-recorder.py`
- `opsdev` ledger-first audit/reconciliation patterns

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`
- [ ] Runtime parity commands demonstrate OBPI-first completion semantics.

## Alternatives Considered

- Keep this work in pool until reprioritized.
- Continue ADR-only closeout semantics and defer OBPI runtime parity.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.7.0 | Pending | | | |
