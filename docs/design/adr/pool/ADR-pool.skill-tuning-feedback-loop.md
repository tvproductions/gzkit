---
id: ADR-pool.skill-tuning-feedback-loop
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
complements: ADR-pool.skill-feedback-loop
inspired_by: arXiv:2603.28052v1 Meta-Harness
---

# ADR-pool.skill-tuning-feedback-loop: Skill Tuning Feedback Loop

## Status

Pool

## Intent

Add an empirical tuning loop for gzkit skills as agent-control surfaces,
complementing `ADR-pool.skill-feedback-loop` rather than replacing it.

`ADR-pool.skill-feedback-loop` captures qualitative friction at the moment a
skill fails, undertriggers, overtriggers, or sends an agent down a suboptimal
path. This pool item defines the next layer: turn that feedback, plus insights,
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

## Alternatives Considered

1. Replace `ADR-pool.skill-feedback-loop` with a broader tuning ADR - rejected.
   The qualitative moment-of-friction capture remains valuable and should stay
   small. Tuning is a second-stage evaluation loop over accumulated feedback,
   not a substitute for recording the feedback when it happens.
2. Keep feedback qualitative only - rejected. Meta-Harness shows that skill
   text quality can dominate search behavior, and short hard-case runs are more
   informative than prose review alone. A qualitative-only queue would preserve
   observations but fail to discriminate candidate fixes.
3. Let agents autonomously edit and promote skills - rejected. gzkit skills are
   governance-critical control surfaces. Candidate generation may be
   agent-assisted, but promotion remains human-reviewed and gate-governed.
4. Store all diagnostic traces in the ledger - rejected. The ledger is Layer-2
   truth, not a bulk trace database. Full traces belong in a queryable proof
   surface with ledger events pointing at accepted decisions.

## Relationship to Existing Work

- Complements: `ADR-pool.skill-feedback-loop` -- qualitative feedback events
  become one source of tuning cases.
- Consumes: `.gzkit/insights/agent-insights.jsonl` -- recurring wrong approach,
  misunderstood request, premature implementation, and skill friction patterns
  become hard basket inputs.
- Consumes: ARB receipts -- command-observed failures and successes ground
  tuning claims.
- Extends: `skill-authoring-quality` chore -- structural quality becomes a
  preflight validator for candidate skills.
- Extends: `skill-trigger-testing` chore -- synthetic goal testing becomes
  evidence-backed hard-basket evaluation.
- Aligns with: `ADR-0.0.26-evaluation-feedback-loop-doctrine` -- this is the
  skill-surface version of the same feedback-loop doctrine.

## Target Scope

- Define the `skill_tuning` episode record shape and storage layer.
- Extend skill-quality chores to build and run hard goal baskets.
- Add a report surface showing baseline vs candidate skill behavior.
- Define promotion criteria for accepting a candidate skill edit.
- Add provenance links from accepted skill edits to tuning episodes.
- Preserve human review and existing `skill-version` / mirror-sync discipline.

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
