---
id: OBPI-0.37.0-14-layered-trust
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 14
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-14: layered-trust

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-14 — "Compare and absorb layered-trust.md — trust model documentation"`

## OBJECTIVE

Compare `docs/governance/GovZero/layered-trust.md` between airlineops and gzkit. This document defines the layered trust model — how trust is established, verified, and maintained across human-agent governance boundaries. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/layered-trust.md`
- **gzkit:** `docs/governance/GovZero/layered-trust.md`

## ASSUMPTIONS

- The trust model is foundational to GovZero governance philosophy
- Both repos should describe the same trust layers
- The trust model should be governance-generic, not domain-specific

## NON-GOALS

- Changing the trust model
- Adding domain-specific trust layers

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in trust layers, verification mechanisms, boundary definitions
1. Evaluate which version is more complete and philosophically sound
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/layered-trust.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
