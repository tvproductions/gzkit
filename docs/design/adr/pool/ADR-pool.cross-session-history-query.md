---
id: ADR-pool.cross-session-history-query
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.cross-session-history-query: Cross-session history query skill

## Status

Pool

## Intent

`gz-session-handoff` covers the static state slice between engineering
sessions (most-recent handoff, open GHIs, active OBPI claims, recent ledger
events). It does not cover the **dynamic question**: *"have I seen this
failure shape before in a prior session?"* Operators routinely debug a
class of failure whose prior occurrence is buried in a Claude Code, Codex,
or Cursor session transcript that the handoff doc does not surface.

EveryInc's `/ce-sessions` skill is the cross-corpus exemplar — query
session history across tools and return cited results. The MCP surface
`mcp__ccd_session_mgmt__search_session_transcripts` already exists in this
environment; what is missing is a thin gzkit-shaped skill that always
cites session IDs (Layer-2 evidence) and routes findings into the
existing insight/GHI surface rather than into freeform agent recall
(which is the named vibing failure class).

## Decision

_[To be filled at promotion time]_

Sketch:

- New skill `gz-session-search` (canonical) wrapping
  `mcp__ccd_session_mgmt__search_session_transcripts`.
- Skill contract: every returned hit MUST include the session ID, the
  matched span, and a date — narrative paraphrase without citation is
  rejected (same rule as ARB receipt-IDs).
- Skill output routes findings explicitly: confirmed prior occurrence
  → cite session ID inline in current work; recurring pattern → file
  GHI via `ghi-author`; isolated lesson → `agent-insights.jsonl`.
- Skill never modifies session transcripts — they are read-only Layer-2
  evidence.

## Alternatives Considered

1. **Rely on agent recall across sessions.** Rejected — narrative
   reconstruction from memory is the canonical vibing failure. The
   ledger-of-truth doctrine forbids it.
2. **Fold into `gz-session-handoff`.** Rejected — handoff is forward-
   looking (what does the next session need to know); search is
   backward-looking (have I seen this before). Conflating them muddies
   both contracts.
3. **Use the MCP tool directly without a skill wrapper.** Rejected —
   without the skill's citation contract, the surface degrades into
   "agent searched and tells you what it found," which is the failure
   shape the citation contract exists to prevent.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
