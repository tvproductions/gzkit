---
id: OBPI-STUB-airlineops-surface-breadth-parity-01
parent: ADR-pool.airlineops-surface-breadth-parity
item: 1
lane: Heavy
status: Draft
---

# OBPI-STUB-airlineops-surface-breadth-parity-01: Canonical `.claude/**` and `.gzkit/**` Breadth Intake

## ADR Item

- **Source ADR:** `docs/design/adr/pool/ADR-pool.airlineops-surface-breadth-parity.md`
- **Checklist Item:** #1 -- "Inventory and classify canonical `.claude/**` and `.gzkit/**` candidates for governance-only extraction."

**Status:** Draft (pre-promotion stub)

## Objective

Create a deterministic intake and reconciliation workflow for the remaining breadth-parity backlog in canonical `.claude/**` and `.gzkit/**` surfaces.

## Governance Note

This file is a planning stub only. It is **not** an active OBPI artifact until the parent pool ADR is promoted to a SemVer ADR.

## Proposed Scope

- Produce canonical inventory with path-level evidence for `.claude/**` and `.gzkit/**`.
- Apply `docs/governance/parity-intake-rubric.md` to each candidate.
- Identify `Import Now` and `Import with Compatibility` candidates for first execution tranche.
- Record exclusions and deferrals with explicit rationale and revisit date.

## Proposed Verification Commands

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz adr audit-check ADR-0.6.0-pool-promotion-protocol
uv run mkdocs build --strict
```

## Draft Acceptance Criteria

- [ ] Candidate inventory covers all canonical `.claude/**` and `.gzkit/**` governance-relevant paths.
- [ ] Each candidate has intake-rubric classification and rationale.
- [ ] At least one import tranche is defined with ADR/OBPI linkage for implementation.
- [ ] Product-capability exclusions are explicitly tracked.

## Linkage

- Parent parity reports:
  - `docs/proposals/REPORT-airlineops-parity-2026-03-02.md`
  - `docs/proposals/REPORT-airlineops-govzero-mining-2026-03-02.md`
