---
id: OBPI-0.37.0-18-release-major
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-18: release-major

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-18 — "Compare and absorb releases/major-release.md — major release process"`

## OBJECTIVE

Compare `docs/governance/GovZero/releases/major-release.md` between airlineops and gzkit. This document defines the major release process — prerequisites, steps, validation, and rollback procedures. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/releases/major-release.md`
- **gzkit:** `docs/governance/GovZero/releases/major-release.md`

## ASSUMPTIONS

- Major release processes should be consistent across GovZero-governed projects
- gzkit's version should reflect its own release tooling
- airlineops may have operational refinements from actual major releases

## NON-GOALS

- Changing the major release process
- Adding domain-specific release steps

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in prerequisites, steps, validation, rollback procedures
1. Evaluate which version is more complete and actionable
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/releases/major-release.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
