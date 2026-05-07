---
id: ADR-0.42.0-gz-preflight-health-orchestration
status: Proposed
kind: feature
semver: 0.42.0
lane: lite
parent:
date: 2026-04-19
promoted_from: ADR-pool.gz-preflight-health-orchestration
---

# ADR-0.42.0-gz-preflight-health-orchestration: Pre-Session Health Orchestration and Governance Design Tooling

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

Eliminate mid-session governance blockers by extending `gz preflight` into a tiered, self-healing
health orchestrator, and establish a GovZero-native design workflow that keeps all design artifacts
inside governance structures instead of parallel product surfaces.

Two capabilities are bundled here because they share a single root cause: agents and operators
encountering preventable friction (stale receipts blocking gates, drift discovered mid-implementation,
design artifacts landing outside GovZero). Both are pre-condition improvements, not feature additions.

---

## Decision

Promote `ADR-pool.gz-preflight-health-orchestration` into active implementation and execute the following tracked scope:

- Check pipeline
- Auto-repair tier
- CLI surface
- Receipt artifact
- Advisory gate

## Comparator Uplift (2026-05-07)

Preflight is the practical front door for an existing repository. It should
summarize not only broken checks, but whether the current workspace has a
witnessed spec/plan/tasks chain, fresh vendor-capability sources, injection-scan
clearance, and known compounding-loop follow-ups.

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

- [ ] OBPI-0.42.0-01: Check pipeline
- [ ] OBPI-0.42.0-02: Auto-repair tier
- [ ] OBPI-0.42.0-03: CLI surface
- [ ] OBPI-0.42.0-04: Receipt artifact
- [ ] OBPI-0.42.0-05: Advisory gate

## Target Scope

Extend the existing `gz preflight` command from a passive reporter into an active pre-session health orchestrator with tiered auto-repair. The scope decomposes into five OBPIs — each bullet below becomes one OBPI slug at promotion time. Rich detail for each OBPI lives in § Detailed Specification below; OBPI-specify workflows draw objectives and acceptance criteria from that section.

- Check pipeline
- Auto-repair tier
- CLI surface
- Receipt artifact
- Advisory gate

## Non-Goals

- Do not replicate `gz validate`, `gz-adr-recon`, or `gz-tidy` logic inside preflight
- Do not add auto-repair for orphan briefs (judgment call, always human-required)
- Do not introduce new governance ledgers or receipt schemas
- Do not add `gz-design` OBPIs (already shipped)

---

## Dependencies

- ADR-0.20.0 OBPI-04 (`gz drift` CLI surface) — preflight consumes drift output
- ADR-0.20.0 OBPI-05 (advisory gate integration) — optional but preferred before promotion

---

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.gz-preflight-health-orchestration` on 2026-04-19; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.42.0 | Pending | | | |
