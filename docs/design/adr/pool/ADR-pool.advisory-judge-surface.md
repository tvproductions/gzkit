---
id: ADR-pool.advisory-judge-surface
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
promoted_to: ADR-0.0.39-llm-as-judge-doctrine
---

# ADR-pool.advisory-judge-surface: Advisory LLM-as-judge surface (non-gating)
> Promoted to `ADR-0.0.39-llm-as-judge-doctrine` on 2026-05-06. This pool file is retained as historical intake context.


## Status

Superseded

## Intent

The anti-vibing mantra forbids treating LLM-as-judge as a **gate** —
correctly so. It does not forbid using LLM-as-judge as an
**evidence-producing advisory surface** that pairs with mechanical
floors. gzkit currently has no surface for the residual-subjective
question that mechanical validators cannot answer:

- *Does this ADR's Intent prose actually communicate the intent?*
  `gz-adr-evaluate` scores 8 mechanical dimensions but cannot judge
  prose clarity.
- *Are these three insight records near-duplicates?*
  `gz-insights-refresh` (proposed) needs pre-classification help that
  is fundamentally a similarity-judgment task.
- *Does this attestation text's enrichment actually cite concrete
  facts, or is it vague adjectives in disguise?* AGENTS.md
  § Attestation forbids vague adjectives but provides no mechanical
  detector for them.

Each of these is a residual-subjective surface where mechanical
validation is impossible and Gate-5 attestation is too heavy. A bounded,
non-gating judge surface — paired with a mechanical floor and a
reproducibility receipt — fills the gap without re-opening the
LLM-as-gate failure class.

## Decision

_[To be filled at promotion time]_

Sketch — bound by four governance invariants (mirror of the corpus
invariants):

1. **Never a gate.** Judge output is advisory; operator decides
   accept/revise/reject. Same shape as `gz-plan-audit` findings.
   Schema-rejected if any caller treats output as pass/fail.
2. **Always paired with a mechanical floor.** Judge runs *after*
   mechanical validators pass, never instead. Doctrine: *floor catches
   the failure class; judge catches the residual subjective surface.*
3. **Reproducibility receipt.** Each judge invocation emits an
   ARB-shaped receipt (model, prompt-hash, input-hash, output, exit
   status). Judge verdicts cited in attestation MUST cite the receipt
   ID, same as any other citation.
4. **Bounded scope.** Judge fires only on explicitly-named subjective
   surfaces (initial set: prose-clarity, near-duplicate, grounding-
   check). Surface list lives in
   `.gzkit/rules/advisory-judge-surfaces.md`; adding a surface
   requires foundation-kind ADR justifying why mechanical validation
   cannot cover it.

Possible CLI shape: `gz judge prose <path>`, `gz judge dedup
<corpus>`, `gz judge grounding <attestation-text>`. All emit receipts
under `artifacts/receipts/judge-*.json`.

## Target Scope

- **rule-and-doctrine** — Author the canonical rule file at `.gzkit/rules/llm-as-judge.md` codifying the survey-aligned framework: three-axis declaration (what/how/where) per [arxiv 2411.15594](https://arxiv.org/abs/2411.15594); named bias roster (position bias, verbosity bias, self-preference bias, preference leakage); methodology menu with rationale-of-choice (single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble); output-format discipline (explanation-precedes-verdict; no naked verdict); meta-evaluation cadence (sample human-agreement N times per 100 verdicts); inheritance from ADR-0.0.38 Evidentiary axis.
- **judge-invocation-schema** — Define the judge-invocation declaration schema (Pydantic + JSON Schema) every LLM-as-judge surface must populate at invocation time: `judge_model`, `judge_model_family`, `candidate_provenance` (model + family of the artifact under judgment), `methodology`, `what_axis` (judged content type), `how_axis` (judging technique), `where_axis` (application domain), `bias_mitigations` (named mitigations applied), `explanation_text`, `verdict`, `prompt_hash`, `input_hash`. Receipts that fail to populate any required field are rejected by the existing ARB validator.
- **existing-judge-surface-classification** — Classify every existing LLM-as-judge surface in gzkit (`gz-adr-evaluate --red-team`, runtime `advisor()` tool, `gz-complexity-distill` advisor verdicts) under the three-axis taxonomy; emit `judge_surface_classified` ledger event per surface; produce baseline at `artifacts/audits/judge-surface-classification-2026-05-06.md`; supersede the three pool ADRs governed by this doctrine (`advisory-judge-surface` self-supersession at promotion; `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` marked as governed-by-ADR-0.0.39 in their pool frontmatter, remaining in pool until later promotion).

## Proposed OBPI Decomposition

| Slug | Description |
|---|---|
| `rule-and-doctrine` | Author `.gzkit/rules/llm-as-judge.md` codifying the survey-aligned framework (three-axis what/how/where, named bias roster, methodology menu, explanation-then-verdict output discipline, meta-eval cadence); register in advisory-rules-audit scorecard as **Mechanical** (forward-reference to ADR-0.0.40 validators); declare own `surface_axis: authoritative` per ADR-0.0.38 |
| `judge-invocation-schema` | Define `JudgeInvocation` Pydantic model + `judge_invocation.json` JSON Schema mirror covering every field the doctrine requires (judge_model, judge_model_family, candidate_provenance, methodology, three-axis, bias_mitigations, explanation_text, verdict, hashes); extend ARB receipt validator to require these fields on judge-prefixed receipts; tests assert schema validation passes for compliant invocations and fails for missing/off-enum values |
| `existing-judge-surface-classification` | Retroactively classify every existing judge surface under the three-axis taxonomy with cited rationale anchors; emit `judge_surface_classified` ledger event per surface; produce `artifacts/audits/judge-surface-classification-2026-05-06.md` baseline; mark dependent pool ADRs (`attestation-advisory-agent`, `lightweight-pre-implementation-challenger`) as governed-by-ADR-0.0.39 in their frontmatter; Gate 5 walkthrough confirms each classification |

## Alternatives Considered

1. **Reject LLM-as-judge categorically.** Original position; rejected
   under the four-invariant boundary. Categorical rejection forfeits
   the only viable surface for residual-subjective surfaces, which
   fall through the cracks today (vague-adjective enrichment passes
   mechanical attestation validation; near-duplicate insight records
   accumulate uncaught).
2. **Treat judge output as a gate.** Rejected — reproduces the named
   LLM-as-gate failure class. The four-invariant frame exists
   specifically to forbid this.
3. **Use a deterministic heuristic instead.** Rejected for the named
   surfaces — prose clarity, near-duplicate semantic detection, and
   grounding judgment are not amenable to deterministic heuristics
   that don't themselves degrade into vibing surfaces. The judge is
   the lower-vibing-surface choice.
4. **Operator-only judgment.** Plausible but loses the receipt
   surface — operator judgment in chat does not produce a citable
   artifact. The receipt is the point.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
