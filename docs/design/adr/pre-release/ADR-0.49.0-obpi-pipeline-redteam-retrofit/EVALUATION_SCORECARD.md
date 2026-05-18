ADR EVALUATION SCORECARD
========================

ADR: ADR-0.49.0
Evaluator: gz adr eval (deterministic)
Date: 2026-05-18

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 1 | 0.15 | Decision section has no numbered items; Missing or thin Alternatives Considered section |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 3 | 0.30 | No explicit exclusions or non-goals stated |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No anti-pattern guidance |

WEIGHTED TOTAL: 3.05/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| redteam-terminal-stage-addition-to-gz-obpi-pipeline-runtime-engine | 4 | 4 | 2 | 4 | 3 | 3.4 |
| redteam-dispatch-wiring-codex-inline-primary-opposite-claude-model-fallback-reusing-redteam-verifier-persona-from-adr-0-0-50 | 4 | 4 | 3 | 4 | 3 | 3.6 |
| from-redteam-resume-point-iron-law-update | 4 | 4 | 2 | 4 | 3 | 3.4 |
| validator-extension-covering-obpi-pipeline-scope-under-gz-validate-redteam-verification-receipts | 4 | 4 | 2 | 4 | 3 | 3.4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
