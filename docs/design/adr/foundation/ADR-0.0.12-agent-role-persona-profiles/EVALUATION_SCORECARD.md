ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.12
Evaluator: gz adr eval (deterministic)
Date: 2026-04-03

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 3 | 0.45 | No rationale language in Decision |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 3 | 0.30 | No lane in ADR frontmatter |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.45/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| main-session-persona | 4 | 4 | 3 | 4 | 4 | 3.8 |
| implementer-agent-persona | 4 | 4 | 4 | 4 | 4 | 4.0 |
| reviewer-agent-personas | 4 | 4 | 3 | 4 | 4 | 3.8 |
| narrator-agent-persona | 4 | 4 | 3 | 4 | 4 | 3.8 |
| pipeline-orchestrator-persona | 4 | 4 | 3 | 4 | 4 | 3.8 |
| dispatch-integration | 4 | 4 | 4 | 4 | 4 | 4.0 |
| agents-md-persona-reference | 2 | 4 | 4 | 4 | 4 | 3.6 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
