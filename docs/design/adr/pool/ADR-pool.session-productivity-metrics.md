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
