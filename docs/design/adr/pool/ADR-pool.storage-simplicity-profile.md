---
id: ADR-pool.storage-simplicity-profile
status: archived
superseded_by: ADR-0.0.10
archived_date: 2026-03-29
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-0.0.2
---

# ADR-pool.storage-simplicity-profile: Storage Simplicity Profile for Agent Runtime

> **Archived.** Promoted to [ADR-0.0.10 — Storage Tiers and Simplicity Profile](../foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md).
> See Architecture Planning Memo Section 3.

## Status

Archived (superseded by ADR-0.0.10)

## Date

2026-03-01

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Runtime posture and operator ergonomics

---

## Intent

Define a storage-and-sync posture for new agent runtime surfaces that preserves
`gzkit` simplicity by default. Adopt only the minimum persistence complexity
needed to satisfy governance invariants, deterministic readiness, and multi-agent
safety.

---

## Target Scope

- Define storage tiers for runtime features:
  - Tier A: canonical docs + append-only ledger
  - Tier B: deterministic derived indexes/caches rebuilt from canonical sources
  - Tier C: external/stateful runtime backends only by explicit ADR authorization
- Define canonical identity surfaces that all tiers must preserve:
  - `ADR-*` (feature intent)
  - `OBPI-*` (delivery unit)
  - `REQ-*` (acceptance/proof unit)
- Define explicit escalation criteria for moving from Tier A/B to Tier C.
- Define sync boundaries for CLI + hooks workflows and local-first operation.
- Specify MCP posture for this track: optional integration, never a hard dependency.
- Require design notes for conflict, replay, and recovery behavior before storage expansion.

---

## Non-Goals

- No immediate adoption of Dolt/SQL storage for `gzkit`.
- No replacement of ledger as canonical proof record.
- No requirement that operators use MCP-enabled editors.

---

## Dependencies

- **Blocks on**: ADR-0.0.2-stdlib-cli-and-agent-sync
- **Blocked by**: ADR-0.0.2-stdlib-cli-and-agent-sync

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Storage tiering and escalation triggers are accepted in governance docs.
2. Conflict/recovery behavior is documented for CLI + hooks operation.
3. At least one pending runtime ADR references this profile as binding guidance.

---

## Notes

- This ADR intentionally captures selective learning: absorb useful execution
  patterns while avoiding unnecessary backend complexity.
- BEADS alignment: dependency/query ergonomics.
- Plumb alignment: spec-test-code reconciliation needs deterministic IDs and proof joins.
- Scope guard: storage choices must not weaken deterministic readiness/proof derivation.
