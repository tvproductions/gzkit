ADR EVALUATION SCORECARD
═══════════════════════════

ADR: ADR-0.0.32 — Canonical Surface Packaging
Evaluator: claude-haiku-4-5 (manual review, supersedes CLI pre-screen)
Date: 2026-05-11

CLI Pre-Screen (for traceability):
  Verdict: NO GO | Weighted total: 3.85/4.0
  Action items (CLI): OBPI-02 independence=1 (structural defect),
    OBPI-04 independence=1 (structural defect), OBPI-04 avg=2.8<3.0

─── ADR-Level Scores ───────────────────────────

| # | Dimension | Weight | CLI | Manual | Weighted | Rationale |
|---|-----------|--------|-----|--------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 4 | 0.60 | Problem quantified: 61 skills + 14 rules missing from wheel; before/after is `pip install py-gzkit && gz init` yields stubs vs. canonical content; failure classes A-D mapped to GHI #318 with concrete states |
| 2 | Decision Justification | 15% | 3 | 4 | 0.60 | CLI heuristic fired on "no numbered items" but Decision carries full package-layout block + resolution-order paragraph + 5 lettered alternatives each dismissed with specific reasons (A: include-only closes symptom not class; B: asymmetry with chores; C: single-ADR scope conflict; D: no upgrade path; E: unit tests covered for dogfood blindness). Every choice traces to chores precedent (ADR-0.0.21) |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | 8 items each with unambiguous capability loss if removed: remove-01 → skills never reach wheel; remove-02 → gz init still produces stubs; remove-08 → mirrors stale post-promotion. Items at consistent granularity, dependency order respected |
| 4 | OBPI Decomposition | 15% | 4 | 3 | 0.45 | Decomposition structure is sound (migration-then-scaffolder precedent from ADR-0.0.21-01), but OBPI-05 through OBPI-08 carry stale `item:` frontmatter (05→3, 06→4, 07→5, 08→6 from the 6-item original sketch). OBPI-06 Denied Paths contains a stale cross-reference ("mirror sync belongs to OBPI-0.0.32-06" — should be OBPI-08). These are metadata defects from the 6→8 OBPI expansion that must be corrected before implementation |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | All 8 OBPIs Heavy, each with concrete external-contract justification: 01/03 restructure package layout; 02/04 change scaffolder runtime contract; 05 adds CLI flag and changes gz init contract; 06 modifies wheel ship contract; 07 adds gz validate scope; 08 changes gz agent sync resolution path |
| 6 | Scope Discipline | 10% | 4 | 3 | 0.30 | Scope is clear through Denied Paths in each OBPI (exemplary detail); ADR lacks an explicit "Non-Goals" section, relying instead on Consequences § Negative and per-OBPI denials. Three implicit non-goals: persona/hook promotion (named in Intent but deferred to future), mirror content authoring (OBPI-08 consumes not authors), and ADR-0.0.31 doctrine prose (owned by parent ADR) |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Every OBPI has a Verification section with concrete bash commands and expected numeric outputs (e.g. `wc -l # expect 61`). REQ-numbered acceptance criteria support `gz adr audit-check`. Gate-specific evidence placeholders are present for TDD, Docs, BDD, and Human |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | Every technical decision cites ADR-0.0.21 chores precedent by name. Integration points listed with module paths: `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py`, `importlib.resources.files("gzkit.skills")`, `init_cmd._scaffold_project_skeleton`, `_repair_missing_artifacts`. Novel patterns (module-to-package conversion) are justified as unavoidable and mirroring the exact chores shape |

WEIGHTED TOTAL: 3.75/4.0
CLI PRE-SCREEN TOTAL: 3.85/4.0

Divergence explanation:
- Dimension 2: CLI scored 3 ("no numbered items") — false negative; Decision carries full
  bullet-point justification + 5 lettered alternatives. Manual: 4.
- Dimension 4: CLI scored 4 — overscored; stale `item:` frontmatter in OBPI-05 through -08
  and stale cross-reference in OBPI-06 are decomposition metadata defects. Manual: 3.
- Dimension 6: CLI scored 4 — overscored; ADR has no explicit Non-Goals section. Manual: 3.
  Net manual total (3.75) lower than CLI (3.85); both above GO threshold.

THRESHOLD: 3.0 (GO) | 2.5 (CONDITIONAL GO) | <2.5 (NO GO)

─── OBPI-Level Scores ──────────────────────────

| OBPI | CLI-Indep | Manual-Indep | Testability | Value | Size | Clarity | Avg |
|------|-----------|--------------|-------------|-------|------|---------|-----|
| 01 skills-physical-migration | 2 | 3 | 4 | 4 | 3 | 4 | **3.6** |
| 02 skills-scaffolder-refactor | 1 | 3 | 4 | 4 | 3 | 4 | **3.6** |
| 03 rules-physical-migration | 2 | 4 | 4 | 4 | 3 | 4 | **3.8** |
| 04 rules-scaffolder-authoring | 1 | 3 | 4 | 4 | 3 | 4 | **3.6** |
| 05 init-update-flag | 4 | 3 | 4 | 4 | 2 | 3 | **3.2** |
| 06 t0-smoke-test | 4 | 3 | 4 | 4 | 3 | 4 | **3.6** |
| 07 validate-distribution | 4 | 3 | 4 | 4 | 3 | 4 | **3.6** |
| 08 mirror-sync | 2 | 3 | 4 | 4 | 3 | 3 | **3.4** |

All OBPI averages ≥ 3.0. No OBPI scores 1 on any dimension in manual scoring.

OBPI Independence reconciliation (overrides CLI):
- OBPI-02 (CLI=1 → Manual=3): CLI fired on STOP language "If OBPI-01 has not
  landed, STOP" and scored independence=1. Rubric score-3 = "Depends only on
  declared predecessors." OBPI-02 has exactly one declared hard prerequisite
  (OBPI-01); no other OBPIs block it. The STOP language is a safety gate, not
  a dependency on "most other OBPIs." CLI score is a false positive.
- OBPI-04 (CLI=1 → Manual=3): Same pattern. OBPI-04 declares exactly one hard
  STOP (OBPI-03 not landed). OBPI-02 is referenced in Discovery Checklist as a
  pattern reference ("same scaffolder pattern applied to skills"), not as a
  hard prerequisite or STOP condition. CLI score is a false positive.

OBPI-05 Size=2 rationale: Three-state detection (IDENTICAL/STALE/EDITED) with
  operator-edit marker mechanism, three behave scenarios, manpage + runbook.
  Three marker mechanism options are presented; one must be chosen and documented.
  Scope complexity pushes toward 4-5 days.

OBPI-08 Clarity=3 rationale: Brief acknowledges sync surface is "fragmented"
  across multiple source files; the Discovery Checklist correctly names this but
  the implementation-time ambiguity is real.

─── Metadata Defects (must be fixed before implementation) ─────────

1. OBPI-05 frontmatter: `item: 3` → should be `item: 5`
2. OBPI-06 frontmatter: `item: 4` → should be `item: 6`
3. OBPI-07 frontmatter: `item: 5` → should be `item: 7`
4. OBPI-08 frontmatter: `item: 6` → should be `item: 8`
5. OBPI-06 Denied Paths: "mirror sync belongs to OBPI-0.0.32-06" →
   should be OBPI-0.0.32-08

These are from the 6→8 OBPI expansion in the Q&A Transcript.
ADR Q&A Transcript also retains the old 6-OBPI sequencing narrative
("01 (skills) and 02 (rules) in parallel...") — this is now stale;
OBPI-01 is skills migration and OBPI-03 is rules migration.

─── Overall Verdict ────────────────────────────

[ ] NO GO
[~] CONDITIONAL GO — was conditional; all metadata defects resolved in session
[x] GO — post-fix verdict (see Post-Fix Verdict section below)

ADR weighted total: 3.75/4.0 ≥ 3.0 → above GO threshold on ADR quality
All OBPIs: avg ≥ 3.0 → no blocking OBPI
No OBPI scores 1 on any dimension → no structural defect at OBPI level

The CONDITIONAL GO is driven entirely by the five metadata defects (item
frontmatter and one stale cross-reference). The ADR reasoning, decomposition
logic, evidence requirements, and architectural alignment are all excellent.
Fix the defects, and this ADR is ready for human proposal/defense review.

ACTION ITEMS (RESOLVED — fixed in same evaluation session):
1. [FIXED] OBPI-05 frontmatter: `item: 3` → `item: 5`
2. [FIXED] OBPI-06 frontmatter: `item: 4` → `item: 6`
3. [FIXED] OBPI-07 frontmatter: `item: 5` → `item: 7`
4. [FIXED] OBPI-08 frontmatter: `item: 6` → `item: 8`
5. [FIXED] OBPI-06 Denied Paths: stale OBPI-0.0.32-03/-05/-06 refs → OBPI-0.0.32-05/-07/-08
6. [FIXED] OBPI-07 Denied Paths + Discovery: stale OBPI-0.0.32-04/-06 refs → OBPI-0.0.32-06/-08
7. [FIXED] OBPI-08 Denied Paths + Discovery: stale OBPI-0.0.32-04/-05 refs → OBPI-0.0.32-06/-07
8. [FIXED] OBPI-05 Denied Paths: stale OBPI-0.0.32-04/-05/-06 refs → OBPI-0.0.32-06/-07/-08
9. [OPEN] Update ADR Q&A Transcript sequencing narrative from 6-item to 8-item OBPI scheme
10. [OPEN] Add explicit "Non-Goals" section to ADR to elevate Scope Discipline to 4

Post-fix verdict: All five structural metadata defects resolved (items 1-8 above).
Remaining open items (9-10) are advisory improvements; they do not block GO.

─── Post-Fix Verdict ───────────────────────────

[x] GO — All metadata defects resolved. ADR is ready for human proposal/defense review.

ADR weighted total: 3.75/4.0 ≥ 3.0
All OBPI averages ≥ 3.0
No OBPI scores 1 on any dimension
