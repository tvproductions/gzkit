---
id: ADR-pool.obpi-pipeline-enforcement-parity
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
promoted_to: ADR-0.12.0-obpi-pipeline-enforcement-parity
---

# ADR-pool.obpi-pipeline-enforcement-parity: AirlineOps-Style OBPI Pipeline Enforcement Parity
> Promoted to `ADR-0.12.0-obpi-pipeline-enforcement-parity` on 2026-03-12. This pool file is retained as historical intake context.


## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Canonical GovZero extraction completeness

---

## Intent

Adopt the same hook-enforced OBPI pipeline behaviors that make AirlineOps route
OBPI work through `gz-obpi-pipeline` reliably instead of relying on agent
memory or instruction-only compliance.

---

## Target Scope

- Import the AirlineOps hook chain that makes OBPI execution mechanically
  pipeline-first:
  - plan-exit audit gate
  - plan-exit pipeline router
  - write-time pipeline gate for `src/` and `tests/`
  - pre-commit / pre-push pipeline completion reminder
- Mirror the same receipt and active-marker behavior needed to bridge plan mode
  into pipeline execution.
- Register those hooks in gzkit Claude settings so they actually run rather than
  remaining documentation-only.
- Align the hook ordering with AirlineOps so pipeline gating fires before other
  write-time governance hooks.
- Preserve gzkit-native command names and file layout while matching AirlineOps
  enforcement semantics exactly.

## Non-Goals

- No partial “reminder only” substitute for write-time gating.
- No weakening of the existing `gz-obpi-pipeline` mandate into advisory text.
- No direct product-domain mirroring from AirlineOps beyond governance hook
  behavior.
- No standalone hook import without the settings registration that makes it
  effective.

## Dependencies

- **Blocks on**: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
- **Blocked by**: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
- **Related**: ADR-pool.prime-context-hooks, ADR-pool.execution-memory-graph

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The canonical AirlineOps enforcement chain is inventoried path-by-path and
   mapped to gzkit-native equivalents.
2. gzkit hook registration surfaces are ready to enforce the pipeline mandate
   automatically.
3. The imported behavior is specified as exact parity, not a looser local
   reinterpretation.

## Notes

- This intake exists because gzkit currently has the `gz-obpi-pipeline` skill
  and written mandate, but not the AirlineOps hook chain that forces agents
  onto that path.
- The parity target is concrete:
  - `.claude/hooks/plan-audit-gate.py`
  - `.claude/hooks/pipeline-router.py`
  - `.claude/hooks/pipeline-gate.py`
  - `.claude/hooks/pipeline-completion-reminder.py`
  - `.claude/settings.local.json` hook registration and ordering
- The defect this ADR tracks is procedural drift caused by advisory-only
  governance where AirlineOps already proved a reliable mechanical path.
