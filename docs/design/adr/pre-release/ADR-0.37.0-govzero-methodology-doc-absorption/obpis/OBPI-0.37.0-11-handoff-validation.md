---
id: OBPI-0.37.0-11-handoff-validation
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 11
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-11: handoff-validation

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-11 — "Compare and absorb handoff-validation.md — session handoff validation"`

## OBJECTIVE

Compare `docs/governance/GovZero/handoff-validation.md` between airlineops and gzkit. This document defines how agent session handoffs are validated for completeness and accuracy. Determine: Absorb, Confirm, or Merge.

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/handoff-validation.md`
- **gzkit:** `docs/governance/GovZero/handoff-validation.md`

## ASSUMPTIONS

- Handoff validation is critical for multi-session governance continuity
- Both repos should have the same validation criteria
- gzkit's version should reflect the tooling's actual handoff validation behavior

## NON-GOALS

- Changing the handoff validation protocol
- Adding domain-specific validation criteria

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions completely
1. Document differences in validation criteria, required fields, failure handling
1. Evaluate which version is more complete
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-11-01: Read both versions completely
- [x] REQ-0.37.0-11-02: Document differences in validation criteria, required fields, failure handling
- [x] REQ-0.37.0-11-03: Evaluate which version is more complete
- [x] REQ-0.37.0-11-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/handoff-validation.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
