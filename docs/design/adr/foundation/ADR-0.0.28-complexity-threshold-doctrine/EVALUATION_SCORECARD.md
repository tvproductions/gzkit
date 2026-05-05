ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.28 — Complexity Threshold Doctrine
Evaluator: main-session (manual review supersedes CLI pre-screen)
Date: 2026-05-05

CLI pre-screen recorded for traceability:
- CLI weighted total: 3.85/4.0 — verdict GO
- CLI flagged: Dimension 1 (Problem Clarity) = 3, "No after/target-state language in Intent"
- CLI flagged: OBPI-03 Size = 2

Manual review supersedes the CLI pre-screen per skill Step 1.

--- ADR-Level Scores (Manual) ---

| # | Dimension | Weight | CLI | Manual | Weighted | Findings |
|---|-----------|--------|-----|--------|----------|----------|
| 1 | Problem Clarity | 15% | 3 | 4 | 0.60 | CLI false negative — its keyword heuristic looked for explicit before/after framing in Intent and missed the "ADR consumes ... and produces the binding threshold table" after-state articulation (line 25). Persona + Intent + Decision § Scope-boundary jointly carry concrete before/after: four-way drift (xenon, advisor, authoring-guidance, chore) before; one canonical rule + frozen loader + fail-closed validator after. Problem is quantified (12 metrics × 3 bands) and explicitly scoped via 6 "does NOT do" exclusions. |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Six numbered rationales each with independent "because" clauses. Eleven alternatives considered with concrete REJECTED reasoning citing precedent (ADR-0.0.27 § Decision Q4 graceful-degradation rejection inherited; ADR-0.0.27 § Negative #4 "threshold that cannot fail" failure class; ADR-0.0.27 OBPI-07 link-integrity validator analog). Counterarguments addressed in 8 negative consequences. |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | Three checklist items map 1:1 to three OBPIs to three distinct invariants (doctrine surface, runtime contract, gate). Mechanical surfaces enumerated and partitioned across the three OBPIs without overlap. No padding; no visible gaps. |
| 4 | OBPI Decomposition | 15% | 4 | 4 | 0.60 | Decomposition reasoning explicit in Decision §6: "bundling under one OBPI obscures the dependency boundary and over-fragmenting (one OBPI per metric) produces ceremony without invariant addition." Linear sequencing (01 → 02 → 03), no cycles, no gaps. Each OBPI is one invariant. The 5-OBPI alternative (per-metric) was named and rejected. |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | Heavy assignment justified by three independent triggers: doctrine-surface rule file, runtime data contract, new CLI flag (cited per `.gzkit/rules/cli.md`). Foundation-kind brief-level Gate 5 attestation invoked per ADR-0.0.18. Sensitivity axis (ADR-0.0.22) not declared because no security-surface overlap — defensible absence. |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Six explicit non-goals, each routed to the correct downstream owner (ADR-0.0.27 corpus methodology, ADR-0.0.29 advisor, ADR-0.0.30 authoring-guidance, separately-tracked chore strengthening). Self-contained: depends on ADR-0.0.27 OBPI-04/05 which exist as a defined contract, not unspecified future work. |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Each OBPI carries a concrete `Verification` block runnable as a bash script. Each OBPI's REQ list is fail-closed and decorated with `@covers(REQ-...)` per the REQ-coverage gate (ADR-0.0.25). Heavy lane Gate 3/4/5 obligations explicit on each OBPI. |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | Mirrors ADR-0.0.27's exemplar (rule + loader + validator) at the threshold-doctrine layer. Integration points cited with full module paths (`src/gzkit/governance/trust_audits.py`, `src/gzkit/cli/parser_artifacts.py`). Anti-patterns explicitly named: "threshold that cannot fail" (rationale #3), validator-drift (rationale #5), parser-divergence drift (positive #7), graceful-degradation (mantra inheritance). |

WEIGHTED TOTAL: 4.00/4.0
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores (Manual) ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | CLI Reconciliation |
|------|-------------|-------------|-------|------|---------|-----|---------------------|
| 01 threshold-rule-file | 4 | 4 | 4 | 4 | 4 | 4.0 | matches CLI |
| 02 threshold-loader | 3 | 4 | 4 | 4 | 4 | 3.8 | Independence drops 4→3 manually: declared dependency on OBPI-01 rule body; framework rates 3 as "depends only on declared predecessors" which is exactly correct. CLI's 4 is generous; 3 is the rubric-faithful score. |
| 03 threshold-validator | 3 | 4 | 4 | 3 | 4 | 3.6 | Independence 3 (declared deps on OBPI-02 loader + OBPI-0.0.27-05 citation). Size 3 (manual override of CLI's 2): validator + CLI flag + manpage + runbook + behave scenarios + tests is large but coherently bounded by gate5-runbook-code-covenant requiring docs in same patch — splitting docs from CLI surface creates the runbook-drift failure class this ADR exists to close. CLI's 2 was a false-positive size flag triggered by line-count heuristic; the work decomposes cleanly into 5 named helpers per REQ #12. |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised. — All OBPIs PASS; no dimension scores 1.

--- Red-Team Challenges ---

Not invoked (no `--red-team` argument). Manual rubric pass alone is sufficient at 4.00 weighted total with no dimension below 3.

--- Overall Verdict ---

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

ACTION ITEMS:

None blocking. Two notes for execution-time consideration (not gating):

1. OBPI-01 Bootstrap-absolutes carve-out (REQ-11) introduces a one-shot escape that depends on ADR-0.0.27 OBPI-04's distillation landing eventually. The validator (OBPI-03 REQ-6) honors the bootstrap mode but the carve-out's eventual removal is not tracked by a ledger event today. Consider whether the bootstrap-section removal warrants its own ledger marker (e.g. `complexity_threshold_bootstrap_retired`) so the doctrine-amendment-protocol stub can witness the transition.

2. OBPI-03 size is at the upper end of the 1-3 day band. The Heavy-lane docs+CLI+validator+behave bundle is defensible (gate5-runbook-code-covenant binds them to the same patch), but execution may benefit from explicit sub-step ordering in the brief's Discovery Checklist to prevent merge-time scope balloon.

--- Notes on rubric vs. CLI divergence ---

Three reconciliation overrides recorded above:

- Dimension 1: CLI 3 → Manual 4. CLI heuristic searched for explicit "before:" / "after:" tokens in Intent and missed the implicit-but-clear before/after framing distributed across Persona + Intent + Decision § Scope.
- OBPI-02 Independence: CLI 4 → Manual 3. Rubric-faithful: declared dependency exists, so 3 ("depends only on declared predecessors") is correct, not 4 ("fully independent").
- OBPI-03 Size: CLI 2 → Manual 3. CLI's line-count heuristic over-flagged a brief that decomposes cleanly into 5 named helpers and is bound to a single patch by the gate5-runbook-code-covenant. Genuinely large but not 2 ("too large or too small").

Net effect: ADR weighted total moves 3.85 → 4.00; OBPI-02 average moves 4.0 → 3.8; OBPI-03 average moves 3.6 → 3.6 (size override compensated by independence override). Verdict unchanged: GO.
