---
id: OBPI-0.31.0-09-sync-manpage-docstrings
parent: ADR-0.31.0-new-cli-command-absorption
item: 9
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-09: Sync Manpage Docstrings

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-09 --- "Port sync-manpage-docstrings (473 lines) --- docstring synchronization"`

## OBJECTIVE

Port opsdev's `sync-manpage-docstrings` command (473 lines, shared with `validate-manpages`) to gzkit as `gz sync-manpage-docstrings`. The command synchronizes command module docstrings with their corresponding manpage documentation, ensuring single-source-of-truth for command descriptions. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `sync-manpage-docstrings` command implementation (473 lines shared with validate-manpages)
- **gzkit equivalent:** None --- gzkit has no docstring-to-manpage synchronization capability

## ASSUMPTIONS

- Docstring synchronization is governance-generic --- every CLI project benefits from consistent docs
- The command likely reads command module docstrings and updates manpage description sections (or vice versa)
- The sync direction (code-to-docs vs docs-to-code) must be clearly defined
- The command shares infrastructure with validate-manpages (OBPI-08)

## NON-GOALS

- Generating complete manpages from docstrings --- this syncs specific sections
- Replacing docstring conventions --- this enforces consistency, not format
- Bidirectional sync --- one direction must be authoritative

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation
1. Ensure integration with manpage validation infrastructure from OBPI-08

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.31.0-09-01: Read the opsdev implementation completely
- [x] REQ-0.31.0-09-02: Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
- [x] REQ-0.31.0-09-03: Include help text with description, usage, options, and at least one example
- [x] REQ-0.31.0-09-04: Write unit tests with >= 40% coverage
- [x] REQ-0.31.0-09-05: Create manpage documentation
- [x] REQ-0.31.0-09-06: Ensure integration with manpage validation infrastructure from OBPI-08


## ALLOWED PATHS

- `src/gzkit/commands/` --- target for ported command
- `tests/` --- tests for ported command
- `docs/user/manpages/` --- manpage documentation
- `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/` --- this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Manpage and help text complete
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
