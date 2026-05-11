ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.43
Evaluator: gz adr eval (deterministic)
Date: 2026-05-11

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | OK |
| 2 | Decision Justification | 15% | 4 | 0.60 | OK |
| 3 | Feature Checklist | 15% | 4 | 0.60 | OK |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | OK |
| 5 | Lane Assignment | 10% | 4 | 0.40 | OK |
| 6 | Scope Discipline | 10% | 4 | 0.40 | OK |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | OK |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | OK |

WEIGHTED TOTAL: 4.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| prd-section-schema-scaffolder | 4 | 4 | 4 | 2 | 3 | 3.4 |
| dm-artifact-schema-template | 4 | 4 | 4 | 2 | 3 | 3.4 |
| gz-domain-cli-subcommand-group | 2 | 4 | 4 | 3 | 3 | 3.2 |
| frontmatter-cascade-keys-validators | 4 | 4 | 4 | 2 | 3 | 3.4 |
| ledger-event-schemas-emit-paths | 4 | 4 | 4 | 2 | 3 | 3.4 |
| domain-cascade-validators-check-pipeline | 4 | 4 | 4 | 3 | 3 | 3.6 |
| legacy-mapping-classification-ratification | 4 | 4 | 4 | 2 | 3 | 3.4 |
| gz-domain-skills-canonical-mirrors | 4 | 4 | 4 | 2 | 3 | 3.4 |
| existing-skill-extensions | 4 | 4 | 4 | 2 | 3 | 3.4 |
| ghi-workflow-extensions | 4 | 4 | 3 | 3 | 3 | 3.4 |
| cross-context-ast-import-enforcer | 4 | 4 | 4 | 4 | 3 | 3.8 |
| documentation-cross-coverage | 4 | 4 | 4 | 3 | 3 | 3.6 |
| prd-gzkit-amendment | 4 | 4 | 4 | 4 | 3 | 3.8 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Overall Verdict ---

[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
