---
id: ADR-0.43.0-ghi-triage-closeout
status: Proposed
semver: 0.43.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-19
promoted_from: ADR-pool.ghi-triage-closeout
---

# ADR-0.43.0-ghi-triage-closeout: GitHub Issue Triage and Closeout Integration

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

Promoted from `ADR-pool.ghi-triage-closeout` for active implementation.

## Decision

Add a `gz ghi` subcommand group that wraps `gh` CLI calls and correlates issues against ADR identifiers for triage and closeout workflows. Per the three-layer tool/skill/runbook alignment rule (`tool-skill-runbook-alignment.md`), the CLI verbs ship alongside operator-facing skills (`gz-ghi-fix`, `gz-ghi-triage`) and runbook entries so every invariant (tool-wielded-by-skill, skill-matches-runbook-moment, output-form-honored) is satisfied on landing. Scope is merged from the original tool-layer proposal (2026-03-29) and the skill-layer/runbook complements surfaced during the 2026-04-19 `/insights` session.

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

- [ ] OBPI-0.43.0-01: gz ghi cli verbs
- [ ] OBPI-0.43.0-02: gz ghi fix skill
- [ ] OBPI-0.43.0-03: gz ghi triage skill
- [ ] OBPI-0.43.0-04: runbook and manpage docs
- [ ] OBPI-0.43.0-05: gz patch release integration

## Target Scope

Scope decomposes into five OBPIs. Each bullet below becomes one OBPI slug at promotion; narrative detail for each lives in § Detailed Specification.

- gz ghi cli verbs
- gz ghi fix skill
- gz ghi triage skill
- runbook and manpage docs
- gz patch release integration

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.ghi-triage-closeout` on 2026-04-19; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.43.0 | Pending | | | |
