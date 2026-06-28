ADR STRUCTURAL-COMPLETENESS SCORECARD
=====================================

ADR: ADR-0.30.0-okf-documentation-knowledge-structure
Evaluator: gz adr eval (deterministic STRUCTURAL-COMPLETENESS lint)
Date: 2026-06-28

NOTE: This scorecard grades STRUCTURAL COMPLETENESS only — section
presence, depth, counts, and references. It is NOT a judgment of decision
SUBSTANCE or quality, and its verdict is NOT an authoritative quality GO.
Substance is graded only by recorded judge verdicts (see the Substance
channel below) or reported UNGRADED. Do NOT composite these scores with a
human substance review — they measure different things (GHI #624).

--- Structural Completeness (deterministic) ---

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
| okf-concept-frontmatter-model | 4 | 4 | 4 | 4 | 4 | 4.0 |
| okf-bundle-generator | 4 | 4 | 4 | 3 | 4 | 3.8 |
| okf-conformance-validator | 4 | 4 | 4 | 3 | 4 | 3.8 |
| okf-cli-surface | 4 | 4 | 4 | 3 | 4 | 3.8 |
| progressive-disclosure-path-docs | 4 | 4 | 4 | 4 | 4 | 4.0 |
| content-boundary-doctrine | 4 | 4 | 4 | 4 | 4 | 4.0 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

--- Substance (judge-graded; never derived from the scores above) ---

| Dimension | Grade | Source |
|-----------|-------|--------|
| Problem Substance | UNGRADED | no judge verdict recorded |
| Decision Substance | UNGRADED | no judge verdict recorded |

--- Structural-Completeness Summary (NOT a quality/substance verdict) ---

[x] STRUCTURALLY COMPLETE
[ ] STRUCTURAL GAPS
[ ] STRUCTURALLY INCOMPLETE


================================================================
MANUAL JUDGE EVALUATION (authoritative — supersedes CLI pre-screen)
================================================================

Evaluator: main-session (gz-adr-evaluate Step 2-7, manual rubric pass)
Date: 2026-06-28 (re-run after operator-ratified path/verb edits)
CLI pre-screen: 4.00/4.0 structural completeness, STRUCTURALLY COMPLETE, 6 OBPIs.

Ratified amendments applied since the prior manual pass (no structural-quality change):
- Bundle root moved to the dedicated sub-root `.gzkit/governance/knowledge/` (cleanly
  separate from the pre-existing `.gzkit/governance/ontology.json`).
- CLI verb renamed `gz okf` -> `gz knowledge` (now agrees with the `src/gzkit/knowledge/`
  package); validator flag kept as `--okf-conformance` (names the OKF standard checked,
  not a namespace).
- Content-boundary doctrine doc placed INSIDE the bundle at
  `.gzkit/governance/knowledge/content-boundary.md` so it genuinely IS an OKF concept node.

ADR weighted total: 4.00/4.0 -> GO. All 6 OBPIs average >= 3.6; no dimension scored 1.
Substance: Problem SOUND, Decision SOUND (orientation-not-authority fenced; domain-named
homing per the OKF spec; content boundary seated as doctrine with the migration deferred).

[x] GO — Ready for human proposal/defense review. No revisions outstanding.
