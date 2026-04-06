# ADR-pool.pool-dag-promotion-routing

- **Status:** Pool
- **Lane:** Lite
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — pull-model pool management

## Intent

Make the implicit dependency graph between pool ADRs explicit and queryable, enabling
agent-assisted promotion routing. Pool ADRs already declare relationships in prose
(`## Dependencies` sections) but this information isn't machine-readable. As the
active ADR queue clears and the workflow shifts from push (pre-queued backlog) to
pull (evaluate pool, promote best next item), the agent needs a queryable graph to
recommend which pool ADR to promote next based on satisfied prerequisites, project
priorities, and topological ordering.

## Target Scope

### Machine-Readable Pool Frontmatter

Extend pool ADR frontmatter with structured relationship fields:

```yaml
---
id: ADR-pool.svfr-quick-adhoc
status: Pool
lane: heavy
depends_on:
  - ADR-0.12.0   # SVFR execution mode (satisfied)
  - ADR-0.13.0   # Pipeline runtime (satisfied)
complements:
  - ADR-pool.agent-execution-intelligence  # gz next routes to gz quick
  - ADR-pool.atomic-obpi-commits           # quick tasks produce atomic commits
blocks:
  - ADR-pool.wave-dependency-execution     # waves build on quick's SVFR patterns
tags:
  - velocity
  - svfr
  - operator-experience
---
```

- `depends_on`: Hard prerequisites — must be completed (or satisfied by existing work) before promotion makes sense. References either versioned ADRs (already done) or other pool ADRs (must promote first).
- `complements`: Soft relationships — value increases when both exist, but neither blocks the other.
- `blocks`: Reverse dependencies — this pool ADR should be promoted before these others (advisory, not enforced).
- `tags`: Thematic labels for filtering and grouping (e.g., `velocity`, `governance`, `multi-agent`, `operator-experience`).

### Graph Query Surface

`gz pool graph` builds and queries the pool DAG:

- `gz pool graph` — render the full DAG as a dependency tree (text or `--json`)
- `gz pool graph --ready` — list pool ADRs whose `depends_on` are all satisfied (promotion candidates)
- `gz pool graph --path ADR-pool.X` — show what promoting X would unblock
- `gz pool graph --tags velocity` — filter the graph by thematic tags
- `gz pool graph --dot` — output Graphviz DOT format for visualization

### Integration with `gz next --pool`

`gz next --pool` uses the DAG to recommend the best next promotion:

1. **Filter to ready nodes** — all `depends_on` satisfied
2. **Score by unblock potential** — how many other pool ADRs does this unblock?
3. **Score by complement density** — how many complementary ADRs are also ready?
4. **Weight by project priorities** — tags matching current project focus score higher
5. **Present recommendation** with rationale: "Promote X because it unblocks Y and Z, complements the recently completed W, and aligns with current velocity focus."

The recommendation is advisory — the human makes the promotion decision.

### Integration with `gz promote`

`gz promote ADR-pool.X` already handles pool-to-versioned promotion. Extend it to:

- Validate `depends_on` are satisfied before allowing promotion
- Warn if promoting out of topological order (promoting a node before its dependencies)
- After promotion, update the graph: mark the promoted ADR as satisfied in other pool ADRs' `depends_on` lists

### Backfill Existing Pool ADRs

One-time migration to add structured frontmatter to existing pool ADRs:

- Parse existing `## Dependencies` prose sections
- Generate `depends_on`, `complements`, `blocks` fields
- Human reviews and corrects the auto-generated relationships
- `gz pool graph --validate` checks for cycles, missing references, and stale dependencies

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No automatic promotion — the graph recommends, the human decides.
- No priority scoring beyond topological ordering and tag matching — no LLM-based
  "importance" ranking.
- No cross-repository pool graphs — this operates within a single project's pool.
- Does not replace `ADR-pool.execution-memory-graph` — that pool ADR is about runtime
  execution state. This is about pool-level planning state. Different layers.

## Dependencies

- **Depends on:** None — this is foundational infrastructure for pool management
- **Complements:** ADR-pool.agent-execution-intelligence CAP-22 (`gz next` decision
  table extends to pool routing)
- **Complements:** ADR-pool.pool-health-management (graph health is a dimension of
  pool health)
- **Enables:** The pull-model workflow — without a queryable graph, `gz next --pool`
  is just `gz status --pool` with opinions

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Frontmatter schema (`depends_on`, `complements`, `blocks`, `tags`) is accepted.
3. At least 10 existing pool ADRs are backfilled with structured frontmatter to
   validate the schema against real relationships.
4. `gz next --pool` recommendation algorithm is defined — scoring weights for
   unblock potential, complement density, and tag matching.
5. Cycle detection and validation logic is specified.

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) `/gsd-next` — auto-detects the
  next workflow step from state. gzkit extends this to pool-level promotion routing.
- Make/build system dependency graphs — topological sort with parallel-ready node
  identification.
- Package manager dependency resolution — SAT-solving over versioned constraints
  (simplified here to DAG traversal since pool ADRs don't have version ranges).

## Notes

- This is likely one of the first pool ADRs to promote under the new pull model —
  it's the infrastructure that makes the pull model work. Bootstrap problem:
  the first promotion is chosen without the tool this ADR provides.
- The graph should be lightweight. Pool ADRs are ~60 items. A full DAG traversal
  is trivial — no need for caching or incremental updates.
- Consider: `gz pool graph --stale` to identify pool ADRs whose dependencies
  have changed (e.g., a prerequisite ADR was abandoned or superseded).
- The `tags` field enables thematic promotion batches — "promote all velocity-tagged
  pool ADRs that are ready" — useful for focused sprints.
- Risk: over-specifying dependencies creates artificial promotion ordering. Keep
  `depends_on` for hard prerequisites only. Use `complements` for soft relationships.
