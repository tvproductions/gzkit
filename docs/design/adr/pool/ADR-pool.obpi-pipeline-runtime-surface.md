---
id: ADR-pool.obpi-pipeline-runtime-surface
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
inspired_by: 12-factor-agents
---

# ADR-pool.obpi-pipeline-runtime-surface: OBPI Pipeline Runtime Surface

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Long-horizon agent execution effectiveness

---

## Intent

Elevate `gz-obpi-pipeline` from a skill-only workflow into a first-class gzkit
runtime surface so OBPI execution has one canonical command contract for
launch, stage progression, resume, abort, and sync.

---

## Target Scope

- Introduce a runtime command contract such as:
  - `gz obpi pipeline <obpi>`
  - `gz obpi pipeline <obpi> --from=verify`
  - `gz obpi pipeline <obpi> --from=ceremony`
- Persist pipeline stage state in a repository-local, machine-readable form.
- Expose structured stage outputs for:
  - current stage
  - blockers
  - required human action
  - next command or resume point
- Keep Stage 4 human attestation as an explicit authority boundary for Heavy and
  Foundation work.
- Make skills, hooks, and future agent control surfaces call into the same
  runtime engine instead of re-implementing stage logic in prose.

## Non-Goals

- No weakening of Heavy/Foundation human attestation.
- No mandatory external orchestrator or queue service.
- No replacement of ADR/OBPI artifacts as governance authority.

## Dependencies

- **Blocks on**: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
- **Blocked by**: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
- **Related**: ADR-pool.obpi-pipeline-enforcement-parity, ADR-pool.pause-resume-handoff-runtime

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. A stable CLI contract for launch/resume/abort semantics is approved.
2. Repository-local stage persistence and cleanup rules are defined.
3. Human-gate behavior is specified for Heavy/Foundation stages.
4. Skill text and hook adapters are reduced to thin wrappers over the runtime
   surface.

## Inspired By

[12-factor-agents](https://github.com/humanlayer/12-factor-agents), especially:

- Factor 6: Launch/Pause/Resume with simple APIs
- Factor 8: Own your control flow

## Notes

- gzkit already has the stage model in `.gzkit/skills/gz-obpi-pipeline/SKILL.md`;
  this ADR turns that model into a command contract instead of an instruction
  contract.
- This is complementary to AirlineOps-style hook enforcement parity:
  enforcement decides *when* the pipeline must run; this ADR defines *what*
  runtime actually executes.
