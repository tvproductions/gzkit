---
id: OBPI-0.32.0-17-adr-evidence-autolink-sync
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-17: adr-evidence-autolink-sync

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-17 -- "Compare adr evidence/autolink/sync/promote -- opsdev adr_tools.py vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's ADR lifecycle subcommands (`adr evidence`, `adr autolink`, `adr sync`, `adr promote`) from adr_tools.py against gzkit's equivalents in cli.py. These subcommands manage evidence linking, automatic cross-referencing, ADR synchronization, and promotion from pre-release to released. Determine whether opsdev's implementations offer superior lifecycle management.

## SOURCE MATERIAL

- **opsdev:** `adr_tools.py` -- evidence/autolink/sync/promote subcommands
- **gzkit equivalent:** `cli.py` (adr lifecycle subcommand sections)

## ASSUMPTIONS

- ADR lifecycle management is core governance functionality
- Autolink and sync are automation features that reduce manual governance burden
- Promote handles the pre-release to release transition

## NON-GOALS

- Changing ADR lifecycle state transitions
- Modifying the pre-release/release directory structure

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely for all four subcommands
1. Document comparison per subcommand: evidence, autolink, sync, promote
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
