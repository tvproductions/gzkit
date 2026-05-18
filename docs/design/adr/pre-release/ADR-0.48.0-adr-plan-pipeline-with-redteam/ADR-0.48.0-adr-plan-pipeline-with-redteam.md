---
id: ADR-0.48.0-adr-plan-pipeline-with-redteam
status: Proposed
kind: feature
semver: 0.48.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-18
promoted_from: ADR-pool.adr-plan-pipeline-with-redteam
---

# ADR-0.48.0-adr-plan-pipeline-with-redteam: ADR Plan Pipeline with Redteam Verification (gz-adr-plan-pipeline)

## Persona

`pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md`. Stage discipline, ceremony completion, and evidence anchoring are not rules to follow — they are who you are when running this pipeline. The plan pipeline orchestrator dispatches design-phase skills sequentially through their natural authoring flow, then converges on a redteam-verify terminal stage that consumes Codex (cross-vendor) verification of the produced ADR design.

## Intent

**Before this ADR:** The design phase has no orchestrator skill. `gz-design`, `gz-plan`, `gz-obpi-specify`, `gz-justify`, `gz-plan-audit`, and `gz-adr-evaluate` exist as discrete skills with no sequencing contract. Authoring an ADR end-to-end requires invoking these skills in the right order without mechanical enforcement of stage completion. Operators routinely skip `gz-justify` (when confidence is presumed high) and `gz-adr-evaluate` (when fatigue sets in after the design conversation), producing ADRs with weak intent and untested rationale.

**After this ADR:** `gz-adr-plan-pipeline` orchestrates the design-phase skills end-to-end, fail-closes on skipped stages, emits per-stage receipts that `gz validate --plan-pipeline-receipts` consumes as evidence the design phase ran to completion, and terminates in a redteam-verify stage that catches blind spots before the ADR ships to `Proposed`.

This ADR completes the three-ADR redteam cohort initiated by ADR-0.0.50 (validation pipeline canonical) and continued by ADR-0.49.0 (implementation pipeline retrofit):

| Pipeline | Skill | Redteam terminal | ADR |
|---|---|---|---|
| **Design** | **`gz-adr-plan-pipeline` (THIS ADR — feature adapter into 0.0.50's port)** | **✓** | **ADR-0.48.0** |
| Implementation | `gz-obpi-pipeline` (retrofit) | ✓ | ADR-0.49.0 |
| Validation | `gz-adr-validation-pipeline` (port + canonical adapter) | ✓ | ADR-0.0.50 |

Exemplar / precedent: `gz-obpi-pipeline` is the reference orchestrator shape (runtime engine, persona dispatch table, Iron Law, per-stage receipts, `--from=<stage>` resume) that this skill MUST conform to. The new redteam terminal stage is specified by ADR-0.0.50 § Stage 2 and reused verbatim here (same `redteam-verifier` persona, same Codex-primary mechanism, same receipt schema, same `/goal`-bounded convergence on Claude Code with bounded-iteration fallback for other harnesses).

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

## Consequences

### Positive

- Design phase gains mechanical enforcement equivalent to the implementation phase. Operators cannot land an ADR through `gz-design` shortcuts that skip `gz-justify` or `gz-adr-evaluate` — the pipeline runs to its redteam terminal or fails closed.
- Anti-pattern guard: ADRs reaching `Proposed` without redteam verification carry an unmistakable signal — a missing `plan_pipeline_completed` ledger event. `gz validate --plan-pipeline-receipts` fail-closes `gz check`, making the anti-pattern mechanically untenable.
- Cohort coherence: the third pipeline in the redteam cohort conforms to ADR-0.0.50's contract verbatim. Three orchestrators, one shape, one redteam doctrine — reduces cognitive load on operators switching between phases.

### Negative

- Adds friction to ADR authoring. Quick "scaffold an ADR for X" sessions now run a longer pipeline; operators who previously skipped stages will feel the time cost. Mitigated by `--from=<stage>` resume (re-run only failed stages) and the redteam stage's bounded convergence (max 4 iterations on `/goal`, equivalent on fallback).
- Codex dependency for primary-path redteam. If Codex CLI is unavailable, falls back to opposite-Claude-model — weaker cross-vendor signal. Same trade as ADR-0.0.50; mitigation is identical.
- Skill-layer code grows. Yet another orchestrator to maintain. Mitigated by reusing the runtime-engine contract from `src/gzkit/pipeline_runtime.py` — new runtime is a structural clone, not a green-field implementation.

### Anti-patterns this ADR forbids

- Running `gz-design` and `gz-adr-create` outside the pipeline and pretending the design phase is complete. (Mechanical guard: ledger event absence.)
- Treating `gz-justify` as optional when the operator "knows" the answer. (Mechanical guard: stage-skip detection in runtime engine.)
- Skipping the redteam terminal because "the work is clearly correct." (Mechanical guard: fail-closed `gz check`.)

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
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.48.0-01: Plan pipeline orchestrator skill + runtime engine
- [ ] OBPI-0.48.0-02: Stage-1-to-N sequencing of `gz-design` → `gz-plan` → `gz-obpi-specify` → `gz-justify` → `gz-plan-audit` → `gz-adr-evaluate`
- [ ] OBPI-0.48.0-03: Redteam terminal stage (Codex inline primary; opposite-Claude-model fallback)
- [ ] OBPI-0.48.0-04: Plan pipeline validators (fail-closed in `gz check`) + bypass flag
- [ ] OBPI-0.48.0-05: `gz status --next-action` integration for design-phase recommendation

## Target Scope

Create the design-phase orchestrator skill `gz-adr-plan-pipeline` conforming to ADR-0.0.50's multi-skill orchestrator contract and redteam-terminal doctrine. The scope decomposes into five OBPIs — each bullet below becomes one OBPI slug at promotion time. Detailed specification lives in § Decision above; OBPI-specify workflows draw objectives and acceptance criteria from those stage definitions.

- Plan pipeline orchestrator skill + runtime engine
- Stage-1-to-N sequencing of `gz-design` → `gz-plan` → `gz-obpi-specify` → `gz-justify` → `gz-plan-audit` → `gz-adr-evaluate`
- Redteam terminal stage (Codex inline primary; opposite-Claude-model fallback)
- Plan pipeline validators (fail-closed in `gz check`) + bypass flag
- `gz status --next-action` integration for design-phase recommendation

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

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.adr-plan-pipeline-with-redteam` on 2026-05-18; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- **No design orchestrator — keep discrete skill invocation.** Rejected: same failure mode as pre-`gz-obpi-pipeline` implementation phase — operators skip stages, especially `gz-justify` and `gz-adr-evaluate`. Mechanical enforcement is the only durable fix.
- **Single mega-orchestrator across design / implementation / validation.** Rejected per session decision (2026-05-18): three separate orchestrations, each with its own scope and operator moments. Bundling violates kind-taxonomy and creates a god-object orchestrator that cannot be reasoned about.
- **Redteam as optional opt-in stage.** Rejected: redteam-terminal is doctrine per ADR-0.0.50, not advisory. Optional redteam degrades to no-redteam in practice (the canonical failure mode of every "optional ceremony" rule in gzkit's history).
- **Codex/Copilot byte-equivalent skill body (no harness branching).** Rejected per Claude-Code-primary vendor posture (ADR-0.0.50 § Stage 5). Designing for the lowest-common-denominator surface leaves Claude Code's strongest primitives (`/goal`, inline Codex) unused. Single canonical skill body with internal harness branching satisfies ADR-0.0.31 distribution invariant.
- **Different orchestrator contract from `gz-obpi-pipeline`.** Rejected: the operator's explicit cohort-coherence preference (2026-05-18 session) names `gz-obpi-pipeline` as the reference exemplar. Three orchestrators conforming to one shape is the design goal; divergence is the anti-goal.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.48.0 | Pending | | | |
