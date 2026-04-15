---
id: OBPI-0.31.0-08-validate-manpages
parent: ADR-0.31.0-new-cli-command-absorption
item: 8
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-08: Validate Manpages

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-08 --- "Port validate-manpages (473 lines) --- manpage structure validation"`

## OBJECTIVE

Port opsdev's `validate-manpages` command (473 lines, shared with `sync-manpage-docstrings`) to gzkit as `gz validate-manpages`. The command validates manpage structure: required sections, heading hierarchy, example completeness, cross-reference validity, and consistency with CLI help text. At 473 lines (shared), this represents substantial documentation governance logic. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `validate-manpages` command implementation (473 lines shared with sync-manpage-docstrings)
- **gzkit equivalent:** None --- gzkit has no manpage structure validation capability

## ASSUMPTIONS

- Manpage validation is governance-generic --- every gzkit-governed project with CLI commands needs validated manpages
- The command likely checks for required sections (NAME, SYNOPSIS, DESCRIPTION, EXAMPLES, EXIT CODES)
- Validation rules should be configurable to accommodate different manpage conventions
- The command shares infrastructure with sync-manpage-docstrings (OBPI-09)

## NON-GOALS

- Generating manpages from scratch --- this validates existing manpages
- Supporting non-Markdown manpage formats --- gzkit uses Markdown manpages
- Replacing human review of manpage content --- this validates structure, not prose quality

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation (meta: the command validates its own manpage)
1. Ensure shared infrastructure is reusable by OBPI-09 (sync-manpage-docstrings)

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.31.0-08-01: Read the opsdev implementation completely
- [x] REQ-0.31.0-08-02: Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
- [x] REQ-0.31.0-08-03: Include help text with description, usage, options, and at least one example
- [x] REQ-0.31.0-08-04: Write unit tests with >= 40% coverage
- [x] REQ-0.31.0-08-05: Create manpage documentation (meta: the command validates its own manpage)
- [x] REQ-0.31.0-08-06: Ensure shared infrastructure is reusable by OBPI-09 (sync-manpage-docstrings)


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
