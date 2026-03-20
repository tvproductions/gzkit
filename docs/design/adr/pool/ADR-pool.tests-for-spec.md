---
id: ADR-pool.tests-for-spec
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-pool.spec-triangle-sync
promoted_to: ADR-0.21.0-tests-for-spec
---

# ADR-pool.tests-for-spec: Tests as Spec Verification Surface
> Promoted to `ADR-0.21.0-tests-for-spec` on 2026-03-20. This pool file is retained as historical intake context.


## Status

Superseded

## Date

2026-03-05

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance verification fidelity

---

## Intent

Make "tests for spec" explicit: tests must prove named requirements from ADR/OBPI specs, not only execute code paths.

---

## Target Scope

- Define traceability contract from spec artifacts to tests.
- Enforce requirement-level coverage anchors across three levels:
  - `ADR-*`
  - `OBPI-*`
  - `REQ-*`
- Add command surfaces to report missing and present `@covers(...)` mappings.
- Integrate traceability output with ADR audit and status reporting.
- Produce operator-facing docs with examples of compliant annotations.
- Define language-agnostic proof metadata patterns for non-Python test stacks.

---

## Non-Goals

- No immediate mandate for branch-level 100% requirement coverage.
- No replacement of code coverage tools.
- No lock-in to decorator syntax if equivalent metadata surfaces emerge later.

---

## Dependencies

- **Blocks on**: ADR-pool.spec-triangle-sync
- **Blocked by**: ADR-pool.spec-triangle-sync

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Minimum traceability schema is approved.
2. CLI evidence check proves missing/covered targets deterministically.
3. Migration plan exists for legacy tests lacking explicit spec linkage.
4. Non-Python proof annotation contract is defined (equivalent to `@covers`).

---

## Notes

- "Tests for spec" is interpreted as requirement-level behavioral proof.
- Recommended granularity is three linked IDs:
  - `ADR-*` for feature intent anchor,
  - `OBPI-*` for implementation-unit anchor,
  - `REQ-*` for acceptance-criterion anchor.
- REQ ID term: `Requirement Identifier` (`REQ-<semver>-<obpi_item>-<criterion_index>`).
- This aligns with Beads graph discipline: small linked units, explicit dependencies, and queryable readiness/proof state.
- This does not imply Beads storage/runtime parity; it applies the graph-and-proof pattern to gzkit governance artifacts.
