---
id: OBPI-0.31.0-03-test-times
parent: ADR-0.31.0-new-cli-command-absorption
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-03: Test Times

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-03 --- "Port test-times (87 lines) --- per-test duration tracking"`

## OBJECTIVE

Port opsdev's `test-times` command (87 lines) to gzkit as `gz test-times`. The command provides per-test duration tracking with sorting, threshold alerting, and trend analysis. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `test-times` command implementation (87 lines)
- **gzkit equivalent:** None --- gzkit has no per-test duration tracking capability

## ASSUMPTIONS

- Per-test duration tracking is governance-generic --- every project benefits from identifying slow tests
- The command likely wraps unittest/pytest timing output and provides structured analysis
- The command should support configurable duration thresholds for exit code determination
- No external dependencies expected beyond stdlib --- this is likely pure Python analysis

## NON-GOALS

- Replacing unittest's timing --- this is analysis on top of existing test output
- Historical trend storage --- this is a point-in-time analysis (trends may come later)
- Test parallelization --- this tracks durations, not execution strategy

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.31.0-03-01: Read the opsdev implementation completely
- [x] REQ-0.31.0-03-02: Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
- [x] REQ-0.31.0-03-03: Include help text with description, usage, options, and at least one example
- [x] REQ-0.31.0-03-04: Write unit tests with >= 40% coverage
- [x] REQ-0.31.0-03-05: Create manpage documentation


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
