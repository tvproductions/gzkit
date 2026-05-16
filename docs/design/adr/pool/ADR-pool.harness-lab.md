---
id: ADR-pool.harness-lab
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.harness-trace-bundles
inspired_by: "arXiv:2603.28052v1 Meta-Harness"
complements:
  - ADR-pool.workflow-specification
  - ADR-pool.harness-trace-bundles
  - ADR-pool.harness-fitness-report
  - ADR-pool.skill-tuning-feedback-loop
---

# ADR-pool.harness-lab: Offline Harness Lab

## Status

Pool

## Date

2026-05-16

## Intent

Add an offline experiment loop for gzkit's own harness surfaces: workflows,
skills, rules, hooks, reviewer stages, sidecars, receipts, and control-surface
composition. The loop should compare candidate harness variants against hard
task baskets, preserve full traces, and emit human-reviewed proposals.

This is the gzkit translation of Meta-Harness, not a copy of its autonomous
optimization posture. Meta-Harness demonstrates that harness code and control
surfaces can be improved by an outer loop that keeps full prior source, scores,
and execution traces available through the filesystem. gzkit should absorb that
lesson while preserving its own boundary: no candidate can promote itself into
canon, and no experiment result bypasses ADR/OBPI/Gate 5.

## Decision

When promoted, create a `gz harness lab` surface that runs controlled offline
experiments over harness variants.

Candidate command shape:

```bash
gz harness lab run <basket> --candidate <candidate-ref>
gz harness lab compare <episode-id>
gz harness lab ablate <basket> --module <module-id>
gz harness lab report <episode-id>
```

An episode compares a baseline against one or more candidates:

```text
episode_id
basket_id
baseline_ref
candidate_refs
module_matrix
workflow_ref
control_surface_snapshot_refs
trace_bundle_refs
scorecard
pareto_frontier
failure_clusters
proposal_refs
promotion_recommendation
human_disposition
```

The first implementation should be export-first:

1. Consume `ADR-pool.workflow-specification` output for the OBPI pipeline so the
   lab evaluates a declared workflow object rather than re-inferring the
   pipeline from prose.
2. Consume `ADR-pool.harness-trace-bundles` for raw run evidence.
3. Produce reports and proposals only. Canon edits remain manual,
   ADR/OBPI-governed, and human-attested.

## Module Ablation Scope

The lab should support module-level ablation rather than whole-system folklore
comparisons. Candidate module IDs include:

- `workflow_spec`
- `file_backed_state`
- `review_agent_stage`
- `skill_feedback`
- `skill_tuning`
- `receipt_binding`
- `hook_enforcement`
- `sidecar_watch`
- `validator_telemetry`
- `context_surface_weight`
- `multi_candidate_search`

Each ablation report should distinguish:

- behavioral score changes,
- cost changes,
- solved-set replacement vs true frontier expansion,
- failure classes introduced by the module,
- trace-backed evidence for each claim.

## Target Scope

- Define harness-lab episode and basket schemas.
- Add a read-only report surface for existing trace bundles before enabling any
  candidate execution.
- Add a small hard basket seeded from existing gzkit evidence: wrong-skill
  invocations, OBPI pipeline friction, eval-feedback clusters, hook blocks, and
  reviewer findings.
- Add candidate isolation rules: temporary worktree or sandbox, clean root
  commit, no direct mutation of canonical control surfaces.
- Add report output that names candidate winners, regressions, and uncertainty.
- Add proposal emission to a human review queue, not direct edits.

## Non-Goals

- No autonomous self-modification of skills, rules, workflows, or hooks.
- No use of test-set results during candidate generation.
- No replacement for `gz check`, `gz status`, or Gate 5 attestation.
- No generic benchmark runner unrelated to gzkit governance surfaces.
- No claim that higher aggregate score means safe promotion without operator
  review.

## Alternatives Considered

1. **Tune individual skills only.** Rejected as too narrow. Existing
   `ADR-pool.skill-tuning-feedback-loop` remains valuable, but the latest paper
   comparison exposed a broader harness question: workflows, hooks, state,
   receipts, reviewers, and guide weight interact.
2. **Let a coding agent rewrite the harness directly.** Rejected. Meta-Harness
   is useful as an experimental pattern, but gzkit's canon changes require
   governed review.
3. **Run only scalar benchmarks.** Rejected. Scalar scores help rank candidates
   but cannot explain failure classes. Trace bundles are required evidence.
4. **Use harness lab before workflow export exists.** Rejected for v1.
   Experimenting against inferred prose would reproduce the ambiguity the lab is
   meant to reduce.

## Dependencies

- **Requires:** `ADR-pool.harness-trace-bundles` for raw diagnostic evidence.
- **Consumes:** `ADR-pool.workflow-specification` so workflows are explicit
  experiment objects.
- **Consumes:** `ADR-pool.skill-tuning-feedback-loop` as the narrower skill-only
  lab mode.
- **Feeds:** `ADR-pool.harness-fitness-report` with episode outcomes and module
  ablation data.
- **Related:** the validator-telemetry concept from the 2026-04-26
  harness-engineering improvement handoff; `validator_telemetry` is one module
  in this lab's scorecard unless it later receives its own pool ADR.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. `ADR-pool.harness-trace-bundles` has a stable manifest schema or is promoted
   in the same ADR package.
2. `ADR-pool.workflow-specification` has at least read-only OBPI pipeline export
   or a promotion plan that lands before candidate execution.
3. The first hard basket is selected and built from existing gzkit evidence, not
   invented examples.
4. Candidate isolation rules are accepted.
5. The operator accepts the boundary that the lab emits proposals, never direct
   canon edits.

## Notes

Pool ADRs are backlog items -- they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
