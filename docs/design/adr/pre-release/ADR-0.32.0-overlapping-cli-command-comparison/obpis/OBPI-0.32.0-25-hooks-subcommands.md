---
id: OBPI-0.32.0-25-hooks-subcommands
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 25
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-25: hooks-subcommands

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-25 -- "Compare hooks subcommands -- opsdev hooks_tools.py 81 lines vs gzkit hooks/"`

## OBJECTIVE

Compare opsdev's hooks subcommands (hooks_tools.py, 81 lines) against gzkit's `hooks/` module. opsdev manages hooks through a CLI tools module; gzkit has a dedicated hooks package with multiple modules. Determine whether opsdev's CLI surface for hook management offers capabilities that gzkit's architecture does not expose through its CLI.

## SOURCE MATERIAL

- **opsdev:** `hooks_tools.py` (81 lines)
- **gzkit equivalent:** `hooks/` package (multiple modules)

## ASSUMPTIONS

- gzkit's hooks/ package is architecturally more sophisticated (dedicated package vs single file)
- opsdev's CLI surface may expose hook management operations gzkit does not
- The comparison is about CLI surface, not hook execution infrastructure (which ADR-0.34.0 covers)

## NON-GOALS

- Duplicating ADR-0.34.0's hook implementation comparison
- Changing hook execution architecture

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: CLI subcommands, hook management operations, listing, validation
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's hooks CLI surface is sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.32.0-25-01: Read both implementations completely
- [x] REQ-0.32.0-25-02: Document comparison: CLI subcommands, hook management operations, listing, validation
- [x] REQ-0.32.0-25-03: Record decision with rationale: Absorb Improvements / Confirm Sufficient
- [x] REQ-0.32.0-25-04: If absorbing: adapt to gzkit conventions and write tests
- [x] REQ-0.32.0-25-05: If confirming: document why gzkit's hooks CLI surface is sufficient


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
