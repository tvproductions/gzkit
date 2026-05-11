ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.32-canonical-surface-packaging
Evaluator: claude-haiku-4-5 (manual review, supersedes CLI pre-screen)
Date: 2026-05-11

CLI PRE-SCREEN: NO GO (weighted total 3.85/4.0 — flagged due to OBPI-level
independence=1 defects, not ADR-level quality). This scorecard supersedes.

─── ADR-Level Scores ───────────────────────────────────────────────────────────

| # | Dimension | Weight | Score (1-4) | Weighted | Findings |
|---|-----------|--------|-------------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | CLI score matches. Intent names the problem (T0 invariant not mechanically satisfied; surfaces exist only in .gzkit/ tree) and target state (pip install → gz init → byte-equivalent canonical content), but lacks explicit "currently X → target Y" framing. Depth is distributed across Intent + Consequences; an explicit before-state sentence in Intent would close the heuristic gap. |
| 2 | Decision Justification | 15% | 4 | 0.60 | CLI score matches. Decision section carries canonical-routing direction with three numbered binding rules, a package layout diagram, and an Alternatives Considered block with 6 named, explicitly-rejected alternatives (A–F), each citing specific principle violations. |
| 3 | Feature Checklist | 15% | 4 | 0.60 | CLI score matches. 14 checklist items — each scoped, dependency-annotated, and mapped 1:1 to OBPI IDs. Decomposition Scorecard documents scoring math, revision history (8→13→14), and parser contract compliance. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | CLI score matches. 14 OBPIs with documented sequencing plan in Q&A Transcript, parallelism opportunities named (migrations 03/09/11/13 run in parallel; scaffolders 04/10/12 follow respective migrations). Hooks correctly carved out as named exception. |
| 5 | Lane Assignment | 10% | 4 | 0.40 | CLI score matches. foundation+heavy correctly assigned. Consequences section explicitly cites AGENTS.md § Lane & Kind Attestation Matrix, names the brief-level Gate 5 rigor that applies. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | CLI score matches. Explicit in-scope (5 surface families), out-of-scope (hooks — named exception with extended rationale referencing pre-existing pool ADR framework), post-1.0 deferred (adopter-extension framework), and Forward Extension Policy (future surfaces must adopt dual-surface absent attested carve-out). |
| 7 | Evidence Requirements | 10% | 4 | 0.40 | CLI score matches. Evidence section covers: per-surface unit + byte-parity tests, BDD smoke test (build-install-gz-init), wheel manifest audit, two CLI surfaces (gz init --update, gz upgrade), validation surface (gz validate --distribution), canonical sync, docs cross-links. |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | CLI score matches. ADR traces to ADR-0.0.31 (parent doctrine), ADR-0.0.21 (chores precedent — explicitly adopted and explicitly diverged from), and parks two design gaps at named pool ADRs for future promotion. Canonical-routing model is consistent with existing src/gzkit/ structure. |

WEIGHTED TOTAL: 3.85/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

ADR-LEVEL VERDICT: GO (no dimension scores 1; weighted total well above threshold)

─── CLI Reconciliation (ADR Dimensions) ─────────────────────────────────────────

All 8 manual dimension scores match the CLI pre-screen. The only flagged heuristic
mismatch (Dimension 1, Problem Clarity) is a confirmed false negative: the CLI's
"no after/target-state language in Intent" heuristic fires because the ADR
distributes before/after depth across Intent + Consequences rather than using
explicit "currently" / "after" phrasing in Intent alone. Score of 3 is correct
for both; no override.

─── OBPI-Level Scores ───────────────────────────────────────────────────────────

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | CLI Δ |
|------|-------------|-------------|-------|------|---------|-----|-------|
| 01 skills-physical-migration | 2★ | 4 | 4 | 3 | 3 | 3.2 | CLI=1 |
| 02 skills-scaffolder-refactor | 2★ | 4 | 4 | 2 | 3 | 3.0 | CLI=1 |
| 03 rules-physical-migration | 2 | 4 | 4 | 3 | 3 | 3.2 | match |
| 04 rules-scaffolder-authoring | 1 | 4 | 4 | 2 | 3 | 2.8 | match |
| 05 init-update-flag | 4 | 4 | 4 | 2 | 3 | 3.4 | match |
| 06 t0-smoke-test | 4 | 4 | 4 | 2 | 3 | 3.4 | match |
| 07 validate-distribution | 4 | 4 | 4 | 3 | 3 | 3.6 | match |
| 08 mirror-sync | 2 | 4 | 4 | 2 | 3 | 3.0 | match |
| 09 personas-physical-migration | 2 | 4 | 4 | 3 | 3 | 3.2 | match |
| 10 personas-scaffolder-authoring | 1 | 4 | 4 | 2 | 3 | 2.8 | match |
| 11 templates-reverse-migration | 4 | 4 | 4 | 2 | 3 | 3.4 | match |
| 12 templates-scaffolder-authoring | 1 | 4 | 4 | 2 | 3 | 2.8 | match |
| 13 chores-normalization | 4 | 4 | 4 | 3 | 3 | 3.6 | match |
| 14 gz-upgrade-subcommand | 1 | 4 | 4 | 2 | 4 | 3.0 | Clarity 3→4 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

★ CLI Reconciliation (OBPI Independence Overrides):

OBPI-01 (CLI independence=1 → manual 2):
  CLI heuristic: flagged "Scaffolder refactor deferred to OBPI-02; sync mechanism
  deferred to OBPI-08" as a blocking dependency. Manual read: these are OUT-OF-SCOPE
  deferments (work excluded from OBPI-01) not prerequisites (work that must complete
  before OBPI-01 starts). OBPI-01 itself has no STOP-on-BLOCKERS gates requiring
  other OBPIs first. Confirmed by ledger state: OBPI-01 is attested_completed —
  it was executed and attested without any blocking predecessors. Override 1→2.

OBPI-02 (CLI independence=1 → manual 2):
  CLI heuristic: correctly identified "Depends on OBPI-01 landing first" as a
  blocking dependency. The brief's STOP-on-BLOCKERS gate explicitly confirms it:
  "If OBPI-01 has not landed (skills not yet at src/gzkit/skills/<slug>/SKILL.md),
  STOP." However, OBPI-01 is now attested_completed (verified via gz adr status
  output, 2026-05-11). The blocking condition is cleared. Override 1→2; OBPI-02
  is READY TO START. Brief should be updated to mark the OBPI-01 prerequisite as
  satisfied.

OBPI-14 (CLI Clarity=3 → manual 4):
  CLI heuristic underscored. The checklist item specifies --surface (comma-separated
  filter), --force (override), --dry-run (reporting without write), three-state
  IDENTICAL/STALE/EDITED detection (inherited from OBPI-05 semantics), idempotent
  exit-0, and bootstrap-retrofit semantics (works without prior gz init). This is
  the most precisely specified scope in the ADR. Override Clarity 3→4; avg 3.0.

Remaining independence=1 (structural defects per framework — require action):
  OBPI-04: depends on OBPI-03 (rules-physical-migration) — pending, unresolved.
  OBPI-10: depends on OBPI-09 (personas-physical-migration) — pending, unresolved.
  OBPI-12: depends on OBPI-11 (templates-reverse-migration) — pending, unresolved.
  OBPI-14: depends on OBPI-02 AND OBPI-06 — both pending, unresolved.

Root cause analysis:
  The independence=1 pattern on scaffolder OBPIs (04, 10, 12) is inherent to the
  canonical-surface-packaging architecture: scaffolders cannot copy from
  importlib.resources.files("gzkit.<surface>") until the physical files exist at
  src/gzkit/<surface>/ (placed by the migration OBPIs). This is an architectural
  necessity documented explicitly in the ADR Q&A Transcript's sequencing plan, not
  a decomposition flaw. The migrations (03, 09, 11, 13) CAN run in parallel; once
  each migration completes, its paired scaffolder OBPI immediately unblocks.
  OBPI-14 has dual dependency (OBPI-02 + OBPI-06) — both must land before the
  gz upgrade subcommand can wire its importlib.resources resolution path and
  verify wheel includes.

  Framework mandate: "Any dimension scoring 1 must be revised." Revision for
  OBPI-04/10/12 means updating the briefs to explicitly state the "ready to
  start when: OBPI-[migration] attested_completed" gate in the Discovery Checklist's
  Prerequisites section, and executing migrations in parallel to unblock them
  as rapidly as possible. For OBPI-14, the brief should enumerate the dual
  dependency gates explicitly.

─── Overall Verdict ─────────────────────────────────────────────────────────────

[ ] GO
[x] CONDITIONAL GO
[ ] NO GO

ADR level: GO (3.85/4.0; no ADR dimension at 1)
OBPI level: CONDITIONAL GO (independence=1 on OBPI-04/10/12/14; avg<3.0 on OBPI-04/10/12;
  inherent sequencing constraints rather than decomposition flaws; briefs require
  sequencing-gate updates before OBPI-04/10/12/14 execution)

ACTION ITEMS:

1. OBPI-02 brief — Mark OBPI-01 prerequisite SATISFIED in the Prerequisites
   checklist (OBPI-01 is attested_completed per ledger). OBPI-02 is READY TO
   START. Update the brief's Discovery Checklist > Prerequisites section to
   reflect the cleared gate.

2. OBPI-04, OBPI-10, OBPI-12 briefs — Add explicit "Ready to start when:
   OBPI-[03/09/11] attested_completed" gate language to the Prerequisites
   section. This makes the sequencing constraint operational (agents can check
   the ledger state and self-gate) rather than implicit ("depends on XX landing
   first"). The migrations (OBPI-03, OBPI-09, OBPI-11) can execute in parallel
   immediately — each one unblocks its paired scaffolder.

3. OBPI-14 brief — Document the dual dependency explicitly in the Prerequisites
   section: (a) OBPI-02 attested_completed (importlib.resources resolution path
   wired), AND (b) OBPI-06 attested_completed (wheel includes ship canonical
   content). Both gates must clear before OBPI-14 implementation begins.

4. Immediate execution priority (no brief changes needed before starting):
   - OBPI-02: UNBLOCKED — begin now (OBPI-01 complete)
   - OBPI-03, OBPI-09, OBPI-11, OBPI-13: UNBLOCKED — run in parallel
   - OBPI-05, OBPI-06, OBPI-07: UNBLOCKED — run in parallel with migrations
   These five parallel tracks (03/09/11/13 + 05/06/07) represent the bulk of
   remaining ADR-0.0.32 implementation.

5. CONDITIONAL GO lifts to GO when: (a) all four brief updates above are
   committed, AND (b) OBPI-02 has been started (confirming OBPI-01's unblocking).
   No re-evaluation needed; the ADR quality is not in question.

─── Red-Team (not invoked) ──────────────────────────────────────────────────────

--red-team not requested. ADR-level GO verdict with 3.85/4.0 and thorough
Alternatives Considered section (6 named alternatives, each explicitly rejected)
does not indicate red-team is necessary at this evaluation point. If the ADR is
proposed for human defense, a red-team pass is recommended before the defense
session.
