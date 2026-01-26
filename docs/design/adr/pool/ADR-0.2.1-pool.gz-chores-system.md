# ADR-0.2.1: pool.gz-chores-system

## Status

Proposed

## Date

2026-01-26

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Phase 2: Gates / Parity

---

## Intent

Introduce a gzkit-native chore system (registry + runner + logs) so maintenance work is first-class and portable
from AirlineOps without copying bespoke opsdev tooling.

---

## Target Scope

- Add a `gz chores` command group that can list, plan, run, and audit chores (minimal viable surface).
- Define a config-first chore registry with lanes, evidence commands, and acceptance checks.
- Add per-chore logs and plan templates under a gzkit-owned path.
- Produce migration guidance and seed a portable chore set.

---

## Non-Goals

- Port AirlineOps domain-specific chores (warehouse, SQL hygiene) until gzkit has equivalent surfaces.
- Implement heavy-lane Gate 3/4 enforcement beyond what the chore runner needs for evidence capture.

---

## Dependencies

- ADR-0.1.0 enforced-governance-foundation (ledger + doc layout)
- ADR-0.2.0 pool.gate-verification (recommended, not required)

---

## Checklist

1. Stand up a minimal gz chores system (registry + list/plan/run/audit).

---

## Proposed OBPI

- `OBPI-0.2.1-01-chores-system-core`

---

## References

- `docs/design/briefs/REPORT-airlineops-chores-migration.md`
