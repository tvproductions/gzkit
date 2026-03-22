---
id: OBPI-0.36.0-01-cli-instructions
parent_adr: ADR-0.36.0-instruction-file-reconciliation
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-01: cli-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-01 — "Reconcile cli.instructions.md vs .claude/rules/cli.md"`

## OBJECTIVE

Compare airlineops's `cli.instructions.md` against gzkit's `.claude/rules/cli.md` to identify content gaps in either direction. Both files govern CLI design principles, exit codes, flag conventions, output contracts, and help text requirements. Determine: Absorb (airlineops has content gzkit lacks), Confirm (gzkit's version is complete), or note bidirectional gaps for remediation.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/cli.instructions.md`
- **gzkit equivalent:** `.claude/rules/cli.md`

## ASSUMPTIONS

- Both files serve the same purpose: governing CLI design for agent sessions
- Content may have diverged as both repos evolved independently
- airlineops may have added CLI patterns from operational experience (airline-domain commands)
- gzkit may have added patterns from governance tooling experience (ADR/OBPI commands)

## NON-GOALS

- Rewriting the CLI doctrine from scratch
- Changing CLI design principles — this is about content completeness
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: exit codes, flag conventions, output contracts, help text, adding features
1. Document content present in airlineops but missing from gzkit
1. Document content present in gzkit but missing from airlineops (for awareness)
1. Record decision with rationale: Absorb / Confirm

## ALLOWED PATHS

- `.claude/rules/cli.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
