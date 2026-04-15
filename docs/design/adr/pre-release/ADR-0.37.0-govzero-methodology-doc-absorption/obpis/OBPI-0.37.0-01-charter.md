---
id: OBPI-0.37.0-01-charter
parent: ADR-0.37.0-govzero-methodology-doc-absorption
item: 1
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.37.0-01: charter

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/ADR-0.37.0-govzero-methodology-doc-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.37.0-01 — "Compare and absorb charter.md — GovZero charter and principles"`

## OBJECTIVE

Compare `docs/governance/GovZero/charter.md` between airlineops and gzkit. The charter defines GovZero's foundational principles, mission, and governance philosophy. Determine: Absorb (airlineops version is more complete), Confirm (gzkit version is sufficient or superior), or Merge (both have unique valuable content).

## SOURCE MATERIAL

- **airlineops:** `docs/governance/GovZero/charter.md`
- **gzkit:** `docs/governance/GovZero/charter.md`

## ASSUMPTIONS

- The charter is the foundational GovZero document — completeness matters
- Both repos may have evolved the charter independently
- gzkit as the governance toolkit should have the authoritative version
- The charter should be governance-generic, not domain-specific

## NON-GOALS

- Rewriting the charter from scratch
- Adding domain-specific principles
- Changing the governance philosophy

## REQUIREMENTS (FAIL-CLOSED)

1. Read both versions of `charter.md` completely
1. Document differences: sections, principles, mission statements, philosophy
1. Evaluate which version is more complete and authoritative
1. Record decision with rationale: Absorb / Confirm / Merge

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.37.0-01-01: Read both versions of `charter.md` completely
- [x] REQ-0.37.0-01-02: Document differences: sections, principles, mission statements, philosophy
- [x] REQ-0.37.0-01-03: Evaluate which version is more complete and authoritative
- [x] REQ-0.37.0-01-04: Record decision with rationale: Absorb / Confirm / Merge


## ALLOWED PATHS

- `docs/governance/GovZero/charter.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.37.0-govzero-methodology-doc-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run mkdocs build --strict` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
