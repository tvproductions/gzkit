---
id: ADR-pool.obpi-runtime-surface
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.7.0-obpi-first-operations
---

# ADR-pool.obpi-runtime-surface: OBPI Runtime Surfaces

## Status

Proposed

## Date

2026-02-17

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance parity and operator ergonomics

---

## Intent

Add first-class OBPI runtime surfaces so operators can execute, verify, and reconcile completion directly at OBPI scope rather than through ADR-only commands.

---

## Target Scope

- Add OBPI-oriented CLI surfaces (status/list/reconcile workflows at OBPI granularity).
- Add OBPI-native ledger events and state derivation semantics.
- Provide compatibility mapping from current ADR-focused flows.
- Ensure Gate 2/Gate 3 evidence can be attached to OBPI progress checkpoints.
- Define drift detection and audit outputs keyed by OBPI identifiers.

---

## Non-Goals

- No deprecation of ADR lifecycle state machine.
- No weakening of human attestation requirements.
- No pool OBPIs before this entry is promoted.

---

## Dependencies

- **Blocks on**: ADR-0.7.0-obpi-first-operations
- **Blocked by**: ADR-0.7.0-obpi-first-operations

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. OBPI-first doctrine ADR is accepted for implementation.
2. CLI contract and ledger compatibility plan is approved.
3. Migration plan exists for current `gz adr ...` operator flows.

---

## Notes

- AirlineOps OBPI completion anchoring and reconciliation behavior should be treated as canonical reference patterns.
