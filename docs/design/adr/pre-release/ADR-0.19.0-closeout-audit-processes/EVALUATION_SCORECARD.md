ADR EVALUATION SCORECARD
========================

ADR: ADR-0.19.0
Evaluator: gz adr eval (deterministic)
Date: 2026-03-21

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | OBPI allowed paths overlap significantly |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 3.85/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| gz-closeout-adr-x-y-z-end-to-end-closeout-pipeline | 4 | 4 | 4 | 3 | 4 | 3.8 |
| gz-audit-adr-x-y-z-end-to-end-audit-pipeline | 4 | 4 | 4 | 4 | 4 | 4.0 |
| equivalent-commands-in-airlineops-opsdev-closeout-opsdev-audit | 4 | 4 | 4 | 4 | 3 | 3.8 |
| audit-includes-attestation-record-gate-results-evidence-links | 4 | 4 | 4 | 4 | 4 | 4.0 |
| audit-generated-event-appended-to-ledger | 4 | 4 | 4 | 3 | 4 | 3.8 |
| audit-templates-and-evidence-aggregation-from-ledger | 4 | 4 | 4 | 3 | 4 | 3.8 |
| adr-status-transition-completed-validated-after-audit | 4 | 4 | 4 | 4 | 4 | 4.0 |
| deprecate-gz-gates-as-a-standalone-command-subsumed-by-closeout | 4 | 4 | 4 | 4 | 4 | 4.0 |
| deprecate-manual-gz-attest-during-closeout-subsumed-by-closeout | 4 | 4 | 4 | 4 | 4 | 4.0 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO

