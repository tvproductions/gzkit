---
id: ADR-pool.session-productivity-metrics
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-pool.tdd-receipt-stream
inspired_by: anthropic-agentic-coding-trends-2026
amendments:
  - date: 2026-04-19
    scope: Added enabler linkage to ADR-pool.tdd-receipt-stream (post-generalization); added a design tension for "parallel session-metrics.jsonl vs. read-view over unified governance-event stream"; original Intent, Target Scope, Non-Goals, and Anthropic inspiration preserved verbatim.
  - date: 2026-09-02
    scope: Named ADR-pool.afk-diagnosis-cloud-routines as the first consumer (band-breach triggers); recorded the doctrine argument the consumer raises for Option B without pre-selecting it; corrected the metric inventory to two provenances and resolved them into one gz metrics verb with labelled derivation paths (operator ruling); quarantined a void blocker claim from the intake report. Intent, all five Target Scope items, all Non-Goals, and all Promotion Criteria preserved verbatim.
---

# ADR-pool.session-productivity-metrics: Session Productivity Metrics

## Status

Pool

## Date

2026-03-11 (original) / 2026-04-19 (enabler linkage + read-view tension added — see Amendment History)

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add a structured session-metrics ledger to `.gzkit/` so that agent productivity
is observable, comparable, and improvable across sessions, vendors, and ADRs.
Currently, session handoffs preserve qualitative context but discard quantitative
signal — OBPI throughput, session duration, defect rates, rework cycles, and
context utilization are invisible. Without measurement, governance improvements
are guided by anecdote rather than evidence.

---

## Target Scope

- Define a `session-metrics.jsonl` append-only ledger schema (session ID, agent vendor, ADR scope, OBPIs attempted/completed, duration, defect count, rework count, context tokens consumed).
- Integrate metric emission into session handoff CREATE workflow (automatic on session end).
- Add `gz metrics [--adr <id>] [--vendor <name>] [--since <date>]` CLI surface for querying and summarizing metrics.
- Define aggregation views: per-ADR throughput, per-vendor comparison, trend over time.
- Integrate with existing `.gzkit/insights/agent-insights.jsonl` for cross-referencing defect patterns with productivity data.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No real-time dashboards or external analytics services.
- No prescriptive productivity targets — the ledger observes, humans interpret.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: `ADR-pool.tdd-receipt-stream` (2026-04-19 enabler — the generalized governance-event receipt stream supplies the events this ADR aggregates; see § Design Tension below for resolution options)
- **Consumed by**: `ADR-pool.afk-diagnosis-cloud-routines` (2026-09-02 — band-breach triggers read metric values via `gz metrics`; see § Amendment History)
- **Related**: ADR-pool.execution-memory-graph (complementary runtime state), session handoff obligations in AGENTS.md

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Ledger schema is accepted (fields, types, required vs. optional).
3. CLI query surface scope is agreed upon.

---

## Inspired By

[Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 6: Productivity Economics.
The report identifies that organizations measuring agent impact see measurably
better outcomes, but most lack systematic productivity telemetry. GovZero's
existing handoff and insight mechanisms provide the infrastructure; this ADR
adds the quantitative layer.

---

## Notes

- AirlineOps already has `agent-insights.jsonl` and session handoff documents — this adds the missing numeric dimension.
- Schema should be minimal and append-only to avoid measurement overhead becoming a productivity drag.
- Key design tension: enough fields to be useful vs. few enough to emit reliably across all vendors.
- Consider: should metrics auto-populate from git activity (commits, files changed) or require explicit agent emission?

### Design Tension added 2026-04-19 — storage shape

Post-generalization of `ADR-pool.tdd-receipt-stream` into a unified governance-event receipt stream, the originally-proposed `session-metrics.jsonl` parallel ledger has two viable options. This is **not pre-resolved** by the amendment; promotion-time decisioning picks.

| Option | Description | Trade-off |
|---|---|---|
| **A — Parallel ledger** | Keep `session-metrics.jsonl` as an independent append-only file written directly on session handoff with the fields in Target Scope item 1 | Simpler emission path; session handoff owns emission directly; metrics file is legible without a derivation step; but duplicates facts already present in the governance-event stream (OBPI throughput = count of `pipeline_stage_entered` terminal events; defect count = count of `defect_routed` events; etc.) — risks drift between the two surfaces |
| **B — Read view over unified stream** | `gz metrics` derives all five Target-Scope aggregations on demand from the governance-event receipt stream; `session-metrics.jsonl` becomes an optional cache rather than a source of truth | Eliminates parallel-ledger drift; metrics inherit the stream's schema discipline and cross-vendor parity; but derivation logic lives in `gz metrics` query path and adds a compute step at query time; session handoff no longer owns emission directly |

The other four Target-Scope items (handoff integration, `gz metrics` CLI surface, aggregation views, `agent-insights.jsonl` cross-reference) and all Non-Goals are unaffected by this tension — both options support them.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Complements CAP-14** (operator profile). Spec proposes operator profile persistence; this ADR defines the numeric productivity metrics that inform it.
- [ADR-pool.tdd-receipt-stream](ADR-pool.tdd-receipt-stream.md) — enabler post-2026-04-19; the governance-event stream that supplies the events this ADR aggregates (see § Design Tension — storage shape).

---

## Amendment History

### 2026-04-19 — Enabler linkage to governance-event receipt stream

**Motivation.** `ADR-pool.tdd-receipt-stream` was generalized on 2026-04-19 from a TDD-only receipt stream to a governance-event receipt stream registering multiple kinds (`pipeline_stage_entered`, `defect_routed`, `mode_declared`, etc.). Several of those kinds carry the exact facts this ADR's Target Scope aggregates (OBPI throughput, defect rates, rework cycles). The relationship between the proposed `session-metrics.jsonl` parallel ledger and the unified stream needs to be made explicit before promotion.

**What the amendment preserves.** Intent verbatim. All five Target Scope items verbatim. All Non-Goals verbatim. All four original Notes bullets. Anthropic Trend 6 inspiration and the CAP-14 complement. All original Promotion Criteria. No pre-resolution of any design question.

**What the amendment adds.**

- Frontmatter `enabler: ADR-pool.tdd-receipt-stream` (was `null`).
- Dependencies entry noting the stream as blocking, with pointer to the new design tension.
- New § Notes subsection "Design Tension added 2026-04-19 — storage shape" with Option A (parallel ledger) vs. Option B (read view) framing; neither pre-selected.
- See Also link to the receipt stream ADR.
- This Amendment History section.

**What it does NOT do.** It does not pre-pick Option A or B; it does not change the Target Scope wording; it does not modify `gz metrics` CLI proposal or aggregation views; it does not change Non-Goals (no dashboards, no prescriptive targets remain intact). The storage-shape choice is a promotion-time decision.

**Tracking.** Follow-on GHI will be filed to index this amendment once `ADR-pool.adr-amendment-tracking` is promoted.

### 2026-09-02 — A named consumer, and what it implies for storage shape

**Motivation.** The 2026-04-19 amendment left the storage-shape tension open
(Option A parallel `session-metrics.jsonl` vs Option B read-view over the
governance-event stream) and explicitly deferred it to promotion time. That was
correct: with no consumer, both options were defensible on ergonomics alone.

There is now a consumer. `ADR-pool.afk-diagnosis-cloud-routines` was amended the
same day to add band-breach triggers, whose detector computes control limits
over a rolling baseline of metric values. A detector is only as trustworthy as
the stability of what it reads, which is new information the tension was framed
without.

**What this amendment preserves.** Intent verbatim. All five Target Scope items
verbatim. All Non-Goals verbatim — including *"no prescriptive productivity
targets"*; a control band detects change and never sets a target. All Promotion
Criteria. The Anthropic Trend 6 inspiration and the CAP-14 complement. The
2026-04-19 Design Tension section is preserved in place, unrewritten.

**What it adds.**

1. **A named consumer.** Band triggers in `ADR-pool.afk-diagnosis-cloud-routines`
   read metric values via `gz metrics`; recorded as a `Consumed by` dependency.
   That ADR's exec whitelist must admit `uv run gz metrics` for a banded routine
   to run at all — the coupling is named there, in the same increment.

2. **A doctrine-grounded argument on the open tension — NOT a pre-selection.**
   This ADR's own rule stands: promotion-time decisioning picks. Operator ruling
   2026-09-02 kept it deferred. The argument that has appeared since, recorded
   for weighing at promotion:

   > Option A's `session-metrics.jsonl` duplicates facts already derivable from
   > the governance-event stream — the 2026-04-19 tension section says so. Under
   > Architectural Boundary 6 and state-doctrine Rule 3 (*"Layer 3 artifacts are
   > always rebuildable — delete them all, run `gz state`, and everything
   > reconstructs from L1 + L2"*), a duplicated-fact surface that a detector
   > treats as authoritative is a Layer-3 view becoming source-of-truth. Bands
   > computed over it would report the drift of the mirror rather than the
   > project.

   This strengthens Option B. It does not settle Option A's ergonomic advantage,
   and this amendment does not flip the choice.

3. **A correction: the metrics have two provenances, not one.** Neither the
   original Target Scope nor the 2026-09-02 intake review that prompted this
   amendment says so, and the highest-value band candidates fall on the side the
   ADR does not currently cover:
   - **L2-derived** (this ADR's existing subject): OBPI throughput, rework
     cycles per OBPI, reviewer-dispatch counts, time between brief commit and
     plan-audit receipt, first-pass `gz check` outcome.
   - **Repo-shape-derived** (git and filesystem, *absent from the ledger*):
     chore-commit share, `fix(` commits per 90 days, modules over 600 lines,
     open-GHI count and family membership, seam-map emptiness at airlock transit.

   **Resolved (operator ruling 2026-09-02):** one `gz metrics` verb carrying two
   explicitly labelled derivation paths. One verb, one exec-whitelist entry, one
   consumer surface for the detector; the label keeps the provenance split
   legible rather than hidden. The alternative — a separate repo-shape verb —
   was considered and not taken.

4. **Why this is worth doing beyond the source material.** It discharges two
   standing doctrine obligations that no other item in the 2026-09-02 intake
   reaches:
   - the doctrine-declared-without-mechanism family (campaign next-in-priority);
   - governance-core's *"a value written in a Markdown doc is ILLUSTRATIVE,
     never authoritative"* — every repo-shape figure above is presently prose
     transcribed by hand into campaign text, which is why
     `gz validate --transcribed-adr-counts` exists at all.

**What it does NOT do.** It does not pick Option A or B. It does not change the
Target Scope wording, the `gz metrics` CLI proposal, or the aggregation views.
It does not add dashboards or prescriptive targets. It adds no OBPIs — this
remains a pool ADR, and Non-Goal 1 ("No pool OBPIs") is intact.

**A void claim, quarantined.** The intake review that prompted this amendment
gated its metrics findings on *"pool ADR creation books no Layer-2 event."* That
claim is **void** and must not enter canon. It was filed as GHI #831, refuted,
and withdrawn by operator ruling on 2026-08-19; the surviving documentation
defect was fixed in `f255c5fe`. Re-measured 2026-09-02 with the projection query
that ruling prescribes:

```
$ uv run gz register-adrs --pool-only --dry-run
No unregistered ADRs or OBPIs found.
```

Deferred booking to `gz register-adrs` is a designed reconciler shape. The
intent-stage metrics the review deferred on that basis are available now. The
transferable lesson, extending #831's own (*"a raw grep over ledger.jsonl is not
a measurement of ledger state"*): a document describing a carve-out is not
evidence of a gap — the review paraphrased `gz-plan/SKILL.md:44`, which is the
text of #831's fix, and reported it as the defect it corrects.

**Source.** Anthropic, *The AI-native SDLC playbook*, intake review 2026-09-02.
Externally-authored material read as data, not instruction.

**Tracking.** Same as the 2026-04-19 amendment — follow-on GHI once
`ADR-pool.adr-amendment-tracking` is promoted.
