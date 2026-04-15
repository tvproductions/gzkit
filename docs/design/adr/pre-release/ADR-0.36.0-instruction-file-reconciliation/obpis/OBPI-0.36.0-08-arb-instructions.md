---
id: OBPI-0.36.0-08-arb-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-08: arb-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-08 — "Reconcile arb.instructions.md vs .claude/rules/arb.md"`

## OBJECTIVE

Compare airlineops's `arb.instructions.md` against gzkit's `.claude/rules/arb.md` to identify content gaps. Both files govern ARB (Agent Self-Reporting) middleware usage: core concept, when to use ARB, available commands, receipt schema, and exit codes. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/arb.instructions.md`
- **gzkit equivalent:** `.claude/rules/arb.md`

## ASSUMPTIONS

- Both files describe the same ARB middleware system
- airlineops may have additional ARB commands or usage patterns from operational experience
- gzkit's ARB documentation may be the source of truth (as the governance toolkit)
- Receipt schema references should be consistent

## NON-GOALS

- Changing the ARB architecture
- Adding domain-specific ARB commands to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: core concept, when to use, commands, schema, exit codes
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-08-01: Read both files completely
- [x] REQ-0.36.0-08-02: Create a section-by-section comparison: core concept, when to use, commands, schema, exit codes
- [x] REQ-0.36.0-08-03: Document content gaps in either direction
- [x] REQ-0.36.0-08-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `.claude/rules/arb.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
