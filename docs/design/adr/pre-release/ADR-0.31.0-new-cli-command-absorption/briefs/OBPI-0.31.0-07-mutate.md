---
id: OBPI-0.31.0-07-mutate
parent_adr: ADR-0.31.0-new-cli-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-07: Mutate

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-07 --- "Port mutate (450 lines) --- Cosmic Ray mutation testing"`

## OBJECTIVE

Port opsdev's `mutate` command (450 lines) to gzkit as `gz mutate`. The command provides Cosmic Ray-based mutation testing with configurable operator sets, survival analysis, and structured reporting. At 450 lines, this is a substantial command that likely includes session management, result analysis, and threshold enforcement. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `mutate` command implementation (450 lines)
- **gzkit equivalent:** None --- gzkit has no mutation testing capability

## ASSUMPTIONS

- Mutation testing is governance-generic --- every project benefits from test effectiveness validation
- Cosmic Ray is the underlying tool; gzkit wraps it with governance-standard output
- The command should support configurable survival thresholds for exit code determination
- Optional dependency: cosmic-ray must be declared as an optional dependency in pyproject.toml
- At 450 lines, the command likely manages mutation sessions, analyzes survivors, and reports results

## NON-GOALS

- Replacing Cosmic Ray --- this is a wrapper, not a reimplementation
- Supporting mutation testing frameworks beyond Cosmic Ray
- Implementing custom mutation operators --- use Cosmic Ray's built-in operators

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation
1. Preserve session management and survival analysis from the original implementation

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
