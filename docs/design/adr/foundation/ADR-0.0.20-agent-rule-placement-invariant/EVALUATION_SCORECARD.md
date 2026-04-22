ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.20 — Agent Rule Placement Invariant
Evaluator: main-session (manual, supersedes CLI pre-screen)
CLI pre-screen: GO, 4.00/4.0 (2026-04-22)
Date: 2026-04-22

--- ADR-Level Scores ---

| # | Dimension | Weight | CLI | Manual | Weighted | Rationale |
|---|-----------|--------|-----|--------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 4 | 0.60 | Quantified before (~25 KB / ~1,800 lines per-turn preamble; ~60% duplication with AGENTS.md; 3 specific files, 448 canonical lines) and after (570 lines removed, normalized L0 surface). "So what?" explicit: attention-dilution citing Lindsey 2025 reporting-vs-execution pathway drift applied at context-window level. |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Six alternatives rejected with specific reasoning — amend ADR-0.17.0 (taxonomy violation), fold into ADR-0.36.0 (kind/lane/dependency mismatch), shrink in place (measurement: ~60% of shrunken draft still duplicates), inverse trim (only ~3 of 213 lines are Claude-specific), direct fix (exceeds defect-fix-routing thresholds), pool parking (design is complete). Each citation grounded in measured evidence or explicit threshold. |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | 5 items, 1:1 with OBPIs, logical sequencing (substrate → parallel folds → closeout). Each is testable. No padding, no gaps. |
| 4 | OBPI Decomposition | 15% | 4 | 4 | 0.60 | Dependency graph 01 → {02,03,04 parallel} → 05 is explicit and acyclic. Groupings follow domain boundaries (one OBPI per rule file for the three folds; substrate separated; closeout separated). Numbering has no gaps. |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | All OBPIs Lite with citation to cli.md § New Flag (additive on existing `gz validate` subcommand; no new subcommand, no breaking schema, no runtime contract change). Foundation-kind walkthrough discipline acknowledged per ADR-0.0.18 regardless of Lite lane. |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | "Scope boundary — what this ADR explicitly does NOT do" enumerates 7 non-goals (three-layer model unchanged, pool ADRs not superseded, sync mechanism only consumed, hierarchical placement remains judgment, no general progressive-disclosure architecture, no expiry enforcement, mirrors not checked independently). Edge cases explicit (4 items covering broad-glob PASS, Claude-specific rules, transition allow-list, root vs per-directory). |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Every OBPI has Verification blocks with concrete commands (`uv run gz validate --unscoped-rules`, `--all`, `gz check`, `mkdocs build --strict`, `unittest` invocations). Acceptance Criteria carry REQ-IDs for @covers decoration. OBPI-01 has 20 explicit REQs; tests derived from REQs, not implementation. |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | References existing `gz validate --<scope>` precedent (`--taxonomy`, `--pydantic-models`, `--type-ignores`) for pattern consistency. Cites concrete integration points (`src/gzkit/validators/`, `parser_validate.py`, `manifest.schema.json`). Respects trust-doctrine T2 (no silent passlists), skill-surface-sync (mirrors not checked — canonical is single source of truth), tests.md (table-driven unittest, tempfile isolation, ≥40% coverage floor). |

WEIGHTED TOTAL: 4.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

**CLI reconciliation:** Manual scores match CLI pre-screen across all 8 ADR dimensions. No heuristic mismatches surfaced — the ADR's structure (explicit before/after in Intent, numbered Decisions with alternatives, explicit non-goals section) maps cleanly to the CLI's keyword/section patterns.

--- OBPI-Level Scores ---

| OBPI | Indep | Test | Value | Size | Clarity | Avg | Notes |
|------|-------|------|-------|------|---------|-----|-------|
| 01 validator-and-allowlist | 4 | 4 | 4 | 3 | 4 | 3.8 | 20 REQs, substantial surface (Pydantic models + CLI flag + schema fragment + manifest allow-list + tests + docs). Size scored 3 (not 2): scope is bounded and enumerated; likely 2-3 days focused work. CLI gave 2 — manual override, the scope is larger than a micro-OBPI but still fits a single-agent completion window. |
| 02 fold-agent-contract | 4 | 4 | 4 | 3 | 3 | 3.6 | Largest fold (213 lines, ~15 inbound refs). Clarity scored 3: dedupe against existing AGENTS.md is semantic-match not string-match; placement judgment is load-bearing. CLI gave size 4 / clarity 3 — manual size=3 recognizes the ~15-file sweep surface. |
| 03 fold-attestation-enrichment | 4 | 4 | 4 | 2 | 4 | 3.6 | Widest blast radius (6 Python docstrings + 8 ARB command docs + new governance file + GHI filing). Size 2 reflects the surface count — still a single coherent OBPI but sits at the upper boundary of independent-completability. |
| 04 fold-defect-fix-routing | 4 | 4 | 4 | 4 | 3 | 3.8 | Smallest fold (80 lines, ~5-8 inbound refs). Cleanest scope of the three folds. Clarity 3: AGENTS.md section placement still involves judgment. |
| 05 closeout-and-downstream | 4 | 4 | 4 | 4 | 3 | 3.8 | Pure ceremony (grep sweep + 3 GHI filings + foundation walkthrough + attestation). No code. Clarity 3: foundation-kind walkthrough per ADR-0.0.18 is a human-judgment protocol. |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

All OBPIs clear the threshold. No dimension scored 1.

--- Red-Team Challenges ---

Not invoked (no `--red-team` flag). Strengths surfaced during manual evaluation that an adversarial pass would likely probe:

- **Challenge 2 (Scope):** Could probe the "mirrors not checked" decision — ADR defends this via the skill-surface-sync + GHI #210 pre-commit-sync-guard contract. Defensible.
- **Challenge 8 (Consumer):** A future ADR author adding a new `paths: "**"` rule hits the validator at pre-commit and gets three-option recovery. The 2am-operator test is explicit in § Persona and § Pre-mortem.
- **Challenge 9 (Regression):** The validator IS the regression mechanism. Secondary concern — allow-list expiry not enforced in v1; ADR flags this as a follow-up GHI and names the drift signal (`tracking_ref` resolution as informal expiry).
- **Challenge 10 (Parity):** ADR's weakest parity claim is "agents.md/ hierarchical discipline honored by agent runtimes" — ADR acknowledges this is the shakiest assumption in "What Would Have to Be True" and scopes it out of mechanical enforcement (validator can't litigate AGENTS.md hierarchy placement).

If adversarial review is desired before promotion, invoke `/gz-adr-evaluate ADR-0.0.20 --red-team`.

--- Overall Verdict ---

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

**Strengths:**

1. Quantified problem with measured evidence (~60% duplication audit, 448 canonical lines, 570-line per-turn reduction target).
2. Six-alternative analysis where rejections cite specific thresholds (defect-fix-routing line/scope/precedent table, ADR-0.0.18 taxonomy binding, ADR-0.36.0 kind/lane mismatch).
3. Explicit mechanical backstop (`gz validate --unscoped-rules` with Pydantic models, manifest schema extension, 12-scenario table-driven test coverage).
4. Transition allow-list designed with exit semantics — each entry carries `tracking_ref` to the OBPI that will remove it, preventing permanent escape-hatch drift.
5. Foundation-kind rigor acknowledged regardless of Lite lane (OBPI-05 runs the walkthrough).
6. Forcing-function stress tests applied during design (pre-mortem, What Would Have to Be True, constraint archaeology, 2am operator, reversibility, scope minimization).

**Action items:** None required before promotion. The ADR is ready for human proposal/defense review and subsequent ledger registration + OBPI-01 kickoff.
