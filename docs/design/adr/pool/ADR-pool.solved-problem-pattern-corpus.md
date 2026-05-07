---
id: ADR-pool.solved-problem-pattern-corpus
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.solved-problem-pattern-corpus: Solved-problem pattern corpus (governed)

## Status

Pool

## Intent

EveryInc's `/ce-compound` skill codifies solved-problem patterns into a
reusable corpus. The original objection — that free-form learnings
corpora reproduce training-corpus bias — holds for **ungoverned** dumps,
not for governed evidence surfaces. gzkit already operates two governed
corpora: `.gzkit/insights/agent-insights.jsonl` (append-only,
schema-bound, course-correction-driven) and the exemplar corpus governed
by `gz-complexity-distill`. A third governed corpus — *solved-problem
patterns* — fills a real gap: the recurring-failure-pattern question
that `gz-session-search` (proposed under `ADR-pool.cross-session-history-
query`) answers per-occurrence has no aggregated artifact.

The four invariants below are what separate a governed corpus from a
vibing surface; without them, this ADR should be rejected.

## Decision

_[To be filled at promotion time]_

Sketch — bound by the four governance invariants:

1. **Append-only and Layer-2.** Pattern entries are written by a skill,
   never hand-edited. Same shape as `.gzkit/ledger.jsonl`.
2. **Each entry cites primary evidence.** Session ID, GHI number, ADR
   ID, or commit SHA. Entries without citations are rejected at
   schema-validation time. Same contract as ARB receipts.
3. **Schema-validated.** JSON shape under `src/gzkit/schemas/`,
   validated by a new `gz validate --patterns` scope. No free-form
   prose blob that would let training-corpus-style drift in.
4. **Refreshable.** Subject to the cadence pattern proposed under
   `ADR-pool.insights-corpus-refresh-cadence` (keep / update / replace
   / archive against current doctrine), so the corpus does not silently
   drift from canon.

Possible storage path: `.gzkit/patterns/solved-problem-patterns.jsonl`.
Skill: `gz-pattern-record` to write entries (with mandatory citation),
`gz-pattern-search` to read.

## Amendment 2026-05-07: Pattern entries as compounding capital

The corpus absorbs Compound Engineering and Superpowers strengths only when a
pattern entry proves it made future work more governable. Promotion design
should add fields beyond the initial sketch:

- `failure_class`: taxonomy value from ADR-0.0.23 or a GHI-linked extension
- `source_evidence`: non-empty array of GHIs, receipts, commits, or ADR/OBPI IDs
- `resolution_shape`: the reusable move that solved the problem
- `future_trigger`: concrete condition telling a later agent when to load the
  pattern
- `canonization_status`: `candidate`, `human_reviewed`, `promoted_to_skill`,
  `promoted_to_rule`, or `archived`

The key comparator lesson is the compounding loop; the gzkit-specific
constraint is that compounding cannot become a free-form memory dump. Pattern
entries are useful only when they are searchable, evidenced, and subject to
human-reviewed promotion or archival.

## Alternatives Considered

1. **Free-form learnings dump (compound-engineering shape).** Rejected
   — fails all four invariants above; reproduces training-corpus bias.
2. **Fold into `agent-insights.jsonl`.** Rejected — different shape:
   insights are course-correction records (operator told the agent to
   do X differently); patterns are solved-problem aggregates (this
   class of failure was solved by Y). Conflating them muddies both
   surfaces and breaks the cadence trigger for each.
3. **Encode patterns as ADRs directly.** Rejected — ADRs are
   architectural intent, not pattern aggregation. Each solved-problem
   pattern would be too small for an ADR; the aggregation is the
   point.
4. **Store under `docs/governance/` as prose.** Rejected — prose is
   not schema-validated; vibing-surface risk reappears at the prose
   layer. Layer-2 truth requires Layer-2 shape.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
