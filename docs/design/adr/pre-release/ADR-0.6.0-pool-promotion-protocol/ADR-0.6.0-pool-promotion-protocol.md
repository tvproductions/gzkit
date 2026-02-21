---
id: ADR-0.6.0-pool-promotion-protocol
status: Proposed
semver: 0.6.0
lane: heavy
parent: ADR-0.5.0-skill-lifecycle-governance
date: 2026-02-21
promoted_from: ADR-pool.pool-promotion-protocol
---

# ADR-0.6.0-pool-promotion-protocol: Pool Promotion Protocol and Tooling

## Intent

Replace manual, drift-prone pool intake promotion with a deterministic, auditable protocol so prioritized pool entries become canonical ADR packages without losing lineage or operator context.

## Decision

Adopt a canonical promotion workflow centered on `uv run gz adr promote`:

1. Source must be a pool ADR (`ADR-pool.*`).
2. Target ADR ID resolves as `ADR-{semver}-{slug}` and lands in semver bucket path (`foundation/`, `pre-release/`, `<major>.0/`).
3. Source pool file is retained as historical intake context and marked `Superseded` with `promoted_to`.
4. Promotion lineage is recorded in ledger as `artifact_renamed` with reason `pool_promotion`.
5. Promotion behavior is operator-visible in command docs and governance lifecycle documentation.

## Consequences

### Positive

- Pool prioritization becomes deterministic and repeatable.
- Ledger lineage makes promotion events auditable and reconcilable.
- Canonical ADR packaging is enforced at promotion time rather than by manual follow-up.

### Negative

- Promotion introduces stricter prerequisites for pool documents and naming consistency.
- Existing manual habits require migration to the canonical command flow.

## OBPIs

1. [`OBPI-0.6.0-01-pool-source-contract`](obpis/OBPI-0.6.0-01-pool-source-contract.md)
2. [`OBPI-0.6.0-02-promotion-command-lineage`](obpis/OBPI-0.6.0-02-promotion-command-lineage.md)
3. [`OBPI-0.6.0-03-operator-narratives-and-auditability`](obpis/OBPI-0.6.0-03-operator-narratives-and-auditability.md)

## Evidence

- [x] Protocol docs updated: `docs/design/adr/pool/README.md`, `docs/governance/GovZero/adr-lifecycle.md`.
- [x] Command surface added and documented: `src/gzkit/cli.py`, `docs/user/commands/adr-promote.md`, `docs/user/commands/index.md`.
- [x] Tests added and passing: `tests/test_cli.py` (`TestAdrPromoteCommand`).
- [x] Quality gates run for implementation batch: `uv run gz lint`, `uv run gz typecheck`, `uv run gz cli audit`, `uv run gz check`.
- [ ] ADR-level Gate 5 attestation pending.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.6.0 | Pending | | | |
