---
id: OBPI-0.37.0-10-architectural-enforcement
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-10: architectural-enforcement

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-10 — "Compare and absorb architectural-enforcement.md — enforcement patterns"`

## OBJECTIVE

Compare `docs/governance/GovZero/architectural-enforcement.md` between airlineops and gzkit. This document defines how architectural decisions are enforced through hooks, gates, and automated checks. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/architectural-enforcement.md`
- **gzkit:** `docs/governance/GovZero/architectural-enforcement.md`

## ASSUMPTIONS

- Enforcement documentation must match actual hook and gate behavior
- gzkit implements the enforcement; its documentation should be authoritative
- airlineops may have additional enforcement patterns from operational use

## NON-GOALS

- Changing the enforcement architecture
- Adding domain-specific enforcement rules

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in enforcement patterns, hook descriptions, gate definitions
1. Evaluate which version is more accurate and complete
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/architectural-enforcement.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
