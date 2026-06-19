---
id: ADR-0.0.39-llm-as-judge-doctrine
status: Proposed
kind: foundation
semver: 0.0.39
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-05-06
promoted_from: ADR-pool.advisory-judge-surface
---

# ADR-0.0.39-llm-as-judge-doctrine: LLM-as-Judge Doctrine

## Persona

Active persona: `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.

LLM-as-judge is a paradigm whose canonical literature ([arxiv 2411.15594 — *From Generation to Judgment*](https://arxiv.org/abs/2411.15594), [llm-as-a-judge.github.io](https://llm-as-a-judge.github.io/)) names specific failure modes — preference leakage, position bias, verbosity bias, self-preference, calibration drift — that are invisible to mechanical validation and easy to miss without explicit roster. The author of this ADR reads the survey before authoring; refusing to codify a bias the survey names but the codebase has not yet observed is craft, not deference. The doctrine is not a description of what gzkit does today; it is the structural floor every future judge surface inherits, including failure modes that have not yet surfaced in practice.

## Why foundation tier?

Without this ADR, LLM-as-judge invocation is ungoverned — judges fire with no doctrine on calibration, leakage prevention, output discipline, or attestation, so judge verdicts have no contractual standing in the governance chain.

This ADR authors a port: the LLM-as-judge doctrine every judge-invoking surface (eval, review, meta-evaluation) binds to.

## Intent

**Current state.** gzkit already runs LLM-as-judge surfaces — `gz-adr-evaluate --red-team` (10 structured red-team challenges + 8-dim ADR / 5-dim OBPI rubric scoring), the runtime `advisor()` tool (stronger reviewer model on full conversation transcript), `gz-complexity-distill` advisor verdicts, and the proposed advisory-judge surface that this ADR's pool source originally seeded. **Today**, none of these surfaces declares its judging methodology, names the biases it inherits, requires explanation-before-verdict output structure, or runs a meta-evaluation cadence that would surface judge-correctness drift over time.

**Survey-aligned framework.** The canonical LLM-as-judge literature — [arxiv 2411.15594 — *From Generation to Judgment: Opportunities and Challenges of LLM-as-a-Judge*](https://arxiv.org/abs/2411.15594) and [llm-as-a-judge.github.io](https://llm-as-a-judge.github.io/) — organizes the field along a three-axis taxonomy (**what** to judge, **how** to judge, **where** to judge) and names a roster of bias failure modes that mechanical validation cannot detect: position bias (judges weight earlier candidates more), verbosity bias (judges prefer longer responses), self-preference bias (judges prefer outputs from their own model family), and **preference leakage** (judges from the same family as the candidate inherit shared biases that look like agreement). The survey also names methodology choices (single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble) that a judging surface implicitly adopts — silently, today, in gzkit — without declaring which choice was made or why.

**The gap this ADR closes.** Every existing gzkit judge surface is implicitly choosing a methodology, implicitly inheriting biases, implicitly emitting verdict-without-explanation or verdict-after-explanation in non-canonical order, and operating with no meta-evaluation cadence. The state **before this ADR**: the doctrine that would name these choices and bound them does not exist; ADR-pool.advisory-judge-surface had a four-invariant sketch (never-gate, paired-with-floor, reproducibility-receipt, bounded-scope), but the sketch did not name the bias roster, the methodology menu, the output discipline, or the meta-eval cadence — the four pillars the survey paper identifies as load-bearing.

**Inheritance from ADR-0.0.38.** This ADR depends on ADR-0.0.38's three-axis function-axis taxonomy: every LLM-as-judge surface in gzkit classifies as **Evidentiary** (informs operator judgment, never binds gates) per ADR-0.0.38's Decision § "The three categories". This ADR adds five judge-specific invariants on top of that classification — what/how/where declaration, named bias mitigations, methodology declaration, output-format discipline, meta-eval cadence — without re-litigating the function-axis question.

**What this ADR does NOT do.** Validators are ADR-0.0.40's scope. This ADR codifies the doctrine and lands the schema; ADR-0.0.40 ships `gz validate --judge-leakage`, `gz validate --judge-output-discipline`, `gz judge meta-eval`, the receipt-shape extension, and the existing-surface retrofit. Splitting the two preserves clean ADR boundaries: 0.0.39 is doctrine-rich; 0.0.40 is mechanism-heavy.

## Decision

Codify the LLM-as-judge doctrine as a **survey-aligned framework**
inheriting ADR-0.0.38's Evidentiary classification and adding five
judge-specific invariants. The doctrine has four parts: the three-axis
declaration, the named bias roster, the methodology menu with
rationale-of-choice, and the output-discipline-plus-meta-evaluation
contract.

### Inherited foundation invariants (from ADR-pool.advisory-judge-surface)

These four invariants from the original pool sketch carry forward unchanged. They are necessary but not sufficient — the survey-aligned invariants below extend them.

1. **Never a gate.** Judge output is Evidentiary per ADR-0.0.38 § "The three categories". Schema-rejected if any caller treats output as fail-closed pass/fail.
2. **Always paired with a mechanical floor.** Judge runs *after* mechanical validators pass, never instead. Doctrine: *floor catches the failure class; judge catches the residual subjective surface.*
3. **Reproducibility receipt.** Each judge invocation emits an ARB-shaped receipt with the schema fields named under § "Judge-invocation declaration schema" below. Judge verdicts cited in attestation MUST cite the receipt ID.
4. **Bounded scope.** Judge fires only on explicitly-named subjective surfaces. Adding a surface requires foundation-kind ADR justifying why mechanical validation cannot cover it.

### Survey-aligned invariants (new — the doctrine ADR-0.0.39 contributes)

#### Invariant 5 — Three-axis declaration (what / how / where)

Every LLM-as-judge invocation in gzkit MUST declare three axes in its receipt, per the survey paper's organizing taxonomy:

| Axis | Definition | Enum values (initial set) |
|---|---|---|
| **what** — judged content type | The class of artifact being judged | `prose-clarity`, `near-duplicate`, `attestation-grounding`, `code-review`, `adr-rationale`, `obpi-feasibility`, `plan-design-lens`, `scope-boundary`, `agent-reasoning-trace`, `red-team-challenge` |
| **how** — judging technique | The methodology applied (see Invariant 7) | `single-grading`, `pairwise`, `list-wise`, `reference-based`, `criteria-decomposed`, `ensemble`, `red-team-challenge` |
| **where** — application domain | The downstream consumer of the verdict | `adr-evaluation`, `obpi-pre-implementation`, `attestation-quality`, `insight-deduplication`, `runtime-advisor`, `complexity-distillation`, `pattern-corpus-curation` |

Adding an enum value requires foundation-kind ADR amendment (the same gate ADR-0.0.39 itself is foundation-kind). The enum is the schema-encoded surface area of LLM-as-judge use in gzkit; growing the surface is a doctrine event.

#### Invariant 6 — Named bias roster (declaration + mitigations)

Every judge invocation MUST declare which biases from the canonical roster apply and which mitigations were applied. The roster (initial set) covers:

| Bias | Survey-paper class | Default mitigation gzkit doctrine requires |
|---|---|---|
| **Position bias** | Judge weights earlier candidates more in pairwise/list-wise | When `how=pairwise` or `how=list-wise`, the receipt MUST declare order-randomization-applied or order-sweep (judge runs both orderings, verdict requires agreement) |
| **Verbosity bias** | Judge prefers longer responses | When candidate length is variable, receipt MUST declare length-normalization-applied or length-controlled-prompt |
| **Self-preference bias** | Judge prefers outputs from own model family | Receipt MUST declare `judge_model_family` and `candidate_provenance.model_family`; same-family pairs flagged at validator (ADR-0.0.40) |
| **Preference leakage** | Judges related to candidate model (same family, inheritance, training-set overlap) inherit shared biases | Receipt MUST declare `candidate_provenance` (model + family + training-relationship if known); cross-family judging is the default, same-family judging requires waiver in `data/judge_leakage_waivers.json` (ADR-0.0.40) |
| **Calibration drift** | Judge's verdict distribution shifts over time | Meta-eval cadence (Invariant 9) catches this; receipts contribute to the windowed kappa metric |

Adding a bias to the roster — same as adding an axis enum value — requires foundation-kind ADR amendment.

#### Invariant 7 — Methodology menu with rationale-of-choice

The judging methodology MUST be declared from a fixed menu. Each invocation cites which methodology was used and a one-sentence rationale:

| Methodology | When appropriate | Rationale shape |
|---|---|---|
| **single-grading** | Score one artifact against a rubric independently | Default for rubric scoring (e.g., gz-adr-evaluate's 8-dim rubric); rationale: "rubric-based independent score across N dimensions" |
| **pairwise** | Compare two artifacts directly | Best for ranking; rationale: "comparative judgment with order-randomization" |
| **list-wise** | Rank a set of artifacts | When >2 candidates and ordering matters; rationale: "ranked judgment across N candidates with order-sweep" |
| **reference-based** | Compare against a known-good reference | When ground truth exists; rationale: "graded relative to reference X with diff justification" |
| **criteria-decomposed** | Break the judgment into named sub-criteria, score each | Default for high-stakes structural review (e.g., red-team challenge); rationale: "decomposed across N named criteria with per-criterion verdict" |
| **ensemble** | Multiple judges, aggregated verdict | Highest-stakes / when single-judge variance is the concern; rationale: "M-judge ensemble with aggregation method Y" |
| **red-team-challenge** | Adversarial judging with explicit critical-reviewer framing | gz-adr-evaluate's --red-team path; rationale: "adversarial review against named challenge axes" |

Implicit methodology choice — invoking a judge without declaring which menu entry applies — is a doctrine violation detectable at receipt-emit time (ADR-0.0.40 validator).

#### Invariant 8 — Output-format discipline (explanation-precedes-verdict)

Every judge invocation MUST structure its prompt and its receipt so that **explanation precedes verdict**. This is a known bias mitigation: judges that emit verdict first and rationale second tend to confabulate the rationale to match the verdict; judges that emit explanation first and verdict second produce more calibrated verdicts.

The mechanical floor:

- Prompts to the judge MUST elicit explanation before verdict (e.g., "First, explain your reasoning. Then, state your verdict.")
- Receipt fields are ordered so that `explanation_text` appears before `verdict` in the JSON object schema
- A receipt with `verdict` populated but `explanation_text` empty is rejected at emit time
- A receipt where `explanation_text` is non-empty but trivial (length below a configurable floor, default 50 characters) is flagged

#### Invariant 9 — Meta-evaluation cadence (human-agreement metric)

LLM-as-judge correctness is itself an empirical question, not an axiom. Every judging surface in gzkit operates under a **meta-evaluation cadence**: every N verdicts (default N=100, configurable per surface in `data/judge_meta_eval_floor.json`), an operator-attested human-agreement sample is taken and Cohen's kappa (or equivalent agreement metric) is computed against the sampled judge verdicts.

The mechanical floor (ADR-0.0.40 ships the validator):

- The metric is computed by `gz judge meta-eval`
- A `judge_meta_eval` ledger event records the metric value, sample size, window timestamps
- The metric has a configurable floor (default kappa=0.6, "substantial agreement" per Landis-Koch)
- Below the floor: the surface is flagged in `gz status` as drift-suspect; the operator decides whether to retire the surface, retune the prompt, or change the judge model
- The metric is NEVER itself a gate — it informs operator judgment per the inherited Evidentiary classification

### Judge-invocation declaration schema (the surface every receipt must populate)

Authored in OBPI-0.0.39-02. The schema is the mechanical surface for invariants 5–8.

**Contract stability declaration (binding at `Proposed` and after):** The field set, types, ordering, and Pydantic / JSON-Schema mirror invariants enumerated below — together with OBPI-0.0.39-02's REQ-01 through REQ-09 — constitute the **contract-stable judge surface** that downstream ADRs depend on. From the moment ADR-0.0.39 reaches `Proposed`, additions to the schema require a foundation-kind ADR amendment with explicit propagation accounting (per ADR-0.0.52); removals or type changes require ADR supersession. This declaration is what ADR-0.0.52's hard-prereq language ("ADR-0.0.39 must `Proposed` with named judge-contract surface subsection locked") binds to.

```text
JudgeInvocation:
  judge_model: str            # e.g. "claude-opus-4-7"
  judge_model_family: str     # e.g. "claude-opus-4" (per equivalence registry)
  candidate_provenance:
    model: str
    model_family: str
    training_relationship: str | None  # "same-family" | "ancestor" | "sibling" | "unrelated"
  what_axis: str              # enum from Invariant 5
  how_axis: str               # enum from Invariant 5
  where_axis: str             # enum from Invariant 5
  methodology: str            # enum from Invariant 7
  methodology_rationale: str  # one-sentence rationale
  bias_mitigations:
    position_bias: str        # "order-randomized" | "order-swept" | "n/a"
    verbosity_bias: str       # "length-normalized" | "length-controlled" | "n/a"
    self_preference: str      # "cross-family" | "same-family-waived" | "n/a"
    preference_leakage: str   # "cross-family" | "same-family-waived" | "n/a"
  explanation_text: str       # required, MIN 50 chars (Invariant 8)
  verdict: str                # populated AFTER explanation_text in prompt
  prompt_hash: str            # SHA-256 of prompt
  input_hash: str             # SHA-256 of judged artifact
  receipt_id: str             # arb-step-judge-* prefix per ADR-0.0.40
  timestamp: str              # ISO-8601
```

### Foundation rule deliverable

A new canonical rule file at `.gzkit/rules/llm-as-judge.md`,
authored under OBPI-0.0.39-01 and registered in the advisory-rules-audit
scorecard at `docs/governance/advisory-rules-audit.md` as **Mechanical**
with forward-references to ADR-0.0.40's validator scopes. The rule
declares its own `surface_axis: authoritative` per ADR-0.0.38.

### Existing-surface classification deliverable

A one-time audit pass under OBPI-0.0.39-03 classifying every existing
LLM-as-judge surface (`gz-adr-evaluate --red-team`, runtime
`advisor()` tool, `gz-complexity-distill` advisor verdicts) under the
three-axis taxonomy with cited rationale anchors; emits a
`judge_surface_classified` ledger event per surface; produces
`artifacts/audits/judge-surface-classification-2026-05-06.md`. The
audit is the snapshot; ADR-0.0.40's validators are the going-forward
enforcement.

### Pool ADR supersession

This ADR **self-supersedes** `ADR-pool.advisory-judge-surface` (already auto-marked Superseded by promotion). It additionally marks `ADR-pool.attestation-advisory-agent` and `ADR-pool.lightweight-pre-implementation-challenger` as **governed-by-ADR-0.0.39** in their pool frontmatter — they remain in pool until later promotion, but their invariants now inherit from this doctrine rather than re-deriving.

### Sequencing into ADR-0.0.40

ADR-0.0.40 (Judge Enforcement Validators) is the next ADR. It ships:
`gz validate --judge-leakage`, `gz validate --judge-output-discipline`,
`gz judge meta-eval`, the ARB receipt-shape extension, and the
existing-surface retrofit (gz-adr-evaluate --red-team field
population, advisor() bias-profile documentation, historical waiver
backfill). 0.0.40 cannot land before 0.0.39 closes — the schema and
classification baseline are 0.0.40's input.

## Rationale

**Claim 1 — Implicit methodology choice is doctrine drift.** Today, `gz-adr-evaluate --red-team` runs a red-team-challenge methodology, but its receipt does not declare the methodology. The runtime `advisor()` tool runs single-grading on a full conversation transcript, but its receipt does not declare the methodology. `gz-complexity-distill` advisor verdicts run criteria-decomposed methodology against complexity dimensions, but the receipt does not declare the methodology. The methodology choice is invisible at the receipt layer — which means a later agent reading the corpus cannot reconstruct what kind of judging was done, which means the verdict cannot be re-judged or audited. The survey paper names this as a load-bearing axis; making the choice explicit is the structural defense.

**Claim 2 — Preference leakage is the highest-leverage bias to mechanize.** Position, verbosity, and self-preference biases are each named in the survey but each has a relatively contained mitigation (order-randomization, length-normalization, cross-family judging). **Preference leakage** — where the judge's biases align with the candidate's because they share training-data lineage — is structurally insidious because it produces *agreement that looks like correctness*. A claude-opus judge of a claude-opus candidate will tend to agree with the candidate's reasoning shape on aesthetic grounds the judge cannot articulate; the verdict may be "the candidate is right" when the truth is "I share the candidate's blind spots." The cross-family default + same-family-requires-waiver pattern (mechanized in ADR-0.0.40) is the structural floor against this. gzkit ships with the failure latent today — the operator's own `advisor()` tool likely runs same-family on operator's working session.

**Claim 3 — Explanation-precedes-verdict is the cheapest output discipline with the highest leverage.** The survey paper and adjacent literature (e.g., chain-of-thought prompting research) consistently find that judges asked to emit verdict-first then-rationalize confabulate justifications to match the verdict; judges asked to emit explanation-first then-verdict produce more calibrated verdicts. This costs nothing — same model, same context — and is mechanically detectable at receipt-emit time (verdict populated but explanation empty → reject). It is the cheapest invariant in the doctrine and one of the highest-leverage.

**Claim 4 — Meta-evaluation cadence is the only way to detect judge-correctness drift.** A judge that was calibrated correctly when initially deployed will drift over time as the model is updated, as the prompt is edited, as the artifact distribution shifts. Without a cadence that periodically samples human-agreement, drift is silent. Cohen's kappa over a sampled window is the standard meta-eval metric; the floor (kappa ≥ 0.6) is configurable per surface. Operators can tune; what they cannot do is opt out — every judging surface in gzkit operates under the cadence by default.

**Why this is foundation-kind.** The doctrine is invariant-shaped — every judging surface in gzkit must honor it. ADR-0.0.18 reserves foundation-kind for app/system invariants; this qualifies. Foundation-kind triggers brief-level human attestation (per the lane × kind matrix), which is appropriate because a doctrine that under-mitigates a bias would silently weaken every downstream judge surface for an indefinite period.

**Why heavy lane.** OBPI-0.0.39-02 introduces a new schema (`judge_invocation.json`) and Pydantic model, which is a contract-surface change. ADR-0.0.39 also extends `CANONICAL_STEP_COMMANDS` indirectly (the validator and CLI verbs land in ADR-0.0.40, but the receipt-prefix slots are reserved doctrine-side). Heavy lane is the canonical trigger per AGENTS.md § Gate Covenant.

**Exemplars and precedents.**

- **ADR-0.0.38 (evidence-authority-projection-doctrine)** is the direct parent — this ADR inherits its Evidentiary classification and adds judge-specific invariants on top. The shape (rule + schema + classification audit) follows 0.0.38's structure exactly.
- **ADR-0.0.22 (security-sensitivity-doctrine)** is the architectural precedent for adding invariants atop a registry: registry → rule → validator → retroactive baseline → Gate 5 walkthrough. This ADR follows the same shape; ADR-0.0.40 is the validator half.
- **ADR-0.0.27 (exemplar-corpus-doctrine)** anchors the brief-level Gate 5 walkthrough on foundation-kind ADRs regardless of lane, which OBPI-0.0.39-03's classification audit honors.
- **ADR-0.0.5 (evaluation-infrastructure)** explicitly **rejected** LLM-as-judge for deterministic regression scoring; this ADR honors that boundary — the doctrine governs judge surfaces that are *already evidentiary* (gz-adr-evaluate red-team, advisor, complexity-distill), not the deterministic scoring path 0.0.5 named.
- **arxiv 2411.15594** and **llm-as-a-judge.github.io** are the canonical literature sources; the three-axis taxonomy, bias roster, methodology menu, output discipline, and meta-eval cadence are all sourced from them.

## Comparator Uplift (2026-05-07)

External frameworks increasingly include AI review and quality scoring. This ADR
should make clear that judge outputs are advisory until a validator binds their
input corpus, rubric, output schema, and leakage controls. Review polish is not
authority; receipt-bound judge discipline is the only acceptable absorption.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: the judge-doctrine enforcement validators are unlanded (ADR is Proposed); the advisory-rules-audit scorecard that tracks this LLM-as-judge doctrine as a classified rule holds green. | uv run gz validate --advisory-scorecard | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.39-llm-as-judge-doctrine --check | 0 |

## Consequences

### Positive

- **Closes the implicit-methodology drift class.** Every existing judge surface gains an explicit methodology declaration; no more invisible choice at the receipt layer.
- **Closes the preference-leakage failure class structurally** once ADR-0.0.40 ships the validator. Same-family judging requires waiver; cross-family is the default.
- **Adds explanation-precedes-verdict discipline at zero cost.** Mechanically detectable; cheapest leverage in the doctrine.
- **Adds meta-eval cadence so judge-correctness drift is detectable.** Operators can tune the floor; they cannot opt out.
- **Inherits ADR-0.0.38's Evidentiary classification cleanly** — no doctrine fragmentation; the function-axis question is settled upstream.
- **Unblocks ADR-0.0.40 (judge enforcement validators).** Without this doctrine + schema landing, 0.0.40 has no contract to validate against.

### Negative

- **Existing-surface retrofit labor.** OBPI-0.0.39-03 audits every existing judge surface and classifies each under the new taxonomy. The labor is bounded (gzkit has ≤10 judging surfaces today) but non-trivial, and the operator must walk through the classification at Gate 5.
- **Schema rigidity at the receipt layer.** Adding a new what-axis, how-axis, where-axis, or bias requires foundation-kind ADR amendment. This is intentional — the schema is doctrine — but it raises the floor on adding new judge surfaces.
- **Potential for over-mitigation.** Some surfaces (e.g., insight-deduplication) genuinely have no position-bias concern because they're not pairwise. Receipts on those surfaces declare `position_bias: n/a`; the schema requires a value but accepts `n/a` with cited rationale.

### Risks

- **Misclassification of an existing surface's bias profile at OBPI-0.0.39-03.** Mitigation: Gate 5 walkthrough requires operator to confirm each classification; the survey paper's bias roster is the canonical source for the audit's rationale anchors.
- **Trajectory dependency on ADR-0.0.40.** This ADR's invariants are mechanical-witness-shaped, but the witnesses (validators) ship in 0.0.40. Until 0.0.40 closes, the doctrine is honor-system enforced (a Promotable-but-unpromoted state). Mitigation: ADR-0.0.40 is committed-to as the next ADR and explicitly cites this risk as its Intent.
- **Cohen's kappa as the meta-eval metric is opinionated.** Other agreement metrics exist (Krippendorff's alpha, Fleiss' kappa for >2 raters); the choice of Cohen's kappa is conventional but not universal. Mitigation: ADR-0.0.40's `gz judge meta-eval` accepts a `--metric` flag; the default is `cohens-kappa`; operators may select alternatives without re-litigating doctrine.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 0
- Dimension Total: 4
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.39-01: **rule-and-doctrine** — Author the canonical rule file at `.gzkit/rules/llm-as-judge.md` codifying the survey-aligned framework: three-axis declaration (what/how/where) per [arxiv 2411.15594](https://arxiv.org/abs/2411.15594); named bias roster (position bias, verbosity bias, self-preference bias, preference leakage); methodology menu with rationale-of-choice (single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble); output-format discipline (explanation-precedes-verdict; no naked verdict); meta-evaluation cadence (sample human-agreement N times per 100 verdicts); inheritance from ADR-0.0.38 Evidentiary axis.
- [ ] OBPI-0.0.39-02: **judge-invocation-schema** — Define the judge-invocation declaration schema (Pydantic + JSON Schema) every LLM-as-judge surface must populate at invocation time: `judge_model`, `judge_model_family`, `candidate_provenance` (model + family of the artifact under judgment), `methodology`, `what_axis` (judged content type), `how_axis` (judging technique), `where_axis` (application domain), `bias_mitigations` (named mitigations applied), `explanation_text`, `verdict`, `prompt_hash`, `input_hash`. Receipts that fail to populate any required field are rejected by the existing ARB validator.
- [ ] OBPI-0.0.39-03: **existing-judge-surface-classification** — Classify every existing LLM-as-judge surface in gzkit (`gz-adr-evaluate --red-team`, runtime `advisor()` tool, `gz-complexity-distill` advisor verdicts) under the three-axis taxonomy; emit `judge_surface_classified` ledger event per surface; produce baseline at `artifacts/audits/judge-surface-classification-2026-05-06.md`; supersede the three pool ADRs governed by this doctrine (`advisory-judge-surface` self-supersession at promotion; `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` marked as governed-by-ADR-0.0.39 in their pool frontmatter, remaining in pool until later promotion).

## Target Scope

- **rule-and-doctrine** — Author the canonical rule file at `.gzkit/rules/llm-as-judge.md` codifying the survey-aligned framework: three-axis declaration (what/how/where) per [arxiv 2411.15594](https://arxiv.org/abs/2411.15594); named bias roster (position bias, verbosity bias, self-preference bias, preference leakage); methodology menu with rationale-of-choice (single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble); output-format discipline (explanation-precedes-verdict; no naked verdict); meta-evaluation cadence (sample human-agreement N times per 100 verdicts); inheritance from ADR-0.0.38 Evidentiary axis.
- **judge-invocation-schema** — Define the judge-invocation declaration schema (Pydantic + JSON Schema) every LLM-as-judge surface must populate at invocation time: `judge_model`, `judge_model_family`, `candidate_provenance` (model + family of the artifact under judgment), `methodology`, `what_axis` (judged content type), `how_axis` (judging technique), `where_axis` (application domain), `bias_mitigations` (named mitigations applied), `explanation_text`, `verdict`, `prompt_hash`, `input_hash`. Receipts that fail to populate any required field are rejected by the existing ARB validator.
- **existing-judge-surface-classification** — Classify every existing LLM-as-judge surface in gzkit (`gz-adr-evaluate --red-team`, runtime `advisor()` tool, `gz-complexity-distill` advisor verdicts) under the three-axis taxonomy; emit `judge_surface_classified` ledger event per surface; produce baseline at `artifacts/audits/judge-surface-classification-2026-05-06.md`; supersede the three pool ADRs governed by this doctrine (`advisory-judge-surface` self-supersession at promotion; `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` marked as governed-by-ADR-0.0.39 in their pool frontmatter, remaining in pool until later promotion).

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.advisory-judge-surface` on 2026-05-06; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Rule file: `.gzkit/rules/llm-as-judge.md` (authored under OBPI-0.0.39-01)
- [ ] Advisory-rules-audit registration: `docs/governance/advisory-rules-audit.md` — Mechanical, validator-by-ADR-0.0.40 (registered under OBPI-0.0.39-01)
- [ ] Pydantic model: `src/gzkit/governance/judge_invocation.py` — `JudgeInvocation`, `BiasMitigations`, `CandidateProvenance` (authored under OBPI-0.0.39-02)
- [ ] JSON Schema: `src/gzkit/schemas/judge_invocation.json` (authored under OBPI-0.0.39-02)
- [ ] Schema tests: `tests/governance/test_judge_invocation_schema.py` (authored under OBPI-0.0.39-02)
- [ ] Classification audit: `artifacts/audits/judge-surface-classification-2026-05-06.md` (produced under OBPI-0.0.39-03)
- [ ] Ledger events: `judge_surface_classified` (one per surface, emitted under OBPI-0.0.39-03)
- [ ] Surface inventory baseline: `data/judge_surface_inventory.json` (produced under OBPI-0.0.39-03)
- [ ] Pool ADR frontmatter updates: `governed_by: ADR-0.0.39-llm-as-judge-doctrine` on `ADR-pool.attestation-advisory-agent` and `ADR-pool.lightweight-pre-implementation-challenger`
- [ ] BDD scenarios: `features/governance/llm_as_judge_schema.feature` (Heavy lane Gate 4)
- [ ] Operator runbook: `docs/user/runbook.md` — judge surface classification protocol added
- [ ] Governance runbook: `docs/governance/governance_runbook.md` — judge surface classification protocol added
- [ ] OBPI briefs: OBPI-0.0.39-01-rule-and-doctrine, OBPI-0.0.39-02-judge-invocation-schema, OBPI-0.0.39-03-existing-judge-surface-classification

## Alternatives Considered

1. **Reject LLM-as-judge categorically.** Original position from the pool ADR; rejected — categorical rejection forfeits the only viable surface for residual-subjective questions (prose clarity, near-duplicate detection, grounding-check) that mechanical validation cannot answer. The four-invariant boundary (never-gate, paired-floor, receipt, bounded-scope) plus the survey-aligned five judge-specific invariants together produce a structurally bounded surface that earns its keep.

2. **Treat judge output as a gate.** The pool ADR's named alternative #2; rejected — reproduces the LLM-as-gate failure class the anti-vibing mantra exists to forbid. The Evidentiary classification inherited from ADR-0.0.38 is explicit on this; rule 1 of the inherited four-invariant set re-states it.

3. **Use deterministic heuristics instead.** The pool ADR's alternative #3; rejected for the named subjective surfaces — prose clarity, near-duplicate semantic detection, attestation-grounding judgment are not amenable to deterministic heuristics that don't themselves degrade into vibing surfaces. The judge is the lower-vibing-surface choice when paired with the doctrine's five new invariants.

4. **Operator-only judgment (no LLM judge at all).** The pool ADR's alternative #4; rejected — operator judgment in chat does not produce a citable artifact. Receipts are the point; provenance is the point. An LLM judge with a survey-aligned receipt schema produces auditable, replayable verdicts; operator chat does not.

5. **Codify only the original four-invariant frame, defer the survey-aligned five.** The minimum-viable promotion of the pool sketch. Rejected — the four-invariant frame is necessary but not sufficient. The survey paper names load-bearing failure modes (preference leakage, calibration drift, implicit methodology choice, verdict-first confabulation) that the original four invariants do not address. Shipping only the four-invariant frame would land a doctrine that doesn't close the failure classes the survey-paper literature has already identified.

6. **Fold all judge-specific doctrine into ADR-0.0.38.** Plausible — same shape as ADR-0.0.38 folds its validator into one ADR. Rejected: ADR-0.0.38's function-axis taxonomy applies to all surfaces (validators, derived views, evidentiary-non-judge surfaces like `gz-plan-audit`); the LLM-as-judge-specific invariants apply only to judging surfaces. Folding them in would muddle the function-axis invariant with the judge-specific invariant set. Two ADRs, sequenced, keeps each doctrine's surface coherent.

7. **Defer to per-surface SKILL.md declarations rather than a foundation rule.** Same alternative the pool ADR considered for the function-axis question; rejected for the same reason — local declaration without a global rule leaves the cross-cutting invariant unenforced; advisory-rules-audit scorecard cannot grade against a missing rule. Six existing or proposed judge surfaces will each re-derive their boundary.

8. **Skip the existing-surface classification (OBPI-0.0.39-03).** Rejected: leaves the existing judge surfaces with no axis declarations until each is independently edited. ADR-0.0.40's validator from OBPI-0.0.40-02 cannot fail-close on missing declarations until the baseline exists; lazy classification means the validator is advisory-only at landing, which reproduces the Promotable-but-unpromoted anti-pattern at the classification layer (same anti-pattern named in ADR-0.0.38 § Alternatives #6).

9. **Keep this work in the pool backlog until reprioritized.** Rejected per the operator's explicit "DO IT RIGHT, MAX OUT" directive: the trajectory is locked at ADR-0.0.38 → ADR-0.0.39 → ADR-0.0.40 with the survey-aligned framework as the doctrinal floor.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.39 | Pending | | | |
