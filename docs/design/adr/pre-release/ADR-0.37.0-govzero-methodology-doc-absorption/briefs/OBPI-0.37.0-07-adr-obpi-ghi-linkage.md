---
id: OBPI-0.37.0-07-adr-obpi-ghi-linkage
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-07: adr-obpi-ghi-linkage

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-07 — "Compare and absorb adr-obpi-ghi-audit-linkage.md — governance artifact linkage"`

## OBJECTIVE

Compare `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md` between airlineops and gzkit. This document defines how ADRs, OBPIs, GitHub Issues, and audits link together in the governance hierarchy. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`
- **gzkit:** `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md`

## ASSUMPTIONS

- The linkage model is foundational to the four-tier governance hierarchy
- Both repos should describe the same linkage model
- gzkit's version should reflect the tooling's actual enforcement

## NON-GOALS

- Changing the governance hierarchy
- Adding new artifact types

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in linkage definitions, hierarchy descriptions, enforcement rules
1. Evaluate which version is more complete
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
