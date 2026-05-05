---
id: ADR-pool.insights-corpus-refresh-cadence
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.insights-corpus-refresh-cadence: Insights corpus refresh cadence (gz-insights-refresh)

## Status

Pool

## Intent

Behavior Rule 11 requires agents to append `improvement` records to
`.gzkit/insights/agent-insights.jsonl` whenever an operator course-corrects in
flight. The accumulator is wired; the **review cadence is not**. Records
accrete indefinitely with no defined keep/update/replace/archive pass,
producing a corpus whose oldest entries silently drift from current doctrine
the same way an unmaintained rule file does. EveryInc's
`/ce-compound-refresh` is the cross-corpus exemplar — a periodic pass that
explicitly classifies each learning into `keep | update | replace | archive`
and records the verdict.

`gz-complexity-distill` already proves the cadence-pattern works for the
exemplar corpus (annual + drift-triggered). This ADR proposes mirroring that
pattern for the insights corpus so Behavior Rule 11's accumulator does not
silently rot.

## Decision

_[To be filled at promotion time]_

Sketch:

- New skill `gz-insights-refresh` (canonical) + `gz insights refresh` CLI
  surface that walks `.gzkit/insights/agent-insights.jsonl` in cadence
  triggers (annual; or operator-invoked).
- Each record is classified `keep | update | replace | archive` against
  current doctrine in `AGENTS.md` / `.gzkit/rules/**` / promoted ADRs.
- Verdicts are written as a refresh-receipt event to the ledger
  (Layer-2 truth), never by mutating the insights file in place — the
  insights corpus stays append-only.
- Possible promotion path: a record classified `replace` whose pattern
  recurs across N≥3 entries triggers a `Promotable` rule candidate per
  `docs/governance/advisory-rules-audit.md`.

## Alternatives Considered

1. **Do nothing.** Insights pile up; oldest records silently drift from
   doctrine. Rejected — drift in the insights corpus is the same shape as
   doctrine drift in `.gzkit/rules/**`, which gzkit's anti-vibing mantra
   names as a foundational failure class.
2. **Mutate insights.jsonl in place.** Rejected — violates the
   append-only ledger-of-truth invariant. Verdicts must be a separate
   event surface.
3. **Fold into `gz-complexity-distill`.** Rejected — different corpus,
   different cadence (insights churn faster than complexity exemplars).
   Co-locating risks the same kind of conflation Architectural Boundary
   #6 warns against.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
