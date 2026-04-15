---
id: OBPI-0.37.0-03-governance-registry-design
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-03: governance-registry-design

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-03 — "Compare and absorb governance-registry-design.md — registry architecture"`

## OBJECTIVE

Compare `docs/governance/GovZero/governance-registry-design.md` between airlineops and gzkit. This document defines the governance registry architecture (content type registration, schema validation, discovery). Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/governance-registry-design.md`
- **gzkit:** `docs/governance/GovZero/governance-registry-design.md`

## ASSUMPTIONS

- gzkit implements the registry; its documentation should be authoritative
- airlineops may have usage patterns or lessons learned from registry consumption
- The registry design should be governance-generic

## NON-GOALS

- Changing the registry architecture
- Adding domain-specific registry types

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in architecture descriptions, schema definitions, usage patterns
1. Evaluate which version is more complete
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-03-01: Read both versions completely
- [x] REQ-0.37.0-03-02: Document differences in architecture descriptions, schema definitions, usage patterns
- [x] REQ-0.37.0-03-03: Evaluate which version is more complete
- [x] REQ-0.37.0-03-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/governance-registry-design.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
