---
id: OBPI-0.32.0-08-tidy-clean
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-08: tidy-clean

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-08 -- "Compare tidy/clean -- opsdev clean_tools.py 57 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's `tidy/clean` command (clean_tools.py, 57 lines) against gzkit's equivalent in cli.py. The tidy/clean command removes build artifacts, caches, and temporary files. Determine whether opsdev's implementation handles additional artifact types, has safer deletion patterns, or provides better dry-run support.

## SOURCE MATERIAL

- **opsdev:** `clean_tools.py` (57 lines)
- **gzkit equivalent:** `cli.py` (tidy/clean section)

## ASSUMPTIONS

- Both implementations remove similar artifact types (__pycache__, .ruff_cache, etc.)
- Cross-platform safety (especially Windows) is critical for cleanup operations
- Dry-run support is important for destructive operations

## NON-GOALS

- Adding new artifact types to clean without justification
- Changing the tidy/clean command contract

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: artifact types, safety checks, dry-run, cross-platform handling
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
