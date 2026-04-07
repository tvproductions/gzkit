ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.15 — GHI-Driven Patch Release Ceremony
Evaluator: Claude Opus 4.6 (manual evaluation with CLI pre-screen)
Date: 2026-04-07

CLI Pre-Screen: CONDITIONAL GO (2.75/4.0) — pattern-matching penalties
on Dimensions 1 and 2 overridden by manual assessment below.

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | Problem is specific and measurable: no formal patch release path leads to manual version edits, drift (0.24.1 in pyproject.toml vs 0.24.0 in `__init__.py`), and missing release artifacts. Three concrete failure modes documented in Rationale. Before/after states testable. CLI scored 1 because Intent section is concise — but Rationale + Agent Context Frame carry the depth. |
| 2 | Decision Justification | 15% | 3 | 0.45 | Six decisions in Decision section with bullet points. Four alternatives explicitly rejected with specific reasoning (automatic release, label-only, diff-only, separate version-sync). Cross-validation design traced to Q&A dialogue conclusions. CLI scored 1 because Decision uses bullets not numbered items — pattern mismatch, not substance gap. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | Six items, each necessary and independently valuable. Consistent granularity. Logical ordering (scaffold -> discovery -> sync -> manifest -> ceremony -> dogfood). Removing any item leaves a visible capability gap. No padding. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | Six OBPIs at domain-driven boundaries. Each independently implementable and testable. Dependency graph acyclic with clear parallelization (02 and 03 can run in parallel after 01). 1-3 day work units. No gaps in numbering. |
| 5 | Lane Assignment | 10% | 3 | 0.30 | Heavy/Lite assignments correct and justified. OBPI-01 (new CLI subcommand = external contract), OBPI-05 (operator ceremony), OBPI-06 (git tag + release) all correctly Heavy. OBPI-02/03/04 correctly Lite (internal logic). Gate obligations acknowledged per lane in briefs. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Four explicit non-goals with specific reasoning: major/minor bumps, automatic release, backports, GHI triage. Critical constraint (single version-sync path) stated as guardrail. Anti-pattern warning names the exact failure mode. ADR is self-contained. |
| 7 | Evidence Requirements | 10% | 3 | 0.30 | Five-gate evidence structure specified. Each OBPI brief has concrete verification commands. REQ-level acceptance criteria with clear pass/fail. Verification sections include specific bash commands. Could be slightly more CI-automation-ready. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | Integration points listed with module paths (closeout.py, parser_governance.py, ledger.py, ledger_events.py). Pattern reuse from gz closeout documented. Anti-pattern warning explicit. Does not reference exemplar files as thoroughly as ADR-0.0.4. |

WEIGHTED TOTAL: 3.25/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 - CLI Command Scaffold | 4 | 4 | 3 | 4 | 4 | 3.8 |
| 02 - GHI Discovery + Cross-Validation | 3 | 4 | 4 | 3 | 4 | 3.6 |
| 03 - Version Sync Integration | 3 | 4 | 4 | 4 | 4 | 3.8 |
| 04 - Dual-Format Manifest | 3 | 3 | 3 | 4 | 4 | 3.4 |
| 05 - Ceremony Skill | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 06 - Dogfood Fix Version Drift | 2 | 4 | 4 | 4 | 4 | 3.6 |

OBPI AVERAGE: 3.57
OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.
All OBPIs pass. No dimension scores 1.

OBPI Notes:
- OBPI-05 has the lowest average (3.2): Testability is limited because the skill
  is agent-orchestrated rather than CLI-testable. Clarity relies on "mirroring
  closeout ceremony Steps 9-10" as a reference rather than spelling out each step.
  Acceptable but worth noting for implementation.
- OBPI-06 Independence scores 2 because it depends on all 5 prior OBPIs by
  design (it is the dogfood invocation). This is inherent to its purpose, not a
  decomposition defect.

--- Red-Team Challenges ---

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | Pass | Every checklist item has a concrete capability answer: (1) no entry point, (2) no GHI discovery, (3) no mislabel detection, (4) version drift, (5) no audit trail, (6) no operator ceremony. |
| 2 | Scope | Pass | Strongest exclusion: backport/hotfix workflows — justified because patch releases apply to HEAD only. Strongest inclusion challenge: OBPI-06 (dogfood) could be a separate ADR, but it validates the whole chain and fixes a real drift, so inclusion is warranted. |
| 3 | Alternative | Pass | Current 6-OBPI decomposition is defensible. OBPI-02 and OBPI-03 could theoretically merge (both add logic to patch_release.py), but they address orthogonal concerns (discovery vs version sync) and benefit from independent testability. OBPI-05 (ceremony skill) is appropriately scoped — splitting it would create trivial sub-units. |
| 4 | Dependency | Pass | If OBPI-01 fails, all downstream OBPIs are blocked — but this is inherent (CLI scaffold is the foundation). OBPI-02 and OBPI-03 can run in parallel after OBPI-01, reducing critical path. No single point of failure beyond the expected scaffold dependency. |
| 5 | Gold Standard | Pass | Compared to ADR-0.0.4 (CLI Standards, Completed): ADR-0.0.15 has stronger anti-pattern warnings and a more concrete motivating example (0.24.1 drift). ADR-0.0.4 has a more thorough exemplar reference section and quantified problem statement (~50% of arguments lack help). ADR-0.0.15 could strengthen by adding a quantified "before" metric (e.g., number of manual version edits in recent history). |
| 6 | Timeline | Pass | Critical path: 01 -> (02 || 03) -> 04 -> 05 -> 06. Stages: 01 alone (1d), 02+03 parallel (2d), 04 alone (1d), 05 alone (2d), 06 alone (1d). Theoretical minimum: ~7 days. Parallelization at stage 2 saves ~1 day. |
| 7 | Evidence | Pass | Every OBPI has concrete verification commands. OBPI-01: `gz patch release --help` exit 0. OBPI-02: `gz patch release --dry-run` shows GHIs. OBPI-03: `--dry-run` shows proposed version. OBPI-04: `test -f docs/releases/PATCH-vX.Y.Z.md`. OBPI-05: skill file exists + manifest registration. OBPI-06: `python -c "import gzkit; print(gzkit.__version__)"` + `git tag | grep v0.24.1`. |
| 8 | Consumer | Pass | An operator reading this ADR would understand: what the command does, when to use it (patch releases), how qualification works (label + diff), and what artifacts are produced. Minor gap: the ADR doesn't explicitly describe what happens when no GHIs qualify (empty release scenario). |
| 9 | Regression | Conditional Pass | The cross-validation engine (label + diff check) depends on GitHub label taxonomy remaining stable and `src/gzkit/` remaining the runtime source path. If the project restructures source directories, the diff check path would silently stop qualifying GHIs. The ADR does not specify a contract test that guards the qualification path regex. Worth a follow-up regression test. |
| 10 | Parity | Pass | The ADR claims pattern alignment with `gz closeout` ceremony. Weakest claim: "RELEASE_NOTES + git-sync + GitHub release follow the same patterns as gz closeout ceremony Steps 9-10." This is stated as aspiration in the ADR, with OBPI-05 tasked to implement it. The closeout ceremony is the reference, not duplicated. The risk is divergence over time, but the shared `sync_project_version` function provides a structural coupling that prevents the most dangerous drift (version sync). |

RED-TEAM RESULTS: 9 Pass, 1 Conditional Pass, 0 Fail
RED-TEAM THRESHOLD: <=2 failures = GO, 3-4 = CONDITIONAL GO, >=5 = NO GO

--- Overall Verdict ---

[x] GO - Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

SUMMARY:
- ADR weighted total: 3.25/4.0 (exceeds 3.0 GO threshold)
- All OBPIs average >= 3.0 with no dimension scoring 1
- Red-team: 9/10 pass (1 conditional on regression testing)
- CLI automated scoring (2.75) was penalized by pattern-matching heuristics
  that missed the ADR's distributed structure (problem clarity across Intent +
  Rationale + Agent Context Frame; justification across Decision + Alternatives)

ACTION ITEMS (non-blocking, recommended improvements):
1. Challenge 9 finding: Add a regression/contract test that validates the GHI
   qualification path regex (`src/gzkit/`) still matches the actual source
   directory. This prevents silent qualification failure if the project
   restructures.
2. Challenge 5 finding: Consider adding a quantified "before" metric to the
   Intent section (e.g., "N manual version edits in the last M releases")
   to strengthen the problem statement.
3. Challenge 8 finding: Document the empty-release scenario — what happens
   when `gz patch release` finds no qualifying GHIs. Should it exit 0 with
   a message, or exit 1?
