---
id: OBPI-0.31.0-06-metrics-report
parent: ADR-0.31.0-new-cli-command-absorption
item: 6
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-06: Metrics Report

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-06 --- "Port metrics report/watch (429 lines) --- continuous monitoring and reporting"`

## OBJECTIVE

Port opsdev's `metrics report` and `metrics watch` subcommands (429 lines shared with `metrics scan`) to gzkit as `gz metrics report` and `gz metrics watch`. The report subcommand provides aggregate quality metrics with trend comparison. The watch subcommand provides continuous file-system monitoring with automatic re-scanning. Both must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `metrics report` and `metrics watch` subcommand implementations (429 lines shared across metrics subcommands)
- **gzkit equivalent:** None --- gzkit has no continuous quality monitoring capability

## ASSUMPTIONS

- Quality reporting and continuous monitoring are governance-generic --- every project benefits from trend tracking
- The report/watch subcommands build on the scan infrastructure (OBPI-05)
- The watch subcommand likely uses filesystem events (watchdog or polling) for change detection
- Optional dependency: watchdog may be required for efficient file monitoring

## NON-GOALS

- Reimplementing file monitoring from scratch --- use established libraries
- Building a dashboard --- report produces structured output, visualization is separate
- Replacing CI/CD quality gates --- watch is for local development workflow

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port report and watch subcommands to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example per subcommand
1. Write unit tests with >= 40% coverage
1. Create manpage documentation
1. Ensure integration with scan infrastructure from OBPI-05

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.31.0-06-01: Read the opsdev implementation completely
- [x] REQ-0.31.0-06-02: Port report and watch subcommands to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
- [x] REQ-0.31.0-06-03: Include help text with description, usage, options, and at least one example per subcommand
- [x] REQ-0.31.0-06-04: Write unit tests with >= 40% coverage
- [x] REQ-0.31.0-06-05: Create manpage documentation
- [x] REQ-0.31.0-06-06: Ensure integration with scan infrastructure from OBPI-05


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
