---
id: ADR-pool.judge-enforcement-validators
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.0.39
inspired_by:
  - https://arxiv.org/abs/2411.15594
  - https://llm-as-a-judge.github.io/
promoted_to: ADR-0.0.40-judge-enforcement-validators
---

# ADR-pool.judge-enforcement-validators: Judge Enforcement Validators
> Promoted to `ADR-0.0.40-judge-enforcement-validators` on 2026-05-06. This pool file is retained as historical intake context.


## Status

Superseded

## Date

2026-05-06

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

ADR-0.0.39 (LLM-as-judge doctrine) codifies the survey-aligned
framework — three-axis declaration, named bias roster, methodology
menu, explanation-then-verdict output discipline, meta-evaluation
cadence — and lands the judge-invocation schema. ADR-0.0.39's
invariants are mechanical-witness-shaped (every invariant has a
named field in the schema; every field has a named validator floor),
but ADR-0.0.39 does not ship the validators themselves. Without the
validators firing, ADR-0.0.39 is a Promotable-but-unpromoted rule per
`docs/governance/advisory-rules-audit.md` — the canonical anti-pattern
the maxim disqualifies.

This ADR closes the loop: it ships the validator scopes, the
meta-evaluation CLI, the receipt-shape extensions to existing judge
surfaces (`gz-adr-evaluate --red-team`, runtime `advisor()` tool), and
the canonical ARB step slots that judge invocations cite from
attestation. After this ADR closes, every invariant in ADR-0.0.39 has
a fail-closed mechanical floor; LLM-as-judge in gzkit becomes
structurally bounded, not honor-system bounded.

The survey paper's named bias surface — **preference leakage** (judge
and candidate from the same model family) — is the highest-leverage
class this ADR's validator closes. gzkit currently runs
`gz-adr-evaluate --red-team` and the runtime `advisor()` tool with no
mechanism to detect or flag same-family judging across the receipt
corpus. The leakage validator scans every judge receipt and either
fail-closes (heavy lane) or flags (lite lane) on detected
preference-leakage risk.

## Decision

_[To be filled at promotion time]_

Sketch:

1. **`gz validate --judge-leakage`** (new validator scope, Authoritative axis per ADR-0.0.38). Scans every judge invocation receipt under `artifacts/receipts/judge-*.json` and the historical ledger; flags same-family judge⇄candidate pairs; fail-closes (exit 3) under heavy lane unless an explicit waiver in `data/judge_leakage_waivers.json` covers the case with cited rationale.
2. **`gz validate --judge-output-discipline`** (new validator scope, Authoritative axis). Verifies that every judge invocation receipt carries: explanation_text populated AND positioned BEFORE verdict in the prompt, methodology field declared from the menu enum, bias_mitigations field naming applied mitigations, three-axis declaration. Fail-closes on missing fields or out-of-order explanation/verdict.
3. **`gz judge meta-eval`** (new CLI verb, Evidentiary axis). Produces the human-agreement metric over a sampled window: takes a receipt-corpus window and a sampled human-attestation set; computes Cohen's kappa or equivalent agreement metric; emits a `judge_meta_eval` ledger event; receipt cited in attestation. Surfaces drift if the metric falls below a configurable floor.
4. **Receipt-shape extension** to ARB validator. The judge-invocation schema from OBPI-0.0.39-02 lands the schema; this OBPI extends `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` with `arb-step-judge-*` slots for canonical citations and updates ARB middleware to validate judge receipts against the schema at emit time.
5. **Existing-judge-surface retrofit.** Update `gz-adr-evaluate --red-team` to populate every judge_invocation field (judge_model, judge_model_family, candidate_provenance, methodology, three-axis, bias_mitigations) — emitting compliant receipts going forward. Update the runtime `advisor()` tool's documentation in `CLAUDE.md` to declare its bias profile and the cases where invoking it is itself a doctrine violation (e.g., when same-family preference-leakage is the failure mode under test). Backfill historical waivers for receipts emitted before this ADR closed.

---

## Target Scope

- **receipt-shape-extension** — Extend `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` with `arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*` canonical slots; extend ARB middleware to validate judge-invocation receipts against the schema authored under OBPI-0.0.39-02 at emit time; add `judge_invocation_validated` ledger event family.
- **judge-leakage-validator** — Implement `gz validate --judge-leakage` validator scope: enumerate all judge-invocation receipts, detect same-family judge⇄candidate pairs from the model_family declarations, fail-close under heavy lane on unwaived violations, honor `data/judge_leakage_waivers.json` registry; document model-family equivalence taxonomy (e.g. claude-opus-4-X all share family `claude-opus-4`); BDD acceptance scenarios.
- **judge-output-discipline-validator** — Implement `gz validate --judge-output-discipline` validator scope: verify explanation_text populated AND positioned before verdict, methodology declared from the enum, bias_mitigations declared, three-axis declared; fail-close on out-of-order or missing fields; integrate into default `gz check` scope set.
- **meta-eval-cli** — Implement `gz judge meta-eval` CLI verb: takes `--window` (receipt range), `--human-attestations` (sampled-attestation source), computes Cohen's kappa or equivalent; emits `judge_meta_eval` ledger event with metric value, sample size, window timestamps; receipt name `arb-step-judge-meta-eval-*`; default floor for kappa configurable in `data/judge_meta_eval_floor.json`; manpage + runbook entries.
- **existing-judge-surface-retrofit** — Update `src/gzkit/commands/adr_evaluate.py` red-team path to populate every judge_invocation field on emitted receipts; update `CLAUDE.md` § Advisor Tool to declare advisor()'s bias profile and the named "do not invoke" cases (same-family-leakage failure-mode tests, peer review of own prior reasoning); backfill historical receipts via waivers in `data/judge_leakage_waivers.json` with cited reason `pre-ADR-0.0.40-baseline`; supersede pool ADRs `attestation-advisory-agent` and `lightweight-pre-implementation-challenger` as governed-by-this-validator-set.

## Proposed OBPI Decomposition

| Slug | Description |
|---|---|
| `receipt-shape-extension` | Extend `CANONICAL_STEP_COMMANDS` with judge-step slots; extend ARB middleware to validate judge-invocation receipts against the OBPI-0.0.39-02 schema at emit time; add `judge_invocation_validated` ledger event family; tests assert receipts missing required schema fields are rejected at emit |
| `judge-leakage-validator` | Implement `gz validate --judge-leakage` (Authoritative axis): enumerate judge receipts, detect same-family pairs, fail-close on unwaived violations under heavy lane, honor `data/judge_leakage_waivers.json` with frozen Pydantic schema; model-family equivalence registry; BDD scenarios cover leakage-detected and waiver-honored cases |
| `judge-output-discipline-validator` | Implement `gz validate --judge-output-discipline` (Authoritative axis): verify explanation_text populated AND positioned before verdict, methodology and three-axis and bias_mitigations declared; fail-close on out-of-order or missing fields; integrate into default `gz check` scope; BDD scenarios cover compliant and each named drift case |
| `meta-eval-cli` | Implement `gz judge meta-eval` (Evidentiary axis CLI verb): compute Cohen's kappa over a receipt-window vs sampled-attestation set; emit `judge_meta_eval` ledger event; receipt prefix `arb-step-judge-meta-eval-`; floor in `data/judge_meta_eval_floor.json`; manpage + runbook + governance-runbook updates |
| `existing-judge-surface-retrofit` | Update `gz-adr-evaluate --red-team` to populate full judge_invocation receipt fields; update `CLAUDE.md` § Advisor Tool with bias-profile declaration and named "do not invoke" cases; backfill historical receipts via waiver registry with cited `pre-ADR-0.0.40-baseline` reason; mark `ADR-pool.attestation-advisory-agent` and `ADR-pool.lightweight-pre-implementation-challenger` as governed-by-ADR-0.0.40 in their frontmatter |

---

## Alternatives Considered

1. **Fold validators into ADR-0.0.39.** Plausible — same shape as ADR-0.0.38 folded its validator into one ADR. Rejected per operator's explicit two-ADR split: ADR-0.0.39 is doctrine-rich (codifies the survey-aligned framework, which is content-heavy); ADR-0.0.40 is mechanism-heavy (validators, CLI verbs, receipt extensions). Splitting keeps each ADR's surface coherent and Gate 5 walkthroughs proportionate.
2. **Author validators inline per surface.** Rejected — leaves the doctrinal floor uncited and unenforced. Each surface re-deriving its leakage check is the same fragmentation pattern ADR-0.0.38 was promoted to close.
3. **Deterministic heuristic for leakage detection (e.g., string-match on model name).** Insufficient — model_family equivalence requires a registered equivalence map (e.g., `claude-opus-4-7` and `claude-opus-4-6` share family `claude-opus-4`), which is doctrine, not heuristic. The validator consults the registry; the registry is doctrine.
4. **Skip the meta-evaluation CLI; rely on operator vibe-check.** Rejected — judge-correctness drift over time is a named survey-paper concern; honor-system "operator notices when the judge gets weird" is the canonical doctrine-drift-as-invariant-drift failure shape.
5. **Defer this ADR until at least one judge surface fails in the wild.** Rejected — the maxim disqualifies "wait for failure" as a sequencing argument when the failure class is structural and the validator is feasible.

---

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
