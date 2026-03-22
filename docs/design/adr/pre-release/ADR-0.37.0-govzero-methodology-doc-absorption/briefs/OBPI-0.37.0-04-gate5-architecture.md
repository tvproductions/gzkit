---
id: OBPI-0.37.0-04-gate5-architecture
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-04: gate5-architecture

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-04 — "Compare and absorb gate5-architecture.md — Gate 5 attestation architecture"`

## OBJECTIVE

Compare `docs/governance/GovZero/gate5-architecture.md` between airlineops and gzkit. This document defines the Gate 5 human attestation architecture — the keystone of GovZero governance. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/gate5-architecture.md`
- **gzkit:** `docs/governance/GovZero/gate5-architecture.md`

## ASSUMPTIONS

- Gate 5 is the most critical governance gate — documentation must be precise
- gzkit implements Gate 5; its documentation should be authoritative
- airlineops may have operational insights from Gate 5 execution experience

## NON-GOALS

- Changing the Gate 5 architecture
- Adding domain-specific attestation requirements

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in architecture descriptions, attestation flows, enforcement rules
1. Evaluate which version is more complete and precise
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/gate5-architecture.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
