---
id: ADR-pool.harness-fitness-report
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: "arXiv:2603.28052v1 Meta-Harness; arXiv:2603.25723 Natural-Language Agent Harnesses"
complements:
  - ADR-pool.harness-lab
  - ADR-pool.harness-trace-bundles
  - ADR-pool.workflow-specification
promoted_to: ADR-0.0.60-harness-fitness-report
---

# ADR-pool.harness-fitness-report: Harness Fitness Report
> Promoted to `ADR-0.0.60-harness-fitness-report` on 2026-05-25. This pool file is retained as historical intake context.


## Status

Superseded

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

## Proposed OBPI Decomposition

Inaugural metric for promotion: **prompt→Stage-5 latency per OBPI lane** (the
factory loop time). Floor policy: advisory + auto-file GHI on persistent
regression; never gate authority. Sequencing: ride coarse on today's wired
`pipeline_launched` / `obpi_receipt_emitted` events; upgrade to per-stage
breakdown when `pipeline_stage_entered` lands via `ADR-pool.tdd-receipt-stream`.
Architecture: pluggable surface registry — `lane-latency` is the first entry;
future surfaces (validators, control-surfaces, receipt-citation, stage-latency)
add registry entries without restructuring this ADR.

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | lane-latency-models | Pydantic models (`LaneLatencyRecord`, `LaneLatencyAggregate`, `LaneLatencyReport`, `HarnessRegressionInsight`, `HarnessLaneLatencyConfig`) + JSON schema export to `src/gzkit/schemas/harness_lane_latency.json` + schema-drift CI gate. | heavy |
| 02 | lane-latency-scanner | Ledger scanner pairing `pipeline_launched` → `obpi_receipt_emitted` (with `obpi_completion ∈ {"completed","attested_completed"}`); orphan handling; lane drift detection; rolling-window aggregation; cache write to `.gzkit/telemetry/lane-latency.json`. | heavy |
| 03 | lane-latency-renderer | Rich-table renderer matching `gz status` house style; `--json` emits `LaneLatencyReport.model_dump_json()` to stdout, diagnostics to stderr; `--lane`, `--since <commit>`, `--list-surfaces`, `--no-auto-ghi` flags; soft-non-zero exit 3 on breach. | heavy |
| 04 | harness-regression-helper | Shared `file_or_comment_ghi` helper in `src/gzkit/harness/regression.py` routing through `/ghi-author` (Behavior Rule 13); deterministic label policy (`harness-regression` + `lane:<lane>` + `surface:<surface>`); always emits `HarnessRegressionInsight` to `.gzkit/insights/agent-insights.jsonl` regardless of file-vs-comment outcome. | heavy |
| 05 | harness-telemetry-validator | New `gz validate --harness-telemetry` scope: schema validity, ledger-event resolution for both event IDs per record, high-water-mark monotonicity, in-flight count sanity. Exit 3 fail-closed on drift; wired into default `gz check`. | heavy |
| 06 | lane-latency-docs-and-attestation | Operator runbook section; `gz harness report` manpage with examples; Gate 4 BDD scenarios; threshold-config doc at `docs/governance/harness/lane-latency-config.md`; Gate 5 attestation evidence bundle. | heavy |

OBPIs 01→02→03 form the implementation spine; 04 plugs into 03; 05 validates
01+02+03 output; 06 closes documentation/attestation gates. Each OBPI carries
its own REQs and tests; no implementation OBPI ships without paired test
coverage per `.gzkit/rules/tests.md`.

## Non-Goals

- No web dashboard.
- No replacement for `gz check`.
- No automatic deletion of rules or validators.
- No telemetry emission into `.gzkit/ledger.jsonl`.
- No operator-facing raw JSON/YAML report as the primary review surface.
- No per-stage latency breakdown (deferred to future ADR after `pipeline_stage_entered` lands).
- No fail-closed gate authority for floor breaches (advisory-only per anti-vibing mantra).

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
