ADR EVALUATION SCORECARD
========================

ADR: ADR-0.19.0-closeout-audit-processes
Evaluator: Claude Haiku 4.5 (gz-adr-eval skill)
Date: 2026-03-21

--- ADR-Level Scores ---

| # | Dimension              | Weight | Score (1-4) | Weighted |
|---|------------------------|--------|-------------|----------|
| 1 | Problem Clarity        | 15%    | 2           | 0.30     |
| 2 | Decision Justification | 15%    | 2           | 0.30     |
| 3 | Feature Checklist      | 15%    | 3           | 0.45     |
| 4 | OBPI Decomposition     | 15%    | 1           | 0.15     |
| 5 | Lane Assignment        | 10%    | 2           | 0.20     |
| 6 | Scope Discipline       | 10%    | 2           | 0.20     |
| 7 | Evidence Requirements  | 10%    | 1           | 0.10     |
| 8 | Architectural Alignment| 10%    | 2           | 0.20     |

WEIGHTED TOTAL: 1.90/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01   | 3           | 1           | 4     | 3    | 1       | 2.4 |
| 02   | 3           | 1           | 4     | 3    | 1       | 2.4 |
| 03   | 2           | 1           | 3     | 2    | 1       | 1.8 |
| 04   | 2           | 1           | 3     | 2    | 1       | 1.8 |
| 05   | 3           | 1           | 3     | 3    | 1       | 2.2 |
| 06   | 2           | 1           | 3     | 3    | 1       | 2.0 |
| 07   | 2           | 1           | 3     | 3    | 1       | 2.0 |
| 08   | 3           | 1           | 2     | 4    | 1       | 2.2 |
| 09   | 3           | 1           | 2     | 4    | 1       | 2.2 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.

RESULT: ALL 9 OBPIs score 1 on Testability and Clarity. All briefs are
raw template scaffolding with placeholder paths, requirements, and
acceptance criteria. None are implementable.

--- Overall Verdict ---

[x] NO GO - Structural revision required

ADR weighted total (1.90) is below the 2.5 CONDITIONAL GO threshold.
All 9 OBPI briefs are unimplemented template placeholders.

ACTION ITEMS:
1. Author all 9 OBPI briefs with real allowed paths, fail-closed
   requirements, concrete acceptance criteria (REQ IDs), and
   verification commands. This is the critical blocker — the ADR
   checklist items are sound but were never carried into the briefs.
2. Resolve lane contradiction: ledger says Lite, ADR frontmatter says
   Heavy, all OBPI briefs say Heavy. Align to a single source of truth.
3. Add Alternatives Considered section to the ADR — why not keep the
   current separate-command model (gz closeout + manual gz attest)?
4. Add explicit non-goals and scope guardrails — especially for
   OBPI-03 (cross-project airlineops parity) which is high creep risk.
5. Add before/after evidence to the Intent section — quantify the pain
   of manual subcommand chaining that motivates this ADR.
