---
id: OBPI-0.36.0-10-gh-cli-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-10: gh-cli-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-10 — "Reconcile gh_cli.instructions.md vs .claude/rules/gh-cli.md"`

## OBJECTIVE

Compare airlineops's `gh_cli.instructions.md` against gzkit's `.claude/rules/gh-cli.md` to identify content gaps. Both files govern GitHub CLI guardrails: allowed commands, prohibited commands, and defect tracking requirements. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/gh_cli.instructions.md`
- **gzkit equivalent:** `.claude/rules/gh-cli.md`

## ASSUMPTIONS

- Both files enforce the same GitHub CLI guardrails
- Allowed commands should be consistent (gh auth, issue, release)
- Prohibited commands should be consistent (settings mutations, secrets, force pushes, unauthorized merges)
- airlineops may have additional gh commands from operational workflows

## NON-GOALS

- Changing the GitHub CLI guardrails policy
- Adding domain-specific gh commands to gzkit
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: allowed commands, prohibited commands, defect tracking
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.36.0-10-01: Read both files completely
- [x] REQ-0.36.0-10-02: Create a section-by-section comparison: allowed commands, prohibited commands, defect tracking
- [x] REQ-0.36.0-10-03: Document content gaps in either direction
- [x] REQ-0.36.0-10-04: Record decision with rationale: Absorb / Confirm


## ALLOWED PATHS

- `.claude/rules/gh-cli.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
