---
id: OBPI-0.37.0-06-adr-status-doc
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-06: adr-status-doc

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-06 — "Compare and absorb adr-status.md — ADR status definitions and transitions"`

## OBJECTIVE

Compare `docs/governance/GovZero/adr-status.md` between airlineops and gzkit. This document defines ADR status values, their meanings, and valid transitions. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/adr-status.md`
- **gzkit:** `docs/governance/GovZero/adr-status.md`

## ASSUMPTIONS

- Status definitions must match what the tooling enforces
- Both repos should have identical status values but descriptions may differ
- gzkit's version should be authoritative since it implements the status machine

## NON-GOALS

- Adding new status values
- Changing status transition rules

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in status definitions, transitions, and descriptions
1. Evaluate which version is more precise
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-06-01: Read both versions completely
- [x] REQ-0.37.0-06-02: Document differences in status definitions, transitions, and descriptions
- [x] REQ-0.37.0-06-03: Evaluate which version is more precise
- [x] REQ-0.37.0-06-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/adr-status.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
