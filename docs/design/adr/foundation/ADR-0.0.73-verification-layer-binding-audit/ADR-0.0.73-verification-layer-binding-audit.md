---
id: ADR-0.0.73-verification-layer-binding-audit
status: Validated
kind: foundation
semver: 0.0.73
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-16
---

# ADR-0.0.73-verification-layer-binding-audit: Verification Layer Binding Audit

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
Treats governance not as overhead but as the discipline that keeps work honest.
The operative stance for this ADR: **a check is only real if it can fail for the
right reason**. A QC step that cannot fail its own negative control is theater no
matter how confident its docstring; an ADR marked VALIDATED whose thesis was never
run against the system is a receipt, not a verification. The work here is to bind
the checkers to behavior — and to make this ADR pass the very check it introduces.

## Why foundation tier?

Without a bound verification layer, gzkit is not gzkit: the project exists to make
stochastic LLM vibing structurally inert, and a QC machinery that verifies
receipt-presence instead of truth lets a facade reach VALIDATED (GHI #623). The
invariance test resolves **yes** — without this ADR, nothing gzkit attests can be
trusted, so the anti-vibing premise is hollow. Operator ruling at interview
(2026-06-16): foundation.

Port-vs-adapter: this ADR is a **port**. "Every QC step is bound to behavior, and
every ADR thesis is run against the running system before it is trusted" is the
abstract contract; `gz validate --qc-binding` (with its per-step negative controls)
and `gz adr fidelity` (running each ADR's `## Fidelity Assertions`) are the first
adapters behind it. The closeout and audit ceremonies are consumers of the same
port, never two prose copies of it.

## Intent

gzkit's premise — make stochastic LLM vibing structurally inert — is only as real as its verification layer, and nothing checks the checkers. The root defect is the GHI #623 facade: a hollow 'facade' implementation of ADR-0.0.37 survived all the way to VALIDATED because gzkit's QC machinery verifies receipt-presence and REQ-coverage, never truth. `gz adr audit` / `gz obpi audit` confirm that receipts exist and that every REQ has a covering test — but a tautology (fixture == fixture) satisfies coverage, and the gz-adr-audit trust_model is literally documented as 'does NOT re-verify evidence'. The one fidelity step in the audit ('Demonstrate Value') is agent-written prose graded by nothing, and dispatch-enforcement still lives in an unpromoted pool ADR (ADR-pool.obpi-pipeline-dispatch-attestation). Nothing mechanically holds an ADR's thesis against the running system. The only thing that caught the ADR-0.0.37 facade was operator skepticism — which does not scale and is not structural.

Before this ADR (current state): an ADR reaches VALIDATED on receipt-presence and REQ-coverage alone, and its thesis is never run against the running system — the checkers are unchecked. After this ADR (target state): every QC step is bound to behavior via a negative control, and every ADR thesis is executed against the running system before it is trusted.

This ADR is foundation by the invariance test: without a bound verification layer, nothing gzkit attests can be trusted; gzkit's premise (make vibing structurally inert) rests on the verification layer being real. In ports/adapters terms this IS the verification port — it points to invariance, not to a feature adapter.

Operator ratification (2026-06-16): design and interview answers approved verbatim; kind ruled foundation at interview. The Tier-2 forcing functions (pre-mortem, WWHTBT, constraint archaeology, assumption surfacing, 2am operator, reversibility, scope minimization) were agent-drafted against the GHI #623 facade evidence and operator-audited per AGENTS.md § Operator Economy claim 4; their content is folded into intent, decision, and consequences below. Constraint archaeology: 'audits verify receipts, not truth' was inherited convenience, never re-tested until the facade — tested now, it fails, and is removed. Assumption surfacing: the implicit assumption being killed is 'an ADR marked VALIDATED has been verified against the running system' — it has not; flip the core assumption (receipts cannot be trusted by default) and the whole design follows. Scope minimization: the smallest valuable version is parts 3+4 alone (the fidelity gate would have caught the ADR-0.0.37 facade); operator called FULL for the initial six OBPIs. Subsequent operator-directed corrections expanded the package to nine OBPIs: OBPI-07 homes GHI #624, OBPI-08 mechanizes fidelity-presence enforcement, and OBPI-09 addresses waiver-ratchet honesty.

## Decision

One mechanism, four parts, currently decomposed 1:1 into nine OBPIs. The original six-OBPI plan was expanded by operator-directed corrections: OBPI-07 homes GHI #624 (`gz adr evaluate` shape-vs-substance), OBPI-08 mechanizes fidelity-presence enforcement, and OBPI-09 addresses waiver-ratchet honesty. The 2026-06-19 recovery evaluation froze OBPI-08 and OBPI-09 until OBPI-02's repudiated behavioral-binding work was repaired and this ADR earned a fresh GO; that freeze was lifted later the same day — OBPI-02 (and OBPI-07) were repaired and re-attested (g0), OBPI-08 and OBPI-09 landed, and `gz adr fidelity ADR-0.0.73` passes 8/8, clearing the ADR for closeout.

1. **QC-step registry + classifier** (`QCStep` model, in `src/gzkit/qc_binding.py`). Every QC step self-registers into a registry, classified `bound` / `advisory` / `unenforced`, because a checker is trustworthy only once its enforcement claim is recorded and classified. The registry is DERIVED from what `gz check` actually runs — never a hand-maintained list (a hand-maintained list would itself be theater). `QCStep` is a frozen Pydantic model: `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`.

2. **`gz validate --qc-binding`** (in `gz check`, fail-closed exit 3; audit in `src/gzkit/governance/trust_audits/qc_binding.py`). The scope flags any QC step whose name/docstring claims enforcement its code does not deliver. Detection is BEHAVIORAL, not static heuristics alone: each step ships a negative-control fixture it MUST fail on; `--qc-binding` runs the step against its negative control, and a step that passes its own negative control is theater. Layered on top are theater signatures calibrated on the ADR-0.0.37 facade: mtime-where-the-name-says-content, empty-input-passes, copy-vs-self, fixture-only, skip-if-PASS, and prose-graded-by-nothing.

3. **`## Fidelity Assertions` block + `gz adr fidelity <ADR>` gate** (in `src/gzkit/fidelity.py` + `src/gzkit/commands/adr_fidelity.py`). Every ADR Decision ships a `## Fidelity Assertions` block: runnable commands that exercise the ADR's thesis against the real system, each with an expected exit. `gz adr fidelity <ADR>` RUNS them. `FidelityAssertion` is a frozen Pydantic model: `{adr_id, claim, command, expected_exit, observed, result}`. This is one standalone gate.

4. **Closeout + audit both invoke the fidelity gate** (`src/gzkit/commands/closeout_ceremony.py`, `src/gzkit/commands/audit_cmd.py`). BOTH the closeout ceremony and the audit ceremony invoke `gz adr fidelity`, replacing the prose 'Demonstrate Value' step with a bound, runnable gate. One gate, two consumers — not duplicated prose.

**Absorption.** This ADR absorbs ADR-pool.obpi-pipeline-dispatch-attestation (its dispatch-attestation concern is the same 'checker not bound' class) and MUST pass its OWN check (`gz validate --qc-binding` over the new scopes; `gz adr fidelity ADR-0.0.73` over this ADR's own Fidelity Assertions).

**Evaluator truth-binding (OBPI-07, homing GHI #624).** `gz adr evaluate` is itself a QC step the mechanism above already governs, surfaced as the first caught instance of the very failure class this ADR exists to kill. It self-registers into the part-1 registry classified `advisory` — it grades quality, it does not gate — and part-2 `gz validate --qc-binding` flags the binding-mismatch it currently exhibits: it renders authoritative dimension scores feeding a GO/NO-GO verdict while its dim-1 (Problem Clarity) and dim-2 (Decision Justification) checks grade only prose SHAPE and KEYWORDS (`_has_keywords` substring membership + a numbered-list regex in `src/gzkit/adr_eval_scoring.py`), not decision truth — so a facade ADR that stuffs the keywords scores high and a rigorous ADR phrased without them is floored to 1 (GHI #624). OBPI-07 is the concrete remediation: the dim-1/dim-2 (and any sibling) heuristics are replaced with checks that grade decision SUBSTANCE (structural presence of weighed alternatives, honest consequences, rationale linkage) such that no truth-score is satisfiable by keyword presence alone and rigorous-but-differently-phrased prose is not floored; and a seventh `shape-graded-not-substance` theater signature — calibrated on GHI #624, distinct from the six ADR-0.0.37 signatures — is added to OBPI-06's facade regression corpus so the evaluator's own former failure mode stays caught.

**Fidelity-presence enforcement (OBPI-08).** Boundary Invariant #4 cannot remain prose-only: `gz validate --fidelity-presence` must fail closed on any new non-pool ADR Decision lacking a parseable `## Fidelity Assertions` block, run inside `gz check`, and keep pre-existing block-less ADRs visible as explicit grandfathered debt rather than silently laundering the bypass.

**Waiver-ratchet honesty (OBPI-09).** Waiver, grandfather, and baseline surfaces that gate `gz check` must carry a closed-set lock, ledger-derived dated cutover, or monotonic shrink-ratchet. `gz validate --waiver-ratchet` is the meta-validator that keeps waiver lists from turning "not built yet" into "attested green."

**Recovery freeze (2026-06-19, lifted).** OBPI-02 was repudiated in its own brief because the central behavioral mechanism shipped green-by-construction; while repudiated, this ADR was a NO GO planning artifact and OBPI-08/OBPI-09 were held at Draft. The freeze was lifted 2026-06-19: OBPI-02's behavioral binding was repaired and re-attested (g0; the verification-invalid repudiation cleared), OBPI-07 was likewise repaired and re-attested, OBPI-08 and OBPI-09 landed, and all Fidelity Assertions below pass (`gz adr fidelity ADR-0.0.73` → 8 pass, 0 fail). The ADR now passes its own check (Boundary Invariant #5) and is cleared for closeout.

**Data model (Pydantic frozen).** `QCStep{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; `FidelityAssertion{adr_id, claim, command, expected_exit, observed, result}`.

**Reversibility (mixed door).** The `gz validate --qc-binding` scope is a two-way door (removable in one commit). The `## Fidelity Assertions` requirement on every ADR Decision is a ONE-WAY door — removing it re-opens the facade — and is the load-bearing commitment, operator-accepted. At 2am, a broken ADR means the operator runs `gz adr fidelity <ADR>` and reads which assertion failed (observed-vs-expected exit), not prose; the fidelity gate delivers exactly that.

**Forced downstream decisions.** The real ADR-0.0.37 corpus rebuild must ship fidelity assertions; a back-fill-and-recheck sweep for already-VALIDATED foundation ADRs is forced (its own chore/ADR); the contract-surface-mechanical-defenses family may fold under this ADR as its general law.

**Scope boundary — what this ADR does NOT do:** It does NOT itself back-fill fidelity assertions onto already-VALIDATED ADRs (that is the forced follow-up sweep); it does NOT fold the mechanical-defenses family in this ADR (named future candidate); it does NOT replace receipt/REQ-coverage checks — it binds them to behavior on top.

## Fidelity Assertions

<!-- Part 4 of the Decision: every ADR Decision ships runnable commands that
     exercise its thesis against the real system. `gz adr fidelity ADR-0.0.73`
     RUNS these (FidelityAssertion: claim / command / expected_exit / observed /
     result). This ADR MUST pass its own check. While OBPI-03 builds the runner,
     these assertions are authored against the surfaces this ADR ships; each
     becomes green as its owning OBPI lands. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The QC-binding scope exists and is wired into `gz check`, fail-closed. | uv run gz validate --qc-binding | 0 |
| This ADR passes its own QC-binding check (self-check, OBPI-06). | uv run gz validate --qc-binding | 0 |
| The fidelity gate exists and the Fidelity Assertions block is parseable by the gate. | uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit --check | 0 |
| The dispatch-attestation pool concern is no longer a free-floating unpromoted item. | uv run gz state | 0 |
| The ADR evaluator is a registered QC step bound to substance — `--qc-binding` finds no shape-graded-as-authoritative mismatch (OBPI-07, GHI #624). | uv run gz validate --qc-binding | 0 |
| Every bound QC step has a genuine negative control; acknowledged `_NEGATIVE_CONTROL_DEBT` is empty. | uv run python -c "from gzkit.governance.trust_audits.qc_binding import _NEGATIVE_CONTROL_DEBT; raise SystemExit(0 if len(_NEGATIVE_CONTROL_DEBT) == 0 else 3)" | 0 |
| Fidelity-presence enforcement exists and is green over the current corpus (OBPI-08). | uv run gz validate --fidelity-presence | 0 |
| Waiver-ratchet honesty enforcement exists and is green over registered waiver surfaces (OBPI-09). | uv run gz validate --waiver-ratchet | 0 |

> Each assertion is a `FidelityAssertion{adr_id, claim, command, expected_exit, observed, result}`.
> The recovery rows above are intentionally red until OBPI-02 is repaired and
> OBPI-08/09 land. A passing parse-only check is not sufficient evidence for
> this ADR; `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` must
> run the table and pass every row before closeout resumes.

## Consequences

### Positive

1. **The verification layer becomes self-verifying.** The checkers are themselves checked, closing the 'nothing checks the checkers' gap that GHI #623 exposed.

2. **Theater signatures are mechanically caught.** The six facade signatures calibrated on ADR-0.0.37 (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing) become detectable, not operator-dependent.

3. **Every ADR thesis is held against the running system.** `gz adr fidelity` RUNS the Decision's claims, so 'VALIDATED' stops meaning 'receipts present' and starts meaning 'thesis exercised'.

4. **The facade failure class becomes structurally inert.** The only thing that caught ADR-0.0.37 (operator skepticism) is now a fail-closed gate rather than a person who happened to be paying attention.

5. **Behavioral detection beats declarative detection.** The negative-control fixture means a hollow step that self-registers as 'bound' with a confident docstring still fails, because it cannot fail its own negative control.

6. **The dispatch-attestation pool concern lands bound.** Absorbing ADR-pool.obpi-pipeline-dispatch-attestation removes a floating unpromoted checker-not-bound item.

### Negative

1. **Authoring cost.** Every ADR Decision must now author runnable fidelity assertions and every QC step must author an honest negative-control fixture. This is real, ongoing labor; OBPI-06 (self-check + facade regression corpus) is the mitigation that keeps the authors honest.

2. **One-way door.** The `## Fidelity Assertions` requirement cannot be cheaply reversed; removing it re-opens the facade. Operator-accepted as the load-bearing commitment.

3. **Forced back-fill sweep.** Already-VALIDATED foundation ADRs lack fidelity assertions; a back-fill-and-recheck sweep is now owed (its own chore/ADR), and until it runs those ADRs remain receipt-validated only.

4. **Pre-mortem failure (18 months out): detection stayed declarative.** A hollow step self-registers as 'bound' with a docstring claiming enforcement, a static check sees the right shape and passes. Mitigation baked in: detection is behavioral (negative-control-per-step that `--qc-binding` runs), not static-shape matching.

5. **Shakiest WWHTBT condition.** The registry must be derived from what `gz check` actually runs AND negative-controls must be authored honestly per step. A dishonest negative control (one the step trivially fails for the wrong reason) is the residual risk; OBPI-06's self-check + regression corpus is the only guard, and it is itself subject to `--qc-binding`. **Honest status (OBPI-06):** of the 34 `bound` steps, only the `qc-binding` step is wired with a genuine negative control so far; the remaining 33 are enumerated as acknowledged `_NEGATIVE_CONTROL_DEBT` (OBPI-0.0.73-02 promised "each step ships a fixture it must fail on" but deferred the wiring — tracked OBPI-02 correction). A green-by-emptiness guard makes any *unwired, unacknowledged* bound step a fail-closed finding, so coverage cannot regress silently and the backlog stays visible rather than passing as "nothing to check."

6. **False-positive risk.** A legitimately advisory step could be mis-flagged as theater. Mitigation: the `bound`/`advisory`/`unenforced` classification is explicit, and advisory steps are not required to fail a negative control.

## Boundary Invariants

1. **The QC-step registry is derived, never hand-maintained.** The registry is
   built from what `gz check` actually runs; a hand-curated list of steps is
   itself theater and is forbidden.
   (REQ-0.0.73-01-05: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
2. **`gz validate --qc-binding` is fail-closed and runs inside `gz check`.** The
   scope exits 3 on any theater finding and is part of the default `gz check`
   pipeline — it cannot be a green-by-default opt-in.
   (REQ-0.0.73-02-06: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
3. **Detection is behavioral, not static-shape alone.** Every QC step classified
   `bound` MUST fail its own negative-control fixture when `--qc-binding` runs it;
   a step that passes its negative control is theater regardless of its docstring.
   (REQ-0.0.73-02-07: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
4. **Every ADR Decision carries a runnable `## Fidelity Assertions` block (one-way
   door).** `gz adr fidelity <ADR>` RUNS those commands and compares observed-vs-
   expected exit; the requirement may never be removed — doing so re-opens the
   facade.
   (REQ-0.0.73-03-06: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
5. **This ADR passes its own check.** `gz validate --qc-binding` and
   `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` are green over
   this ADR's own scopes and Fidelity Assertions — no facade-of-the-facade.
   (REQ-0.0.73-06-05: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
6. **The ADR evaluator never presents shape as authoritative substance (registered
   QC step).** `gz adr evaluate` is a STRUCTURAL-COMPLETENESS lint: its deterministic
   dimensions and verdict grade section presence/depth only and are labelled as such,
   never as a quality or substance judgment. Decision SUBSTANCE is graded ONLY by a
   recorded, disciplined judge verdict (the record-and-validate judge channel,
   `gzkit.adr_eval_substance`), or reported `UNGRADED` — it is never derived from the
   deterministic scores, and the two channels carry distinct labels and are never
   composited. `gz adr evaluate` self-registers as a QC step classified `advisory`
   subject to `gz validate --qc-binding`, so any regression to presenting a
   shape-derived score as authoritative substance is a binding-mismatch finding, never
   a silent pass. (Originally "grade substance, not shape"; reworded 2026-06-19 after
   that letter produced a cosmetic keyword-grading facade — OBPI-07 repudiation. The
   honest contract is non-pretense + a disciplined judge channel, not the mirage of
   deterministic substance grading.)
   (REQ-0.0.73-07-06: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
7. **`## Fidelity Assertions` presence is mechanically enforced (fail-closed).**
   `gz validate --fidelity-presence` exits 3 on any non-pool ADR Decision lacking
   a parseable block and runs inside `gz check`; pre-existing block-less ADRs are
   explicit grandfathered debt and a NEW ADR cannot reach VALIDATED block-less.
   Boundary Invariant #4 is no longer prose-only — the block-less bypass that let
   an ADR reach VALIDATED with its thesis never exercised is closed.
   (REQ-0.0.73-08-05: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
8. **Every waiver/grandfather/baseline surface is honest-ratcheted (fail-closed).**
   Each registered waiver, grandfather, or baseline list that gates a `gz check`
   step MUST carry exactly one of: a closed-set lock (`added_under`, as in
   `historical_self_close_waivers`), a ledger-derived dated cutover (as in
   `lock_handoff_coupling`), or a monotonic shrink-ratchet (a committed baseline
   the list can only decrease against). `gz validate --waiver-ratchet` exits 3 on
   any waiver surface lacking one of the three and runs inside `gz check`. An
   unratcheted waiver launders "not built" into "attested green" — the same facade
   class this ADR exists to close, one layer up. The verb self-registers as a QC
   step subject to `--qc-binding` (no facade-of-the-facade).
   (REQ-0.0.73-09-06: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 8
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 9

<!-- Baseline selected 6 (within the 5+ range): OBPI-07 (evaluate-truth-binding)
     was added 2026-06-16 as an operator-directed scope expansion homing GHI #624
     (gz adr evaluate shape-vs-substance). The evaluator (src/gzkit/adr_eval*.py)
     is a distinct unit the verification-layer mechanism governs, so the baseline
     is selected at 6; with the surface-boundary split (1) the Final Target was
     6 + 1 = 7. OBPI-08 (fidelity-presence enforcement) was added 2026-06-18 as an
     operator-directed CORRECTION: the adversarial audit of OBPI-01..05 found that
     Boundary Invariant #4 (every ADR Decision carries a runnable block) had no
     mechanical enforcement — a block-less ADR reaches VALIDATED unchecked. OBPI-08
     mechanizes BI #4 (a distinct validator surface), so the Final Target is 8.
     OBPI-09 (waiver-ratchet honesty contract) was added 2026-06-18 as an
     operator-directed CORRECTION: a blast-radius determination of the
     unratcheted-self-waiver defect proven for _NEGATIVE_CONTROL_DEBT (OBPI-02)
     found the same no-shrink-force pattern recurs across ~9 of 13 waiver/
     grandfather/baseline surfaces (worst: behave_coverage_waivers, 521 unlocked
     self-exemptions from the BDD gate). The waiver-ratchet meta-validator is a
     distinct surface the verification-layer mechanism governs, so the Final
     Target is 9. The 1:1 mandate holds: checklist (9) <-> OBPI files (9). -->


## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] Registry + classifier model — `QCStep` Pydantic frozen model `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; registry DERIVED from what `gz check` actually runs (never hand-maintained); unit tests
- [ ] `gz validate --qc-binding` scope — behavioral negative-control (each step ships a fixture it must fail on; the scope runs it) + theater-signature detection (the six ADR-0.0.37 facade signatures); wired into `gz check`; fail-closed exit 3; manpage + `gz cli audit` green; unit tests
- [ ] `## Fidelity Assertions` schema + `gz adr fidelity` gate — `FidelityAssertion` Pydantic frozen model `{adr_id, claim, command, expected_exit, observed, result}`; `## Fidelity Assertions` block parsed from the ADR Decision; `gz adr fidelity <ADR>` RUNS the commands and compares observed-vs-expected exit; one standalone gate; manpage + `gz cli audit` green; unit tests
- [ ] Closeout/audit repoint onto the fidelity gate — both the closeout ceremony and the audit ceremony invoke `gz adr fidelity`, replacing the prose 'Demonstrate Value' step; runbook + governance_runbook updated; unit tests
- [ ] Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into this ADR's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests
- [ ] Self-check + facade regression corpus — this ADR passes its OWN `gz validate --qc-binding`; one regression fixture per theater signature (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing); `gz adr fidelity ADR-0.0.73` green over this ADR's own Fidelity Assertions; unit tests
- [ ] Evaluator truth-binding — replace the `gz adr evaluate` dim-1/dim-2 format/keyword heuristics in `src/gzkit/adr_eval_scoring.py` with decision-substance checks (no truth-score satisfiable by keyword/format presence alone); register `gz adr evaluate` as a QC step classified `advisory` (subject to `gz validate --qc-binding`); add a seventh `shape-graded-not-substance` theater signature to the facade regression corpus; manpage + `gz cli audit` green; unit tests
- [ ] Fidelity-presence enforcement (mechanizes Boundary Invariant #4) — `gz validate --fidelity-presence` fails closed (exit 3) on any non-pool ADR Decision lacking a parseable `## Fidelity Assertions` block; wired into `gz check`; pre-existing block-less ADRs grandfathered in an explicit data file (fail-closed on NEW ADRs only, per the sensitivity-floor cutover precedent); ADR template seeds the block stub; the ADR's own `## Fidelity Assertions` gains a row for the new verb; manpage + `gz cli audit` green; unit tests. Closes the block-less-ADR bypass the OBPI-04 adversarial audit surfaced — without it "VALIDATED = thesis exercised" is false for every block-less ADR (operator-directed correction, 2026-06-18).
- [ ] Waiver-ratchet honesty contract + meta-validator (mechanizes Boundary Invariant #8) — `gz validate --waiver-ratchet` fails closed (exit 3) on any registered waiver/grandfather/baseline surface that gates a `gz check` step and lacks one of {closed-set lock `added_under`, ledger-derived dated cutover, monotonic shrink-ratchet against a committed baseline}; templatized from the proven `historical_self_close_waivers` and `lock_handoff_coupling` patterns; retrofit the unratcheted surfaces surfaced by the 2026-06-18 blast-radius determination (`behave_coverage_waivers` [worst — 521 entries, no lock], `tautological_test_waivers` [self-exempt], `_NEGATIVE_CONTROL_DEBT`, `sensitivity_floor_grandfather`, `tautological_test_baseline`, `interview_transcript_waivers`, complexity thresholds, `chores_layout_waivers`, `req_kind_grandfathering`); the verb self-registers as a QC step subject to `--qc-binding`; wired into `gz check`; manpage + `gz cli audit` green; unit tests. An unratcheted waiver launders "not built" into "attested green" — the facade class this ADR closes, one layer up (operator-directed correction, 2026-06-18).

## Q&A Transcript

<!-- Interview transcript preserved for context -->

> Supersession note (2026-06-19): the transcript below records the original
> six-OBPI interview state. It is historical context, not the current contract.
> The authoritative current decomposition is nine OBPIs, as recorded in
> Decision, Decomposition Scorecard, Checklist, and EVALUATION_SCORECARD.md.

*Interview conducted: 2026-06-16T05:48:29.175741*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.73-verification-layer-binding-audit

### Q: What is the title of this ADR?

**A:** Verification Layer Binding Audit

### Q: What is the semantic version?

**A:** 0.0.73

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's premise — make stochastic LLM vibing structurally inert — is only as real as its verification layer, and nothing checks the checkers. The root defect is the GHI #623 facade: a hollow 'facade' implementation of ADR-0.0.37 survived all the way to VALIDATED because gzkit's QC machinery verifies receipt-presence and REQ-coverage, never truth. `gz adr audit` / `gz obpi audit` confirm that receipts exist and that every REQ has a covering test — but a tautology (fixture == fixture) satisfies coverage, and the gz-adr-audit trust_model is literally documented as 'does NOT re-verify evidence'. The one fidelity step in the audit ('Demonstrate Value') is agent-written prose graded by nothing, and dispatch-enforcement still lives in an unpromoted pool ADR (ADR-pool.obpi-pipeline-dispatch-attestation). Nothing mechanically holds an ADR's thesis against the running system. The only thing that caught the ADR-0.0.37 facade was operator skepticism — which does not scale and is not structural.

Before this ADR (current state): an ADR reaches VALIDATED on receipt-presence and REQ-coverage alone, and its thesis is never run against the running system — the checkers are unchecked. After this ADR (target state): every QC step is bound to behavior via a negative control, and every ADR thesis is executed against the running system before it is trusted.

This ADR is foundation by the invariance test: without a bound verification layer, nothing gzkit attests can be trusted; gzkit's premise (make vibing structurally inert) rests on the verification layer being real. In ports/adapters terms this IS the verification port — it points to invariance, not to a feature adapter.

Operator ratification (2026-06-16): design and interview answers approved verbatim; kind ruled foundation at interview. The Tier-2 forcing functions (pre-mortem, WWHTBT, constraint archaeology, assumption surfacing, 2am operator, reversibility, scope minimization) were agent-drafted against the GHI #623 facade evidence and operator-audited per AGENTS.md § Operator Economy claim 4; their content is folded into intent, decision, and consequences below. Constraint archaeology: 'audits verify receipts, not truth' was inherited convenience, never re-tested until the facade — tested now, it fails, and is removed. Assumption surfacing: the implicit assumption being killed is 'an ADR marked VALIDATED has been verified against the running system' — it has not; flip the core assumption (receipts cannot be trusted by default) and the whole design follows. Scope minimization: the smallest valuable version is parts 3+4 alone (the fidelity gate would have caught the ADR-0.0.37 facade); operator called FULL — all six OBPIs ship.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** One mechanism, four parts, decomposed 1:1 into six OBPIs:

1. **QC-step registry + classifier** (`QCStep` model, in `src/gzkit/qc_binding.py`). Every QC step self-registers into a registry, classified `bound` / `advisory` / `unenforced`, because a checker is trustworthy only once its enforcement claim is recorded and classified. The registry is DERIVED from what `gz check` actually runs — never a hand-maintained list (a hand-maintained list would itself be theater). `QCStep` is a frozen Pydantic model: `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`.

2. **`gz validate --qc-binding`** (in `gz check`, fail-closed exit 3; audit in `src/gzkit/governance/trust_audits/qc_binding.py`). The scope flags any QC step whose name/docstring claims enforcement its code does not deliver. Detection is BEHAVIORAL, not static heuristics alone: each step ships a negative-control fixture it MUST fail on; `--qc-binding` runs the step against its negative control, and a step that passes its own negative control is theater. Layered on top are theater signatures calibrated on the ADR-0.0.37 facade: mtime-where-the-name-says-content, empty-input-passes, copy-vs-self, fixture-only, skip-if-PASS, and prose-graded-by-nothing.

3. **`## Fidelity Assertions` block + `gz adr fidelity <ADR>` gate** (in `src/gzkit/fidelity.py` + `src/gzkit/commands/adr_fidelity.py`). Every ADR Decision ships a `## Fidelity Assertions` block: runnable commands that exercise the ADR's thesis against the real system, each with an expected exit. `gz adr fidelity <ADR>` RUNS them. `FidelityAssertion` is a frozen Pydantic model: `{adr_id, claim, command, expected_exit, observed, result}`. This is one standalone gate.

4. **Closeout + audit both invoke the fidelity gate** (`src/gzkit/commands/closeout_ceremony.py`, `src/gzkit/commands/audit_cmd.py`). BOTH the closeout ceremony and the audit ceremony invoke `gz adr fidelity`, replacing the prose 'Demonstrate Value' step with a bound, runnable gate. One gate, two consumers — not duplicated prose.

**Absorption.** This ADR absorbs ADR-pool.obpi-pipeline-dispatch-attestation (its dispatch-attestation concern is the same 'checker not bound' class) and MUST pass its OWN check (`gz validate --qc-binding` over the new scopes; `gz adr fidelity ADR-0.0.73` over this ADR's own Fidelity Assertions).

**Data model (Pydantic frozen).** `QCStep{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; `FidelityAssertion{adr_id, claim, command, expected_exit, observed, result}`.

**Reversibility (mixed door).** The `gz validate --qc-binding` scope is a two-way door (removable in one commit). The `## Fidelity Assertions` requirement on every ADR Decision is a ONE-WAY door — removing it re-opens the facade — and is the load-bearing commitment, operator-accepted. At 2am, a broken ADR means the operator runs `gz adr fidelity <ADR>` and reads which assertion failed (observed-vs-expected exit), not prose; the fidelity gate delivers exactly that.

**Forced downstream decisions.** The real ADR-0.0.37 corpus rebuild must ship fidelity assertions; a back-fill-and-recheck sweep for already-VALIDATED foundation ADRs is forced (its own chore/ADR); the contract-surface-mechanical-defenses family may fold under this ADR as its general law.

**Scope boundary — what this ADR does NOT do:** It does NOT itself back-fill fidelity assertions onto already-VALIDATED ADRs (that is the forced follow-up sweep); it does NOT fold the mechanical-defenses family in this ADR (named future candidate); it does NOT replace receipt/REQ-coverage checks — it binds them to behavior on top.

### Q: What good things result from this decision? List benefits.

**A:** 1. **The verification layer becomes self-verifying.** The checkers are themselves checked, closing the 'nothing checks the checkers' gap that GHI #623 exposed.

2. **Theater signatures are mechanically caught.** The six facade signatures calibrated on ADR-0.0.37 (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing) become detectable, not operator-dependent.

3. **Every ADR thesis is held against the running system.** `gz adr fidelity` RUNS the Decision's claims, so 'VALIDATED' stops meaning 'receipts present' and starts meaning 'thesis exercised'.

4. **The facade failure class becomes structurally inert.** The only thing that caught ADR-0.0.37 (operator skepticism) is now a fail-closed gate rather than a person who happened to be paying attention.

5. **Behavioral detection beats declarative detection.** The negative-control fixture means a hollow step that self-registers as 'bound' with a confident docstring still fails, because it cannot fail its own negative control.

6. **The dispatch-attestation pool concern lands bound.** Absorbing ADR-pool.obpi-pipeline-dispatch-attestation removes a floating unpromoted checker-not-bound item.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Authoring cost.** Every ADR Decision must now author runnable fidelity assertions and every QC step must author an honest negative-control fixture. This is real, ongoing labor; OBPI-06 (self-check + facade regression corpus) is the mitigation that keeps the authors honest.

2. **One-way door.** The `## Fidelity Assertions` requirement cannot be cheaply reversed; removing it re-opens the facade. Operator-accepted as the load-bearing commitment.

3. **Forced back-fill sweep.** Already-VALIDATED foundation ADRs lack fidelity assertions; a back-fill-and-recheck sweep is now owed (its own chore/ADR), and until it runs those ADRs remain receipt-validated only.

4. **Pre-mortem failure (18 months out): detection stayed declarative.** A hollow step self-registers as 'bound' with a docstring claiming enforcement, a static check sees the right shape and passes. Mitigation baked in: detection is behavioral (negative-control-per-step that `--qc-binding` runs), not static-shape matching.

5. **Shakiest WWHTBT condition.** The registry must be derived from what `gz check` actually runs AND negative-controls must be authored honestly per step. A dishonest negative control (one the step trivially fails for the wrong reason) is the residual risk; OBPI-06's self-check + regression corpus is the only guard, and it is itself subject to `--qc-binding`.

6. **False-positive risk.** A legitimately advisory step could be mis-flagged as theater. Mitigation: the `bound`/`advisory`/`unenforced` classification is explicit, and advisory steps are not required to fail a negative control.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Registry + classifier model — `QCStep` Pydantic frozen model `{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`; registry DERIVED from what `gz check` actually runs (never hand-maintained); unit tests
2. `gz validate --qc-binding` scope — behavioral negative-control (each step ships a fixture it must fail on; the scope runs it) + theater-signature detection (the six ADR-0.0.37 facade signatures); wired into `gz check`; fail-closed exit 3; manpage + `gz cli audit` green; unit tests
3. `## Fidelity Assertions` schema + `gz adr fidelity` gate — `FidelityAssertion` Pydantic frozen model `{adr_id, claim, command, expected_exit, observed, result}`; `## Fidelity Assertions` block parsed from the ADR Decision; `gz adr fidelity <ADR>` RUNS the commands and compares observed-vs-expected exit; one standalone gate; manpage + `gz cli audit` green; unit tests
4. Closeout/audit repoint onto the fidelity gate — both the closeout ceremony and the audit ceremony invoke `gz adr fidelity`, replacing the prose 'Demonstrate Value' step; runbook + governance_runbook updated; unit tests
5. Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into this ADR's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests
6. Self-check + facade regression corpus — this ADR passes its OWN `gz validate --qc-binding`; one regression fixture per theater signature (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing); `gz adr fidelity ADR-0.0.73` green over this ADR's own Fidelity Assertions; unit tests

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **(a) Extend the contract-surface-mechanical-defenses family.** REJECTED: that family's subject is content prose (one level down) — the checkers' subject is the QC steps themselves, one level up. Extending it would conflate two different subjects. The mechanical-defenses family may instead fold UNDER this ADR as a special case of its general law.

2. **(b) Add a fourth parallel mechanical-defenses sibling.** REJECTED: this is not a sibling of the existing defenses — it is the general law that governs whether ANY checker is bound. A parallel sibling would re-create the very 'unbound checker' problem at one more level.

3. **(c) Author fidelity-running as prose in both the closeout and audit ceremonies.** REJECTED: duplicated unbound prose is the EXACT defect this ADR exists to kill ('Demonstrate Value' was prose graded by nothing). One bound gate (`gz adr fidelity`) invoked by both ceremonies, never two prose copies.

4. **(d) Keep trusting receipts (do nothing).** REJECTED: trusting receipt-presence over truth IS the defect — it is what let the ADR-0.0.37 facade reach VALIDATED.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **(a) Extend the contract-surface-mechanical-defenses family.** REJECTED: that family's subject is content prose (one level down) — the checkers' subject is the QC steps themselves, one level up. Extending it would conflate two different subjects. The mechanical-defenses family may instead fold UNDER this ADR as a special case of its general law.

2. **(b) Add a fourth parallel mechanical-defenses sibling.** REJECTED: this is not a sibling of the existing defenses — it is the general law that governs whether ANY checker is bound. A parallel sibling would re-create the very 'unbound checker' problem at one more level.

3. **(c) Author fidelity-running as prose in both the closeout and audit ceremonies.** REJECTED: duplicated unbound prose is the EXACT defect this ADR exists to kill ('Demonstrate Value' was prose graded by nothing). One bound gate (`gz adr fidelity`) invoked by both ceremonies, never two prose copies.

4. **(d) Keep trusting receipts (do nothing).** REJECTED: trusting receipt-presence over truth IS the defect — it is what let the ADR-0.0.37 facade reach VALIDATED.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.73 | Completed | g0 | 2026-06-19 | Completed |
