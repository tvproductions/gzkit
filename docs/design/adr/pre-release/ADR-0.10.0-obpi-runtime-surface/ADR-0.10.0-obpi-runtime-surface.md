---
id: ADR-0.10.0-obpi-runtime-surface
status: Validated
semver: 0.10.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-09
promoted_from: ADR-pool.obpi-runtime-surface
---

# ADR-0.10.0-obpi-runtime-surface: OBPI Runtime Surfaces

## Intent

gzkit already has OBPI receipts, audit semantics, and ledger-first status behavior,
but operators still lack first-class OBPI runtime surfaces for querying,
reconciling, and proving OBPI progress directly. AirlineOps parity work now
depends on those missing surfaces: deferred pipeline and lifecycle hooks assume a
clear OBPI-native runtime contract rather than ADR-only closeout flows and
manual brief inspection.

## Decision

Implement OBPI runtime surfaces as a three-unit pre-release track:

1. **Runtime Contract**: Define the OBPI state model, derived-status semantics,
   REQ-proof contract, and compatibility boundaries with existing ADR-first
   lifecycle behavior (`OBPI-0.10.0-01`).
2. **Query + Reconcile Surfaces**: Add OBPI-native operator commands for
   listing, status inspection, and deterministic reconciliation at OBPI
   granularity while preserving existing receipt and validation flows
   (`OBPI-0.10.0-02`).
3. **Proof + Lifecycle Integration**: Connect OBPI runtime state to REQ proof,
   closeout guidance, and operator migration so deferred AirlineOps pipeline
   parity work has a stable gzkit-native foundation (`OBPI-0.10.0-03`).

This ADR remains ledger-first and repository-local. It does not introduce a
separate planner database or weaken human attestation rules. Execution-memory
graph integration remains a declared dependency and should be consumed through
compatibility seams rather than replaced with ad hoc runtime state.

## Consequences

### Positive

- OBPI lifecycle work gets a single governing ADR instead of being split across
  status, receipt, and parity tranches.
- Deferred AirlineOps pipeline parity can target a concrete gzkit runtime
  surface instead of reusing ADR-only workflows.
- REQ-level proof and OBPI reconciliation can become deterministic operator
  surfaces rather than document-only ceremony steps.

### Negative

- Adds another heavy-lane ADR with multiple CLI and lifecycle seams to keep
  coherent.
- Some target behavior depends on backlog prerequisites such as
  `ADR-pool.execution-memory-graph`, so sequencing discipline remains necessary.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [x] OBPI-0.10.0-01: Define the OBPI runtime contract and derived state model.
- [x] OBPI-0.10.0-02: Deliver OBPI-native query and reconcile command surfaces.
- [x] OBPI-0.10.0-03: Integrate OBPI proof state with lifecycle guidance and parity-dependent operator flows.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion seeded via `gz adr promote`; interview transcript not captured.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [x] Tests: `tests/`
- [x] Docs: `docs/`
- [x] Runtime command docs: `docs/user/commands/`
- [x] OBPI concepts/runtime semantics: `docs/user/concepts/`, `docs/governance/GovZero/`
- [x] Closeout form:
      `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-CLOSEOUT-FORM.md`
- [x] Audit artifacts:
      `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/audit/`

## Alternatives Considered

- Keep this work in pool until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.10.0 | Completed | Test User | 2026-03-10 | attest completed |
