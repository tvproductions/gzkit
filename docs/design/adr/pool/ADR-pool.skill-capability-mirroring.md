---
id: ADR-pool.skill-capability-mirroring
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.obpi-first-operations
---

# ADR-pool.skill-capability-mirroring: Skill Capability Mirroring

## Status

Proposed

## Date

2026-02-17

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance parity and operator execution reliability

---

## Intent

Mirror gz command capabilities with skills so operators and agents can use skill-first workflows without command-surface blind spots.

---

## Target Scope

- Define and maintain skill coverage for core gz command surfaces.
- Align command manpages, runbook guidance, and skill triggers for the same behavior.
- Keep canonical skill catalog and Claude mirror synchronized after capability changes.
- Add parity checks so missing skill coverage is visible during governance audits.

---

## Non-Goals

- No change to gate semantics or attestation authority.
- No retirement of existing specialized ADR/OBPI skills.
- No pool OBPIs before promotion.

---

## Dependencies

- **Blocks on**: ADR-pool.obpi-first-operations
- **Blocked by**: ADR-pool.obpi-first-operations

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Required gz command surfaces have explicit skill coverage.
2. Control-surface sync keeps AGENTS and CLAUDE skill catalogs aligned.
3. Human confirms the coverage set and trigger quality are sufficient for daily operation.

---

## Notes

- Prefer additive command-surface skills, while retaining deeper domain skills for complex workflows.
