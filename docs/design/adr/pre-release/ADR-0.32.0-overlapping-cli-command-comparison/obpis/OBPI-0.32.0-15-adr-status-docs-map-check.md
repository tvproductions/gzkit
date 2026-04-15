---
id: OBPI-0.32.0-15-adr-status-docs-map-check
parent: ADR-0.32.0-overlapping-cli-command-comparison
item: 15
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.32.0-15: adr-status-docs-map-check

## ADR ITEM -- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.32.0-15 -- "Compare adr status/docs/map/check -- opsdev adr_tools.py 218 lines vs gzkit cli.py"`

## OBJECTIVE

Compare opsdev's ADR subcommands (`adr status`, `adr docs`, `adr map`, `adr check`) from adr_tools.py (218 lines) against gzkit's equivalents in cli.py. These subcommands provide ADR lifecycle management -- status display, documentation generation, dependency mapping, and validation checking. Determine whether opsdev's 218-line implementation offers deeper functionality.

## SOURCE MATERIAL

- **opsdev:** `adr_tools.py` (218 lines) -- status/docs/map/check subcommands
- **gzkit equivalent:** `cli.py` (adr subcommand sections)

## ASSUMPTIONS

- Multiple subcommands are bundled in this comparison for efficiency
- Each subcommand should be compared individually within the brief
- 218 lines across 4 subcommands is moderate; ~55 lines per subcommand

## NON-GOALS

- Adding new adr subcommands
- Changing ADR lifecycle state machine

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely for all four subcommands
1. Document comparison per subcommand: status, docs, map, check
1. Record decision with rationale: Absorb Improvements / Confirm Sufficient
1. If absorbing: adapt to gzkit conventions and write tests
1. If confirming: document why gzkit's implementations are sufficient

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.32.0-15-01: Read both implementations completely for all four subcommands
- [x] REQ-0.32.0-15-02: Document comparison per subcommand: status, docs, map, check
- [x] REQ-0.32.0-15-03: Record decision with rationale: Absorb Improvements / Confirm Sufficient
- [x] REQ-0.32.0-15-04: If absorbing: adapt to gzkit conventions and write tests
- [x] REQ-0.32.0-15-05: If confirming: document why gzkit's implementations are sufficient


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
