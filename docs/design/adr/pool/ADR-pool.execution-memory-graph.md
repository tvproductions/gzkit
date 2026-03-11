---
id: ADR-pool.execution-memory-graph
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.storage-simplicity-profile
---

# ADR-pool.execution-memory-graph: Execution Memory Graph and Ready Queue

## Status

Proposed

## Date

2026-03-01

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Long-horizon agent execution effectiveness

---

## Intent

Add a first-class execution memory graph for agent work so planning and
coordination are computed from machine-readable relationships instead of prose
task lists.

---

## Target Scope

- Define runtime work nodes for executable units beneath ADR/OBPI scope.
- Support typed relationships with explicit semantics:
  - `blocks`
  - `discovered-from`
  - `validates`
  - `related`
- Define cross-layer graph joins for governance and proof:
  - `ADR -> OBPI -> REQ`
  - `REQ -> test evidence (@covers target)`
- Add deterministic queue surfaces for operators and agents:
  - `ready` (no open blockers)
  - `blocked` (with blocking reason)
- Add claim/in-progress transition semantics to reduce agent collision.
- Ensure `gz state` and `gz status` can consume this graph without weakening
  existing governance lifecycle semantics.

---

## Non-Goals

- No replacement of ADR/OBPI artifacts as governance authority.
- No MCP-first implementation requirement.
- No mandatory external database dependency for initial rollout.

---

## Dependencies

- **Blocks on**: ADR-pool.storage-simplicity-profile, ADR-0.7.0-obpi-first-operations
- **Blocked by**: ADR-pool.storage-simplicity-profile, ADR-0.7.0-obpi-first-operations

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Runtime node/edge schema and CLI contract are approved.
2. Ledger event strategy for runtime state transitions is accepted.
3. Evaluation cases for ready/blocked determinism are defined.
4. Queue semantics define how missing REQ proof affects readiness.

---

## Notes

- This ADR operationalizes the "specification engineering" and "evaluation design"
  discipline in the Nate B. Jones readiness framing.
- BEADS informs dependency/ready queue behavior.
- Plumb informs requirement-proof edges that participate in readiness decisions.
- It also aligns with [12-factor-agents](https://github.com/humanlayer/12-factor-agents),
  especially Factor 5 (unify execution state and business state) and Factor 12
  (make your agent a stateless reducer).
