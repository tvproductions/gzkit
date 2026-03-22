---
id: OBPI-0.37.0-09-audit-protocol
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-09: audit-protocol

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-09 — "Compare and absorb audit-protocol.md — audit execution protocol"`

## OBJECTIVE

Compare `docs/governance/GovZero/audit-protocol.md` between airlineops and gzkit. This document defines how governance audits are executed — steps, evidence requirements, and success criteria. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/audit-protocol.md`
- **gzkit:** `docs/governance/GovZero/audit-protocol.md`

## ASSUMPTIONS

- The audit protocol must match the tooling's `gz audit` command behavior
- airlineops may have audit refinements from operational experience
- gzkit's version should reflect the actual audit enforcement

## NON-GOALS

- Changing the audit protocol
- Adding domain-specific audit steps

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in audit steps, evidence requirements, success criteria
1. Evaluate which version is more complete and accurate
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/audit-protocol.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
