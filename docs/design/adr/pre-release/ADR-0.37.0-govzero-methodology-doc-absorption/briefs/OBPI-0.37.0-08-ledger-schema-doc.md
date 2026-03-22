---
id: OBPI-0.37.0-08-ledger-schema-doc
parent_adr: ADR-0.37.0-govzero-methodology-doc-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-08: ledger-schema-doc

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-08 — "Compare and absorb ledger-schema.md — ledger event schema"`

## OBJECTIVE

Compare `docs/governance/GovZero/ledger-schema.md` between airlineops and gzkit. This document defines the JSONL ledger event schema — the immutable audit trail for governance events. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/ledger-schema.md`
- **gzkit:** `docs/governance/GovZero/ledger-schema.md`

## ASSUMPTIONS

- The ledger schema must match the actual `.gzkit/ledger.jsonl` format
- gzkit implements the ledger; its documentation should be authoritative
- airlineops may have additional event types from domain-specific governance events

## NON-GOALS

- Changing the ledger schema
- Adding domain-specific event types

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in schema fields, event types, validation rules
1. Evaluate which version matches the actual implementation
1. Record decision with rationale: Absorb / Confirm / Merge

## ALLOWED PATHS

- `docs/governance/GovZero/ledger-schema.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
