<!-- markdownlint-disable-file MD013 MD022 MD032 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

ADR: ADR-0.25.0: Core Infrastructure Pattern Absorption
Evaluator: Codex (`gz-adr-eval`)
Date: 2026-03-22

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 4 | 0.60 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 3.15/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

## ADR Dimension Rationale

1. **Problem Clarity - 3/4**
   The problem is concrete in
   [ADR-0.25.0-core-infrastructure-pattern-absorption.md](./ADR-0.25.0-core-infrastructure-pattern-absorption.md):
   airlineops contains 17 core/common modules with potentially reusable
   infrastructure, and gzkit wants the subtraction test to hold. The before and
   after state are understandable. It remains a 3 because the tidy-first audit
   still promises a cross-reference matrix rather than summarizing its findings.

2. **Decision Justification - 3/4**
   The ADR now has explicit alternatives and a checklist necessity table in
   [ADR-0.25.0-core-infrastructure-pattern-absorption.md](./ADR-0.25.0-core-infrastructure-pattern-absorption.md).
   It defends module-by-module comparison against monolithic and grouped
   alternatives, and it directly rejects the anti-pattern of size-based or
   intuition-based confirmation. That is solid and internally consistent.

3. **Feature Checklist - 4/4**
   The structural defect is fixed. The ADR now presents 17 numbered capability
   items that map 1:1 to the 17 briefs, and the necessity table explains the
   concrete loss if any item is removed. The items are consistent in
   granularity and logically ordered.

4. **OBPI Decomposition - 3/4**
   The package now has an explicit dependency graph, critical path, and
   verification spine in
   [ADR-0.25.0-core-infrastructure-pattern-absorption.md](./ADR-0.25.0-core-infrastructure-pattern-absorption.md).
   The module-per-brief split is defensible and auditable. It remains a 3
   rather than a 4 because the 17 modules still vary materially in effort and
   likely wall-clock size.

5. **Lane Assignment - 3/4**
   Heavy lane is now justified more precisely: each comparison may culminate in
   absorption into shared runtime or operator-facing surfaces, and Gate 4 is
   explicitly conditional on actual operator-visible change. That aligns the
   lane rationale with the parent ADR and removes the earlier hand-wave.

6. **Scope Discipline - 3/4**
   The ADR now includes
   `## Non-Goals` and `### Scope Creep Guardrails` in
   [ADR-0.25.0-core-infrastructure-pattern-absorption.md](./ADR-0.25.0-core-infrastructure-pattern-absorption.md).
   The boundaries are clear: no forced absorption, no domain leakage, no hidden
   architecture rewrite inside a module brief.

7. **Evidence Requirements - 3/4**
   The package now has an ADR-level verification spine and every brief now
   carries `### Gate 4: BDD`, `## Acceptance Criteria`,
   `## Verification Commands (Concrete)`, and
   `## Completion Checklist (Heavy)`. An evaluator can now write the proof plan
   directly from the package. It stays at 3 because much of the proof is still
   grep/path/test driven rather than richer module-specific runtime checks.

8. **Architectural Alignment - 3/4**
   The ADR names real local integration points and now follows the same
   structural pattern as strong local heavy ADRs: alternatives, necessity,
   dependency framing, scope guardrails, and long-term validity guards. It is
   solidly aligned with repository standards.

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 02 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 03 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 04 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 05 | 4 | 3 | 3 | 3 | 3 | 3.2 |
| 06 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 07 | 4 | 3 | 3 | 4 | 3 | 3.4 |
| 08 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 09 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 10 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 11 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 12 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 13 | 4 | 3 | 3 | 4 | 3 | 3.4 |
| 14 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 15 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 16 | 4 | 3 | 4 | 4 | 3 | 3.6 |
| 17 | 4 | 3 | 4 | 4 | 3 | 3.6 |

**OBPI THRESHOLD: Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.**

## OBPI Notes

- **Package-wide strength:** each brief now owns one module, one decision
  envelope, one proof contract, and one Heavy-lane gate stack. That makes the
  package reviewable rather than impressionistic.
- **Package-wide improvement:** the earlier proof defect is resolved. Every
  brief now defines acceptance criteria, verification commands, Gate 4
  treatment, and a completion checklist.
- **No-equivalent briefs (03, 04, 07, 10, 12, 14)** are materially clearer now
  that they no longer preserve an impossible `Confirm` branch.
- **Largest residual risk:** actual implementation effort still varies sharply
  across modules, so the schedule may be uneven even though the decision
  framing is now sound.

## Red-Team Challenges

Not run. Re-run `gz-adr-eval ADR-0.25.0 --red-team` to add the 10-challenge
adversarial review.

## Overall Verdict

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO - Address items below, then re-evaluate
[ ] NO GO - Structural revision required

## Action Items

1. No blocking structural actions.
2. Optional improvement: summarize the tidy-first cross-reference audit in the
   ADR once gathered to strengthen Problem Clarity from solid to exemplary.
3. Optional improvement: add one concrete local exemplar citation for a prior
   companion-absorption or heavy governance ADR if you want Architectural
   Alignment to move from 3 to 4.
