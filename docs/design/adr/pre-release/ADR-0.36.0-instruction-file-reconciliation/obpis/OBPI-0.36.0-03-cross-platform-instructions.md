---
id: OBPI-0.36.0-03-cross-platform-instructions
parent: ADR-0.36.0-instruction-file-reconciliation
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.36.0-03: cross-platform-instructions

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/ADR-0.36.0-instruction-file-reconciliation.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.36.0-03 — "Reconcile cross-platform.instructions.md vs .claude/rules/cross-platform.md"`

## OBJECTIVE

Compare airlineops's `cross-platform.instructions.md` against gzkit's `.claude/rules/cross-platform.md` to identify content gaps. Both files govern cross-platform development: pathlib.Path, UTF-8 encoding, temp file handling, subprocess patterns, and line endings. Determine: Absorb or Confirm.

## SOURCE MATERIAL

- **airlineops:** `.github/instructions/cross-platform.instructions.md`
- **gzkit equivalent:** `.claude/rules/cross-platform.md`

## ASSUMPTIONS

- Both files enforce the same core patterns: pathlib, UTF-8, context managers, list-form subprocess
- airlineops may have additional cross-platform patterns from Windows deployment experience
- gzkit's policy may need updates from airlineops's battle-tested patterns

## NON-GOALS

- Changing the cross-platform strategy (Windows primary, macOS, Linux)
- Adding platform-specific workarounds
- Modifying airlineops's instruction file

## REQUIREMENTS (FAIL-CLOSED)

1. Read both files completely
1. Create a section-by-section comparison: paths, encoding, temp files, subprocess, line endings
1. Document content gaps in either direction
1. Record decision with rationale: Absorb / Confirm

## ALLOWED PATHS

- `.claude/rules/cross-platform.md` — target for reconciled content
- `docs/design/adr/pre-release/ADR-0.36.0-instruction-file-reconciliation/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
