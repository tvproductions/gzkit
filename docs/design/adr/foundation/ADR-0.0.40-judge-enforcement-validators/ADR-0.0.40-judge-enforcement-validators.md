---
id: ADR-0.0.40-judge-enforcement-validators
status: Draft
kind: foundation
semver: 0.0.40
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-06
promoted_from: ADR-pool.judge-enforcement-validators
---

# ADR-0.0.40-judge-enforcement-validators: Judge Enforcement Validators

## Persona

Active persona: `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.

This ADR closes the doctrinal-to-mechanical gap left by ADR-0.0.39. Validator authoring requires reading the canonical schema (OBPI-0.0.39-02) before writing the audit; reading the existing `_UTF8_PIPE_WAIVERS` and `data/security_surfaces.json` patterns before designing the leakage waiver registry; reading every existing judge surface (gz-adr-evaluate red-team, advisor(), complexity-distill) before drafting the retrofit. Vibe-shaped validator implementation — pattern-matching another validator's structure without verifying the actual receipt-emit shape — is the canonical failure mode this ADR's careful sequencing exists to prevent. Honest enumeration of mitigation gaps in the retrofit is craft, not deference; concealing a gap to ship faster reproduces the doctrine-drift class the survey paper names.

## Why foundation tier?

Without this ADR, judge outputs have no mechanical enforcement — judges can leak training-corpus bias, output unstructured prose, or self-attest verdicts that don't bind to evidence, and the judge contract from ADR-0.0.39 stays honor-system.

This ADR authors a port: the judge-enforcement validator contract (leakage scope, output discipline scope, meta-eval CLI) that every judge surface must pass.

## Intent

**Current state.** ADR-0.0.39 codifies the LLM-as-judge doctrine and lands the `JudgeInvocation` schema. The schema is the contract; nothing yet enforces it. Specifically: (a) **preference-leakage** is unflagged across the existing receipt corpus — `gz-adr-evaluate --red-team` and runtime `advisor()` likely run same-family judging today; (b) **output discipline** is unenforced — receipts could (in principle) populate `verdict` without `explanation_text` and pass; (c) **meta-evaluation cadence** has no executor — the doctrine names a cadence but no command computes the kappa metric; (d) **existing surfaces** still emit pre-schema receipts because the retrofit hasn't run. ADR-0.0.39 is, until this ADR closes, a Promotable-but-unpromoted rule per `docs/governance/advisory-rules-audit.md` — the canonical anti-pattern the maxim disqualifies.

**This ADR closes the loop.** Five surfaces, each a separately-named OBPI:
- `arb-step-judge-*` canonical slots reserved (OBPI-0.0.39-02) → ARB middleware validates judge-prefixed receipts at emit time (OBPI-0.0.40-01, this ADR);
- `gz validate --judge-leakage` (OBPI-0.0.40-02) — same-family detection across the receipt corpus, with `data/judge_leakage_waivers.json` honoring named exceptions;
- `gz validate --judge-output-discipline` (OBPI-0.0.40-03) — explanation-precedes-verdict + methodology + three-axis + bias-mitigations enforcement;
- `gz judge meta-eval` (OBPI-0.0.40-04) — Cohen's kappa over a sampled window with configurable floor;
- Existing-surface retrofit (OBPI-0.0.40-05) — `gz-adr-evaluate --red-team` populates JudgeInvocation fields; `CLAUDE.md` § Advisor Tool documents bias profile and named "do not invoke" cases; historical receipts backfilled via waiver.

**The state before this ADR.** Today (post-0.0.39 close), gzkit has the doctrine (rule file, schema, classification baseline) but no fail-closed validators, no meta-eval CLI, no compliant-emit retrofit on existing judge surfaces. **The state after.** Every JudgeInvocation field is mechanically validated; every same-family judging pair is flagged or waived with cited rationale; every judge-correctness drift is detectable via the meta-eval cadence; every existing judge surface emits compliant receipts. LLM-as-judge in gzkit becomes structurally bounded.

**Survey-paper alignment.** The arxiv 2411.15594 paper names **preference leakage** as a bias *"harder to detect compared to previously identified biases"* and proposes the J-Detector framework for leakage detection. gzkit's `gz validate --judge-leakage` is the family-match-based version of that detection; the validator's diagnostic explicitly cites the paper's preference-leakage class so future operators reading a flagged receipt understand the structural concern. **Cohen's kappa** is the conventional meta-eval metric; the `--metric` flag accommodates Krippendorff's alpha or Fleiss' kappa for >2 raters per ADR-0.0.39 § Risks.

## Decision

_[To be filled at promotion time]_

Sketch:

1. **`gz validate --judge-leakage`** (new validator scope, Authoritative axis per ADR-0.0.38). Scans every judge invocation receipt under `artifacts/receipts/judge-*.json` and the historical ledger; flags same-family judge⇄candidate pairs; fail-closes (exit 3) under heavy lane unless an explicit waiver in `data/judge_leakage_waivers.json` covers the case with cited rationale.
2. **`gz validate --judge-output-discipline`** (new validator scope, Authoritative axis). Verifies that every judge invocation receipt carries: explanation_text populated AND positioned BEFORE verdict in the prompt, methodology field declared from the menu enum, bias_mitigations field naming applied mitigations, three-axis declaration. Fail-closes on missing fields or out-of-order explanation/verdict.
3. **`gz judge meta-eval`** (new CLI verb, Evidentiary axis). Produces the human-agreement metric over a sampled window: takes a receipt-corpus window and a sampled human-attestation set; computes Cohen's kappa or equivalent agreement metric; emits a `judge_meta_eval` ledger event; receipt cited in attestation. Surfaces drift if the metric falls below a configurable floor.
4. **Receipt-shape extension** to ARB validator. The judge-invocation schema from OBPI-0.0.39-02 lands the schema; this OBPI extends `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` with `arb-step-judge-*` slots for canonical citations and updates ARB middleware to validate judge receipts against the schema at emit time.
5. **Existing-judge-surface retrofit.** Update `gz-adr-evaluate --red-team` to populate every judge_invocation field (judge_model, judge_model_family, candidate_provenance, methodology, three-axis, bias_mitigations) — emitting compliant receipts going forward. Update the runtime `advisor()` tool's documentation in `CLAUDE.md` to declare its bias profile and the cases where invoking it is itself a doctrine violation (e.g., when same-family preference-leakage is the failure mode under test). Backfill historical waivers for receipts emitted before this ADR closed.

---

## Rationale

**Claim 1 — Preference-leakage detection requires a model-family equivalence registry.** Naive string-match on `judge_model == candidate_model` misses the canonical case (`claude-opus-4-7` judging output of `claude-opus-4-6` — different versions, same family, structural leakage). The validator must consult a registry (e.g., `data/judge_model_families.json`) declaring which model strings share family membership. Building the registry is itself a doctrine event: the registry's contents bind every leakage detection. Per `gzkit`'s registry pattern (precedent: `data/security_surfaces.json` from ADR-0.0.22), the registry is frozen-Pydantic-validated and self-bootstrapping (edits require sensitivity declaration in the editing brief).

**Claim 2 — `gz judge meta-eval` is operator-facing, not agent-facing.** The meta-eval cadence is a *human* sampling: an operator reviews N judge verdicts, records their own verdict, and the command computes agreement. This is foundationally different from the validators (-02, -03), which run mechanically against the receipt corpus with no operator-in-the-loop. The CLI verb classifies as **Evidentiary** per ADR-0.0.38 (the kappa metric informs operator judgment about whether the surface drifts; it does NOT bind any gate). The validators classify as **Authoritative** (their exit code 3 stops pipelines).

**Claim 3 — The retrofit (-05) is the highest-risk OBPI of this ADR.** Updating `gz-adr-evaluate --red-team` to populate JudgeInvocation fields requires reading the existing red-team prompt structure, identifying which methodology applies (almost certainly `red-team-challenge` per ADR-0.0.39 § Invariant 7), declaring honest bias profile (almost certainly same-family with no current order-randomization), and emitting compliant receipts going forward. Backfilling historical receipts via waiver requires explicit operator-attested rationale at Gate 5 — the operator confirms each waived receipt is genuinely a pre-baseline emission, not silent retroactive compliance. This is the OBPI most at risk of vibe-shaped completion ("update the call site to add fields, ship it") that conceals the actual mitigation gap.

**Why this is foundation-kind.** The validators bind every future judge invocation; the meta-eval CLI is the only mechanism for catching judge-correctness drift; the receipt-shape extension changes the ARB middleware contract every receipt-emitting surface honors. ADR-0.0.18 reserves foundation-kind for app/system invariants — every one of the five OBPIs lands an invariant-shaped contract. Foundation-kind triggers brief-level Gate 5 attestation, which is necessary because each validator's false-positive or false-negative behavior would silently weaken the LLM-as-judge surface in gzkit for an indefinite period.

**Why heavy lane.** Three new validator scopes (`--judge-leakage`, `--judge-output-discipline`, `--judge-meta-eval` is technically a top-level verb not a validator scope but adds CLI surface), one new top-level CLI verb (`gz judge meta-eval`), one ARB middleware contract change, one receipt-shape extension. Every one of these is heavy-lane-triggering per AGENTS.md § Gate Covenant ("command/API/schema/runtime-contract changes"). Lite lane would skip Gate 3 (docs) and Gate 4 (BDD); both are needed for every new CLI surface this ADR adds.

**Exemplars and precedents.**

- **ADR-0.0.39 (LLM-as-judge doctrine)** is the direct enabler — this ADR ships the validators its sibling specifies. Sequencing is doctrine-before-tooling per gzkit's ordering.
- **ADR-0.0.22 (security-sensitivity-doctrine)** is the architectural precedent for the registry-plus-validator pattern. `data/security_surfaces.json` + `gz validate --sensitivity` is exactly the shape `data/judge_leakage_waivers.json` + `gz validate --judge-leakage` follows — frozen Pydantic schema, named-cited-rationale waivers, fail-closed under the high-rigor lane.
- **ADR-0.0.38 (evidence-authority-projection-doctrine)** classifies the validators here as Authoritative and the meta-eval CLI as Evidentiary — every surface this ADR adds inherits an axis declaration cleanly. ADR-0.0.38's `gz validate --surface-axis` would, in turn, audit this ADR's surfaces for declaration completeness.
- **ADR-0.0.27 (exemplar-corpus-doctrine)** anchors brief-level Gate 5 walkthroughs on every foundation-kind ADR; OBPI-0.0.40-05's retrofit walkthrough is especially load-bearing because it is the highest-risk OBPI per Claim 3 above.
- **arxiv 2411.15594 § Preference Leakage** and **llm-as-a-judge.github.io J-Detector framing** are the canonical literature sources; the leakage validator's diagnostic explicitly cites the paper.

## Comparator Uplift (2026-05-07)

Superpowers-style review stages and Compound Engineering review loops are useful
only when review artifacts cannot float free of enforcement. This ADR should add
validator coverage for review receipts that name `spec_compliance`, `quality`,
`security`, or `performance`: the receipt schema, prompt leakage checks, and
integration citation must all validate before the review can influence
completion.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: the named gz validate --judge-leakage and --judge-output-discipline validators are unlanded (ADR is Draft; Decision unfilled); the advisory-rules-audit scorecard that tracks the judge-doctrine promotion this ADR would close holds green. | uv run gz validate --advisory-scorecard | 0 |

## Consequences

### Positive

- **Closes the LLM-as-judge structural-defense loop.** Every invariant in ADR-0.0.39 gets a fail-closed mechanical witness (or, for meta-eval, an Evidentiary metric with a configurable floor). The doctrine moves from advisory-on-paper to mechanically-bounded.
- **Closes preference leakage as a structural failure class** across the existing receipt corpus and going forward. Same-family judging requires explicit waiver; the diagnostic cites the survey paper.
- **Adds explanation-precedes-verdict + methodology + three-axis + bias-mitigations enforcement** at receipt-emit time and in the corpus-scan validator. Both the emit-time floor (OBPI-01) and the corpus-scan floor (OBPI-03) fire.
- **Unblocks `gz judge meta-eval` as the human-agreement metric surface.** Operators can sample, compute kappa, observe drift, decide remediation.
- **Retrofits existing judge surfaces to compliance,** with honest gap-recording as the explicit alternative to vibe-shaped completion.
- **Marks dependent pool ADRs (`attestation-advisory-agent`, `lightweight-pre-implementation-challenger`) as governed-by-ADR-0.0.40** — when promoted later, they inherit both the doctrine (0.0.39) and the validators (0.0.40) without re-deriving.

### Negative

- **Five OBPIs is the largest decomposition in the trajectory.** Each requires its own Gate 5 walkthrough; the OBPI-0.0.40-05 retrofit walkthrough is especially heavy because the operator must confirm each gap-recording is honest.
- **Model-family equivalence registry is a new doctrine surface.** Adding entries (a new model release, a new family) requires editing `data/judge_model_families.json` under explicit operator authorization. The registry's churn rate scales with the model-release cadence.
- **Cohen's kappa floor is opinionated.** Operators who want a different metric or floor must edit `data/judge_meta_eval_floor.json`; the default is documented but it remains a doctrine choice that operators may push back on.

### Risks

- **OBPI-0.0.40-05's retrofit risks vibe-shaped compliance.** Adding JudgeInvocation field declarations to `gz-adr-evaluate --red-team` looks like a small surgical edit; the actual difficulty is *honest* bias-profile declaration (almost certainly recording that today's red-team has NO order-randomization, NO length-normalization, NO cross-family pairing). Mitigation: Gate 5 walkthrough mandates operator confirmation that each gap is recorded honestly; ADR-0.0.39-03's classification audit is the input the retrofit must match.
- **Leakage validator false-positives on legitimate same-family cases** (e.g., a CLI smoke-test that genuinely runs the operator's own `advisor()` against operator's own session output for sanity-checking purposes). Mitigation: the waiver registry pattern (precedent: `_UTF8_PIPE_WAIVERS`, `data/security_surfaces.json`) — explicit named exceptions with cited rationale and `expires_after` field.
- **Meta-eval CLI sample-size sensitivity.** Cohen's kappa on a small sample is high-variance; the floor (default 0.6) may falsely flag a surface when the sample is too small. Mitigation: the CLI requires `--window` and `--human-attestations` to specify the sample explicitly; the receipt records sample_size; reviewers can re-run with a larger window.
- **ARB middleware extension regression risk.** Routing judge-prefixed receipts to schema validation adds a code path to the ARB validator; a bug here could either (a) silently allow non-compliant receipts through (false negative) or (b) reject legitimate non-judge receipts that happen to share a prefix substring (false positive). Mitigation: OBPI-0.0.40-01's tests explicitly cover the boundary cases (non-judge receipts pass through; judge-prefixed receipts route to validation; near-miss prefixes are NOT routed).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.40-01: **receipt-shape-extension** — Extend `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` with `arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*` canonical slots; extend ARB middleware to validate judge-invocation receipts against the schema authored under OBPI-0.0.39-02 at emit time; add `judge_invocation_validated` ledger event family.
- [ ] OBPI-0.0.40-02: **judge-leakage-validator** — Implement `gz validate --judge-leakage` validator scope: enumerate all judge-invocation receipts, detect same-family judge⇄candidate pairs from the model_family declarations, fail-close under heavy lane on unwaived violations, honor `data/judge_leakage_waivers.json` registry; document model-family equivalence taxonomy (e.g. claude-opus-4-X all share family `claude-opus-4`); BDD acceptance scenarios.
- [ ] OBPI-0.0.40-03: **judge-output-discipline-validator** — Implement `gz validate --judge-output-discipline` validator scope: verify explanation_text populated AND positioned before verdict, methodology declared from the enum, bias_mitigations declared, three-axis declared; fail-close on out-of-order or missing fields; integrate into default `gz check` scope set.
- [ ] OBPI-0.0.40-04: **meta-eval-cli** — Implement `gz judge meta-eval` CLI verb: takes `--window` (receipt range), `--human-attestations` (sampled-attestation source), computes Cohen's kappa or equivalent; emits `judge_meta_eval` ledger event with metric value, sample size, window timestamps; receipt name `arb-step-judge-meta-eval-*`; default floor for kappa configurable in `data/judge_meta_eval_floor.json`; manpage + runbook entries.
- [ ] OBPI-0.0.40-05: **existing-judge-surface-retrofit** — Update `src/gzkit/commands/adr_evaluate.py` red-team path to populate every judge_invocation field on emitted receipts; update `CLAUDE.md` § Advisor Tool to declare advisor()'s bias profile and the named "do not invoke" cases (same-family-leakage failure-mode tests, peer review of own prior reasoning); backfill historical receipts via waivers in `data/judge_leakage_waivers.json` with cited reason `pre-ADR-0.0.40-baseline`; supersede pool ADRs `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` as governed-by-this-validator-set.

## Target Scope

- **receipt-shape-extension** — Extend `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` with `arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*` canonical slots; extend ARB middleware to validate judge-invocation receipts against the schema authored under OBPI-0.0.39-02 at emit time; add `judge_invocation_validated` ledger event family.
- **judge-leakage-validator** — Implement `gz validate --judge-leakage` validator scope: enumerate all judge-invocation receipts, detect same-family judge⇄candidate pairs from the model_family declarations, fail-close under heavy lane on unwaived violations, honor `data/judge_leakage_waivers.json` registry; document model-family equivalence taxonomy (e.g. claude-opus-4-X all share family `claude-opus-4`); BDD acceptance scenarios.
- **judge-output-discipline-validator** — Implement `gz validate --judge-output-discipline` validator scope: verify explanation_text populated AND positioned before verdict, methodology declared from the enum, bias_mitigations declared, three-axis declared; fail-close on out-of-order or missing fields; integrate into default `gz check` scope set.
- **meta-eval-cli** — Implement `gz judge meta-eval` CLI verb: takes `--window` (receipt range), `--human-attestations` (sampled-attestation source), computes Cohen's kappa or equivalent; emits `judge_meta_eval` ledger event with metric value, sample size, window timestamps; receipt name `arb-step-judge-meta-eval-*`; default floor for kappa configurable in `data/judge_meta_eval_floor.json`; manpage + runbook entries.
- **existing-judge-surface-retrofit** — Update `src/gzkit/commands/adr_evaluate.py` red-team path to populate every judge_invocation field on emitted receipts; update `CLAUDE.md` § Advisor Tool to declare advisor()'s bias profile and the named "do not invoke" cases (same-family-leakage failure-mode tests, peer review of own prior reasoning); backfill historical receipts via waivers in `data/judge_leakage_waivers.json` with cited reason `pre-ADR-0.0.40-baseline`; supersede pool ADRs `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` as governed-by-this-validator-set.

## Notes

This ADR is the second half of the LLM-as-judge structural defense.
ADR-0.0.39 lands the doctrine + schema + classification baseline;
this ADR lands the validators + meta-eval CLI + receipt extensions.
Both must close before the LLM-as-judge surface in gzkit moves from
doctrine-codified to doctrine-enforced.

Promotion ordering: this ADR depends on ADR-0.0.38 (Evidentiary axis
for the validators' own classification) and ADR-0.0.39 (judge_invocation
schema, rule file, classification baseline). Promote only after
ADR-0.0.39 is closed.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.judge-enforcement-validators` on 2026-05-06; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] ARB middleware extension: `src/gzkit/arb/validator.py` — judge-prefixed receipt routing + canonical step slots (OBPI-0.0.40-01)
- [ ] Ledger event family: `judge_invocation_validated` registered in `.gzkit/schemas/ledger_events.json` (OBPI-0.0.40-01)
- [ ] Validator: `gz validate --judge-leakage` at `src/gzkit/governance/trust_audits.py` (OBPI-0.0.40-02)
- [ ] Waiver registry: `data/judge_leakage_waivers.json` + `data/judge_model_families.json` (OBPI-0.0.40-02)
- [ ] Validator: `gz validate --judge-output-discipline` at `src/gzkit/governance/trust_audits.py` (OBPI-0.0.40-03)
- [ ] CLI verb: `gz judge meta-eval` at `src/gzkit/commands/judge_meta_eval.py` (OBPI-0.0.40-04)
- [ ] Meta-eval floor config: `data/judge_meta_eval_floor.json` (OBPI-0.0.40-04)
- [ ] Retrofit: `src/gzkit/commands/adr_evaluate.py` red-team path emits compliant JudgeInvocation receipts (OBPI-0.0.40-05)
- [ ] Advisor docs: `CLAUDE.md` § Advisor Tool with bias profile + named "do not invoke" cases (OBPI-0.0.40-05)
- [ ] Pool ADR frontmatter: `governed_by: ADR-0.0.40-judge-enforcement-validators` on `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` (OBPI-0.0.40-05)
- [ ] BDD scenarios: `features/governance/judge_leakage.feature`, `judge_output_discipline.feature`, `judge_meta_eval.feature` (Heavy lane Gate 4)
- [ ] Tests: `tests/governance/test_judge_leakage_validator.py`, `test_judge_output_discipline_validator.py`, `tests/commands/test_judge_meta_eval.py`, `tests/governance/test_judge_retrofit.py`
- [ ] Manpage: `docs/user/manpages/validate.md` — `--judge-leakage` and `--judge-output-discipline` documented; `docs/user/manpages/judge.md` (new) — `meta-eval` verb documented
- [ ] Operator runbook: `docs/user/runbook.md` — judge enforcement workflow added
- [ ] Governance runbook: `docs/governance/governance_runbook.md` — judge enforcement maintainer protocol added
- [ ] OBPI briefs: OBPI-0.0.40-01, -02, -03, -04, -05

## Alternatives Considered

1. **Fold validators into ADR-0.0.39.** Plausible — same shape as ADR-0.0.38 folded its validator into one ADR with three OBPIs. Rejected per operator's explicit two-ADR split: ADR-0.0.39 is doctrine-rich (codifies the survey-aligned framework, schema, classification baseline — content-heavy); ADR-0.0.40 is mechanism-heavy (5 OBPIs covering 3 validator scopes + 1 CLI verb + 1 retrofit). Splitting keeps each ADR's surface coherent and Gate 5 walkthroughs proportionate.

2. **Author validators inline per surface.** Each judge surface (`gz-adr-evaluate --red-team`, runtime `advisor()`, etc.) builds its own leakage check, output-discipline check, meta-eval. Rejected — leaves the doctrinal floor uncited and unenforced; each surface re-deriving its leakage check is the same fragmentation pattern ADR-0.0.38 was promoted to close. Single foundation rule + single validator scope-set, applied to all surfaces.

3. **Deterministic heuristic for leakage detection (e.g., string-match on model name).** Insufficient — model_family equivalence requires a registered equivalence map (e.g., `claude-opus-4-7` and `claude-opus-4-6` share family `claude-opus-4`), which is doctrine, not heuristic. The validator consults the registry; the registry is doctrine. String-match would miss the canonical leakage case.

4. **Skip the meta-evaluation CLI; rely on operator vibe-check.** Rejected — judge-correctness drift over time is a named survey-paper concern; honor-system "operator notices when the judge gets weird" is the canonical doctrine-drift-as-invariant-drift failure shape. Cohen's kappa over a sampled window is the standard metric; the CLI is the only way to make the cadence executable rather than honor-system.

5. **Defer this ADR until at least one judge surface fails in the wild.** Rejected — the maxim disqualifies "wait for failure" as a sequencing argument when the failure class is structural and the validator is feasible. ADR-0.0.39 closing without this ADR landing leaves a known-Promotable-rule unpromoted; the maxim explicitly disqualifies that state.

6. **Skip OBPI-0.0.40-05 (existing-judge-surface retrofit); leave existing surfaces emitting pre-schema receipts.** Rejected — leaves the ADR-0.0.39 schema enforced only on new judge invocations, not on the existing ones. The validators (-02, -03) would then false-flag every existing red-team or advisor receipt because the receipt shape is non-compliant. Either the retrofit happens in this ADR, or the validators have to be soft-gated on existing surfaces (which is precisely the Promotable-but-unpromoted anti-pattern the maxim forbids).

7. **Author the leakage validator without a waiver registry; fail-close on every same-family pair with no escape.** Rejected — there are legitimate same-family cases (operator's own `advisor()` smoke-test on operator's own session output for sanity verification) that would be permanently broken without a waiver path. Per `_UTF8_PIPE_WAIVERS` precedent, the waiver registry is the standard escape with named-cited-rationale and `expires_after` discipline.

8. **Make the meta-eval metric a fail-closed gate (kappa < floor → exit 3).** Rejected — promotes Evidentiary surface to Authoritative without doctrinal warrant. The meta-eval metric *informs* operator judgment about whether the surface is drifting; the operator decides whether to retire, retune, or replace. Promoting the metric to a gate would (a) violate ADR-0.0.39's Invariant 9 ("metric is NEVER itself a gate"), and (b) require a foundation-kind ADR amendment per ADR-0.0.38's promotion-requires-foundation-ADR rule.

9. **Use Krippendorff's alpha or Fleiss' kappa as the default meta-eval metric.** Plausible — both have advantages over Cohen's kappa for >2 raters. Rejected as default per ADR-0.0.39 § Risks: Cohen's kappa is conventional; the `--metric` flag accepts alternatives; operators who want Krippendorff's or Fleiss' explicitly opt in. Defaults are stickier than flags; the default is the most-cited literature choice.

10. **Keep this work in the pool backlog until reprioritized.** Rejected per the operator's explicit "DO IT RIGHT, MAX OUT" + "DIRMAX" directive: the trajectory is locked at ADR-0.0.38 → ADR-0.0.39 → ADR-0.0.40, and this ADR is the closing third.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.40 | Pending | | | |
