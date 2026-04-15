---
id: OBPI-0.36.0-06-gate5-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-06: gate5-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-06 — "Reconcile gate5_runbook_code_covenant.instructions.md vs .claude/rules/gate5-runbook-code-covenant.md"`

## OBJECTIVE

Compare airlineops's `gate5_runbook_code_covenant.instructions.md` against gzkit's `.claude/rules/gate5-runbook-code-covenant.md` to identify content gaps. Both files govern the documentation-as-first-class-deliverable covenant: three-layer documentation model, required updates when behavior changes, validation bundle, and anti-patterns. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/gate5_runbook_code_covenant.instructions.md`
- **gzkit equivalent:** `.claude/rules/gate5-runbook-code-covenant.md`

## ASSUMPTIONS

- Both files enforce the same three-layer documentation model (operator runbook, governance runbook, command docs)
- Validation bundles may differ (airlineops may have additional validation steps)
- Anti-patterns should be consistent across both repos
- airlineops may have added Gate 5 lessons from operational documentation experience

## NON-GOALS

- Changing the Gate 5 architecture
- Adding domain-specific documentation requirements to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: documentation model, required updates, validation bundle, anti-patterns
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-06-01: Read both files completely
- [x] REQ-0.36.0-06-02: Create a section-by-section comparison: documentation model, required updates, validation bundle, anti-patterns
- [x] REQ-0.36.0-06-03: Document content gaps in either direction
- [x] REQ-0.36.0-06-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `.claude/rules/gate5-runbook-code-covenant.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
