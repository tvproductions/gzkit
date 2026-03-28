---
id: OBPI-0.32.0-06-check-config-paths
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-06: check-config-paths

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-06 -- "Compare check-config-paths -- opsdev 321 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `check-config-paths` implementation (321 lines) against gzkit's equivalent in cli.py. At 321 lines, opsdev's implementation is substantial, suggesting it may validate multiple configuration sources, check path existence, verify schema compliance, or cross-reference manifest entries. Determine what gzkit's implementation covers and what it may be missing.

## SOURCE MATERIAL

- **opsdev:** check-config-paths implementation (321 lines)
- **gzkit equivalent:** `cli.py` (check-config-paths section)

## ASSUMPTIONS

- 321 lines suggests comprehensive config path validation beyond simple existence checks
- opsdev may validate against manifest schemas, check cross-references, or verify path conventions
- gzkit's cli.py implementation may be a simpler subset

## NON-GOALS

- Changing config path conventions
- Modifying manifest.json schema

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: validation scope, path types checked, error reporting, schema awareness
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementation is sufficient

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
