---
id: ADR-0.4.0-skill-capability-mirroring
status: Proposed
semver: 0.4.0
lane: heavy
parent: ADR-0.3.0
date: 2026-02-17
promoted_from: ADR-pool.skill-capability-mirroring
---

# ADR-0.4.0: Skill Capability Mirroring

## Intent

Promote skill-capability mirroring from pool to an active ADR so skill coverage tracks the operational command surface as first-class work.

## Decision

Adopt a centralized canonical skills source in `.gzkit/skills`, mirror capabilities into Claude, Codex, and Copilot control surfaces, and enforce parity through sync and path-audit behavior.

Execution starts with one OBPI:

1. Align canonical skill source and mirrors (`OBPI-0.4.0-01`).

## Consequences

### Positive

- Skills and command surfaces are explicitly linked and auditable.
- Operators can rely on a single canonical source with deterministic mirrors.
- Drift risk between runtime capability and agent skill surfaces is reduced.

### Negative

- Control-surface sync now has broader path responsibilities.
- Promotion introduces heavy-lane governance follow-through requirements.

## OBPIs

1. [`OBPI-0.4.0-01-skill-source-centralization`](obpis/OBPI-0.4.0-01-skill-source-centralization.md) — centralize canonical skills and mirror to Claude/Codex/Copilot.

## Evidence

- [x] Skill source and mirror topology implemented in runtime/config/sync surfaces.
- [x] Quality checks and path audits pass for mirrored topology.
- [ ] Human attestation recorded after remaining heavy-lane gate flow.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.4.0 | Pending | | | |
