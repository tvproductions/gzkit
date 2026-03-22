---
id: OBPI-0.31.0-02-complexity-check
parent_adr: ADR-0.31.0-new-cli-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-02: Complexity Check

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-02 --- "Port complexity-check (122 lines) --- xenon cyclomatic complexity"`

## OBJECTIVE

Port opsdev's `complexity-check` command (122 lines) to gzkit as `gz complexity-check`. The command provides xenon-based cyclomatic complexity checking with configurable thresholds and per-module violation reporting. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `complexity-check` command implementation (122 lines)
- **gzkit equivalent:** None --- gzkit has no cyclomatic complexity checking capability

## ASSUMPTIONS

- Cyclomatic complexity checking is governance-generic --- every project benefits from complexity monitoring
- xenon is the underlying tool; gzkit wraps it with governance-standard output
- The command should support configurable thresholds (A/B/C grades) for exit code determination
- Optional dependency: xenon must be declared as an optional dependency in pyproject.toml

## NON-GOALS

- Replacing xenon --- this is a wrapper, not a reimplementation
- Supporting complexity metrics beyond cyclomatic (e.g., cognitive complexity)
- Real-time monitoring --- this is a point-in-time check

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation

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
