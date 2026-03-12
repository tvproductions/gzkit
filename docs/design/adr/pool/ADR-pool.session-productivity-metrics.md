---
id: ADR-pool.session-productivity-metrics
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026
---

# ADR-pool.session-productivity-metrics: Session Productivity Metrics

## Status

Pool

## Date

2026-03-11

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
- **Blocked by**: None
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
