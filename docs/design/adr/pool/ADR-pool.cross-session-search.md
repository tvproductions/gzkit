---
id: ADR-pool.cross-session-search
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent session_search_tool.py
---

# ADR-pool.cross-session-search: FTS5 Cross-Session Search Index

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add a searchable FTS5 index over ledger events, session handoff documents, and
agent insights so agents can recall prior decisions and rationale without
re-reading full transcripts or relying on human memory.

---

## Target Scope

- Build a SQLite FTS5 virtual table indexing: ledger events (attestation text, event metadata), session handoff documents (`.gzkit/handoffs/`), and agent insights (`agent-insights.jsonl`).
- Add `gz search <query>` CLI surface returning grouped, ranked results with source attribution (ledger event ID, handoff file, insight entry).
- Support FTS5 query syntax: boolean operators, phrase matching, prefix search.
- Define the index as Layer 3 (derived) — fully rebuildable from Layer 1/Layer 2 sources via `gz search rebuild`.
- Add incremental indexing: new ledger events and insights are indexed on append; full rebuild is available but not required for normal operation.
- Scope results by ADR ID, date range, or event type for focused recall.

---

## Non-Goals

- No embeddings or vector search — FTS5 keyword search is sufficient for governance recall and avoids external dependencies.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No cross-repo search — index is project-scoped.
- No session transcript indexing — transcripts are ephemeral and vendor-specific. Only governance artifacts are indexed.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.rag-anything-governance-retrieval (heavier graph-based RAG this ADR intentionally avoids — FTS5 is a lite stepping stone), ADR-pool.execution-memory-graph (graph queries complement keyword search), ADR-pool.focused-context-loader (search results could feed focused context payloads)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Indexed source set is agreed upon (ledger + handoffs + insights as baseline).
3. Storage tier classification is confirmed (L3 derived, rebuildable).

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
`tools/session_search_tool.py` and `hermes_state.py` implement SQLite FTS5
over past session transcripts. Search results are grouped by session,
truncated around match positions with proximity windowing, then summarized via
a fast auxiliary model. The key insight is that full-text search over
structured governance artifacts is dramatically cheaper and more auditable
than embedding-based retrieval, and sufficient for the "what did we decide
last time?" recall pattern.

---

## Notes

- Hermes indexes raw session transcripts (noisy, vendor-specific). gzkit should index only governance artifacts (clean, schema-validated, project-owned). This is a better signal-to-noise tradeoff.
- FTS5 is stdlib SQLite — no external dependencies. The index file lives alongside the ledger.
- Hermes uses a fast model (Gemini Flash) to summarize search results before presenting them. gzkit could skip this — structured ledger events are already concise. Raw results with source attribution are likely sufficient.
- The index should be gitignored (L3 derived) but its rebuild command should be idempotent and fast.
- Consider: should `gz search` results include a "relevance to current ADR" score? Or is raw FTS5 ranking sufficient?
