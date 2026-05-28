---
id: ADR-pool.adr-plan-pipeline-with-redteam
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.adr-plan-pipeline-with-redteam: ADR Plan Pipeline with Redteam Verification (gz-adr-plan-pipeline)

## Status

Superseded

## Intent

gzkit has four artifact-lifecycle pipelines, three of which require redteam
verification as their terminal stage:

| Pipeline | Skill | Redteam terminal |
|---|---|---|
| Design | `gz-adr-plan-pipeline` (THIS POOL ADR) | ✓ |
| Implementation | `gz-obpi-pipeline` (exists; retrofit tracked in `ADR-pool.obpi-pipeline-redteam-retrofit`) | ✓ |
| Validation | `gz-adr-validation-pipeline` (canonical ADR-0.0.50) | ✓ |

The Design phase currently has no orchestrator skill — `gz-design`, `gz-plan`,
`gz-obpi-specify`, `gz-justify`, `gz-plan-audit`, and `gz-adr-evaluate` exist
as discrete skills with no sequencing contract. Authoring an ADR end-to-end
requires invoking these skills in the right order without mechanical
enforcement of stage-completion.

This ADR codifies a multi-skill orchestrator at the design phase, mirroring
the contract established by `gz-obpi-pipeline` (implementation phase) and
`gz-adr-validation-pipeline` (validation phase, ADR-0.0.50).

## Decision

Create `gz-adr-plan-pipeline` skill conforming to the pipeline-orchestrator
contract:

- **Stages**: gz-design → gz-plan → gz-obpi-specify → gz-justify → gz-plan-audit → gz-adr-evaluate → **redteam-verify** (terminal)
- **Driver persona**: `pipeline-orchestrator`
- **Runtime engine**: `src/gzkit/plan_pipeline_runtime.py`
- **Redteam**: Codex inline via `codex:codex-rescue` Agent subagent (cross-vendor
  adversarial check); fallback to opposite-Claude-model Agent for Codex/Copilot harnesses
- **Per-stage receipts** + unified `plan_pipeline_completed` ledger event
- **`--from=<stage>` resume** for partial runs
- **Iron Law**: Plan pipeline is not complete until redteam-verify receipt is
  PASS or operator-bypassed with logged reason
- **`gz status --next-action`** extension recommends this orchestrator when an
  ADR is in `Proposed` or `Accepted` state without complete OBPI scaffolding
- **Validator**: `gz validate --plan-pipeline-receipts` fail-closed in `gz check`

## Target Scope

Create the design-phase orchestrator skill `gz-adr-plan-pipeline` conforming to ADR-0.0.50's multi-skill orchestrator contract and redteam-terminal doctrine. The scope decomposes into five OBPIs — each bullet below becomes one OBPI slug at promotion time. Detailed specification lives in § Decision above; OBPI-specify workflows draw objectives and acceptance criteria from those stage definitions.

- Plan pipeline orchestrator skill + runtime engine
- Stage-1-to-N sequencing of `gz-design` → `gz-plan` → `gz-obpi-specify` → `gz-justify` → `gz-plan-audit` → `gz-adr-evaluate`
- Redteam terminal stage (Codex inline primary; opposite-Claude-model fallback)
- Plan pipeline validators (fail-closed in `gz check`) + bypass flag
- `gz status --next-action` integration for design-phase recommendation

## Alternatives Considered

- **No design orchestrator** — keep discrete skill invocation. Rejected: same
  failure mode as pre-`gz-obpi-pipeline` implementation phase — operators skip
  stages, especially `gz-justify` and `gz-adr-evaluate`. Mechanical enforcement
  is the only durable fix.
- **Single mega-orchestrator across all three phases** — rejected per session
  decision (2026-05-18): three separate orchestrations, each with its own
  scope and operator moments. Bundling violates kind-taxonomy and creates a
  god-object orchestrator.
- **Redteam as optional opt-in stage** — rejected: redteam-terminal is
  doctrine per ADR-0.0.50, not advisory. Optional redteam degrades to
  no-redteam in practice.

## Notes

**Session context (2026-05-18):** This pool ADR preserves framing established
during the design dialogue that authored ADR-0.0.50 (validation pipeline).
The design pipeline orchestrator is the second of three pipeline ADRs in that
cohort — validation booked canonical, design and implementation retrofit
booked as pool stubs to be elaborated in follow-up `gz-design` sessions
before OBPI scoping.

Naming: `gz-adr-` prefix reflects ADR-scope (one orchestrator run per ADR).
`gz-obpi-pipeline` retains its prefix because its scope is per-OBPI, not
per-ADR. Renaming `gz-obpi-pipeline` for consistency is a separate question
deferred to `ADR-pool.obpi-pipeline-redteam-retrofit`.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
