<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.22.0: Task-Level Governance
Evaluator: Codex (`gz-adr-eval`)
Date: 2026-03-22

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 3.00/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem is concrete in
   [ADR-0.22.0-task-level-governance.md](./ADR-0.22.0-task-level-governance.md):
   TASKs already exist informally in plan files, but lack a typed model, ledger
   events, and four-tier traceability. The before/after state is operationally
   clear, though not exemplary, because the tidy-first audit is called out but
   not yet quantified.

2. **Decision Justification - 3/4**
   The ADR presents clear decisions and four rejected alternatives in
   [ADR-0.22.0-task-level-governance.md](./ADR-0.22.0-task-level-governance.md),
   and the repaired package is now internally consistent around escalation and
   resume semantics. The ADR, the event brief, the CLI brief, and the
   reporting brief all agree that escalation is operable through `gz task
   escalate`, that escalated tasks are visible in reporting, and that
   `task_started` is reused for `blocked -> in_progress` resume without adding
   a fifth event kind.

3. **Feature Checklist - 3/4**
   The main Feature Checklist in
   [ADR-0.22.0-task-level-governance.md](./ADR-0.22.0-task-level-governance.md)
   now uses an explicit numbered 1:1 mapping to the five briefs. Escalation,
   resume semantics, and lane-sensitive policy surfacing are all visibly owned
   rather than implied across later sections only.

4. **OBPI Decomposition - 3/4**
   The decomposition is mostly domain-shaped: model, events, commit linkage,
   CLI, and status/reporting are reasonable work units. It stops at solid
   rather than exemplary because the reporting brief still bundles escalated
   visibility and lane-policy surfacing into one output-facing unit. The
   ADR-level dependency graph is now coherent with the CLI brief's blockers.

5. **Lane Assignment - 3/4**
   Lite for OBPIs 01-03 and Heavy for OBPIs 04-05 is broadly correct. The
   package now carries Heavy-lane obligations consistently into
   [OBPI-0.22.0-04-gz-task-cli.md](./obpis/OBPI-0.22.0-04-gz-task-cli.md)
   and
   [OBPI-0.22.0-05-status-and-state-integration.md](./obpis/OBPI-0.22.0-05-status-and-state-integration.md),
   including Gate 4. The Lite-versus-Heavy tracing policy is also operationally
   owned by OBPI-05's reporting contract.

6. **Scope Discipline - 3/4**
   The ADR has explicit non-goals and clear guardrails in
   [ADR-0.22.0-task-level-governance.md](./ADR-0.22.0-task-level-governance.md).
   The relationship to ADR-0.18.0 is also bounded clearly: 0.22.0 owns the
   TASK entity; 0.18.0 consumes it.

7. **Evidence Requirements - 3/4**
   The package now includes concrete verification-command sections in all five
   briefs, plus an ADR-level verification spine in
   [ADR-0.22.0-task-level-governance.md](./ADR-0.22.0-task-level-governance.md).
   Heavy obligations are explicit and backed by real lint/docs-build evidence
   from this evaluation run.

8. **Architectural Alignment - 3/4**
   The ADR has good local alignment: it names
   `src/gzkit/tasks.py`, `src/gzkit/events.py`,
   `src/gzkit/commands/task.py`, `src/gzkit/pipeline_runtime.py`, and the
   surrounding ADR boundaries. It is solid rather than exemplary because it
   relies more on conceptual rationale than on explicit local exemplars for
   similar command and reporting surfaces.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 02 | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 03 | 3 | 3 | 4 | 4 | 3 | 3.4 |
| 04 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 05 | 3 | 3 | 4 | 3 | 3 | 3.2 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **OBPI-01** is a strong foundational unit with clear model value and
  reasonable boundaries.
- **OBPI-02** follows naturally from the entity model and aligns well with
  existing event patterns.
- **OBPI-03** is compact and useful, though it depends on identifier semantics
  from OBPI-01 to make the traceability chain credible.
- **OBPI-04** now cleanly owns escalation and resume behavior in the operator
  surface, which removes the largest prior lifecycle gap.
- **OBPI-05** now clears threshold: it includes Gate 4, escalated visibility,
  lane-policy surfacing, and concrete verification commands for reporting.

## Red-Team Challenges

Not run. The user requested standard `gz-adr-eval` evaluation without the
`--red-team` protocol.

## Overall Verdict

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

## Action Items

1. No blocking structural actions.
2. Optional improvement: quantify the current plan-file and ledger baseline
   from the tidy-first audit to strengthen Problem Clarity from solid to
   exemplary.
3. Optional improvement: cite one or two local command/reporting exemplars in
   the ADR rationale to strengthen Architectural Alignment.
