ADR EVALUATION SCORECARD
═══════════════════════════

ADR: ADR-0.0.37-constitutional-invariant-composition — Constitutional Invariant Composition
Evaluator: manual (pipeline-orchestrator, dispatching spec-reviewer + quality-reviewer)
Date: 2026-05-19 (second evaluation, post-authoring; action items applied)

CLI Pre-screen (2026-05-19, second run): GO — Weighted total 3.75/4.0
Manual evaluation (2026-05-19, second run): GO — Weighted total 3.50/4.0
Manual evaluation (2026-05-19, first post-authoring run): GO — Weighted total 3.50/4.0
Manual evaluation (2026-05-18, pre-authoring): CONDITIONAL GO — Weighted total 2.90/4.0

Note: `gz adr evaluate` overwrites `EVALUATION_SCORECARD.md` on each run with the CLI-only
pre-screen. This `.md` is the authoritative manual scorecard and supersedes the CLI-generated
content. `EVALUATION_SCORECARD.json` is similarly CLI-only.

─── ADR-Level Scores (authoritative manual) ────────────────

| # | Dimension | Weight | CLI | Manual | Weighted | Override? |
|---|-----------|--------|-----|--------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | 3 | 0.45 | No — correct score; CLI rationale inaccurate |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | No |
| 3 | Feature Checklist | 15% | 4 | 3 | 0.45 | **Yes (-1)** — BDD feature-file coverage gap (resolved as action item) |
| 4 | OBPI Decomposition | 15% | 4 | 4 | 0.60 | No |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | No |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | No |
| 7 | Evidence Requirements | 10% | 4 | 3 | 0.30 | **Yes (-1)** — BDD verification non-runnable; OBPI-01 seed verb gap (acknowledged); OBPI-10 git diff check (fixed) |
| 8 | Architectural Alignment | 10% | 3 | 3 | 0.30 | No |

MANUAL WEIGHTED TOTAL: 3.50/4.0
CLI WEIGHTED TOTAL: 3.75/4.0
THRESHOLD: >= 3.0 (GO), 2.5–3.0 (CONDITIONAL GO), < 2.5 (NO GO)

─── Dimension Rationale and CLI Override Notes ───────────────

**D1 — Problem Clarity: 3 (CLI: 3 — same score, corrected rationale)**

The before-state is named concretely: AGENTS.md treated as Layer-1 prose, two pool stubs citing AGENTS.md as their structural anchor in the same week. The after-state is explicitly named in the Decision section (registry as Layer 1, AGENTS.md as derived view, CIC-1 + CIC-2 as load-bearing invariants). Score 3 rather than 4: the problem lacks quantified metrics — no count of invariants to migrate, no measurable drift-event frequency, no before/after measurement. CLI cited "No after/target-state language in Intent" — incorrect; the after-state IS present in the Decision section. The correct D1 deduction is the quantification gap. Score 3 confirmed; spec-reviewer independent score: 3.

**D2 — Decision Justification: 4 (CLI: 4 — confirmed)**

12 alternatives dismissed with named structural failure modes. 8 numbered rationale points with independent "because" clauses. Operator verbatim quotes are load-bearing rationale per OEE rule 3. Alternative 12 distinguishes mutation-timestamp from wall-clock TTL semantics. All checklist items pass. Quality-reviewer independent score: 4.

**D3 — Feature Checklist Completeness: 3 (CLI: 4 — manual override -1, action item applied)**

All 10 checklist items are independently meaningful and non-redundant. Override rationale: `features/constitutional_invariants.feature` (required by Gate 4 on OBPIs 02, 03, 04, 09) and `features/brief_reconcile.feature` (required by Gate 4 on OBPIs 05, 06, 07, 08) were not assigned to any OBPI's Allowed Paths — no OBPI claimed authorship. This was a coverage gap. Action item applied: OBPI-02 now owns creation of `features/constitutional_invariants.feature`; OBPIs 03/04/09 own `(modify)`. OBPI-05 now owns creation of `features/brief_reconcile.feature`; OBPIs 06/07/08 own `(modify)`. Post-action the gap is closed; score is held at 3 (a gap existed at evaluation time; the fix is committed under this evaluation). Spec-reviewer independent score: 3.

**D4 — OBPI Decomposition Quality: 4 (CLI: 4 — confirmed)**

All 10 OBPIs independently implementable with explicit Allowed Paths, Denied Paths naming OBPI-N consume-not-modify handoffs, and REQ-derived Acceptance Criteria. Dependencies sequenced explicitly in the ADR. No OBPI trivially small (OBPI-10 touches four doc surfaces with per-target requirements); no OBPI overwhelmingly large (OBPI-09 bounded to analysis + registration + round-trip + per-section attestation). BDD feature-file authorship gap is a D3/D7 issue, not a decomposition-logic defect. Spec-reviewer independent score: 4.

**D5 — Lane Assignment Correctness: 4 (CLI: 4 — confirmed)**

OBPIs 01-09 Heavy: each brief's Lane section names the specific triggering surface (schema, CLI verb, pipeline gate, etc.) — not template boilerplate. OBPI-10 Lite: correct per Gate Covenant; GHI #495 correction explicitly documented in the brief. Quality-reviewer independent score: 4.

**D6 — Scope Discipline: 4 (CLI: 4 — confirmed)**

6 explicit non-goals with named successor artifacts. Pre-mortem scenarios #2 and #7 in Negative Consequences function as plausible-creep guardrails. OBPI-10 documents the pool-stub temporal dependency (Negative Consequence #4 mitigation). Quality-reviewer independent score: 4.

**D7 — Evidence Requirements: 3 (CLI: 4 — manual override -1, two of three sub-gaps addressed)**

CLI over-counted because it detected the ADR-level Evidence section (test files, doc targets) as per-OBPI verification. The unit-test and inline-python Verification commands are genuinely concrete and falsifiable. Three sub-gaps were identified:

1. **BDD verification non-runnable (closed by ACTION-A)**: Gate 4 verification in OBPIs 02-09 invoked feature files not in any brief's Allowed Paths. Fixed: feature file creation now explicitly assigned to OBPI-02 (constitutional_invariants.feature) and OBPI-05 (brief_reconcile.feature); downstream OBPIs have `(modify)` in Allowed Paths.

2. **OBPI-01 seed structural_witness forward-references (acknowledged, not blocking)**: CIC-1.yaml and CIC-2.yaml reference `gz validate --invariant-coherence` and `gz validate --brief-reconcile` which are unresolvable at OBPI-01 landing time. Addressed by ACTION-B: explicit forward-reference acknowledgment added to OBPI-01 Requirements, distinguishing this from the "placeholder structural witness" anti-pattern (the distinction: these verbs become real at OBPI-03/05 landing per the explicit sequencing mandate; a placeholder witness never becomes real).

3. **OBPI-10 REQ-05 git diff check (fixed by ACTION-C)**: `git diff HEAD..HEAD~1` was post-commit-dependent. Replaced with `git status --porcelain | rg -v '^.. docs/'` working-tree check.

Score 3 maintained: these corrections are committed under this evaluation rather than retroactively upgrading the score. Spec-reviewer independent score: 3.

**D8 — Architectural Alignment: 3 (CLI: 3 — confirmed)**

All integration points confirmed on disk. Jinja2 declared dependency. trust_audits package structure correctly referenced. Gap preventing 4: no explicit anti-pattern inventory for structural_witness minItems:1 enforcement, byte-deterministic rendering, or mutation-timestamp freshness comparison semantics. Pre-mortems #2 and #7 cover outcome-level failure scenarios but not implementation-level "what wrong looks like" for implementing agents. Quality-reviewer independent score: 3.

─── OBPI-Level Scores (manual) ──────────────────────────────

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 invariant-schema-and-registry | 4 | 4 | 4 | 3 | 4 | **3.8** |
| 02 composition-renderer | 4 | 3 | 4 | 3 | 4 | **3.6** |
| 03 composition-drift-validator | 4 | 3 | 4 | 2 | 4 | **3.4** |
| 04 brief-structural-schema | 4 | 3 | 4 | 4 | 4 | **3.8** |
| 05 brief-reconcile-engine | 4 | 3 | 4 | 3 | 4 | **3.6** |
| 06 brief-reconcile-cli | 4 | 3 | 4 | 2 | 4 | **3.4** |
| 07 pipeline-stage1-gate | 4 | 3 | 4 | 3 | 4 | **3.6** |
| 08 obpi-complete-gate | 4 | 3 | 4 | 3 | 4 | **3.6** |
| 09 agents-md-migration | 4 | 3 | 4 | 3 | 4 | **3.6** |
| 10 doctrine-refresh | 4 | 4 | 3 | 4 | 3 | **3.8** |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.
All averages ≥ 3.4. No dimension scores 1. Threshold passes for all 10.

Testability notes:
- OBPI-01: 4 — correctly defers BDD to OBPI-02 with explicit gate deferral note; unit-test and inline-python verification is complete
- OBPIs 02-09: 3 — BDD Gate 4 verification depended on feature files that were not in Allowed Paths at initial authoring (D7 gap). Feature file assignments now applied (ACTION-A). At time of evaluation the verification was partially non-runnable; post-action it is complete. Score reflects the state at evaluation time.
- OBPI-10: 4 — Lite lane; Gate 4 not required; grep/rg verification commands are concrete and runnable

─── Overall Verdict ─────────────────────────────────────────

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

VERDICT RATIONALE:
Manual weighted total 3.50/4.0 — above the 3.0 GO threshold. All 10 OBPI
averages ≥ 3.4; no dimension scores 1; no mandatory revision triggered. All
three action items from this evaluation are committed in the same batch as this
scorecard. The ADR's decision justification, decomposition logic, lane
assignments, and scope discipline are all sound.

─── Evaluation Provenance ───────────────────────────────────

| Date | Event | Manual | CLI | Verdict |
|------|-------|--------|-----|---------|
| 2026-05-18 | First evaluation; 10 briefs in scaffold state | 2.90 | 3.60 | CONDITIONAL GO |
| 2026-05-19 | All 10 briefs authored; OBPI-10 lane corrected; ADR id canonicalized (GHI #495) | — | — | — |
| 2026-05-19 | Second evaluation (post-authoring) | 3.50 | 3.75 | **GO** |
| 2026-05-19 | Second evaluation action items applied (BDD file assignments, forward-ref note, OBPI-10 git diff fix) | — | — | — |

CLI diverges from manual by 0.25 (CLI 3.75 vs manual 3.50):
- D3: CLI=4, manual=3 — BDD feature-file coverage gap (fixed by action item)
- D7: CLI=4, manual=3 — CLI counted ADR-level evidence; manual evaluated per-OBPI runability

All other six dimensions agree between CLI and manual.
