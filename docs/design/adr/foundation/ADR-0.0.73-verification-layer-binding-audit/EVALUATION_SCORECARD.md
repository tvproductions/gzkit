ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.73-verification-layer-binding-audit
Evaluator: manual (spec-reviewer + quality-reviewer personas; narrator rendering)
CLI pre-screen: gz adr eval (deterministic) — 2026-06-17, weighted total 3.85/4.0
Date: 2026-06-17

---

## Part 1 — ADR-Level Scores (Manual)

| # | Dimension | Weight | CLI Score | Manual Score | Weighted | Override? |
|---|-----------|--------|-----------|--------------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 4 | 0.60 | No |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | No |
| 3 | Feature Checklist Completeness | 15% | 3 | **4** | **0.60** | **Yes — see below** |
| 4 | OBPI Decomposition Quality | 15% | 4 | 4 | 0.60 | No |
| 5 | Lane Assignment Correctness | 10% | 4 | 4 | 0.40 | No |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | No |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | No |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | No |

**MANUAL WEIGHTED TOTAL: 4.00/4.0**
(CLI: 3.85/4.0)

---

### Dimension-by-Dimension Rationale

**Dim 1 — Problem Clarity (CLI: 4 / Manual: 4)**

All five checklist items pass on evidence:
- One-sentence statement without jargon: "The QC machinery verifies receipt-presence, never truth — the ADR-0.0.37 facade reached VALIDATED."
- Concrete "before" with evidence: `gz adr audit` trust_model documented as "does NOT re-verify evidence"; GHI #623 facade is the named specimen; tautological test (`fixture == fixture`) satisfies coverage.
- Concrete "after" that is testable: `gz validate --qc-binding` exit 0; `gz adr fidelity ADR-0.0.73` exit 0.
- "So what?" immediate: "without a bound verification layer, nothing gzkit attests can be trusted; gzkit's premise is hollow."
- Problem explicitly scoped: "audits verify receipts, not truth" is the named class; not all auditing.

No CLI heuristic mismatch — the before/after language that triggers keyword detection is substantively present.

**Dim 2 — Decision Justification (CLI: 4 / Manual: 4)**

Four numbered decisions each carry an independent "why":
1. Registry classified `bound/advisory/unenforced` — "a checker is trustworthy only once its enforcement claim is recorded and classified"; derived-not-hand-maintained because "a hand-maintained list would itself be theater."
2. Behavioral negative-control detection — "behavioral detection beats declarative detection" (Boundary Invariant #3 encodes the rule).
3. `## Fidelity Assertions` block + `gz adr fidelity` gate — replaces "prose 'Demonstrate Value' step with a bound, runnable gate."
4. One gate, two consumers (closeout + audit) — "not duplicated prose."

Four alternatives engaged and dismissed with specific reasons:
- (a) Extend mechanical-defenses family: wrong subject level.
- (b) Add parallel sibling: not a sibling, it IS the general law.
- (c) Author fidelity-running as prose: exactly the defect being killed.
- (d) Keep trusting receipts: IS the defect.

Counterarguments (false-positive risk on `bound` vs. `advisory`, dishonest negative control) addressed in Consequences.

**Dim 3 — Feature Checklist Completeness (CLI: 3 / Manual: 4 — OVERRIDE)**

CLI heuristic: "Checklist items not prefixed with OBPI-."
Why this is a false negative: ADR checklist items are prose descriptions authored before OBPIs are created; OBPI- prefix on checklist items is not the project convention. The 1:1 mandate is satisfied by position (7 items → 7 OBPI files, confirmed by `ls obpis/`). The CLI heuristic fires on format shape, not content gap.

All 7 items evaluated for necessity and coverage:
1. QCStep registry — foundation for all subsequent OBPIs; removing it means no classifier.
2. `gz validate --qc-binding` — primary detection engine; removing means theater steps invisible.
3. `gz adr fidelity` gate — thesis-binding gate; removing means VALIDATED is still receipt-only.
4. Closeout/audit repoint — integrates gate into ceremony; removing leaves ceremony with prose step.
5. Dispatch-attestation absorption — closes the floating-pool gap; removing means concern is abandoned.
6. Self-check + facade regression corpus — the meta-test; removing means this ADR could be its own facade.
7. Evaluator truth-binding (GHI #624) — fixes the binding-mismatch in `gz adr evaluate` itself; removing leaves the evaluator in the class of defects this ADR governs.

No gaps visible. Ordering is logical (data model → validator → gate → ceremony → absorption → self-check → evaluator). Items are at consistent granularity. Decomposition Scorecard is filled in with rationale for 7.

**Dim 4 — OBPI Decomposition Quality (CLI: 4 / Manual: 4)**

OBPI-01: Data model layer, fully independent, 1-2 days.
OBPI-02: Validation scope, depends on OBPI-01 (registry exists), well-bounded, 2-4 days.
OBPI-03: New CLI verb + fidelity gate, independent of OBPI-02, 2-3 days.
OBPI-04: Ceremony integration, depends on OBPI-03 (verb must exist), 1.5-2 days.
OBPI-05: Pool absorption + extension of OBPI-01 surface, 0.5-1 day.
OBPI-06: Self-check + regression corpus, depends on OBPI-02/03 surfaces, 1-2 days.
OBPI-07: Evaluator rescore + QC registration, depends on OBPI-01/06, 2-3 days.

Dependency graph is acyclic: 01 → 02 → 06; 03 → 04; 03 → 06; 01 → 05; 01 + 06 → 07. Domain boundaries respected. No OBPI is monolithic or atomized. Numbering is gapless.

**Dim 5 — Lane Assignment Correctness (CLI: 4 / Manual: 4)**

Lite OBPIs (01, 05, 06): internal data model, pool annotation, regression tests — no new CLI surface. Correct.
Heavy OBPIs (02, 03, 04, 07): each introduces or modifies a CLI scope, CLI verb, ceremony runtime contract, or scoring algorithm with user-observable changes. Correct. Gate 3/4/5 obligations present in each Heavy brief.

**Dim 6 — Scope Discipline (CLI: 4 / Manual: 4)**

Three explicit non-goals with justification:
1. No back-fill onto already-VALIDATED ADRs — named as forced follow-up; reason: own ADR/chore.
2. No mechanical-defenses family consolidation — named future candidate; reason: separate concern.
3. No replacement of receipt/REQ-coverage checks — additive bind, not replacement.

Reversibility documented per decision (two-way vs. one-way door). The one-way door (Fidelity Assertions requirement) is operator-accepted and stated.

**Dim 7 — Evidence Requirements (CLI: 4 / Manual: 4)**

Every OBPI has concrete verification commands (not vague descriptions). Heavy OBPIs name Gate 3/4/5 criteria explicitly. The ADR itself carries a `## Fidelity Assertions` table with 6 runnable rows and expected exits — this ADR exemplifies its own proposal. "Done" is operationally defined for each OBPI through REQ IDs with proof channels.

**Dim 8 — Architectural Alignment (CLI: 4 / Manual: 4)**

Module paths are explicit throughout: `src/gzkit/qc_binding.py`, `src/gzkit/governance/trust_audits/qc_binding.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/quality.py`, `src/gzkit/fidelity.py`, `src/gzkit/commands/adr_fidelity.py`, `src/gzkit/commands/closeout_ceremony.py`, `src/gzkit/commands/audit_cmd.py`, `src/gzkit/adr_eval_scoring.py`.

Pydantic frozen models follow the established project pattern (`frozen=True, extra="forbid"`). The ports/adapters framing is the project's existing vocabulary. The `trust_audits/` module path follows the established directory pattern for governance checks.

Minor note: no positive exemplar file referenced; negative exemplar (ADR-0.0.37 facade) is well-used. This is mitigated by the explicit module paths serving as implementation exemplars.

---

## Part 2 — OBPI-Level Scores (Manual)

| OBPI | Independence | Testability | Value | Size | Clarity | Manual Avg | CLI Avg |
|------|-------------|-------------|-------|------|---------|------------|---------|
| 01 qc-step-registry | 4 | 4 | 4 | 4 | 4 | **4.0** | 4.0 |
| 02 qc-binding-scope | 4 | 4 | 4 | 3 | 4 | **3.8** | 3.6 |
| 03 fidelity-gate | 4 | 4 | 4 | 3 | 4 | **3.8** | 3.8 |
| 04 closeout-repoint | 3 | 4 | 4 | 3 | 4 | **3.6** | 3.8 |
| 05 dispatch-absorb | 4 | 4 | 4 | 4 | 4 | **4.0** | 4.0 |
| 06 self-check-corpus | 3 | 4 | 4 | 4 | 4 | **3.8** | 4.0 |
| 07 eval-truth-binding | 4 | 4 | 4 | 3 | 4 | **3.8** | 3.8 |

OBPI THRESHOLD: All averages >= 3.0. No dimension scored 1. **Threshold met.**

### OBPI Score Notes

**OBPI-02 Size (CLI: 2 / Manual: 3):** CLI gave size a 2, suggesting the scope is too large. Manual assessment: 6 theater signatures + behavioral negative-control + `gz check` wiring is substantial but well-bounded by the Allowed Paths. 2-4 days is within the 1-3 day band if the behavioral negative-control is treated as a single protocol applied per step, not 6 separate investigations. Score 3 (adequate, not deficient).

**OBPI-04 Independence (4 / Manual: 3):** Depends on OBPI-03 (`gz adr fidelity` verb must exist to invoke). The dependency is not listed in the OBPI-04 Prerequisites as a "STOP if missing" item — it is inferable from the Allowed Paths and objective, but not formally declared. Minor authoring gap. Score 3.

**OBPI-06 Independence (4 / Manual: 3):** Self-check tests invoke `gz validate --qc-binding` (OBPI-02) and `gz adr fidelity` (OBPI-03); without those, tests would verify non-existent CLI verbs. Neither OBPI-02 nor OBPI-03 is listed as a formal prerequisite in the OBPI-06 Discovery Checklist. Dependencies are inferable but not declared. Minor authoring gap. Score 3.

**Action item for OBPI-04 and OBPI-06 briefs:** Add OBPI-03 (and for OBPI-06, OBPI-02) to the Prerequisites → "Required path exists or is intentionally created in this OBPI" checklist as "OBPI-03 must have landed (verb `gz adr fidelity` must be registered)." This is a minor spec-tightening fix, not a blocker.

---

## Self-Referential Audit Notice

This evaluation was performed using the current `gz adr evaluate` CLI — the tool that OBPI-07 / GHI #624 identifies as grading prose shape and keywords rather than decision substance. Dims 1 and 2 both scored 4 from the CLI; the manual evaluation CONFIRMS those scores are substantively correct (the ADR's problem clarity and decision justification are genuinely exemplary). The current evaluator reached the right answer for the wrong reason (keyword patterns happen to be present because the problem IS well-stated). OBPI-07 fixes the tool to reach correct answers for the right reason — this evaluation is not compromised by the defect, but the defect is noted per AGENTS.md "flag and track" doctrine.

---

## Overall Verdict

| Gate | Threshold | Result |
|------|-----------|--------|
| ADR Weighted Total | >= 3.0 | 4.00/4.0 — **PASS** |
| OBPI Average (all) | >= 3.0 per OBPI | 3.6–4.0 — **PASS** |
| Any dimension scored 1? | Must be 0 | None — **PASS** |

**[x] GO — Ready for human proposal/defense review**
[ ] CONDITIONAL GO
[ ] NO GO

---

## Action Items

1. **(Non-blocking, Authoring)** OBPI-04 brief: add OBPI-03 to Prerequisites as a declared dependency ("`gz adr fidelity` verb must be registered before OBPI-04 implementation begins").
2. **(Non-blocking, Authoring)** OBPI-06 brief: add OBPI-02 and OBPI-03 to Prerequisites as declared dependencies.
3. **(Informational)** OBPI-06 Demo fenced block uses double-backtick (` `` `) instead of triple (` ``` `) — the `gz-validate-skip: command-shape` comment suppresses the check but the malformed fence should be corrected when the brief is updated.

None of the above are blockers for GO. The ADR is well-formed and ready for defense review.
