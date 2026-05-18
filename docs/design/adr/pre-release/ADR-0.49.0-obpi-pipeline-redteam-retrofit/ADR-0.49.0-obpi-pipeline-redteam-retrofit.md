---
id: ADR-0.49.0-obpi-pipeline-redteam-retrofit
status: Proposed
kind: feature
semver: 0.49.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-18
promoted_from: ADR-pool.obpi-pipeline-redteam-retrofit
---

# ADR-0.49.0-obpi-pipeline-redteam-retrofit: OBPI Pipeline Redteam Verification Retrofit (gz-obpi-pipeline)

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

`gz-obpi-pipeline` is gzkit's existing implementation-phase orchestrator and
the reference exemplar for the multi-skill orchestrator pattern. ADR-0.0.50
(validation pipeline) codifies the redteam-terminal-stage doctrine as binding
for all three artifact-lifecycle pipelines:

| Pipeline | Skill | Redteam terminal |
|---|---|---|
| Design | `gz-adr-plan-pipeline` (`ADR-pool.adr-plan-pipeline-with-redteam`) | ✓ |
| Implementation | `gz-obpi-pipeline` (THIS POOL ADR — retrofit) | ✓ |
| Validation | `gz-adr-validation-pipeline` (ADR-0.0.50) | ✓ |

`gz-obpi-pipeline` currently has five stages (verify → ceremony → guarded
sync → completion) with persona dispatch (`implementer`, `spec-reviewer`,
`quality-reviewer`, `narrator`) but no redteam terminal stage. This ADR
retrofits the redteam stage to bring the implementation orchestrator into
conformance with the cohort doctrine.

## Decision

Retrofit `gz-obpi-pipeline` with a redteam-verify terminal stage following
the contract established by ADR-0.0.50:

- **New terminal stage**: redteam-verify (after Stage 5 completion, before
  pipeline marks complete)
- **Redteam mechanism**: Codex inline via `codex:codex-rescue` Agent subagent
  (cross-vendor adversarial check); fallback to opposite-Claude-model Agent
  for Codex/Copilot harnesses
- **Iron Law update**: "OBPI pipeline is not complete until redteam-verify
  receipt is PASS or operator-bypassed with logged reason" (replaces "Stage 5
  finishes")
- **Receipt**: `.gzkit/receipts/redteam-obpi-pipeline-<OBPI-ID>-<iso>.json`
- **Validator**: `gz validate --redteam-verification-receipts` extension
  covers the OBPI-pipeline scope (validator authored under ADR-0.0.50;
  this retrofit extends its coverage)
- **`--from=redteam`** resume point for partial runs

**Naming question (deferred):** ADR-0.0.50 established `gz-adr-*` prefix for
ADR-scope orchestrators. `gz-obpi-pipeline` operates per-OBPI not per-ADR, so
its prefix is internally consistent (scope-reflective). The question of
whether to rename to `gz-adr-obpi-pipeline` for cohort visual consistency is
explicitly deferred to this retrofit ADR's design dialogue. Default: no rename
(scope-reflective prefix wins; cohort recognition lives in the manifest, not
the skill name).

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
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 7
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.49.0-01: Redteam terminal stage addition to `gz-obpi-pipeline` runtime engine
- [ ] OBPI-0.49.0-02: Redteam dispatch wiring (Codex inline primary; opposite-Claude-model fallback) reusing `redteam-verifier` persona from ADR-0.0.50
- [ ] OBPI-0.49.0-03: `--from=redteam` resume point + Iron Law update
- [ ] OBPI-0.49.0-04: Validator extension covering OBPI-pipeline scope under `gz validate --redteam-verification-receipts`

## Target Scope

Retrofit existing `gz-obpi-pipeline` with redteam-verify terminal stage per ADR-0.0.50's redteam-terminal doctrine. Implementation-phase orchestrator already exists (5 stages, persona dispatch, runtime engine in `src/gzkit/pipeline_runtime.py`); this ADR adds the terminal redteam stage and updates the Iron Law. The scope decomposes into four OBPIs — each bullet below becomes one OBPI slug at promotion time. Detailed specification lives in § Decision above.

- Redteam terminal stage addition to `gz-obpi-pipeline` runtime engine
- Redteam dispatch wiring (Codex inline primary; opposite-Claude-model fallback) reusing `redteam-verifier` persona from ADR-0.0.50
- `--from=redteam` resume point + Iron Law update
- Validator extension covering OBPI-pipeline scope under `gz validate --redteam-verification-receipts`

## Notes

**Session context (2026-05-18):** This pool ADR preserves framing established
during the design dialogue that authored ADR-0.0.50 (validation pipeline).
The implementation-retrofit ADR is the third of three pipeline ADRs in that
cohort — validation booked canonical, design and implementation retrofit
booked as pool stubs to be elaborated in follow-up `gz-design` sessions
before OBPI scoping.

**Out of scope (separate future ADR):** A fourth pipeline — the
"maintenance milestone" pipeline that fires after validation completes,
ships the architecture-review skill (Matt Pocock improve-codebase-architecture
inspiration), and uses `/goal` as its first-class convergence primitive — is
explicitly NOT in this cohort. That pipeline does NOT require redteam (its
output is findings routing, not state transitions). To be booked as a
separate ADR when prioritized.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.obpi-pipeline-redteam-retrofit` on 2026-05-18; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.49.0 | Pending | | | |
