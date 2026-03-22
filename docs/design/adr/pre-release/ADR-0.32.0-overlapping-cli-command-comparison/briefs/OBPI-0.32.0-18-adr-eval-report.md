---
id: OBPI-0.32.0-18-adr-eval-report
parent_adr: ADR-0.32.0-overlapping-cli-command-comparison
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-18: adr-eval-report

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-18 -- "Compare adr eval/report -- opsdev adr_tools.py vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `adr eval` and `adr report` subcommands from adr_tools.py against gzkit's equivalents in cli.py. The eval command evaluates ADR readiness; the report command generates human-readable ADR status reports. Determine whether opsdev's implementations provide deeper evaluation criteria or better reporting.

## SOURCE MATERIAL

- **opsdev:** `adr_tools.py` -- eval/report subcommands
- **gzkit equivalent:** `cli.py` (adr eval/report sections)

## ASSUMPTIONS

- `adr report` is the primary status display command per governance rules
- `adr eval` assesses readiness for progression through governance stages
- Reporting quality directly impacts operator experience

## NON-GOALS

- Changing report output schema
- Adding new evaluation criteria without justification

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely for both subcommands
1. Document comparison per subcommand: eval criteria, report format, data completeness
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
