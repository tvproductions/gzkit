---
id: OBPI-0.37.0-12-session-handoff-obligations
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 12
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-12: session-handoff-obligations

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-12 — "Compare and absorb session-handoff-obligations.md — handoff obligations"`

## OBJECTIVE

Compare `docs/governance/GovZero/session-handoff-obligations.md` between airlineops and gzkit. This document defines agent obligations when handing off sessions — what must be documented, what state must be preserved, and what the successor agent needs. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/session-handoff-obligations.md`
- **gzkit:** `docs/governance/GovZero/session-handoff-obligations.md`

## ASSUMPTIONS

- Handoff obligations are governance-generic — apply to any agent-governed project
- Both repos should have the same obligations but may describe them differently
- Quality of handoff documentation directly impacts governance continuity

## NON-GOALS

- Changing the handoff obligation requirements
- Adding domain-specific handoff fields

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in obligation lists, required fields, documentation standards
1. Evaluate which version is more comprehensive
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/session-handoff-obligations.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
