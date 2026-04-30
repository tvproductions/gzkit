---
id: ADR-pool.artifact-graph-navigation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.artifact-graph-navigation: Artifact Graph Navigation

## Status

Pool

## Intent

Provide graph-shaped navigation over gzkit's existing artifact corpus (PRDs,
constitutions, ADRs, OBPI briefs, GHIs, ledger events, attestation receipts)
without introducing a probabilistic LLM-extracted layer that would violate
Architectural Boundary #6 ("do not let derived views silently become
source-of-truth") or the trust-doctrine T1/T2/T3 invariants.

Tabular views (`gz status`, `gz state --json`) start losing structural signal
as the artifact graph grows. The hypothesis is that at ~50+ active ADRs or
~200+ OBPIs, operators and agents would benefit from navigating relationships
as a graph rather than as a flattened list. Until that scale is reached, this
ADR is intentionally pooled — the surface is sufficient today.

The triggering survey was a question about adopting `safishamsi/graphify`
(see chat 2026-04-30). graphify's `INFERRED`/`AMBIGUOUS` edge classes and
parallel `graphify-out/` cache are a Layer-3-becomes-Layer-1 hazard under
gzkit doctrine; the *function* (graph-shaped navigation) is real, but the
*shape* (third-party LLM extraction) is wrong for gzkit. This ADR captures
the in-house alternative.

## Decision

Defer until operator workflow is demonstrably friction-bound on graph
navigation. When promoted, scope to two independently-shippable increments:

1. **`gz state --graph` extension.** Emit existing artifact relationships in
   GraphML / DOT / Cytoscape-JSON shapes. Every node and edge traces to
   Layer 1 (canon: ADR/OBPI frontmatter, brief content) or Layer 2 (ledger
   events). No `INFERRED` class — every relationship is `EXTRACTED` in
   graphify's vocabulary. Optional interactive HTML view as a derived Layer-3
   render that explicitly is *not* source-of-truth.

2. **MCP wrapper around the ledger.** A `gz mcp serve` command exposing
   read-only ledger queries (`query_artifact`, `get_lineage`, `events_since`,
   `gates_pending`) to MCP-capable clients. Backed directly by
   `.gzkit/ledger.jsonl` — no derived cache.

Both increments stay inside the existing `gz` CLI surface and the existing
control-surface generator (`gz agent sync control-surfaces`). Stdlib-First
posture: NetworkX-style adjacency dicts, GraphML/DOT emitters are stdlib-doable;
the MCP server is the only third-party surface and is already a likely
post-1.0 dependency for other reasons.

## Alternatives Considered

- **Adopt `safishamsi/graphify` directly.** Rejected: introduces probabilistic
  `INFERRED` edges (LLM-extracted relationships), a parallel `graphify-out/`
  Layer-3 state, third-party `graphifyy` + tree-sitter + faster-whisper +
  Leiden + NetworkX dep stack with no stdlib-First-compliant departure
  rationale, and `CLAUDE.md`/`AGENTS.md`/PreToolUse-hook edits that collide
  with `gz agent sync control-surfaces`. The "always-on graph report ahead of
  grep" mechanism is duplicative of gzkit's existing direction to consult
  `gz state` / `gz status` first.

- **Build only the MCP wrapper, skip `gz state --graph`.** Possible but loses
  the human-facing benefit. Operators reviewing an artifact corpus benefit
  from the same graph view agents query through MCP; building both shares the
  underlying graph representation.

- **Status quo.** `gz state --json` (with file-handoff parsing per
  `.gzkit/rules/cross-platform.md` § Windows-safe helper patterns) and
  `gz status` cover most queries today. This is the right answer until
  the scale threshold is crossed — hence this ADR pools rather than
  activates.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Promotion signal: artifact corpus crosses ~50 active ADRs or ~200 active
OBPIs, OR an operator workflow surfaces friction that tabular views cannot
resolve. Likely `kind: feature` (extends the public CLI surface) at
`semver: 0.y.z` once the post-1.0 line is open, `lane: heavy` (adds CLI
verbs and an MCP server contract).
