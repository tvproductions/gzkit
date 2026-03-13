---
id: ADR-0.13.0-obpi-pipeline-runtime-surface
status: Proposed
semver: 0.13.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-13
promoted_from: ADR-pool.obpi-pipeline-runtime-surface
---

# ADR-0.13.0-obpi-pipeline-runtime-surface: OBPI Pipeline Runtime Surface

## Intent

Elevate `gz-obpi-pipeline` from a skill-only workflow into a first-class gzkit
runtime surface so OBPI execution has one canonical command contract for
launch, stage progression, resume, abort, and sync.

## Decision

Promote `ADR-pool.obpi-pipeline-runtime-surface` into active implementation and
execute the following tracked scope:

- Introduce a runtime command contract such as
  `gz obpi pipeline <obpi>`, `--from=verify`, and `--from=ceremony`
- Persist pipeline stage state in a repository-local, machine-readable form
- Expose structured stage outputs for current stage, blockers, required human
  action, and next command or resume point
- Keep Stage 4 human attestation as an explicit authority boundary for Heavy
  and Foundation work
- Make skills, hooks, and future agent control surfaces call into the same
  runtime engine instead of re-implementing stage logic in prose

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
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.13.0-01: Introduce a runtime command contract such as `gz obpi pipeline <obpi>`, `--from=verify`, and `--from=ceremony`
- [ ] OBPI-0.13.0-02: Persist pipeline stage state in a repository-local, machine-readable form
- [ ] OBPI-0.13.0-03: Expose structured stage outputs for current stage, blockers, required human action, and next command or resume point
- [ ] OBPI-0.13.0-04: Keep Stage 4 human attestation as an explicit authority boundary for Heavy and Foundation work
- [ ] OBPI-0.13.0-05: Make skills, hooks, and future agent control surfaces call into the same runtime engine instead of re-implementing stage logic in prose

## Target Scope

- Introduce a runtime command contract such as:
  - `gz obpi pipeline <obpi>`
  - `gz obpi pipeline <obpi> --from=verify`
  - `gz obpi pipeline <obpi> --from=ceremony`
- Persist pipeline stage state in a repository-local, machine-readable form.
- Expose structured stage outputs for:
  - current stage
  - blockers
  - required human action
  - next command or resume point
- Keep Stage 4 human attestation as an explicit authority boundary for Heavy and
  Foundation work.
- Make skills, hooks, and future agent control surfaces call into the same
  runtime engine instead of re-implementing stage logic in prose.

## Non-Goals

- No weakening of Heavy/Foundation human attestation.
- No mandatory external orchestrator or queue service.
- No replacement of ADR/OBPI artifacts as governance authority.

## Dependencies

- **Blocks on**: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
- **Blocked by**: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
- **Related**: ADR-pool.obpi-pipeline-enforcement-parity, ADR-pool.pause-resume-handoff-runtime

## Promotion Criteria

1. A stable CLI contract for launch/resume/abort semantics is approved.
2. Repository-local stage persistence and cleanup rules are defined.
3. Human-gate behavior is specified for Heavy/Foundation stages.
4. Skill text and hook adapters are reduced to thin wrappers over the runtime
   surface.

## Inspired By

[12-factor-agents](https://github.com/humanlayer/12-factor-agents), especially:

- Factor 6: Launch/Pause/Resume with simple APIs
- Factor 8: Own your control flow

## Notes

- gzkit already has the stage model in `.gzkit/skills/gz-obpi-pipeline/SKILL.md`;
  this ADR turns that model into a command contract instead of an instruction
  contract.
- This is complementary to AirlineOps-style hook enforcement parity:
  enforcement decides *when* the pipeline must run; this ADR defines *what*
  runtime actually executes.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.obpi-pipeline-runtime-surface` on 2026-03-13;
executable scope was carried forward from the pool ADR instead of reseeded as
placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.13.0 | Pending | | | |
