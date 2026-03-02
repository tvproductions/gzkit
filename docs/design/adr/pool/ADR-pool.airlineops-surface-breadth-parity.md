---
id: ADR-pool.airlineops-surface-breadth-parity
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.3.0
---

# ADR-pool.airlineops-surface-breadth-parity: AirlineOps Control-Surface Breadth Parity

## Status

Pool

## Date

2026-03-02

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Canonical GovZero extraction completeness

---

## Intent

Track and govern the remaining parity backlog for broad canonical control surfaces (`.claude/**` and `.gzkit/**`) after baseline parity closure of instruction files, skills, and GovZero docs.

---

## Target Scope

- Build a governance-only import map for canonical `.claude/**` surfaces.
- Build a governance-only import map for canonical `.gzkit/**` surfaces.
- Classify each candidate by intake rubric outcome (`Import Now`, `Import with Compatibility`, `Defer (Tracked)`, `Exclude`).
- Add/adjust extraction surfaces in gzkit with explicit ADR lineage and evidence.
- Preserve path-level and procedure-level parity reporting with repeatable evidence commands.

---

## Non-Goals

- No wholesale mirroring of AirlineOps product-domain assets.
- No weakening of GovZero identity rule (`GovZero = AirlineOps - product capabilities`).
- No pool OBPIs before promotion.

---

## Dependencies

- **Blocks on**: ADR-0.3.0-airlineops-canon-reconciliation, ADR-0.5.0-skill-lifecycle-governance
- **Blocked by**: ADR-0.3.0-airlineops-canon-reconciliation

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Canonical candidate inventory for `.claude/**` and `.gzkit/**` is documented with path-level evidence.
2. Intake-rubric classification decisions are approved for high-impact candidates.
3. At least one OBPI execution plan exists for governance-only extraction without product-capability leakage.

---

## Notes

- This pool entry is opened from parity findings recorded in:
  - `docs/proposals/REPORT-airlineops-parity-2026-03-02.md`
  - `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-02.md`
