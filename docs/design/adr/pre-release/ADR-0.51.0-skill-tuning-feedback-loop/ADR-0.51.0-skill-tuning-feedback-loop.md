---
id: ADR-0.51.0-skill-tuning-feedback-loop
status: Proposed
kind: feature
semver: 0.51.0
lane: heavy
parent: PRD-GZKIT-1.0.0
bounded_context: skill-evaluation
date: 2026-05-22
promoted_from: ADR-pool.skill-tuning-feedback-loop
---

# ADR-0.51.0-skill-tuning-feedback-loop: Skill Tuning Feedback Loop

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active driver:** `quality-reviewer` — see `.gzkit/personas/quality-reviewer.md`.

Agents working on this ADR treat skill quality as an empirically measurable property, not a vibes assessment. Architectural-rigor demands that candidate skill edits be evaluated against a hard goal basket built from observed failures — `skill_feedback` events, OBPI pipeline friction, wrong-skill invocations, ARB-backed command failures — never against synthetic test sets. The qualitative intake (`skill_feedback`) and the empirical tuning loop are deliberately separate: collapsing them is the named anti-pattern because friction capture and behavioral measurement have different fidelity contracts. Skills constrain outputs and safety, not the agent's diagnostic path — a skill body that over-scripts inspection of scores, traces, and prior failures is overreach, not discipline. Validation precedes behavioral evaluation: structural defects (lint, schema, mirror parity) are caught before a candidate consumes evaluation budget. Maintainability-assessment demands that the tuning chore stay reproducible across model cycles; non-deterministic evaluation is a defect, not a quirk.

## Intent

Add an empirical tuning loop for gzkit skills as agent-control surfaces,
complementing `ADR-pool.skill-feedback-loop` rather than replacing it.

**Current state.** Skill quality is assessed by qualitative friction capture
(`skill_feedback` events) and static structural checks (`skill-authoring-quality`,
`skill-trigger-testing` chores). There is no empirical measurement of whether a
skill edit improves agent behavior against observed failure classes. Skills
accumulate prose across model cycles with no reproducible signal that trimming
or recalibrating them maintains behavioral fidelity.

**Target state.** A `skill_tuning` chore evaluates candidate skill edits
(trim proposals or model-recalibration passes) against hard goal baskets built
from observed failures — insights, OBPI friction, ARB receipts. A cross-model-
family evaluator produces a dry-run walkthrough (narrated tool calls, scored on
call-shape fidelity) and rubric score for baseline-vs-candidate, creating a
reproducible trim/recalibrate signal. Each skill's evaluation genealogy persists
in a dedicated `optimize:` metadata block in `SKILL.md` frontmatter. The chore
is ad-hoc — run when the operator decides to trim or when a new model lands;
it is not a commit gate.

`ADR-pool.skill-feedback-loop` captures qualitative friction at the moment a
skill fails, undertriggers, overtriggers, or sends an agent down a suboptimal
path. This ADR defines the next layer: turn that feedback, plus insights,
ARB receipts, OBPI friction, wrong-skill invocations, and review findings, into
hard skill evaluation baskets and measured candidate-skill tuning runs.

The motivating claim from Meta-Harness is narrow and useful for gzkit: skill
text is the primary interface for steering a search or agent workflow, and its
quality is best improved by short empirical runs against difficult cases, full
trace access, lightweight validation, and explicit output/safety constraints.
For gzkit, that means a skill edit is not better because the prose reads better;
it is better when it improves behavior against observed failure classes.

## Decision

Create a complementary skill-tuning capability with these boundaries:

1. Qualitative feedback remains separate. `skill_feedback` events identify
   friction, ambiguity, missing instructions, or bad skill routing. They are the
   intake signal, not the whole tuning loop.
2. Tuning episodes compare candidates. A `skill_tuning` episode evaluates a
   baseline skill version and one or more candidate edits against a hard goal
   basket before promotion.
3. Hard cases come from gzkit evidence. Search sets are built from
   `.gzkit/insights/agent-insights.jsonl`, prior `skill_feedback` events, OBPI
   pipeline friction, wrong-skill invocations, review comments, and ARB-backed
   command failures.
4. Skills constrain outputs and safety, not diagnosis. Skill bodies should
   define role, directory layout, CLI commands, output format, forbidden
   behavior, artifacts to produce, and objectives to optimize. They should not
   over-script the agent's diagnostic path when the right behavior is to inspect
   scores, traces, files, and prior failures.
5. Validation comes before behavioral evaluation. Candidate skill edits must
   pass frontmatter schema, registered command resolution, output-contract
   presence, mirror-sync rules, and forbidden-scope checks before any expensive
   behavioral comparison.
6. Traces are diagnostic, not ledger truth. ARB remains observed command
   evidence; the ledger records governance decisions and accepted tuning
   events. Full tuning traces live in a queryable proof surface so future agents
   can inspect raw candidate behavior without relying on summaries.

Candidate episode shape:

```text
skill_id
skill_version
baseline_skill_path
candidate_skill_patch
hard_goal_basket_id
source_evidence_refs
validation_results
trigger_alignment_score
output_contract_score
safety_boundary_score
scope_violation_count
trace_refs
arb_receipt_refs
promotion_decision
```

The first implementation should extend the existing `skill-authoring-quality`
and `skill-trigger-testing` chores rather than invent a parallel framework.
Those chores already encode the correct local vocabulary: descriptions are
routing signals, bodies encode domain reasoning, and output contracts are
downstream parse surfaces.

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

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
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.51.0-01: **evaluation-episode-contract** — Define the skill_tuning episode shape: dry-run walkthrough method (evaluator narrates the tool calls it would make against reference tasks, scored on call-shape fidelity), rubric dimensions (comprehension + tool-fidelity; tool-fidelity weight → 0 for non-tool skills), pass threshold, cross-model-family evaluator protocol, AND register the skill-evaluation vocabulary in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR (per ADR-0.0.43 cascade contract).
- [ ] OBPI-0.51.0-02: **hard-basket-builder** — Extend the skill-authoring-quality and skill-trigger-testing chores to build and run hard goal baskets from agent-insights.jsonl, skill_feedback events, OBPI pipeline friction, wrong-skill invocations, and ARB-backed failures.
- [ ] OBPI-0.51.0-03: **skill-md-frontmatter-schema** — Define the optimize: metadata block in SKILL.md frontmatter: tested_against (model + date), content_hash, rubric_score, prior_opinion_trail. Persists the evaluation genealogy with no per-model skill forks.
- [ ] OBPI-0.51.0-04: **chore-run-modes** — Implement the Optimize ad-hoc chore with two run-modes: trim-and-verify (proposes a trim, evaluates fidelity before and after) and recalibrate-verify (new-model landing, no trim, re-scores against current model). Logging and report artifact with governance trail.
- [ ] OBPI-0.51.0-05: **prose-improvement-loop** — Add the evaluator prose-improvement suggestion step: after rubric scoring the evaluator suggests specific skill prose improvements; human gate and attestation closes the loop.
- [ ] OBPI-0.51.0-06: **docs-validation-fixtures** — Add docs, examples, and validation fixtures for ad-hoc chore invocation patterns and skill coverage tracking.

## Target Scope

- **evaluation-episode-contract** — Define the skill_tuning episode shape: dry-run walkthrough method (evaluator narrates the tool calls it would make against reference tasks, scored on call-shape fidelity), rubric dimensions (comprehension + tool-fidelity; tool-fidelity weight → 0 for non-tool skills), pass threshold, and cross-model-family evaluator protocol.
- **hard-basket-builder** — Extend the skill-authoring-quality and skill-trigger-testing chores to build and run hard goal baskets from agent-insights.jsonl, skill_feedback events, OBPI pipeline friction, wrong-skill invocations, and ARB-backed failures.
- **skill-md-frontmatter-schema** — Define the optimize: metadata block in SKILL.md frontmatter: tested_against (model + date), content_hash, rubric_score, prior_opinion_trail. Persists the evaluation genealogy with no per-model skill forks.
- **chore-run-modes** — Implement the Optimize ad-hoc chore with two run-modes: trim-and-verify (proposes a trim, evaluates fidelity before and after) and recalibrate-verify (new-model landing, no trim, re-scores against current model). Logging and report artifact with governance trail.
- **prose-improvement-loop** — Add the evaluator prose-improvement suggestion step: after rubric scoring the evaluator suggests specific skill prose improvements; human gate and attestation closes the loop.
- **docs-validation-fixtures** — Add docs, examples, and validation fixtures for ad-hoc chore invocation patterns and skill coverage tracking.

## Non-Goals

- No autonomous skill promotion.
- No replacement of `skill_feedback` events.
- No direct ledger storage of bulky traces.
- No cross-repo skill marketplace or sharing protocol.
- No model-specific optimization that only works for one vendor harness.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The operator agrees that skill tuning should complement, not replace,
   qualitative skill feedback.
2. The hard-basket source set is accepted: insights, feedback events, OBPI
   friction, wrong-skill invocations, review findings, and ARB-backed failures.
3. The first tuned skill target is selected; recommended first target is
   `gz-obpi-pipeline` or `gz-design` because both are high-leverage and have
   clear failure modes.
4. The storage boundary is agreed: ledger for accepted governance events, proof
   surface for full traces.
5. Acceptance criteria can be decomposed into OBPIs without weakening
   human-review boundaries for skill edits.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Bounded Context

This ADR belongs to the **`skill-evaluation`** bounded context (per ADR-0.0.43 DDD Domain Cascade). Vocabulary codified in PRD-GZKIT-1.0.0 § 2.1 with provenance to this ADR: `evaluation-episode`, `hard-basket`, `dry-run-walkthrough`, `tool-fidelity`, `baseline-vs-candidate`, `prior-opinion-trail`. Cross-cutting rubric terms (`rubric-dimension`, `rubric-finding`, `evidence-citation`) are shared with the `governance-triage` BC via the cross-cutting kernel.

## Dependencies

- **`ADR-0.0.43-ddd-domain-cascade`** (Draft, foundation) — Provides the bounded-context frontmatter convention, the `UbiquitousLanguageTerm`/`BoundedContextDeclaration` Pydantic models, the `gz-glossary-<term>` marker convention, and the three-point pre-Gate-1 cascade enforcement. This ADR is one of the first consumers of that cascade (Path 2 use-pull); implementation of ADR-0.51.0 requires ADR-0.0.43's OBPI-01 (PRD section schema + Pydantic foundation) and OBPI-04 (frontmatter cascade keys validators) to land first or in parallel.
- **`src/gzkit/chores/skill-authoring-quality/`** and **`src/gzkit/chores/skill-trigger-testing/`** — existing chores that `hard-basket-builder` (OBPI-02) extends rather than reinvents.

## Implementation Precedent

- `src/gzkit/chores/skill-authoring-quality/` — existing chore extended by
  `hard-basket-builder`; structural quality checks become a preflight validator
  for candidate skill edits.
- `src/gzkit/chores/skill-trigger-testing/` — existing chore extended by
  `hard-basket-builder`; synthetic goal tests become evidence-backed hard-basket
  evaluation.
- `.gzkit/skills/**/SKILL.md` — the surface the `skill-md-frontmatter-schema`
  OBPI writes the `optimize:` metadata block to; no per-model skill forks.
- `.gzkit/insights/agent-insights.jsonl` — primary hard-basket signal source
  (recurring failure patterns, wrong-approach, premature implementation); also
  consumed by `ADR-0.0.26-evaluation-feedback-loop-doctrine`.
- `src/gzkit/commands/register.py` — ledger registration pattern this ADR
  follows for accepted `skill_tuning` episode events.

**Exemplar / Precedent.** The three-step chore pattern mirrors `ghi-triage`
(mechanical pre-pass, agent cognitive pass, deterministic report — GHI #424
round-3 hardening). Evaluation-feedback doctrine is established by
`ADR-0.0.26`; this ADR applies it to the skill control surface. Skill lifecycle
transitions follow `ADR-0.5.0-skill-lifecycle-governance`.

**Anti-pattern.** A skill edit is not better because the prose is shorter;
it is better when it improves behavior against observed failure classes. Do not
evaluate skill fidelity with the same model family as the session model — the
evaluator must be cross-model-family. Do not wire Optimize as a commit gate;
it is an ad-hoc operator tool, not a fail-closed surface.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.skill-tuning-feedback-loop` on 2026-05-22; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

### A. Replace `ADR-pool.skill-feedback-loop` with a broader tuning ADR

Rejected. Qualitative moment-of-friction capture remains valuable and should
stay small. Tuning is a second-stage evaluation loop over accumulated feedback,
not a substitute for recording it when it happens.

### B. Keep feedback qualitative only

Rejected. Meta-Harness shows skill text quality can dominate search behavior,
and short hard-case runs are more informative than prose review alone. A
qualitative-only queue preserves observations but fails to discriminate candidate
fixes.

### C. Let agents autonomously edit and promote skills

Rejected. gzkit skills are governance-critical control surfaces. Candidate
generation may be agent-assisted, but promotion remains human-reviewed and
gate-governed under the Universal OBPI Attestation (ADR-0.0.36).

### D. Store all diagnostic traces in the ledger

Rejected. The ledger is Layer-2 truth, not a bulk trace database. Full traces
belong in a queryable proof surface; ledger events point at accepted governance
decisions only.

### E. Keep this work in the pool backlog

Rejected at promotion time (2026-05-22): operator demand signal exists, the
hard-basket source set is defined, and existing chores provide the extension
surface the implementation needs.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.51.0 | Pending | | | |
