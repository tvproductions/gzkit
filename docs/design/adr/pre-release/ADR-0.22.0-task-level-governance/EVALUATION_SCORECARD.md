<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.22.0: Task-Level Governance
Evaluator: Claude Haiku 4.5 (`gz-adr-eval`)
Date: 2026-03-27
Prior Evaluation: Codex (`gz-adr-eval`), 2026-03-22, 3.00/4.0 GO

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 |
| 2 | Decision Justification | 15% | 4 | 0.60 |
| 3 | Feature Checklist | 15% | 4 | 0.60 |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 |
| 5 | Lane Assignment | 10% | 4 | 0.40 |
| 6 | Scope Discipline | 10% | 4 | 0.40 |
| 7 | Evidence Requirements | 10% | 4 | 0.40 |
| 8 | Architectural Alignment | 10% | 4 | 0.40 |

**WEIGHTED TOTAL: 4.00/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity — 4/4**
   The problem is concrete and compelling: "gzkit's governance hierarchy has
   three formal tiers but the fourth (TASK) exists only as informal plan-file
   steps, leaving a traceability gap at the execution level." The before/after
   is quantified (5 states, 5 transitions, 4 event kinds). The "so what?" is
   immediately obvious — ADR-0.18.0 dispatches "per task" on untyped text with
   no audit trail. The anti-pattern warning ("TASKs that add ceremony without
   value") grounds the problem in a concrete failure mode.

2. **Decision Justification — 4/4**
   Seven decisions with independent rationale. The Alternatives Considered table
   presents four alternatives with specific, non-circular rejection reasons.
   The boundary table separating ADR-0.22.0 ownership from ADR-0.18.0
   consumption is exemplary — it eliminates ambiguity about who owns what.
   The `task_started` reuse decision for resume is well-justified (keeps event
   taxonomy small). Counterarguments are addressed in the anti-pattern warning
   and the "complex workflow engine" alternative rejection.

3. **Feature Checklist — 4/4**
   Five items with an explicit Checklist Item Necessity Table answering "if
   removed, what specific capability is lost?" for each. Items are at consistent
   granularity (entity → events → git linkage → CLI → reporting), ordered to
   follow the dependency chain, and each maps 1:1 to an OBPI with testable
   deliverables. No visible gap in the entity-to-reporting pipeline.

4. **OBPI Decomposition — 4/4**
   Five OBPIs with clean domain boundaries. The explicit dependency graph with
   critical path (`01 → 02 → 04 → 05`) and parallelization notes (`02` and
   `03` can run concurrently after `01`) is exemplary. Each OBPI is a
   reasonable 1–3 day unit. No numbering gaps. The ADR-level dependency graph
   is coherent with each brief's STOP-on-BLOCKERS declarations.

5. **Lane Assignment — 4/4**
   OBPIs 01–03 are Lite (internal model, events, parser — no external contract
   change), justified with brief rationale. OBPIs 04–05 are Heavy (new CLI
   command and changes to existing CLI output — external contract), with Gate
   3/4/5 obligations explicitly listed in their completion checklists. The
   lane-sensitive advisory/required policy for TASK tracing is owned by OBPI-05.

6. **Scope Discipline — 4/4**
   Five explicit non-goals, four scope-creep guardrails redirecting to specific
   ADRs or pool items (`ADR-pool.execution-memory-graph`,
   `ADR-pool.session-productivity-metrics`). The ADR-0.18.0 boundary is
   precise. The critical constraint (advisory for Lite, required for Heavy) is
   stated at the ADR level and operationalized in OBPI-05.

7. **Evidence Requirements — 4/4**
   ADR-level verification spine with concrete commands per OBPI. Each brief has
   CI-ready verification commands (unittest, lint, typecheck, mkdocs build,
   behave). Heavy OBPIs explicitly list Gate 3/4/5 obligations with specific
   artifact paths. All commands are scriptable.

8. **Architectural Alignment — 4/4**
   The ADR references events.py discriminated union patterns, names all
   integration points with module paths, and includes the anti-pattern warning.
   The Decision section now cites `ReqId`/`ReqEntity` in `src/gzkit/triangle.py`
   as the explicit exemplar for the TASK entity pattern — frozen `ConfigDict`,
   regex-based `parse()` classmethod, `__str__` round-trip, and `Field(...)`
   with descriptions. This gives implementers a concrete local precedent.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 3 | 4 | 4 | 4 | 4 | 3.8 |
| 02 | 3 | 4 | 4 | 4 | 4 | 3.8 |
| 03 | 3 | 4 | 3 | 3 | 4 | 3.4 |
| 04 | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 05 | 3 | 4 | 4 | 3 | 4 | 3.6 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **OBPI-01 (3.8):** Strong foundational unit. 10 explicit requirements and 6
  acceptance criteria with Given/When/Then. Independence is 3 (not 4) because
  it depends on the ADR-0.20.0 REQ entity for parent linkage, though the brief
  correctly notes string-based references as a fallback.

- **OBPI-02 (3.8):** Follows naturally from OBPI-01 and aligns well with
  existing event patterns. 8 requirements, 4 acceptance criteria. The
  `task_started` reuse for resume is explicitly specified. Size is 4 — four
  event types following established patterns is a clean 1-day unit.

- **OBPI-03 (3.4):** Compact parser/formatter scope. Value is 3 (not 4)
  because removing it breaks commit traceability but doesn't break task
  management itself. Size is 3 — could be less than 1 day but still a
  reasonable increment.

- **OBPI-04 (3.6):** The largest OBPI with 5 subcommands, docs, and BDD.
  Size is 3 because it could push to 3–4 days with the full Heavy-lane
  obligation set. 9 requirements and 7 acceptance criteria provide excellent
  clarity. Correctly owns escalation and resume in the operator surface.

- **OBPI-05 (3.6):** Changes two existing CLI output contracts. Size is 3
  because it touches multiple reporting surfaces. Correctly bundles escalated
  visibility and lane-policy surfacing together since both are reporting
  concerns. 6 requirements, 5 acceptance criteria, full Gate 3/4/5 checklist.

## Red-Team Challenges

Not requested. Standard evaluation only.

## Overall Verdict

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO — Address items below, then re-evaluate
[ ] NO GO — Structural revision required

## Action Items

1. **No blocking actions.** ADR scores 4.00/4.0 with all OBPIs above threshold.
2. **Resolved:** Architectural Alignment upgraded to 4/4 after adding explicit
   `ReqId`/`ReqEntity` exemplar reference in the Decision section.
3. **Observation:** This re-evaluation scores significantly higher than the
   prior Codex evaluation (4.00 vs 3.00). The difference reflects scoring the
   Necessity Table, dependency graph with parallelization, scope-creep
   guardrails, and the added exemplar reference as exemplary (4) rather than
   merely solid (3). The ADR package is well-authored.
