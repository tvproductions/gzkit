ADR EVALUATION SCORECARD
═══════════════════════════

ADR: ADR-0.0.74 — MX Mode: Maintenance Hangar
Evaluator: Claude (Haiku 4.5) — manual substance evaluation
Date: 2026-06-20
CLI Pre-screen: 3.85/4.0 (STRUCTURALLY COMPLETE)

NOTE: The CLI pre-screen grades STRUCTURAL COMPLETENESS only (section
presence, depth, counts, references). This scorecard grades SUBSTANCE —
decision quality, decomposition soundness, evidence adequacy. The two
channels measure different things and MUST NOT be composited (GHI #624).

─── CLI Pre-Screen Summary (for traceability) ────────────────────────

| # | Dimension | CLI Score | CLI Finding |
|---|-----------|-----------|-------------|
| 1 | Problem Clarity | 4 | OK |
| 2 | Decision Justification | 4 | OK |
| 3 | Feature Checklist | 3 | Checklist items not prefixed with OBPI- |
| 4 | OBPI Decomposition | 4 | OK |
| 5 | Lane Assignment | 4 | OK |
| 6 | Scope Discipline | 4 | OK |
| 7 | Evidence Requirements | 4 | OK |
| 8 | Architectural Alignment | 4 | OK |

CLI Weighted Total: 3.85/4.0

─── ADR-Level Scores (Manual Substance) ─────────────────────────────

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | Quantified: ~60-day maintenance quagmire documented in maintenance-guide.md. Before state = fail-closed locks block governance repair; after state = operator enters hangar, most guards advisory, hard exit re-run certifies return to service. "So what?" is immediate: without this, governance stalls when governance itself is the patient. Scope is explicit (global hangar + doc-type taxonomy; Phases 2–3 deferred). CLI score 4 agrees. |
| 2 | Decision Justification | 15% | 4 | 0.60 | 10 decisions, each with independent rationale. 5 alternatives explicitly named and dismissed with specific mechanism reasons (per-guard decorator = opt-in coverage is the vibing surface; global flag = N skeleton-key sites; tool-output banner = fires only on tool runs, not every turn; split taxonomy = deferral is drift; do nothing = status-quo quagmire). Pre-mortem and WWHTBT stress-tested. Decisions internally consistent. CLI score 4 agrees. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | All 10 items are necessary; removing any leaves a named capability gap. Items ordered logically (mechanism 1-3 → interface 4-5 → session contract 6-8 → generalize 9 → enforce 10). Each maps to concrete testable deliverables. **Gap:** items carry prose descriptions not OBPI-ID prefixes, making the 1:1 checklist-to-brief mandate mechanically opaque. The OBPIs' frontmatter establishes the mapping but the checklist itself doesn't surface it. CLI score 3 agrees; this is a real finding. |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 | 10 OBPIs follow domain boundaries: mechanism (1-3), interface (4-5), session contract (6-8), generalize (9), enforce (10). Dependency graph is acyclic: 01-03 parallelizable; 04/05 depend on 01-03; 06/07/08 depend on 01; 09 prereqs 01+02; 10 prereqs 01+04/05+08. Three late OBPIs (06, 09, 10) carry Size=2 (potentially 4+ days) but their scope justifies the sizing — each assembles or enforces across existing surfaces. CLI score 4 agrees. |
| 5 | Lane Assignment | 10% | 4 | 0.40 | All 10 OBPIs correctly assigned Heavy. Every OBPI touches a runtime contract: marker is the truth-source code guards read (01); checkpoint wires into validate_cmd (02); invariants is a code constant (03); enter/exit are new CLI verbs (04/05); log adds ledger events (06); awareness hook fires every agent turn (07); skill/rule are operator-facing surfaces (08); flag retirement changes existing gate behavior (09); validators add new exit-3 scopes (10). No misassignments detected. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Three explicit non-goals with phased rationale: full MEL dispatch-with-limitation binder (Phase 2), Airworthiness Directive artifact (Phase 2), instrumented squawk-velocity auto-grounding (Phase 3). Exclusions justified by sequencing discipline. Per-OBPI Denied Paths mechanically guard against scope expansion. Skeleton-key risk named and mitigated. ADR self-contained: ships global hangar + taxonomy as a complete unit. |
| 7 | Evidence Requirements | 10% | 3 | 0.30 | CLI OBPIs (04, 05, 10) explicitly require manpage + gz cli audit green. Non-CLI OBPIs have concrete verification commands (test file presence, uv run gz lint/typecheck/test). **Gap (CLI false-positive):** CLI scored 4, but Gate 3 (docs) obligations are implicit, not enumerated, for non-CLI Heavy OBPIs (01, 02, 03, 06, 07, 09). Being Heavy means Gate 3 applies; the briefs don't state what documentation is required for those OBPIs. The Fidelity Assertions section retains a placeholder row ("Replace with an assertion...") — this must be filled as OBPIs land. Manual score 3 overrides CLI 4; heuristic missed Gate 3 gap on non-CLI Heavy briefs. |
| 8 | Architectural Alignment | 10% | 4 | 0.40 | Anti-patterns explicitly named and dismissed in Alternatives Considered (the five REJECTED options are the canonical anti-patterns). Integration points carry module paths (validate_cmd.py, events.py, parser_governance.py, etc.) scoped per OBPI brief. Mitigations for known failure modes named: marker/ledger binding prevents forged-marker bypass; gate5_invariants cannot be downgraded; exit-only-clears prevents dangling state; no-force-flag prevents override. Follows established gzkit patterns (token-rail, gz agent sync, Heavy lane, manpage requirement). |

WEIGHTED TOTAL (Manual): 3.75/4.0
CLI WEIGHTED TOTAL: 3.85/4.0
DIVERGENCE: D7 — manual 3 vs CLI 4 (CLI false-positive: Gate 3 docs obligations
  implicit, not enumerated, in non-CLI Heavy OBPIs; Fidelity Assertions placeholder
  not flagged by CLI)
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

─── OBPI-Level Scores (Manual Substance) ────────────────────────────

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | Notes |
|------|-------------|-------------|-------|------|---------|-----|-------|
| 01 (marker-file) | 4 | 4 | 4 | 4 | 4 | 4.0 | Fully standalone; removing eliminates the entire MX truth-source |
| 02 (checkpoint) | 3 | 4 | 4 | 3 | 4 | 3.6 | Logical dep on 01; wiring into validate_cmd is non-trivial |
| 03 (gate5-invariants) | 3 | 4 | 4 | 4 | 4 | 3.8 | Logical dep on 02; constant + fence test is compact |
| 04 (enter) | 3 | 4 | 4 | 3 | 4 | 3.6 | Deps 01-03; new CLI verb + manpage + token-rail; manageable |
| 05 (exit-hard-gate) | 3 | 4 | 4 | 3 | 4 | 3.6 | Dep on 04 for enter-scope; full-strength re-run logic is complex |
| 06 (log-auto-assembled) | 3 | 3 | 4 | 2 | 3 | 3.0 | Size risk: assembling ledger events + commits + ADR/OBPI/REQ attribution is 4-6 days; "how commits are attributed to ADRs/OBPIs/REQs" underspecified |
| 07 (awareness-hook) | 3 | 3 | 4 | 3 | 3 | 3.2 | CLI false-positive Independence=4: logical dep on 01; "how hook adapts per vendor via sync" needs clarification |
| 08 (skill-and-agents-rule) | 3 | 4 | 4 | 4 | 4 | 3.8 | Dep on 04/05 for gz mx verb; skill + rule + tests = 1-2 days |
| 09 (retire-staging-flags) | 2 | 4 | 4 | 3 | 4 | 3.4 | CLI false-positive Independence=4: explicit prereqs 01+02; not independent until both land |
| 10 (doc-type-taxonomy) | 2 | 4 | 4 | 2 | 3 | 3.0 | CLI false-positive Independence=4: explicit prereqs 01+04/05+08; Size risk: 4-class taxonomy + tag initial docs + two new validators; "ONE MX term" form not defined |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.
STATUS: All OBPIs at 3.0+ average. No dimension scored 1.

CLI Independence over-scores: OBPIs 09 and 10 have explicit prerequisite sections naming
  specific predecessor OBPIs (hard deps, not logical); CLI heuristic did not detect these.

─── Overall Verdict ─────────────────────────────────────────────────

[x] GO — Ready for proposal/defense review

Manual weighted total 3.75/4.0 clears the 3.0 GO threshold. All OBPIs at 3.0+
with no dimension scoring 1. The three at 3.0 average (06, 10) are acknowledged
size/clarity risks, not structural defects — they clear the floor.

─── Action Items (pre-implementation) ──────────────────────────────

1. **Feature Checklist OBPI-ID prefixes (D3).** Add OBPI-0.0.74-NN identifiers
   to the checklist items in the parent ADR. Current prose mapping is traceable
   via OBPI frontmatter `item:` field but the checklist itself doesn't surface
   the IDs, making the 1:1 mandate mechanically opaque.

2. **Gate 3 docs obligations for non-CLI Heavy OBPIs (D7).** OBPIs 01, 02, 03,
   06, 07, 09 are Heavy but do not enumerate what docs must be updated or created
   for Gate 3. Add a "Documentation" line to each brief's Requirements section
   specifying the expected doc artifact (e.g. inline code comments, AGENTS.md
   binding rule, runbook update).

3. **Fidelity Assertions placeholder (D7).** The parent ADR's Fidelity Assertions
   table retains the placeholder row. Replace with at least one real claim per
   shipped OBPI as work lands. OBPI-04 (gz mx enter) and OBPI-05 (gz mx exit)
   are the natural first targets.

4. **OBPI-06 log attribution mechanism.** Specify the algorithm for "naming ADRs/
   OBPIs/REQs touched" — is it derived from commit trailers (`ADR:`, `Task:`,
   `OBPI:`), from `@covers` decorator metadata, or from a pattern scan of commit
   messages? The brief leaves this as "commits between enter/exit" without the
   attribution logic. Underspecification here risks divergent implementations.

5. **OBPI-10 MX term definition.** The brief requires `gz validate --mx-term-alignment`
   to fail when the ONE MX term drifts, but doesn't define what the exact term
   form must be (e.g. string literal "MX_MODE_ACTIVE", marker filename "mx.marker",
   YAML key "mx_mode"). Specify the canonical form before implementation to prevent
   the validator from being trivially satisfied by coincidence.

6. **OBPI-07 vendor surface sync integration.** Clarify how the per-vendor awareness
   hook is generated and updated by `gz agent sync control-surfaces`. Is it a
   template under `.gzkit/templates/`? Is it written to `.claude/hooks/` as a
   generated output? The brief says it "adapts per vendor surface the way
   control-surfaces already sync" but doesn't name the sync mechanism.
