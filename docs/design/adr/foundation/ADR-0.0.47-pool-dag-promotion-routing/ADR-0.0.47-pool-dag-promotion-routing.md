---
id: ADR-0.0.47-pool-dag-promotion-routing
status: Proposed
kind: foundation
semver: 0.0.47
lane: lite
parent: ADR-0.6.0-pool-promotion-protocol
date: 2026-05-16
promoted_from: ADR-pool.pool-dag-promotion-routing
---

# ADR-0.0.47-pool-dag-promotion-routing: Pool DAG Promotion Routing

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active driver:** `main-session` — see `.gzkit/personas/main-session.md`.

Agents working on this ADR lift implicit relationships from prose into a machine-readable DAG that validators, queries, and promotion guards can all consult. The craftsperson trait demands that the frontmatter schema, the graph builder, the cycle/missing-reference detector, and the `gz adr promote` guard share a single source of truth — divergence between them is how silent promotion-before-prerequisite bugs slip in. Narrative recall of dependencies is the named failure mode; the goal is to make the dependency graph queryable so it doesn't have to live in agent memory. Backfill from existing prose `## Dependencies` sections is reviewed, not auto-merged — operator judgment ratifies the lift before the new contract binds.

## Why foundation tier?

Without this ADR, pool ADRs lack dependency-aware promotion routing — promotions can land out-of-order against the pool DAG, breaking downstream pool entries that assumed an earlier promotion landed first.

This ADR authors a port: the pool-DAG promotion-routing contract `gz adr promote` and the pool-graph validator both bind to.

## Intent

Make the implicit dependency graph between pool ADRs explicit and queryable, enabling
agent-assisted promotion routing. Pool ADRs already declare relationships in prose
(`## Dependencies` sections) but this information isn't machine-readable. As the
active ADR queue clears and the workflow shifts from push (pre-queued backlog) to
pull (evaluate pool, promote best next item), the agent needs a queryable graph to
recommend which pool ADR to promote next based on satisfied prerequisites, project
priorities, and topological ordering.

**Current state:** pool relationships exist primarily in prose sections under
`docs/design/adr/pool/*.md`. Agents can read those sections, but no validator
can prove that prerequisites are satisfied, no command can list ready pool ADRs,
and no promotion command can warn when an item is being pulled ahead of a hard
dependency. The result is a planning graph that exists only in narrative recall.

**Target state:** pool ADR relationships become structured, validated
frontmatter. gzkit can build a small in-repository DAG, answer readiness
queries, expose unblock paths, and feed a recommendation surface without
auto-promoting anything. The graph stays advisory: it narrows the planning
surface and catches dependency mistakes, while the operator still decides what
enters active SemVer work.

## Decision

Promote `ADR-pool.pool-dag-promotion-routing` into active implementation and execute the following tracked scope:

1. Add structured relationship fields to pool ADR frontmatter so hard
   prerequisites, soft complements, advisory reverse dependencies, and tags are
   machine-readable.
2. Build a pool DAG from `docs/design/adr/pool/*.md` and ledger-backed ADR
   completion state.
3. Add query and recommendation surfaces that can list ready nodes, explain
   unblock paths, and route `gz next` style planning to pool promotion.
4. Bind promotion to the graph by warning or failing when a hard prerequisite is
   unsatisfied.

- **relationship-frontmatter-schema** — Add structured pool ADR frontmatter for `depends_on`, `complements`, `blocks`, and `tags`, with validation against known ADR IDs.
- **pool-graph-builder** — Build the in-repository pool DAG from pool ADR files and ledger-backed completion state, including missing-reference and cycle detection.
- **pool-graph-cli** — Implement `gz pool graph` with `--ready`, `--path`, `--tags`, `--dot`, and `--json` query modes.
- **promote-dependency-guard** — Extend `gz adr promote` to validate hard prerequisites, warn on topological disorder, and update dependent pool ADRs after promotion.
- **pool-backfill-migration** — Backfill existing pool ADR frontmatter from prose dependency sections and provide a reviewed migration path for the current pool.
- **next-pool-recommendation** — Implement `gz next --pool` recommendation logic over ready nodes, unblock potential, complement density, and current project tags.

## Rationale

1. ADR-0.6.0 supplies the act of promotion; it does not model the graph that
   makes promotion order defensible. This ADR supplies that missing graph layer.
2. Structured frontmatter is the smallest durable surface: it keeps pool
   relationships adjacent to the pool ADRs while allowing validators and
   commands to read them without scraping prose.
3. Ledger-backed satisfaction prevents Layer-3 status output from becoming
   source-of-truth. A dependency is satisfied because the source ADR is complete
   in ledger evidence, not because a rendered table says so.
4. The anti-pattern is "agent remembers the pool graph." Pool routing must be a
   query over explicit relationships, not a narrative reconstruction during
   each planning conversation.
5. Implementation should follow existing gzkit command and ledger surfaces
   instead of inventing a parallel graph store: `src/gzkit/commands/adr_promote.py`
   is the promotion boundary, `src/gzkit/commands/register.py` is the current
   ADR registration precedent, and `src/gzkit/ledger.py` remains the source for
   ledger-backed completion state.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Pool ADRs stay isolated from the active DAG — the pool-graph boundary this promotion-routing ADR depends on. | uv run gz validate --pool-adr-isolation | 0 |

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.47-01: **relationship-frontmatter-schema** — Add structured pool ADR frontmatter for `depends_on`, `complements`, `blocks`, and `tags`, with validation against known ADR IDs.
- [ ] OBPI-0.0.47-02: **pool-graph-builder** — Build the in-repository pool DAG from pool ADR files and ledger-backed completion state, including missing-reference and cycle detection.
- [ ] OBPI-0.0.47-03: **pool-graph-cli** — Implement `gz pool graph` with `--ready`, `--path`, `--tags`, `--dot`, and `--json` query modes.
- [ ] OBPI-0.0.47-04: **promote-dependency-guard** — Extend `gz adr promote` to validate hard prerequisites, warn on topological disorder, and update dependent pool ADRs after promotion.
- [ ] OBPI-0.0.47-05: **pool-backfill-migration** — Backfill existing pool ADR frontmatter from prose dependency sections and provide a reviewed migration path for the current pool.
- [ ] OBPI-0.0.47-06: **next-pool-recommendation** — Implement `gz next --pool` recommendation logic over ready nodes, unblock potential, complement density, and current project tags.

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

## Implementation Readiness Criteria

This ADR is promoted. Execution can begin when all are true:

1. ADR-0.0.46-pool-management has stabilized the pool metadata fields this
   graph consumes.
2. Frontmatter schema (`depends_on`, `complements`, `blocks`, `tags`) is accepted.
3. At least 10 existing pool ADRs are selected as backfill fixtures to
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

## Implementation Precedent

- `src/gzkit/commands/adr_promote.py` — existing pool-to-active promotion
  boundary that the dependency guard must wrap.
- `src/gzkit/commands/register.py` — current filesystem-to-ledger
  reconciliation path and status regeneration precedent.
- `src/gzkit/ledger.py` — artifact graph and lifecycle-state derivation
  contract used to decide whether a dependency is satisfied.

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

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.pool-dag-promotion-routing` on 2026-05-16; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

### A. Keep dependencies in prose only

Rejected. Prose can explain relationships, but it cannot be validated for
cycles, missing references, or satisfied prerequisites before promotion.

### B. Treat pool ranking as a flat priority list

Rejected. A flat list hides hard dependency order. It can say which work seems
important, but it cannot explain why an item is not yet promotable.

### C. Auto-promote ready pool ADRs

Rejected. Readiness is advisory. Promotion changes active governance state and
must remain an operator decision under ADR-0.6.0.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.47 | Pending | | | |
