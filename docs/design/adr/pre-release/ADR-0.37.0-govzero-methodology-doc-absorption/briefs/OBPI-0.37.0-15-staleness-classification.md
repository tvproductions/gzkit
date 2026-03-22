---
id: OBPI-0.37.0-15-staleness-classification
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-15: staleness-classification

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-15 — "Compare and absorb staleness-classification.md — staleness definitions"`

## OBJECTIVE

Compare `docs/governance/GovZero/staleness-classification.md` between airlineops and gzkit. This document defines how governance artifacts are classified for staleness — time thresholds, staleness levels, and remediation actions. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/staleness-classification.md`
- **gzkit:** `docs/governance/GovZero/staleness-classification.md`

## ASSUMPTIONS

- Staleness classifications must match the tooling's staleness detection behavior
- Both repos should have the same thresholds but operational experience may have refined them
- gzkit implements staleness detection; its documentation should be authoritative

## NON-GOALS

- Changing the staleness thresholds
- Adding domain-specific staleness criteria

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in staleness levels, thresholds, remediation actions
1. Evaluate which version matches the actual implementation
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/staleness-classification.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
