---
id: ADR-pool.ontology-source-unit-node-type
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.ontology-source-unit-node-type: Ontology source-unit node type — image source→REQ edges in the graph

## Status

Pool

## Intent

The gzkit ontology's source domain (ADR-0.32.0, OBPI-07) extracts `@covers`/`@surface`
anchors in `src/**` as first-class source→REQ edges (REQ-0.32.0-07-01), each carrying a
CODE-origin vertex. Those edges are built and queryable via `source_anchors.json`, but
they **cannot enter the sonar graph** (`project_all`, GHI #672, commit `0f9aa6be`)
because the closed `ObjectType` enum (`src/gzkit/ontology/model.py`) has **no source-unit
member** — an edge's source endpoint is a file path with no materializable node, so
`_add_grounded_edges` drops it. Consequence: `gz ontology trace <REQ>` cannot show a
REQ's covering source and `reach` cannot traverse REQ→source, leaving the "one graph,
queryable" intent (ADR-0.32.0 § Decision) unrealized on the source→code axis. **Moot on
gzkit itself** (0 `src/**` anchors — gzkit anchors on `tests/**`) but a **real gap for
adopter codebases** that anchor in product source.

## Decision

_Proposed; to be ratified at promotion._ Add `ObjectType.SOURCE_UNIT` as an
`ownership:product` × `plane:product` type, seat it in `OBJECT_TYPE_REGISTRY` (satisfying
the REQ-0.32.0-01-04 totality test) and confirm BI#4 Harness-Purity (source units are
product objects, never harness). Materialize a `SOURCE_UNIT` node per distinct source
path referenced by a source→REQ anchor edge so `project_all`'s `_add_grounded_edges`
admits the edge (both endpoints materialized). This is **deliberately a schema/model
change to the frozen OBPI-01 surface** — hence pool/heavy, not a direct-fix: it touches
the closed enum, the registry-totality test, and purity semantics (contrast GHI #672's
no-schema-change composition, which is why this was severed from it).

## Alternatives Considered

- **Keep source→REQ edges index-only (`source_anchors.json`), never graph-imaged** — the
  status quo after GHI #672. Rejected as the promotion target: leaves the "one graph"
  intent unrealized for the source axis. Accepted as the *interim* state precisely because
  imaging requires this schema change.
- **Model source units as a `Doc` subtype** instead of a new `ObjectType` — rejected: a
  source file is not documentation; conflating it with `Doc` corrupts ownership/plane
  semantics and entangles it with the OKF-absorption-open invariant (BI#5) that governs
  `Doc.subtype`.
- **A generic "external/opaque" node type for any unmaterializable endpoint** — rejected:
  an untyped catch-all reintroduces the untyped-dict fragmentation ADR-0.32.0 exists to
  kill; every node must carry a real `ObjectType` with ownership/plane.

## Notes

Follow-on to ADR-0.32.0 (Completed), surfaced during GHI #672 closure (commit
`0f9aa6be`). Discharges REQ-0.32.0-07-01's declared "first-class source→REQ edges" at the
graph layer. Promotion routing: given the frozen-model + purity + registry-totality
surface, promote as a **feature ADR with OBPI ceremony**, not a direct-fix.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
