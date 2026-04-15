---
id: OBPI-0.36.0-05-pythonic-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-05: pythonic-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-05 — "Reconcile pythonic.instructions.md vs .claude/rules/pythonic.md"`

## OBJECTIVE

Compare airlineops's `pythonic.instructions.md` against gzkit's `.claude/rules/pythonic.md` to identify content gaps. Both files govern Python coding conventions: clarity over cleverness, separation of concerns, typed interfaces, EAFP/LBYL, context managers, size limits, imports, error handling, and toolchain. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/pythonic.instructions.md`
- **gzkit equivalent:** `.claude/rules/pythonic.md`

## ASSUMPTIONS

- Both files enforce the same Pythonic principles and Astral toolchain (uv, ruff, ty)
- Size limits should be identical (<=50 lines/function, <=600 lines/module, <=300 lines/class)
- airlineops may have additional coding patterns from domain-specific implementation experience
- Error handling and import rules should be consistent

## NON-GOALS

- Changing the coding style conventions
- Adding domain-specific coding patterns to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: principles, size limits, imports, error handling, toolchain
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-05-01: Read both files completely
- [x] REQ-0.36.0-05-02: Create a section-by-section comparison: principles, size limits, imports, error handling, toolchain
- [x] REQ-0.36.0-05-03: Document content gaps in either direction
- [x] REQ-0.36.0-05-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `.claude/rules/pythonic.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
