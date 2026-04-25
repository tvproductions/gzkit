ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.29
Evaluator: gz adr eval (deterministic)
Date: 2026-04-25

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | No after/target-state language in Intent |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | No anti-pattern guidance |

WEIGHTED TOTAL: 3.75/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| advisor-diagnosis-schema | 4 | 4 | 4 | 4 | 4 | 4.0 |
| diagnosis-engine | 4 | 4 | 4 | 4 | 4 | 4.0 |
| complexity-advise-cli | 4 | 4 | 4 | 4 | 4 | 4.0 |
| complexity-advisor-skill | 4 | 4 | 4 | 4 | 4 | 4.0 |
| auto-chain-hook | 4 | 4 | 4 | 4 | 4 | 4.0 |
| ad-hoc-path | 4 | 4 | 4 | 4 | 4 | 4.0 |
| intrinsic-complexity-attestation | 4 | 4 | 4 | 2 | 4 | 3.6 |
| verdict-proof-binding | 4 | 4 | 4 | 2 | 4 | 3.6 |
| advisor-timeout-fallback | 4 | 4 | 4 | 3 | 4 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
