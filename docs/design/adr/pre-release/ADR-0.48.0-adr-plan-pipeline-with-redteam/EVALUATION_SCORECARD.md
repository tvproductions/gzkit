ADR EVALUATION SCORECARD
========================

ADR: ADR-0.48.0
Evaluator: gz adr eval (deterministic)
Date: 2026-05-18

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 3 | 0.45 | Decision section has no numbered items |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.70/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| plan-pipeline-orchestrator-skill-runtime-engine | 4 | 4 | 2 | 4 | 3 | 3.4 |
| stage-1-to-n-sequencing-of-gz-design-gz-plan-gz-obpi-specify-gz-justify-gz-plan-audit-gz-adr-evaluate | 4 | 4 | 3 | 4 | 3 | 3.6 |
| redteam-terminal-stage-codex-inline-primary-opposite-claude-model-fallback | 4 | 4 | 2 | 4 | 3 | 3.4 |
| plan-pipeline-validators-fail-closed-in-gz-check-bypass-flag | 4 | 4 | 2 | 4 | 3 | 3.4 |
| gz-status-next-action-integration-for-design-phase-recommendation | 4 | 4 | 2 | 4 | 3 | 3.4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
