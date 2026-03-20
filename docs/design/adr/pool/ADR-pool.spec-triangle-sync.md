---
id: ADR-pool.spec-triangle-sync
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.7.0-obpi-first-operations
promoted_to: ADR-0.20.0-spec-triangle-sync
---

# ADR-pool.spec-triangle-sync: Spec-Test-Code Triangle Sync
> Promoted to `ADR-0.20.0-spec-triangle-sync` on 2026-03-20. This pool file is retained as historical intake context.


## Status

Superseded

## Date

2026-03-05

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance tooling and operator reliability

---

## Intent

Introduce explicit runtime/process support for the spec-test-code triangle so implementation speed does not create silent drift between governance specs, tests, and behavior.

---

## Target Scope

- Define triangle-sync semantics for `spec -> tests -> code -> spec`.
- Capture implementation decisions as first-class governance artifacts.
- Add drift surfaces that detect:
  - spec requirements with no tests,
  - tests with no spec linkage,
  - code changes with no corresponding spec/test deltas.
- Provide lightweight command checkpoints suitable for fast AI-assisted loops.
- Keep deterministic checks as default; use LLM inference only where structured signals are absent.

---

## Non-Goals

- No replacement of ADR/OBPI governance authority.
- No mandatory heavy orchestration runtime.
- No hard requirement for one specific coding agent provider.

---

## Dependencies

- **Blocks on**: ADR-0.7.0-obpi-first-operations, ADR-pool.execution-memory-graph
- **Blocked by**: ADR-0.7.0-obpi-first-operations, ADR-pool.execution-memory-graph

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Triangle-sync object model (spec requirement, test linkage, decision record) is approved.
2. CLI contract for drift checks is accepted.
3. Rollout plan exists for gradual adoption (advisory -> required gates).

---

## Notes

- This captures the process direction discussed in Drew Breunig's "spec-driven triangle" framing.
- Initial tooling may ship as advisory checks before any gate becomes fail-closed.
- Plumb alignment (core): implementation feedback updates spec/tests, and reconciliation is a first-class loop.
- BEADS alignment (concrete):
  - Keep work as dependency-aware graph edges (similar to `bd dep`/ready-work semantics).
  - Keep machine-readable IDs for deterministic joins (`ADR/OBPI/REQ` targets in tests).
  - Keep query-first operator surfaces (`--json`, drift checks) for agent workflows.
- BEADS divergence (intentional):
  - We do **not** adopt Beads' Dolt-backed SQL store or sync-branch workflow in this ADR.
  - gzkit remains ledger-first (`.gzkit/ledger.jsonl`) per storage-simplicity constraints.
