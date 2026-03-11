---
id: ADR-pool.pause-resume-handoff-runtime
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.obpi-pipeline-runtime-surface
inspired_by: 12-factor-agents
---

# ADR-pool.pause-resume-handoff-runtime: Pause Resume and Handoff Runtime

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Agent context engineering and session reliability

---

## Intent

Turn session handoff and resume from skill text into a first-class runtime
surface so agents can pause work, emit resumable state, and safely continue
later without relying on manual prose conventions alone.

---

## Target Scope

- Add runtime commands for handoff lifecycle, such as:
  - `gz handoff create`
  - `gz handoff resume`
  - `gz handoff status`
- Define a repository-local handoff schema that captures:
  - ADR/OBPI scope
  - branch
  - active pipeline stage
  - next steps
  - referenced artifacts
  - staleness metadata
- Add deterministic staleness checks based on:
  - commits since handoff
  - changed files since handoff
  - branch mismatch
- Make `gz-obpi-pipeline` consume this runtime surface instead of depending on a
  manual skill-only handoff workflow.
- Repair current handoff skill drift so referenced helpers, docs, and runtime
  surfaces agree.

## Non-Goals

- No cloud-only coordination requirement.
- No replacement of ledger proof with handoff state.
- No multi-agent scheduler or work-stealing system in this ADR.

## Dependencies

- **Blocks on**: ADR-pool.obpi-pipeline-runtime-surface
- **Blocked by**: ADR-pool.obpi-pipeline-runtime-surface
- **Related**: ADR-pool.prime-context-hooks, ADR-pool.execution-memory-graph

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Handoff schema and command surfaces are approved.
2. Staleness classification and resume safety rules are accepted.
3. The current `gz-session-handoff` skill/runtime drift is explicitly resolved.
4. OBPI pipeline integration points are defined.

## Inspired By

[12-factor-agents](https://github.com/humanlayer/12-factor-agents), especially:

- Factor 6: Launch/Pause/Resume with simple APIs

## Notes

- This ADR addresses a concrete gzkit defect: handoff exists conceptually, but
  not yet as a reliable runtime command path.
- The first implementation should stay repository-local and file-backed.
