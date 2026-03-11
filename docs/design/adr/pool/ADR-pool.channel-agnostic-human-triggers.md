---
id: ADR-pool.channel-agnostic-human-triggers
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.pause-resume-handoff-runtime
inspired_by: 12-factor-agents
---

# ADR-pool.channel-agnostic-human-triggers: Channel Agnostic Human Trigger Events

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Long-horizon agent execution effectiveness

---

## Intent

Represent approvals, rejections, escalations, and unblock events as canonical
human-trigger records that are independent of the UI or transport channel used
to deliver them.

---

## Target Scope

- Define canonical trigger types for human-in-the-loop control, including:
  - approval
  - rejection
  - escalation
  - unblock / continue
- Capture channel metadata such as:
  - terminal
  - chat
  - webhook
  - future notification adapters
- Preserve ledger-first auditability for Heavy/Foundation human authority
  boundaries.
- Allow runtime surfaces to wait for or consume the same human trigger event
  regardless of originating channel.
- Align attestation, closeout, and approval semantics so the same acceptance
  decision does not need to be re-expressed per integration surface.

## Non-Goals

- No autonomous approval or synthetic human authority.
- No mandatory SaaS messaging integration.
- No weakening of current attestation rigor.

## Dependencies

- **Blocks on**: ADR-pool.pause-resume-handoff-runtime
- **Blocked by**: ADR-pool.pause-resume-handoff-runtime
- **Related**: ADR-pool.prime-context-hooks, ADR-pool.obpi-pipeline-runtime-surface

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Trigger event schema and lifecycle rules are approved.
2. At least one non-terminal channel is selected for initial support.
3. Audit and attestation semantics are shown to remain fail-closed.
4. Operator-facing request/await/acknowledge flows are documented.

## Inspired By

[12-factor-agents](https://github.com/humanlayer/12-factor-agents), especially:

- Factor 11: Trigger from anywhere
- Factor 5: Unify execution state and business state

## Notes

- gzkit already treats human attestation as the authority boundary; this ADR
  makes that boundary transport-independent without weakening it.
- The first implementation should likely focus on terminal plus one structured
  external channel, not every possible integration at once.
