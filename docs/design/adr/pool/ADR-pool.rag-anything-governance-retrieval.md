---
id: ADR-pool.rag-anything-governance-retrieval
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: rag-anything
---

# ADR-pool.rag-anything-governance-retrieval: Multimodal Retrieval Over the Governance Corpus

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
RAG-Anything-style dual-graph construction (cross-modal + text entity graph
with graph fusion). The goal is to serve semantic and structural queries —
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
- Structure-aware decomposition that preserves markdown tables, frontmatter
  blocks, and code fences as first-class retrieval units (not chunked away).
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
5. A decision is made on whether retrieval augments or replaces the
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

[RAG-Anything: All-in-One RAG Framework](https://arxiv.org/html/2510.12323v1) —
dual-graph construction (cross-modal knowledge graph + text entity graph
with fusion), structure-aware decomposition preserving tables and
hierarchical relationships, hybrid retrieval combining graph traversal and
embedding similarity. The paper reports particularly strong gains on long
documents (68.2% vs 54.6% accuracy on 101-200 page docs), which maps onto
gzkit's growing runbooks and design memos.

Also informed by the BEADS lineage already present in
`ADR-pool.execution-memory-graph` — RAG-Anything is the unstructured-corpus
complement to BEADS's structured dependency DAG.

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
  artifact so rebuilds are themselves attestable.

## See Also

- `docs/governance/state-doctrine.md` — Layer 1/2/3 boundary definitions
- `.gzkit/rules/cli.md` — Heavy-lane CLI contract doctrine
- `ADR-pool.focused-context-loader` — the lite-lane precursor
- `ADR-pool.execution-memory-graph` — the BEADS-shaped structured graph
