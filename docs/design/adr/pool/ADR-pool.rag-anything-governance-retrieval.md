---
id: ADR-pool.rag-anything-governance-retrieval
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: rag-anything, lightrag
---

# ADR-pool.rag-anything-governance-retrieval: Graph-Based Retrieval Over the Governance Corpus

## Status

Pool

## Date

2026-04-14

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Long-horizon agent execution effectiveness

---

## Intent

Add a Layer 3 retrieval surface over the gzkit governance corpus (ADRs, OBPI
briefs, rules, skills, runbooks, ledger events, ARB receipts) using a
graph-based RAG architecture. Two candidate upstream designs should be
evaluated during promotion:

- **LightRAG** (EMNLP 2025) — text-only entity/relation graph with a
  dual-level retrieval scheme (low-level entity lookup + high-level theme
  traversal), plus an incremental update algorithm for dynamic corpora.
  Shipped as the `lightrag-hku` PyPI package under a `uv`-native workflow
  (drop-in to gzkit's existing toolchain). Storage backends include
  PostgreSQL, MongoDB, Neo4j, and OpenSearch; built-in citation support
  (2025.03), reranker (2025.08), document deletion with KG regeneration
  (2025.08), RAGAS evaluation + Langfuse tracing (2025.11), and offline
  deployment guide. Smaller surface area, faster to prototype.
- **RAG-Anything** (2025.06) — LightRAG's multimodal extension. Dual-graph
  construction (cross-modal + text entity graph with fusion) that
  generalizes LightRAG to tables, figures, and structured blocks. Larger
  surface area, warranted if structure-aware decomposition of ADR/OBPI
  tables and frontmatter proves to be the dominant quality lever.

Both are from the same HKU research lineage (HKUDS) and share a
graph-fusion + hybrid-retrieval core. RAG-Anything is explicitly
positioned as LightRAG's multimodal extension in the upstream project's
own release notes. The promotion decision is which extension gzkit
actually needs, not which paper to cite.

The goal in either case is to serve semantic and structural queries —
"which ADRs touch state doctrine", "show receipts citing E501 in the last
month", "pull the rule slices relevant to this OBPI's allowed paths" —
without degrading the deterministic L1 canon / L2 ledger pathways.

This is the retrieval counterpart to `ADR-pool.execution-memory-graph`:
that ADR gives gzkit a BEADS-shaped *structured* dependency graph;
this ADR gives gzkit an *unstructured* retrieval index over the surrounding
documentary corpus. The two are orthogonal and both are needed.

---

## Target Scope

- New CLI surface (provisional): `gz retrieve <query>` returning ranked
  artifact references (ADR, OBPI, rule, skill, receipt, ledger event) with
  short excerpts and source citations.
- Bake-off between LightRAG and RAG-Anything on a seeded governance-corpus
  eval set before the CLI contract is locked, so the promotion decision
  is grounded in measured recall/precision rather than paper selection.
  LightRAG ships with RAGAS integration, which gives the bake-off a
  ready-made eval harness without gzkit owning the scoring code.
- Exploit LightRAG's built-in **citation functionality** (2025.03) to
  satisfy the Layer 3 "must carry source references" requirement — every
  retrieval result traces back to the specific artifact + chunk that
  produced it, which is exactly what state doctrine demands for a
  derived view.
- Exploit LightRAG's **document deletion with automatic KG regeneration**
  (2025.08) so that ADR supersession, OBPI archival, and ledger compaction
  do not leave stale entities in the retrieval graph.
- Structure-aware decomposition that preserves markdown tables, frontmatter
  blocks, and code fences as first-class retrieval units (not chunked away).
  This is the specific capability RAG-Anything adds over LightRAG; whether
  it justifies the extra surface is the bake-off's first question.
- Cross-modal entity graph linking ADR entities to ledger events to receipts
  to test files via fusion, providing a candidate replacement for the manual
  `@covers` decorator scan in `gz-adr-autolink`.
- Modality-aware query routing: frontmatter/table queries hit the structural
  graph first; prose queries hit the text entity graph first; hybrid queries
  traverse both.
- Integration with focused context loading so an agent session can request
  "rules relevant to OBPI-X.Y.Z-NN's allowed paths" and receive only the
  pertinent slices instead of the full `.claude/rules/` glob.
- Fail-closed Layer 3 labeling on every output: retrieval results must carry
  a `layer: 3 (derived, non-authoritative)` marker so downstream tooling
  cannot mistake them for canon.

---

## Non-Goals

- No replacement of `gz state` or `gz status` as the authoritative readout of
  L1/L2 facts. RAG output is advisory.
- No use of retrieval results as Gate evidence. Gate evidence must trace to
  L1 (canon) or L2 (ledger), per `docs/governance/state-doctrine.md`.
- No use of retrieval results in completion attestation or receipt
  generation. ARB receipts remain the only faithful QA record.
- No external vector-DB dependency for initial rollout; prefer a local
  embedding store that can be rebuilt deterministically from L1/L2.
- No automatic ingestion of content outside the repo (no web crawl, no
  external docs).

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**:
  - `ADR-pool.focused-context-loader` — the simpler, rules-aware precursor;
    this ADR generalizes focused loading to the full corpus
  - `ADR-pool.execution-memory-graph` — the structured-graph counterpart
  - `ADR-pool.progressive-context-disclosure` — shared context-efficiency intent

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Layer 3 boundary enforcement is designed — retrieval outputs carry
   explicit non-authoritative markers and cannot be cited as Gate evidence
   by any `gz` subcommand.
2. Rebuild determinism is accepted — the index is reproducible from
   `.gzkit/ledger.jsonl` + canonical artifacts with no hidden state.
3. CLI contract for `gz retrieve` (or equivalent surface) is approved
   against `.gzkit/rules/cli.md` (new subcommand triggers Heavy lane).
4. Evaluation cases for retrieval quality are defined — at minimum
   precision/recall on a seeded set of governance-corpus questions.
5. LightRAG vs RAG-Anything bake-off is complete on the seeded eval set,
   and the chosen upstream is justified by measured quality delta rather
   than architectural preference.
6. A decision is made on whether retrieval augments or replaces the
   `gz-adr-autolink` `@covers` scan, and the transition is staged.

---

## Architectural Fit

Per `CLAUDE.md` (Architecture Planning Memo Section 12):

- **Boundary #6** (derived views must not silently become source-of-truth)
  is the dominant risk. A retrieval index is Layer 3 by construction and
  must be enforced as such.
- **Boundary #3** (lock state doctrine before building graph engines) is
  satisfied — this ADR proposes a *retrieval* graph over artifacts, not a
  state graph. It consumes L1/L2, does not author them.
- **Boundary #1** (no post-1.0 pool ADRs promoted into active work without
  foundation stability) applies — this ADR stays in pool until state
  doctrine and the L1/L2 read paths are stable enough to serve as the
  rebuild source.

---

## Inspired By

Two candidate upstream designs, both from the HKUDS research lineage:

- [**LightRAG: Simple and Fast Retrieval-Augmented Generation**](https://arxiv.org/abs/2410.05779)
  (EMNLP 2025) — [GitHub](https://github.com/HKUDS/LightRAG),
  [`lightrag-hku` on PyPI](https://pypi.org/project/lightrag-hku/).
  Graph-based RAG combining entity/relation extraction with a dual-level
  retrieval scheme (low-level entity lookup + high-level theme traversal)
  and an incremental update algorithm for dynamic corpora. Integration
  surface directly relevant to gzkit:
    - `uv`-native packaging — `uv tool install "lightrag-hku[api]"` is
      the upstream-recommended install path, matching gzkit's existing
      toolchain discipline
    - Storage backends: PostgreSQL, MongoDB, Neo4j, OpenSearch (all-in-one
      mode available for each)
    - Built-in citation functionality (2025.03) → satisfies Layer 3
      source-tracing requirement
    - Reranker support (2025.08) → default for mixed queries
    - Document deletion with automatic KG regeneration (2025.08) →
      handles ADR supersession / OBPI archival cleanly
    - RAGAS evaluation + Langfuse tracing (2025.11) → ready-made bake-off
      harness
    - Large-scale dataset scalability work (2025.10) → repo-scale
      indexing is feasible
    - Enhanced KG extraction for open-source LLMs like Qwen3-30B-A3B
      (2025.09) → viable offline/local indexing path
    - Offline/air-gapped deployment guide → matches Layer 3 rebuild
      determinism requirement
  Sufficient if the governance corpus stays markdown-native and
  structure-aware table handling is not the dominant quality lever.
- [**RAG-Anything: All-in-One RAG Framework**](https://arxiv.org/html/2510.12323v1)
  (2025.06) — [GitHub](https://github.com/HKUDS/RAG-Anything). Explicitly
  released by the LightRAG team as LightRAG's multimodal extension. Adds
  dual-graph construction (cross-modal knowledge graph + text entity
  graph with fusion), structure-aware decomposition preserving tables and
  hierarchical relationships, and hybrid retrieval combining graph
  traversal and embedding similarity. The paper reports particularly
  strong gains on long documents (68.2% vs 54.6% accuracy on 101-200 page
  docs), which maps onto gzkit's growing runbooks and design memos.

The promotion bake-off picks the smaller surface (LightRAG) unless the
larger one measurably earns its complexity on the seeded governance-corpus
eval. LightRAG's `uv`-native packaging and built-in RAGAS harness mean
gzkit can run the bake-off without owning either implementation — the
decision is consumption-shaped, not fork-shaped.

Also informed by the BEADS lineage already present in
`ADR-pool.execution-memory-graph` — either upstream serves as the
unstructured-corpus complement to BEADS's structured dependency DAG.

---

## Notes

- Highest-value first use case is agent context loading for rules and
  skills. Today every session path-globs `.claude/rules/` regardless of the
  OBPI's allowed paths; semantic + structural retrieval could cut that
  substantially. Retrieval failure degrades to current behavior, which
  bounds the downside.
- Second-highest value is cross-artifact entity alignment — the manual
  `@covers` scan and `gz-adr-autolink` skill are a plausible replacement
  target if fusion quality proves out on a seeded eval.
- The governance corpus is table-heavy markdown (ADR frontmatter, OBPI
  allowed-paths tables, rule definition tables). Naive chunking destroys
  those relationships; structure-aware decomposition is the specific
  capability the paper provides.
- Consider whether the index can be emitted as an ARB-wrapped deterministic
  artifact so rebuilds are themselves attestable. LightRAG's offline
  deployment guide plus incremental update algorithm suggest this is
  tractable without forking upstream.
- Consumption posture matters: `lightrag-hku` is a PyPI package under
  `uv tool install`, so gzkit integrates by *calling* it (via a thin
  adapter and a storage backend of our choice) rather than vendoring or
  forking. That keeps the Layer 3 surface swappable if a better upstream
  appears later.

## See Also

- `docs/governance/state-doctrine.md` — Layer 1/2/3 boundary definitions
- `.gzkit/rules/cli.md` — Heavy-lane CLI contract doctrine
- `ADR-pool.focused-context-loader` — the lite-lane precursor
- `ADR-pool.execution-memory-graph` — the BEADS-shaped structured graph
