---
id: ADR-pool.compression-governance-hooks
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent context_compressor.py
---

# ADR-pool.compression-governance-hooks: Pre-Compression Governance Fact Extraction

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Define a pre-compression hook that extracts governance-relevant facts (gate
results, coverage numbers, receipt IDs, decision rationale) from agent context
before messages are compacted, so that Layer 2 signal is preserved in the
ledger even when the conversation that produced it is truncated.

---

## Target Scope

- Define an `on_pre_compress` hook interface that fires when context compression is imminent (token budget approaching threshold).
- Implement fact extractors for key governance signals: gate pass/fail results, ARB receipt IDs, coverage floor numbers, attestation decisions, OBPI completion status.
- Extracted facts are emitted as `context_preserved` ledger events with structured payloads linking to the originating session.
- Add a tool-result pruning pattern: old `gz` command outputs in context are replaced with 1-line summaries (e.g., `[gz gates] ADR-0.1.0: 5/5 passed`) before full compression runs.
- Ensure the hook is vendor-agnostic — it processes message content, not vendor-specific context APIs.

---

## Non-Goals

- No control over when compression fires — that is the host runtime's (Claude Code's) decision. The hook observes the trigger, not causes it.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No summarization model — fact extraction is pattern-based (regex over known `gz` output formats), not LLM-based.
- No replacement for session handoff documents — handoffs preserve narrative context; this hook preserves structured facts.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.progressive-context-disclosure (manages what gets loaded; this ADR manages what survives compaction — complementary lifecycle moments), ADR-pool.cross-session-search (preserved facts become searchable via FTS5 index)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Fact extractor patterns for key governance signals are enumerated.
3. Hook integration point with host runtime is feasible (or a gzkit-side polling alternative is accepted).

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
`agent/context_compressor.py` implements a pre-compression pipeline: first
`_prune_old_tool_results()` replaces old tool outputs with informative 1-line
summaries (e.g., `[terminal] ran npm test -> exit 0, 47 lines`), then
memory providers receive an `on_pre_compress()` callback to extract insights
before messages are discarded. Existing summaries are updated iteratively on
subsequent compressions rather than replaced. The transferable insight is that
context compaction is a governance event — facts produced during the session
should be checkpointed to durable storage before the messages that contain
them are lost.

---

## Notes

- The biggest risk in long gzkit sessions is gate results being compressed away mid-pipeline. An agent that ran `gz gates` 40 messages ago may lose the pass/fail detail and re-run the gates unnecessarily, or worse, proceed without verifying.
- Hermes's tool-result pruning is applicable today: `gz` command outputs are verbose (Rich tables, multi-line status). A 1-line summary preserves the decision-relevant fact while freeing context for new work.
- The hook may need to be a Claude Code hook (`.claude/hooks/`) rather than a gzkit-internal mechanism, since context compression is a host runtime operation. This is a feasibility question for promotion.
- Consider: should the `context_preserved` ledger event include the raw compressed messages? Probably not — that would bloat the ledger. Structured facts only.
