ADR EVALUATION SCORECARD
═══════════════════════════

ADR: ADR-0.0.37 — Constitutional Invariant Composition
Evaluator: manual (pipeline-orchestrator, dispatching spec-reviewer + quality-reviewer)
Date: 2026-05-19 (post-authoring re-evaluation; pre-authoring evaluation 2026-05-18 preserved below)

CLI Pre-screen (post-authoring): GO — Weighted total 3.75/4.0
CLI Pre-screen (pre-authoring, 2026-05-18): GO — Weighted total 3.60/4.0
Manual evaluation (pre-authoring, 2026-05-18): CONDITIONAL GO — Weighted total 2.90/4.0

─── ADR-Level Scores (post-authoring; authoritative) ───

| # | Dimension | Weight | Pre-auth Manual | Post-auth Manual | Weighted | Override Note |
|---|-----------|--------|----|----|----------|---------------|
| 1 | Problem Clarity | 15% | 3 | 3 | 0.45 | Intent text unchanged; same score |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Decision section unchanged (only trust_audits.py path corrected); same score |
| 3 | Feature Checklist | 15% | 3 | 4 | 0.60 | Briefs now carry per-OBPI Requirements; 1:1 mandate satisfied; lifted to 4 |
| 4 | OBPI Decomposition | 15% | 2 | 4 | 0.60 | Allowed Paths now list actual implementation targets per OBPI; CIC-2 self-referential failure resolved |
| 5 | Lane Assignment | 10% | 3 | 4 | 0.40 | OBPI-10 corrected Heavy → Lite (ACTION-5); all 10 assignments now defensible |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Unchanged |
| 7 | Evidence Requirements | 10% | 1 | 4 | 0.40 | Every OBPI now has falsifiable REQ-derived Acceptance Criteria + OBPI-specific Verification commands |
| 8 | Architectural Alignment | 10% | 3 | 3 | 0.30 | trust_audits.py → trust_audits/ package reference corrected (ACTION-6); still no explicit anti-pattern inventory for novel patterns |

MANUAL WEIGHTED TOTAL (post-authoring): 3.75/4.0
CLI WEIGHTED TOTAL (post-authoring): 3.75/4.0 (manual and CLI converge after authoring)
THRESHOLD: >= 3.0 (GO), 2.5–3.0 (CONDITIONAL GO), < 2.5 (NO GO)

─── OBPI-Level Scores (post-authoring; authoritative) ──

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 invariant-schema-and-registry | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 02 composition-renderer | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 03 composition-drift-validator | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 04 brief-structural-schema | 4 | 4 | 4 | 4 | 4 | 4.0 |
| 05 brief-reconcile-engine | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 06 brief-reconcile-cli | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 07 pipeline-stage1-gate | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 08 obpi-complete-gate | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 09 agents-md-migration | 3 | 4 | 4 | 2 | 4 | 3.4 |
| 10 doctrine-refresh | 4 | 4 | 3 | 4 | 4 | 3.8 |

Dimension notes:
- Testability lifted from 2/1 → 4 across the board: each brief now has OBPI-specific Verification commands that exercise REQ-derived assertions and CI-runnable inline `python -c` checks.
- Clarity lifted from 2/3 → 4: Allowed Paths list actual target files; Requirements scoped to the OBPI item; Acceptance Criteria are falsifiable REQ-IDs.
- Size: OBPI-09 retains 2 (one-shot migration risk per ADR § Consequences Negative #2). OBPIs 02/03/05/06/07/08 score 3 (multi-surface but bounded).
- Independence: OBPI-09 scores 3 — has declared predecessor dependencies on OBPIs 01/02/03 explicitly noted in the brief's STOP-on-BLOCKERS line and Discovery Checklist.
- All OBPI averages ≥ 3.4. No dimension scores 1. The mandatory-revision rule does not fire.

─── Overall Verdict ────────────────────────────

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

VERDICT RATIONALE:
Post-authoring, the manual scorecard converges with the CLI pre-screen at 3.75/4.0
GO. The structural defects identified in the 2026-05-18 evaluation (CONDITIONAL GO,
2.90/4.0) were resolved by authoring per-OBPI Allowed Paths, Requirements,
Acceptance Criteria, and Verification commands in commit-batch under GHI #495. The
self-referential CIC-2 failure (briefs that would fail their own `gz brief reconcile`
check) is closed: every brief now has actual implementation Allowed Paths that
match its stated deliverables.

─── ACTION ITEM STATUS (from 2026-05-18 evaluation) ──

| # | Action Item | Status | Evidence |
|---|---|---|---|
| 1 | Author OBPI-specific Allowed Paths for OBPIs 01–08, 10 | ✅ Done | All 10 briefs rewritten under GHI #495 |
| 2 | Replace generic Requirements with OBPI-specific subset | ✅ Done | All 10 briefs rewritten |
| 3 | Author OBPI-specific falsifiable Acceptance Criteria | ✅ Done | Each brief has 4–8 REQ-IDs with concrete assertions |
| 4 | Add OBPI-specific Verification commands | ✅ Done | Inline `python -c` and `gz` invocations per REQ |
| 5 | Change OBPI-10 lane from Heavy to Lite | ✅ Done | OBPI-10 frontmatter `lane: Lite`; rationale recorded in brief Lane section |
| 6 | Correct ADR `trust_audits.py` reference | ✅ Done | ADR § Decision mechanical-surfaces line updated to `trust_audits/` package |
| 7 | Add OBPI-09 round-trip Acceptance Criterion | ✅ Done | OBPI-09 REQ-09-04 (round-trip semantic preservation) added |

─── Re-evaluation Provenance ───

- 2026-05-18: Initial manual evaluation surfaced 4 BLOCKER defects across all 10 OBPI briefs. CONDITIONAL GO, weighted 2.90/4.0, D7=1 mandatory revision.
- 2026-05-18: GHI #495 filed (https://github.com/tvproductions/gzkit/issues/495) as instance of root-cause GHI #485 (`gz specify` --author bundles full ADR Decision).
- 2026-05-19: All 10 OBPI briefs authored from scratch per ACTION items 1–4; OBPI-10 lane corrected (ACTION-5); ADR § Decision trust_audits package reference corrected (ACTION-6); OBPI-09 round-trip REQ added (ACTION-7).
- 2026-05-19: CLI re-evaluation reports GO at 3.75/4.0; manual re-evaluation converges at 3.75/4.0.

Note: `EVALUATION_SCORECARD.json` is overwritten by `gz adr evaluate` and reflects
the CLI-only view at the time of last evaluation. The `.md` here is the
authoritative manual scorecard that supersedes the JSON for traceability.

> Consider: this ADR no longer needs `uv run -m gzkit justify` — the weighted
> total is GO and the OBPI averages all pass the threshold. The walkthrough was
> appropriate for the pre-authoring 2.90 state; it is not required for the
> post-authoring 3.75 state.
