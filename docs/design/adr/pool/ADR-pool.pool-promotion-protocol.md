---
id: ADR-pool.pool-promotion-protocol
status: Superseded
parent: ADR-0.5.0-skill-lifecycle-governance
lane: heavy
enabler: OBPI-0.5.0-04-maintenance-and-deprecation-operations
promoted_to: ADR-0.6.0-pool-promotion-protocol
---

# ADR-pool.pool-promotion-protocol: Pool Promotion Protocol and Tooling
> Promoted to `ADR-0.6.0-pool-promotion-protocol` on 2026-02-21. This pool file is retained as historical intake context.


## Status

Superseded

## Date

2026-02-21

## Parent ADR

[ADR-0.5.0-skill-lifecycle-governance](../pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md) -- lifecycle maintenance and deprecation operations

---

## Intent

Define and enforce a canonical pool-to-ADR promotion process so prioritization decisions are converted into executable ADR packages with auditable lineage and no manual drift.

---

## Target Scope

- Define promotion preconditions for pool entries (`status`, identity, semver target, slug contract).
- Add deterministic tooling to create canonical ADR package paths by semver bucket.
- Preserve pool intake context while marking promoted entries as superseded with an explicit promotion target.
- Record promotion lineage as a ledger rename event for audit/reconciliation workflows.
- Provide operator manpage/documentation so promotion behavior is visible and repeatable.

---

## Non-Goals

- Redefining ADR acceptance or closeout gates.
- Introducing OBPI execution semantics changes beyond promotion handoff.
- Auto-attesting promoted ADRs.

---

## Dependencies

- ADR-0.5.0-skill-lifecycle-governance (lifecycle contract)
- OBPI-0.5.0-04-maintenance-and-deprecation-operations (maintenance operations)
