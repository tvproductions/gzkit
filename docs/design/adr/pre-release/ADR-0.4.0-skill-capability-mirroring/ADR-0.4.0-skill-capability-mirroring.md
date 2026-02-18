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

Execution is decomposed into distribution workstreams:

1. Align canonical skill source and mirrors (`OBPI-0.4.0-01`).
2. Define and enforce agent-native mirror contracts (`OBPI-0.4.0-02`).
3. Make sync deterministic and add recovery behavior (`OBPI-0.4.0-03`).
4. Complete compatibility migration and cleanup (`OBPI-0.4.0-04`).

## Consequences

### Positive

- Skills and command surfaces are explicitly linked and auditable.
- Operators can rely on a single canonical source with deterministic mirrors.
- Drift risk between runtime capability and agent skill surfaces is reduced.

### Negative

- Control-surface sync now has broader path responsibilities and stricter drift accountability.
- Migration must preserve operational continuity while removing legacy assumptions.
- Promotion introduces heavy-lane governance follow-through requirements across multiple tranches.

## OBPIs

1. [`OBPI-0.4.0-01-skill-source-centralization`](obpis/OBPI-0.4.0-01-skill-source-centralization.md) — centralize canonical skills and mirror to Claude/Codex/Copilot.
2. [`OBPI-0.4.0-02-agent-native-mirror-contracts`](obpis/OBPI-0.4.0-02-agent-native-mirror-contracts.md) — codify and enforce mirror contracts per agent surface.
3. [`OBPI-0.4.0-03-sync-determinism-and-recovery`](obpis/OBPI-0.4.0-03-sync-determinism-and-recovery.md) — harden sync determinism, drift detection, and recovery behavior.
4. [`OBPI-0.4.0-04-mirror-compat-migration`](obpis/OBPI-0.4.0-04-mirror-compat-migration.md) — finish compatibility migration and remove stale opsdev-era assumptions.

## Evidence

- [x] Skill source and mirror topology implemented in runtime/config/sync surfaces.
- [ ] Agent-native mirror contracts are explicit and auditable for all control surfaces.
- [ ] Sync determinism and recovery behavior are verified under drift scenarios.
- [ ] Compatibility migration is complete and legacy mirror assumptions are retired.
- [ ] Human attestation recorded after remaining heavy-lane gate flow.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.4.0 | Pending | | | |
