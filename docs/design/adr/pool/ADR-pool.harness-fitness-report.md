---
id: ADR-pool.harness-fitness-report
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: "arXiv:2603.28052v1 Meta-Harness; arXiv:2603.25723 Natural-Language Agent Harnesses"
complements:
  - ADR-pool.harness-lab
  - ADR-pool.harness-trace-bundles
  - ADR-pool.workflow-specification
---

# ADR-pool.harness-fitness-report: Harness Fitness Report

## Status

Pool

## Date

2026-05-16

## Intent

Add an operator-facing report that measures gzkit's harness health: validator
coverage and hit rate, rule and skill surface weight, receipt-citation
discipline, trace availability, guide-vs-sensor redundancy, and module
ablation outcomes.

gzkit's harness is intentionally thick. The missing surface is measurement:
which sensors fire, which guides are still load-bearing, which validators are
noisy, which checks are expensive, and which harness modules improve behavior
rather than only adding ceremony.

## Decision

When promoted, add a `gz harness report` or `gz health` surface that aggregates
harness-fitness signals without replacing `gz check`.

Candidate command shape:

```bash
gz harness report
gz harness report --since <commit>
gz harness report --surface validators
gz harness report --surface control-surfaces
gz health
gz health --since <commit>
```

The report should include:

- validator invocation count, duration, exit code, and hit count;
- zero-hit validator scopes that may be retirement candidates;
- validator scopes with recurring failures and their doctrine anchors;
- control-surface size by file and vendor mirror;
- guide-to-sensor coverage matrix entries;
- receipt-citation coverage for attestation claims;
- trace-bundle availability for harness-lab and skill-tuning episodes;
- module ablation outcomes from `ADR-pool.harness-lab`;
- unresolved skill feedback and tuning proposals;
- stale or unreviewed harness-learning artifacts.

The storage layer for telemetry is explicitly not the ledger. Candidate roots:

- `.gzkit/telemetry/validator-events.jsonl`
- `.gzkit/receipts/harness-fitness/<run-id>/`
- `artifacts/reports/harness-fitness/<date>.md`

The exact root should align with `ADR-pool.canonical-vs-runtime-separation` if
that ADR lands first.

## Relationship To Existing Surfaces

- `gz check` remains the pass/fail quality gate.
- `gz status` remains lifecycle state reporting.
- `gz state` remains artifact relationship reporting.
- `gz harness report` / `gz health` reports the harness itself: cost, coverage,
  redundancy, drift, and learning-loop backlog.

## Target Scope

- Define telemetry event schema for validator and harness-module observations.
- Add a report renderer that produces a compact table plus detailed sections.
- Add `--since <commit>` delta mode.
- Add a zero-hit and high-cost scope review section.
- Add links to doctrine anchors and recovery commands for failing scopes.
- Add a "guide coverage" section that points to rule/skill content whose
  described failure class lacks a corresponding sensor.
- Add harness-lab episode summary ingestion once `ADR-pool.harness-lab` exists.

## Non-Goals

- No web dashboard.
- No replacement for `gz check`.
- No automatic deletion of rules or validators.
- No telemetry emission into `.gzkit/ledger.jsonl`.
- No operator-facing raw JSON/YAML report as the primary review surface.

## Alternatives Considered

1. **Fold this into `gz check`.** Rejected. `gz check` answers "is the repo
   acceptable right now?" Harness fitness answers "is the harness healthy,
   measured, and worth its weight?"
2. **Use `gz status` for everything.** Rejected. Lifecycle state and harness
   fitness are different operator questions.
3. **Create a dashboard first.** Rejected. gzkit's operator surface is CLI and
   markdown-first; a dashboard would add product surface before the data contract
   is stable.
4. **Retire zero-hit validators automatically.** Rejected. Zero hits may mean a
   sensor is working as a preventive guard. The report nominates candidates for
   human review, not automatic removal.

## Dependencies

- **Consumes:** `ADR-pool.harness-trace-bundles` for trace availability and
  trace-quality reporting.
- **Consumes:** `ADR-pool.harness-lab` for module ablation outcomes.
- **Complements:** `docs/governance/harness-engineering-appraisal.md`, which
  names harness-fitness measurement as an open blindspot.
- **May absorb:** The validator-telemetry idea from the 2026-04-26
  harness-engineering improvement handoff if the operator prefers one ADR
  rather than a separate pool ADR.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The operator chooses the command shape: `gz harness report`, `gz health`, or
   both with one delegating to the other.
2. The telemetry storage root is chosen.
3. The first metric set is accepted: validator count/duration/hits,
   control-surface weight, receipt-citation coverage, and trace availability.
4. Delta semantics for `--since <commit>` are defined.
5. The report's authority boundary is accepted: advisory fitness signal, not a
   gate by itself.

## Notes

Pool ADRs are backlog items -- they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
