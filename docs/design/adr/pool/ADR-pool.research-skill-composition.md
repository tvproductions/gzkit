---
id: ADR-pool.research-skill-composition
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent skills/research/arxiv
---

# ADR-pool.research-skill-composition: Composable Research Skills for Prior-Art Discovery

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add a `gz-research` skill family that composes lightweight discovery scripts
(arxiv API, Semantic Scholar, RFC index, NIST standards) with existing web
fetch and PDF reading tools, so agents can ground ADR decisions in prior art
without bespoke retrieval infrastructure.

---

## Target Scope

### Discovery (search → filter → read)

- Author a `gz-research` skill that teaches agents the 7-step workflow: (1) search arxiv by keyword/category, (2) assess impact via Semantic Scholar citation counts and influential citation flags, (3) read abstracts for relevance, (4) read full text only for high-signal papers, (5) explore related work via Semantic Scholar recommendations, (6) trace citation lineage (references and citing papers), (7) generate citations.
- Provide a zero-dependency Python helper script for the arxiv Atom API (stdlib `urllib` + `xml.etree`). Semantic Scholar is REST-only — the agent calls it directly, no script needed.
- Support category-scoped search (e.g., cs.SE for software engineering, cs.AI for agent architectures).

### Persistence (findings → governance artifacts)

Hermes treats research findings as ephemeral conversation context — once the session ends, the knowledge is lost. gzkit closes this gap by linking findings to governance artifacts at three tiers:

- **ADR evidence sections** (Layer 1) — When a paper informs an architectural decision, the agent adds a structured citation to the ADR's evidence or references section. This is the permanent traceability record: "this design decision was informed by [paper Y]."
- **`agent-insights.jsonl`** (Layer 2) — Research findings that don't yet attach to a specific ADR are recorded as insights with structured metadata (paper ID, title, relevance summary, discovery date). This enables cross-session recall: "we found a paper on append-only ledgers last week."
- **FTS5 search index** (Layer 3, if ADR-pool.cross-session-search is promoted) — Insights and evidence citations become searchable, enabling "find everything we've read about X" queries.

### Citation format

- Define a citation format for ADR evidence sections that links to paper IDs (arxiv: `arXiv:XXXX.XXXXX`), RFC numbers (`RFC NNNN`), or standard identifiers (`NIST SP 800-XX`).

---

## Non-Goals

- No embeddings, RAG pipeline, or vector database — this is API-and-skill composition, not retrieval infrastructure.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No citation management system (BibTeX, Zotero integration).
- No automatic paper summarization — the agent reads and synthesizes; the skill provides access.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.structured-research-phase (workflow phase where this skill would be wielded), ADR-pool.rag-anything-governance-retrieval (heavier retrieval infrastructure this skill intentionally avoids)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. API sources are selected (arxiv + Semantic Scholar as baseline; RFC/NIST as extensions).
3. Citation format for ADR evidence sections is agreed upon.

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
`skills/research/arxiv/` implements a zero-dependency arxiv search script
(`search_arxiv.py` using `urllib.request` against the Atom API) composed with
a SKILL.md that teaches the agent a 7-step workflow: discover via script,
filter by Semantic Scholar impact, read selectively via `web_extract()`,
explore citations, generate BibTeX. The discovery and composition pattern is
strong. The persistence gap is the opportunity: Hermes treats findings as
ephemeral conversation context (lost when the session ends, unless the agent
manually writes a note to a 2200-char `MEMORY.md` scratch pad). gzkit's
structured governance artifacts — ADR evidence sections, ledger events,
searchable insights — provide a natural durable home that Hermes lacks.

---

## Notes

- Hermes's arxiv script returns metadata only (title, authors, abstract snippet, links). Full-text reading is delegated to a separate tool. This separation keeps the discovery step fast and cheap.
- Semantic Scholar's API provides citation counts, influential citation flags, and recommendation endpoints — useful for filtering before committing to a full-text read. No auth required; rate limit is 1 req/s (100 req/s with free API key).
- The arxiv Atom API supports boolean queries (`AND`, `OR`, `ANDNOT`), prefix-scoped fields (`ti:`, `au:`, `abs:`, `cat:`), and pagination. Rate limit is ~1 req/3s.
- The persistence model resolves the earlier design tension: findings go to both `agent-insights.jsonl` (cross-session recall) and ADR evidence sections (governance traceability). Insights are the working memory; evidence sections are the permanent record.
- Consider: should `gz-research` emit a `research_finding` ledger event? This would make findings first-class governance events, queryable via `gz search` and auditable alongside gate checks. Lighter alternative: structured entries in `agent-insights.jsonl` only.
