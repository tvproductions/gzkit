<!-- markdownlint-disable-file MD013 -->

# ADR Evaluation Scorecard

**ADR:** ADR-0.40.0 — Reporter Rendering Infrastructure
**Evaluator:** Claude (gz-adr-eval)
**Date:** 2026-03-28

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 4 | 0.40 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 4 | 0.40 |

**WEIGHTED TOTAL: 3.20/4.0**
**THRESHOLD: 3.0 (GO)**

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 - Reporter module scaffold | 4 | 3 | 4 | 3 | 4 | 3.6 |
| 02 - Common rendering helpers | 3 | 4 | 3 | 4 | 4 | 3.6 |
| 03 - Status/report table migration | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 04 - List table migration | 3 | 3 | 3 | 3 | 4 | 3.2 |
| 05 - Ceremony panel migration | 3 | 3 | 4 | 3 | 3 | 3.2 |

**OBPI THRESHOLD: All averages >= 3.0, no dimension scores 1. PASS**

## Scoring Rationale

### ADR Strengths

- **Clear provenance:** Design emerged from a concrete bug (misaligned ceremony box) and a real codebase audit (airlineops reporter vs gzkit ad-hoc output)
- **Well-bounded scope:** Option B (rendering layer only) was chosen over full contract system or replacement, with explicit justification
- **Strong anti-pattern:** "Reporter absorbing business logic" is a concrete, testable boundary
- **Lane assignment:** OBPI-02 correctly scoped as Lite; all output-changing OBPIs correctly Heavy

### ADR Weaknesses

- **Scope discipline:** Non-goals are implicit in the anti-pattern warning rather than explicitly listed as a section
- **Evidence requirements:** OBPI verification commands are "derivable" rather than explicitly stated per OBPI

### OBPI Notes

- **OBPI-01** is the foundation — all others depend on it. Clear single prerequisite, not a bottleneck
- **OBPI-02** is the only Lite OBPI — internal helpers with no output contract change. Correct
- **OBPI-03/04** could theoretically parallelize after 01+02 are done
- **OBPI-05** depends on 01 (ceremony_panel preset) and may benefit from 03/04 patterns

## Overall Verdict

**[x] GO — Ready for proposal/defense review**

**Action items (minor):**

1. Consider adding explicit Non-Goals section to ADR (currently implicit in anti-pattern)
2. Add concrete verification commands per OBPI in briefs during implementation planning
