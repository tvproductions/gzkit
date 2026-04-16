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

- Author a `gz-research` skill that teaches agents the discover-assess-read workflow: search structured APIs for metadata, evaluate relevance from abstracts, read full text only for high-signal hits.
- Provide zero-dependency Python helper scripts for arxiv Atom API and Semantic Scholar REST API (no auth required for either).
- Define a citation format for ADR evidence sections that links to paper IDs, RFC numbers, or standard identifiers.
- Integrate with `agent-insights.jsonl` so research findings persist across sessions.
- Support category-scoped search (e.g., cs.SE for software engineering, cs.AI for agent architectures).

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
a SKILL.md that teaches the agent to assess impact via Semantic Scholar and
read full text via `web_extract()`. The pattern demonstrates that structured
knowledge access requires no heavy infrastructure — a helper script plus a
composable skill document is sufficient.

---

## Notes

- Hermes's arxiv script returns metadata only (title, authors, abstract snippet, links). Full-text reading is delegated to a separate tool. This separation keeps the discovery step fast and cheap.
- Semantic Scholar's API provides citation counts, influential citation flags, and recommendation endpoints — useful for assessing whether a paper is worth reading in full.
- The arxiv Atom API supports boolean queries, category filters, and author search. Rate limit is generous (3 requests/second).
- Key design tension: should research findings go into `agent-insights.jsonl` (session-scoped) or into ADR evidence sections (artifact-scoped)? Likely both — insights for cross-session recall, evidence sections for governance traceability.
