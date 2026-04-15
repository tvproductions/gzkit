---
id: OBPI-0.37.0-13-session-handoff-schema
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 13
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-13: session-handoff-schema

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-13 — "Compare and absorb session-handoff-schema.md — handoff schema definition"`

## OBJECTIVE

Compare `docs/governance/GovZero/session-handoff-schema.md` between airlineops and gzkit. This document defines the structured schema for session handoff documents — required fields, optional fields, and validation rules. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/session-handoff-schema.md`
- **gzkit:** `docs/governance/GovZero/session-handoff-schema.md`

## ASSUMPTIONS

- The handoff schema must match the tooling's validation behavior
- gzkit implements schema validation; its documentation should be authoritative
- airlineops may have field additions from operational handoff experience

## NON-GOALS

- Changing the handoff schema
- Adding domain-specific handoff fields

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in schema fields, types, validation rules
1. Evaluate which version matches the actual implementation
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-13-01: Read both versions completely
- [x] REQ-0.37.0-13-02: Document differences in schema fields, types, validation rules
- [x] REQ-0.37.0-13-03: Evaluate which version matches the actual implementation
- [x] REQ-0.37.0-13-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/session-handoff-schema.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
