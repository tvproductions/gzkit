---
id: OBPI-0.36.0-02-tests-instructions
parent_adr: ADR-0.36.0-instruction-file-reconciliation
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-02: tests-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-02 — "Reconcile tests.instructions.md vs .claude/rules/tests.md"`

## OBJECTIVE

Compare airlineops's `tests.instructions.md` against gzkit's `.claude/rules/tests.md` to identify content gaps. Both files govern testing policy: stdlib unittest, table-driven tests, DB isolation, coverage floors, and cross-platform cleanup. Determine: Absorb (airlineops has content gzkit lacks) or Confirm (gzkit's version is complete).

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/tests.instructions.md`
- **gzkit equivalent:** `.claude/rules/tests.md`

## ASSUMPTIONS

- Both files enforce the same core policies: no pytest, table-driven, DB isolation
- airlineops may have additional test patterns from domain-specific testing experience
- gzkit's test policy may be more focused on governance tooling patterns
- Cross-platform cleanup rules should be identical

## NON-GOALS

- Changing the testing framework policy
- Adding domain-specific test patterns to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: framework, patterns, DB isolation, coverage, cleanup
1. Document content present in airlineops but missing from gzkit
1. Record decision with rationale: Absorb / Confirm

## ALLOWED PATHS

- `.claude/rules/tests.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
