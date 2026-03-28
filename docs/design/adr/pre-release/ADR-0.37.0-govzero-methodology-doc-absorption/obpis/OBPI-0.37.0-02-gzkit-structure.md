---
id: OBPI-0.37.0-02-gzkit-structure
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 2
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-02: gzkit-structure

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-02 — "Compare and absorb gzkit-structure.md — project structure documentation"`

## OBJECTIVE

Compare `docs/governance/GovZero/gzkit-structure.md` between airlineops and gzkit. This document defines the canonical project structure for gzkit-governed repositories. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/gzkit-structure.md`
- **gzkit:** `docs/governance/GovZero/gzkit-structure.md`

## ASSUMPTIONS

- gzkit's version should be authoritative since it defines gzkit's own structure
- airlineops may have additional structure documentation from its companion perspective
- Directory trees and file descriptions should reflect current reality

## NON-GOALS

- Changing the project structure itself
- Adding domain-specific directory conventions

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in directory trees, file descriptions, conventions
1. Evaluate which version is more current and complete
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/gzkit-structure.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
