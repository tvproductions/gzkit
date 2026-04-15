---
id: OBPI-0.36.0-09-chores-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 9
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-09: chores-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-09 — "Reconcile chores.instructions.md vs .claude/rules/chores.md"`

## OBJECTIVE

Compare airlineops's `chores.instructions.md` against gzkit's `.claude/rules/chores.md` to identify content gaps. Both files govern chores workflow: core principles, command sequences, discovery, planning, advice application, and evidence/attestation. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/chores.instructions.md`
- **gzkit equivalent:** `.claude/rules/chores.md`

## ASSUMPTIONS

- Both files describe the same chores workflow system
- Command sequences should reference the correct CLI (`gz` for gzkit)
- airlineops may have additional chore types or workflow patterns
- Evidence and attestation rules should be consistent

## NON-GOALS

- Changing the chores architecture
- Adding domain-specific chore types to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: principles, command sequences, evidence, attestation
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-09-01: Read both files completely
- [x] REQ-0.36.0-09-02: Create a section-by-section comparison: principles, command sequences, evidence, attestation
- [x] REQ-0.36.0-09-03: Document content gaps in either direction
- [x] REQ-0.36.0-09-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `.claude/rules/chores.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
