---
id: OBPI-0.36.0-07-adr-audit-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 7
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-07: adr-audit-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-07 — "Reconcile adr_audit.instructions.md vs .claude/rules/adr-audit.md"`

## OBJECTIVE

Compare airlineops's `adr_audit.instructions.md` against gzkit's `.claude/rules/adr-audit.md` to identify content gaps. Both files govern ADR audit procedures: audit sequence, quality checks, closeout lifecycle, receipt emission, and rules. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/adr_audit.instructions.md`
- **gzkit equivalent:** `.claude/rules/adr-audit.md`

## ASSUMPTIONS

- Both files enforce the same audit sequence and closeout protocol
- airlineops may have additional audit steps from operational experience
- gzkit's audit rules may be more sophisticated (as the governance toolkit)
- Receipt emission commands should be consistent

## NON-GOALS

- Changing the audit protocol
- Adding domain-specific audit steps to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: audit sequence, quality checks, closeout, receipt emission, rules
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-07-01: Read both files completely
- [x] REQ-0.36.0-07-02: Create a section-by-section comparison: audit sequence, quality checks, closeout, receipt emission, rules
- [x] REQ-0.36.0-07-03: Document content gaps in either direction
- [x] REQ-0.36.0-07-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `.claude/rules/adr-audit.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
