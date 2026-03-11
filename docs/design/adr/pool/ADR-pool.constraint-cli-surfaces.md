---
id: ADR-pool.constraint-cli-surfaces
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.constraint-library
---

# ADR-pool.constraint-cli-surfaces: CLI Surfaces for Constraint Capture and Reuse

## Status

Pool

## Date

2026-03-10

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Expose the constraint-library workflow directly in `gz` so rejection capture and
constraint reuse happen where work already happens. The initial delivery should
be CLI-only: capture a rejection, store the articulated constraint, query the
library, and reuse relevant constraints without requiring a separate UI or MCP
runtime.

---

## Target Scope

- Add CLI-native constraint surfaces such as:
  - `gz constraint capture`
  - `gz constraint list`
  - `gz constraint show`
  - `gz constraint search`
  - `gz constraint apply` or equivalent preflight/review helper
- Support both human-readable and `--json` output for query-first agent loops.
- Preserve provenance in command output so operators can see who rejected what,
  why it was rejected, and which constraint was derived.
- Support scoped filtering by team, project, workflow, command, or domain.
- Keep capture friction low enough that rejection logging can happen inline
  during normal review or agent-assisted work.

## Non-Goals

- No web UI, dashboard, or separate pane-of-glass workflow.
- No MCP server requirement in the first phase.
- No autonomous constraint synthesis without explicit human rejection input.
- No fail-closed gate enforcement until CLI semantics and constraint quality
  prove stable.

## Dependencies

- **Blocks on**: ADR-pool.constraint-library
- **Blocked by**: ADR-pool.constraint-library
- **Related**: ADR-pool.command-aliases, ADR-pool.per-command-persona-context, ADR-pool.focused-context-loader

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. CLI grammar for capture/query/apply flows is accepted.
2. One inline rejection-to-constraint workflow is proven simpler than a
   context-switching alternative.
3. JSON output shape is stable enough for agent and automation consumption.

## Notes

- This ADR intentionally stays CLI-only for the first implementation wave.
- Query-first surfaces matter more than rich rendering; the value is fast reuse
  of stored judgment.
- Likely command pattern: capture first, reuse during planning/review, and only
  later add stronger enforcement hooks.
