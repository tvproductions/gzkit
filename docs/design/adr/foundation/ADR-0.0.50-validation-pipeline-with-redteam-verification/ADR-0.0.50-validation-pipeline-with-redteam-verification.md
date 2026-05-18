---
id: ADR-0.0.50-validation-pipeline-with-redteam-verification
status: Draft
kind: foundation
semver: 0.0.50
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-18
---

# ADR-0.0.50-validation-pipeline-with-redteam-verification: ADR Validation Pipeline with Redteam Verification (gz-adr-validation-pipeline)

## Persona

`pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md`. Stage discipline, ceremony completion, and evidence anchoring are not rules to follow — they are who you are when running this pipeline. The validation pipeline orchestrator dispatches the same subagent personas (`spec-reviewer`, `quality-reviewer`, `narrator`) as `gz-obpi-pipeline`, plus a new `redteam-verifier` persona for the terminal stage.

## Why foundation tier?

**Invariance test:** Without this ADR, gzkit would still be the project, but the artifact lifecycle would be missing its validation-phase orchestrator. Every Validated ADR landing without an enforced closeout → audit → redteam sequence corrupts the audit trail. The validation pipeline is the structural gate between Phase-1 (Completed) and Phase-2 (Validated) — its absence is a port-level absence, not a feature gap.

**Port-vs-adapter framing:** This ADR is a **port** — it specifies the contract every validation orchestrator implementation must honor (stage sequence, persona dispatch, receipt shape, redteam terminal, fail-closed gating). `gz-adr-validation-pipeline` is the canonical adapter. The redteam-terminal-stage doctrine declared here is also a port — binding for the design pipeline (`gz-adr-plan-pipeline`, `ADR-pool.adr-plan-pipeline-with-redteam`) and the implementation pipeline retrofit (`gz-obpi-pipeline`, `ADR-pool.obpi-pipeline-redteam-retrofit`).

## Intent

gzkit has four artifact-lifecycle pipelines plus one orthogonal maintenance pipeline:

| # | Pipeline | Orchestrator skill | Redteam terminal | Status |
|---|---|---|---|---|
| 1 | Design | `gz-adr-plan-pipeline` | ✓ Required | Pool — `ADR-pool.adr-plan-pipeline-with-redteam` |
| 2 | Implementation | `gz-obpi-pipeline` | ✓ Required (retrofit) | Exists; retrofit pool — `ADR-pool.obpi-pipeline-redteam-retrofit` |
| 3 | **Validation** | **`gz-adr-validation-pipeline` (THIS ADR)** | **✓ Required** | **Missing — this ADR delivers it** |
| 4 | Maintenance milestone (post-validation, architecture review + sweep) | `gz-milestone-maintenance` (future ADR) | ✗ Not needed (findings routing, not state transitions) | Missing — separate future ADR |
| 5 | Chores (ad hoc) | `gz-chore-runner` | ✗ Not needed | Exists |

The validation phase currently has no orchestrator. `gz-adr-closeout-ceremony` (wields `gz closeout`) and `gz-adr-audit` (wields `gz audit`) exist as discrete skills with no enforced sequencing. Operators chain them manually, with no mechanical guard against running audit before closeout, no unified validation-pipeline receipt, no terminal independent-vendor verification.

This ADR delivers `gz-adr-validation-pipeline` — the third of three multi-skill orchestrators in the artifact lifecycle (mirroring `gz-obpi-pipeline`'s contract) — and codifies the redteam-terminal-stage doctrine binding for all three.

## Decision

### Stage 1 — Validation pipeline orchestrator

Create `gz-adr-validation-pipeline` skill conforming to the multi-skill orchestrator contract established by `gz-obpi-pipeline`:

- **Stages**: closeout → audit → **redteam-verify** (terminal)
- **Driver persona**: `pipeline-orchestrator`
- **Runtime engine**: `src/gzkit/validation_pipeline_runtime.py`
- **Per-stage receipts** at `.gzkit/receipts/validation-pipeline-<ADR-ID>-<iso>.json`
- **Unified ledger event**: `validation_pipeline_completed` on terminal stage success
- **`--from=audit` and `--from=redteam`** resume points
- **Iron Law**: "Validation pipeline is not complete until redteam-verify receipt is PASS or operator-bypassed with logged reason"
- Stage 1 (closeout) and Stage 2 (audit) each preserve their existing operator moments — closeout has Gate-5 attestation, audit has verbal ack on validated receipt. No bundling of attestations.

### Stage 2 — Redteam terminal stage (doctrine binding for pipelines 1, 2, 3)

Every artifact-lifecycle pipeline (design, implementation, validation) MUST have a redteam-verify terminal stage. The redteam:

- **Primary mechanism (Claude Code harness)**: Codex inline via `codex:codex-rescue` Agent subagent — cross-vendor adversarial check provides genuinely different reasoning. The harness already integrates Codex via the `codex:codex-cli-runtime` contract.
- **Fallback (Codex / Copilot harnesses)**: opposite-Claude-model Agent subagent (Sonnet-vs-Opus split). Mirror skill bodies branch on harness detection — ADR-0.0.31 distribution invariant satisfied by single canonical body with conditional execution.
- **Persona**: `redteam-verifier` (NEW) — traits: adversarial, evidence-bound, refuses-narrative-recall, anti-rationalization.
- **Inputs**: prior-stage receipts + ledger evidence for the pipeline run (closeout receipt, audit receipt, all subagent dispatch records).
- **Output**: structured receipt at `.gzkit/receipts/redteam-<pipeline>-<id>-<iso>.json` with fields:
  - `pass: bool`
  - `findings: list[StructuredFinding]` (each: severity, surface, evidence, recommendation)
  - `model_used: str` + `harness: str`
  - `evidence_consumed: list[path]`
- **Convergence**: `/goal`-bounded on Claude Code (condition: "redteam returns PASS or every finding is named with severity and recommendation; stop after 4 turns"). Bounded-iteration fallback on Codex/Copilot (max 4 iterations, exit on PASS or finding-list-complete).

### Stage 3 — Fail-closed gating

`gz check` blocks merge when:
- An ADR is `Validated` but lacks a `validation_pipeline_completed` ledger event newer than the `validated` receipt (`gz validate --validation-pipeline-receipts`).
- A pipeline run's redteam stage produced a non-PASS receipt and was not bypassed (`gz validate --redteam-verification-receipts`).

Bypass paths (each writes an auditable ledger event):
- `gz check --accept-redteam-shortfall <PIPELINE-RUN-ID> --reason <REASON>` — operator-attested redteam shortfall acceptance.
- No bypass for missing pipeline-completion receipts. If the pipeline didn't run, run it.

### Stage 4 — `gz status --next-action` extension

`gz status` extended with `--next-action` flag that surfaces the next phase-orchestrator skill recommended for the current artifact's lifecycle state:

| Current state | `--next-action` recommends |
|---|---|
| ADR `Proposed` or `Accepted` without complete OBPI scaffolding | `gz-adr-plan-pipeline` (when available) |
| OBPI brief approved, no implementation receipt | `gz-obpi-pipeline` |
| ADR `Completed` (all OBPIs done) without validation pipeline completion | `gz-adr-validation-pipeline` |

Mechanical recommendation only; not enforcement. Enforcement lives in fail-closed `gz check` validators.

### Stage 5 — Claude Code as primary vendor harness

gzkit designs optimally for Claude Code as the primary vendor harness. Codex and Copilot harnesses receive a fallback execution path within the same canonical skill body. This ADR is the first to codify this posture explicitly:

- **First-class primitives for Claude Code**: `/goal` (https://code.claude.com/docs/en/goal), inline Codex calls via `codex:codex-rescue`, the existing `Agent` subagent_type contract.
- **Fallback for Codex / Copilot**: bounded-iteration semantics (no `/goal`), opposite-Claude-model Agent for redteam (no cross-vendor inline call), per-harness branching declared in the skill body's `## Harness Detection` section.
- **ADR-0.0.31 distribution invariant satisfied**: single canonical SKILL.md per skill, executes one branch based on detected harness. No mirror divergence.

## Consequences

### Positive

- Validation phase gains mechanical enforcement equivalent to implementation phase. The pipeline runs to completion or fails closed — no half-validated ADRs.
- Redteam-terminal doctrine establishes a structural anti-vibing defense at every artifact-lifecycle boundary. The model doing the work is not the model verifying it; the vendor doing the work is not the vendor verifying it (on Claude Code).
- `gz check` becomes a binding gate on validation pipeline completion — operator cannot land new work while a previous ADR's validation pipeline is incomplete.
- `gz status --next-action` makes phase-orchestrator routing operator-visible without requiring a meta-router skill.
- Claude-Code-primary posture lets gzkit exploit the harness's strongest primitives (`/goal`, inline Codex) without dragging Codex/Copilot mirror execution down to a lowest-common-denominator surface.

### Negative

- Codex dependency for primary-path redteam. If Codex CLI is unavailable in the operator's environment, falls back to opposite-Claude-model — weaker adversarial signal but still cross-model.
- Skill bodies branch on harness detection, increasing per-skill complexity. Mitigated by encapsulating the branching in shared utility functions, not duplicated in every skill.
- Redteam terminal adds one more stage to each pipeline run — additional latency and token cost. Mitigated by bounded iteration (`/goal` or native cap) and the cost is exactly the cost of structural verification (the product, not overhead).
- The `redteam-verifier` persona is new and untested. First instances will calibrate the persona's anti-traits and bias-detection patterns; expect refinement under follow-on GHIs.

## Decomposition Scorecard

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

- [ ] OBPI-0.0.50-01: `gz-adr-validation-pipeline` skill + `src/gzkit/validation_pipeline_runtime.py` runtime engine; stages closeout → audit → redteam-verify; per-stage receipts; `--from=<stage>` resume
- [ ] OBPI-0.0.50-02: `redteam-verifier` persona definition + dispatch contract; Codex-primary via `codex:codex-rescue` Agent subagent, opposite-Claude-model fallback for Codex/Copilot harnesses
- [ ] OBPI-0.0.50-03: Redteam receipt schema + structured-finding model; `/goal`-bounded convergence on Claude Code with bounded-iteration fallback (max 4 iterations) on other harnesses
- [ ] OBPI-0.0.50-04: `gz validate --validation-pipeline-receipts` + `gz validate --redteam-verification-receipts` validators (fail-closed in `gz check`); `--accept-redteam-shortfall` bypass with ledger-recorded operator attestation
- [ ] OBPI-0.0.50-05: `gz status --next-action` extension; Claude-Code-primary doctrine section in this ADR cited by `ADR-pool.adr-plan-pipeline-with-redteam` and `ADR-pool.obpi-pipeline-redteam-retrofit`

## Q&A Transcript

Design dialogue conducted 2026-05-18 via `/gz-design`. Key decisions:

- **Three separate orchestrator ADRs** (not one meta-ADR). Validation booked canonical here; design and implementation retrofit booked as pool stubs (`ADR-pool.adr-plan-pipeline-with-redteam`, `ADR-pool.obpi-pipeline-redteam-retrofit`) preserving session framing for future elaboration.
- **Naming**: `gz-adr-*` prefix for ADR-scope orchestrators (validation, plan). `gz-obpi-pipeline` retains its prefix because its scope is per-OBPI (rename question explicitly deferred to the retrofit ADR).
- **Redteam mechanism**: Codex inline via `codex:codex-rescue` (cross-vendor adversarial check) is primary; opposite-Claude-model fallback for harnesses that can't call Codex inline. Stronger signal than two-Claude-model split.
- **Vendor posture**: Claude Code is primary; design optimally for `/goal` and inline Codex; Codex/Copilot mirrors get fallback execution paths within single canonical skill body (ADR-0.0.31 invariant preserved).
- **Routing**: Active routing lives mechanically below the skill layer — ledger events + fail-closed validators + `gz status --next-action` hint. No god-object meta-router. `gz-skill-router` stays scoped to task→skill pull routing.

Origin: design conversation traces from operator framing of "three separate orchestrations: design, implementation (exists), validation" → addition of redteam-terminal-stage doctrine → Claude-Code-primary vendor posture → cohort booking.

## Evidence

- [ ] Tests: `tests/test_validation_pipeline_runtime.py`, `tests/test_redteam_verifier_persona.py`, `tests/test_validation_pipeline_validators.py`, `tests/test_gz_status_next_action.py`
- [ ] Docs: `docs/user/runbook.md` § Validation pipeline, `docs/governance/governance_runbook.md` § Redteam terminal doctrine, `docs/user/manpages/gz-adr-validation-pipeline.md`

## Alternatives Considered

- **Bundle three orchestrator concerns into one foundation ADR** — rejected per session decision (2026-05-18). Three separate ADRs respect kind-taxonomy, avoid coupled-surface-coherence violations, and let each pipeline's design dialogue be focused. Cost: redteam doctrine has to be declared once and cited twice; benefit: each ADR has a coherent scope and operator moment.
- **No redteam terminal stage; rely on existing in-stage verification (spec-reviewer, quality-reviewer)** — rejected. In-stage reviewers share the same model and harness as the work being reviewed; structural cross-model and cross-vendor verification is the only mechanism that catches model-class blind spots. The product is anti-vibing; in-class verification is not anti-vibing.
- **Redteam as separate skill operators run after the pipeline** — rejected. Optional redteam degrades to no-redteam in practice. Terminal-stage integration with fail-closed gating is the only durable mechanism.
- **Bundle milestone-sweep into validation pipeline** (earlier session proposal) — rejected per session decision. Sweep is a maintenance-phase concern triggered by validation completion, not part of the validation pipeline itself. Becomes its own future pipeline ADR (`gz-milestone-maintenance`, fourth ADR in artifact-lifecycle cohort) that houses the architecture-review skill (Matt Pocock improve-codebase-architecture inspiration) and uses `/goal` as its first-class convergence primitive.
- **Codex/Copilot byte-equivalent skill bodies (no harness branching)** — rejected per Claude-Code-primary vendor posture decision. Designing for the lowest-common-denominator surface leaves the primary harness's strongest primitives unused; the cost in tokens and engineering effort is real. Single canonical skill body with internal harness branching satisfies ADR-0.0.31 distribution invariant.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.50 | Pending | | | |
