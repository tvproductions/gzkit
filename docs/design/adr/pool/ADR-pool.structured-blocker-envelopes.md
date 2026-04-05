---
id: ADR-pool.structured-blocker-envelopes
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.10.0-obpi-runtime-surface
inspired_by: 12-factor-agents
---

# ADR-pool.structured-blocker-envelopes: Structured Blocker Envelopes

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance tooling and operator reliability

---

## Intent

Standardize gzkit failure and blocker reporting as stable machine-readable
envelopes that still render to compact human-readable `BLOCKERS:` output.

---

## Target Scope

- Define a blocker envelope schema with fields such as:
  - `code`
  - `message`
  - `artifact`
  - `stage`
  - `retryable`
  - `next_actions`
- Preserve the current terse text rendering:
  - `BLOCKERS:`
  - one blocker per line
- Add JSON parity for blocker-heavy surfaces such as:
  - `gz obpi validate`
  - `gz obpi reconcile`
  - `gz closeout`
  - `gz git-sync`
  - future pipeline runtime commands
- Make blocker outputs compact enough to feed directly into the next agent turn
  or retry loop without carrying raw stack traces.
- Keep file/line context where relevant.

## Non-Goals

- No verbose exception dumping as the default UX.
- No removal of compact text mode.
- No requirement that every command expose identical fields on day one.

## Dependencies

- **Blocks on**: ADR-0.10.0-obpi-runtime-surface
- **Blocked by**: ADR-0.10.0-obpi-runtime-surface
- **Related**: ADR-pool.obpi-pipeline-runtime-surface, ADR-pool.spec-triangle-sync

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The blocker envelope schema is approved.
2. At least three existing blocker-producing surfaces are migrated.
3. Text and JSON rendering contracts are documented and tested.
4. Retry/next-action semantics are defined clearly enough for agent reuse.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Complements CAP-10** (analysis paralysis guard / stall detection). Spec proposes stall detection; this ADR defines the structured blocker format that stall detection would consume.

## Inspired By

[12-factor-agents](https://github.com/humanlayer/12-factor-agents), especially:

- Factor 9: Compact errors into the context window

## Notes

- gzkit already has strong `BLOCKERS:` conventions; this ADR formalizes them as
  reusable runtime objects instead of plain strings.
- This should improve both operator usability and agent retry behavior.
