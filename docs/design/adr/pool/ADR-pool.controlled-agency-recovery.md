---
id: ADR-pool.controlled-agency-recovery
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-pool.evaluation-infrastructure
---

# ADR-pool.controlled-agency-recovery

## Status

Proposed

## Date

2026-02-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Phase 9: Controlled Agency & Recovery

---

## Intent

Define explicit human-agent control boundaries and recovery policies so autonomy scales only after reliability evidence is established.

---

## Target Scope

- Add human-in-the-loop review surfaces for high-impact outputs and actions.
- Define explicit control handoff events and ownership transitions.
- Define error taxonomy and retry/escalation policy classes.
- Implement progressive agency thresholds (assistant -> supervised actor -> broader autonomy).

---

## Dependencies

- **Blocks on**: ADR-pool.evaluation-infrastructure
- **Blocked by**: ADR-pool.evaluation-infrastructure

---

## Notes

- This phase converts governance doctrine into runtime interaction policy.
- Promotion criteria should include both eval quality and observed recovery behavior in production.
