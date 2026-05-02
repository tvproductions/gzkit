---
id: ADR-pool.semantic-recall-over-ledger
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.semantic-recall-over-ledger: Semantic recall over the ledger (gz recall)

## Status

Pool

## Intent

Add a read-only `gz recall "<question>"` surface that performs semantic search over the ledger (`.gzkit/ledger.jsonl`), ADR packages under `docs/design/adr/{foundation,pre-release}/`, and OBPI briefs, returning ranked pointers (event IDs, ADR paths, brief paths) — never paraphrased prose.

Closes the gap surfaced by the 2026-05-02 "agentic OS" evaluation against the video framework's Memory Level 3 (semantic search). gzkit deliberately chose structured queries (`gz state`, `gz status`) over fuzzy semantic recall because semantic recall is a fabrication vector — but this leaves "what did we decide three months ago about X" as a `gh issue` / `rg` task. A pointer-only `gz recall` reclaims the operator-experience benefit without opening the fabrication surface.

## Decision

Pool. Defer promotion until the foundation work in flight settles. When promoted, target feature-kind, lite lane, with these binding constraints:

- **Layer-3 derived view, never source-of-truth.** Index is rebuildable from canon (Layer 1) and ledger (Layer 2). A flagged `gz validate --recall-fresh` failure is recoverable by a single `gz recall reindex` — same shape as `gz register-adrs` for the ADR status index.
- **Pointer-only output.** Every hit cites a verbatim ledger event ID, ADR path, or OBPI brief path the operator can open. No paraphrased summaries, no synthesized answers. A hit you cannot open is a defect, not an answer.
- **Local embedding model only.** No external API. Closes the exfiltration surface and the popularity-bias dependency drift Stdlib-First defends against. Embedding model choice itself becomes a foundation-attested dependency under the Stdlib-First doctrine.
- **Read-only.** Cannot mutate ledger, ADRs, or briefs. Cannot author attestations.
- **Search scope is governance corpus only** — ledger events, ADR/OBPI markdown, rules, runbooks. Not source code (that surface is `rg` / IDE search).

## Alternatives Considered

1. **Status quo** — `gh issue search` + `rg` over `docs/`. Rejected: operator-experience cost is the named gap. Cross-corpus queries currently require knowing which surface to search.
2. **External vector DB / hosted embedding API** (Pinecone, OpenAI embeddings, etc.). Rejected: exfiltration surface, popularity-bias dependency, conflicts with Stdlib-First and operator-PII guardrails.
3. **Replace structured queries with semantic search.** Rejected: structured queries are audit-grade and deterministic; `gz recall` is additive, not a replacement. `gz state` and `gz status` remain the source of truth for governance state.
4. **Allow synthesized prose answers** (RAG-style summarization). Rejected: paraphrased output is the fabrication vector. Pointer-only output is the structural defense — the operator reads canon, the agent only routes them to it.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
