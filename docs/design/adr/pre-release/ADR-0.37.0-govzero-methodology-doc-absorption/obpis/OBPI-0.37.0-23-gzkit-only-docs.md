---
id: OBPI-0.37.0-23-gzkit-only-docs
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 23
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-23: gzkit-only-docs

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-23 — "Verify gzkit-only docs (obpi-runtime-contract.md + other gzkit-only docs) for completeness"`

## OBJECTIVE

Verify completeness of GovZero methodology documents that exist only in gzkit (not in airlineops). Primary target: `obpi-runtime-contract.md` and any other documents in gzkit's `docs/governance/GovZero/` that have no airlineops counterpart. These documents represent gzkit's unique governance contributions and must be verified as complete, current, and editorially consistent with the rest of the methodology documentation.

## SOURCE MATERIAL

- **gzkit:** `docs/governance/GovZero/` — all files without airlineops counterparts
- **Primary:** `docs/governance/GovZero/obpi-runtime-contract.md`

## ASSUMPTIONS

- gzkit-only docs were authored as gzkit evolved beyond airlineops's governance needs
- These documents may reference other methodology docs that have been updated separately
- Completeness verification includes: all sections filled, no TODOs, no stale references
- These docs should be editorially consistent with absorbed/confirmed docs from OBPIs 01-22

## NON-GOALS

- Creating new methodology documents
- Porting gzkit-only documents back to airlineops
- Changing the governance methodology

## REQUIREMENTS (FAIL-CLOSED)

1. List all files in gzkit's `docs/governance/GovZero/` that have no airlineops counterpart
1. For each gzkit-only file: verify completeness (all sections filled, no TODOs, no stale references)
1. Verify cross-references to other methodology docs are accurate
1. Document any completeness gaps or needed updates
1. Record verification result: Complete / Needs Updates (with specifics)

## ALLOWED PATHS

- `docs/governance/GovZero/` — target for completeness verification and updates
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
