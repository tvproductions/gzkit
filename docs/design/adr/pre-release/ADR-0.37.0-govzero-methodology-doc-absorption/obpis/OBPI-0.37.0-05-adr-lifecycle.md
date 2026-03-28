---
id: OBPI-0.37.0-05-adr-lifecycle
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-05: adr-lifecycle

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-05 — "Compare and absorb adr-lifecycle.md — ADR lifecycle definitions"`

## OBJECTIVE

Compare `docs/governance/GovZero/adr-lifecycle.md` between airlineops and gzkit. This document defines the ADR lifecycle: status transitions, approval gates, and completion criteria. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/adr-lifecycle.md`
- **gzkit:** `docs/governance/GovZero/adr-lifecycle.md`

## ASSUMPTIONS

- The ADR lifecycle is foundational to governance — precision matters
- Both repos should follow the same lifecycle but may have documented it differently
- gzkit's version should reflect the tooling's actual enforcement behavior

## NON-GOALS

- Changing the ADR lifecycle itself
- Adding new lifecycle states

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in lifecycle states, transitions, approval criteria
1. Evaluate which version is more complete and accurate
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/adr-lifecycle.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
