---
id: OBPI-0.32.0-16-adr-recon-audit-receipt
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-16: adr-recon-audit-receipt

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-16 -- "Compare adr recon/audit-check/emit-receipt -- opsdev adr_evidence_audit.py vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's ADR evidence subcommands (`adr recon`, `adr audit-check`, `adr emit-receipt`) from adr_evidence_audit.py against gzkit's equivalents in cli.py. These subcommands handle evidence reconnaissance, audit verification, and receipt emission -- critical governance operations. Determine whether opsdev's implementations are more thorough.

## SOURCE MATERIAL

- **opsdev:** `adr_evidence_audit.py` -- recon/audit-check/emit-receipt subcommands
- **gzkit equivalent:** `cli.py` (adr evidence subcommand sections)

## ASSUMPTIONS

- Evidence handling is governance-critical; thoroughness matters
- opsdev's adr_evidence_audit.py is 453 lines total (shared with OBPI-12 audit comparison)
- Receipt emission must produce valid schema-compliant JSON

## NON-GOALS

- Changing receipt schema format
- Modifying evidence validation criteria

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely for all three subcommands
1. Document comparison per subcommand: recon, audit-check, emit-receipt
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementations are sufficient

## ALLOWED PATHS

- `src/gzkit/` -- target for absorbed improvements
- `tests/` -- tests for absorbed improvements
- `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/` -- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Comparison rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
