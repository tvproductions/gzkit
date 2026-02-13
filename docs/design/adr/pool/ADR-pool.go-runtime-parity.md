---
id: ADR-pool.go-runtime-parity
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.0.2
---

# ADR-pool.go-runtime-parity: Go Runtime Parity for Cross-Platform CLI

## Status

Pool

## Date

2026-02-12

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Foundation runtime direction

---

## Intent

Adopt Go as the target runtime for the `gz` CLI to improve cross-platform distribution while preserving
GovZero behavior, governance invariants, and artifact semantics.

This is a foundation/runtime decision, not a product feature ADR.

---

## Target Scope

- Freeze language-agnostic contracts for CLI behavior, ledger events, and generated artifacts.
- Build Python-vs-Go conformance checks as migration gates.
- Execute phased runtime migration with no governance semantic drift.
- Maintain contributor ergonomics with an explicit `uv`-parity workflow mapping.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No immediate removal of Python runtime.
- No changes to GovZero gate semantics, lifecycle semantics, or attestation authority.

---

## Dependencies

- **Blocks on**: ADR-0.3.0 (canonical governance parity baseline)
- **Blocked by**: ADR-0.3.0

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Contract-freeze scope is accepted.
3. Conformance harness acceptance criteria are approved.

---

## Notes

- Source execution plan: `docs/proposals/PLAN-go-runtime-uv-parity-2026-02-12.md`
- Pool discipline: keep this ADR lightweight and backlog-oriented until promotion.
