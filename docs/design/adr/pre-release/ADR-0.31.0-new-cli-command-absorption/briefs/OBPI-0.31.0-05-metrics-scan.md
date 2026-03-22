---
id: OBPI-0.31.0-05-metrics-scan
parent_adr: ADR-0.31.0-new-cli-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-05: Metrics Scan

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-05 --- "Port metrics scan (429 lines) --- code quality violation scanning"`

## OBJECTIVE

Port opsdev's `metrics scan` subcommand (429 lines, shared with `metrics report/watch`) to gzkit as `gz metrics scan`. The command provides code quality violation scanning with configurable rule sets, severity classification, and structured violation reporting. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `metrics scan` subcommand implementation (429 lines shared across metrics subcommands)
- **gzkit equivalent:** None --- gzkit has no code quality violation scanning capability

## ASSUMPTIONS

- Code quality violation scanning is governance-generic --- every project benefits from automated quality checks
- The metrics module likely has shared infrastructure between scan/report/watch subcommands
- The scan subcommand is the foundation; report and watch (OBPI-06) build on its output
- The command should support configurable rule sets and severity thresholds

## NON-GOALS

- Reimplementing quality rules from scratch --- port the existing rule definitions
- Replacing ruff/linting --- metrics scan provides higher-level quality metrics, not syntax-level linting
- Real-time monitoring --- scan is point-in-time (watch is covered in OBPI-06)

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port the scan subcommand to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation
1. Ensure shared infrastructure is reusable by OBPI-06 (metrics report/watch)

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
