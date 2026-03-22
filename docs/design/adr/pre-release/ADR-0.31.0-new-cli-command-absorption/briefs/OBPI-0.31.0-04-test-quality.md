---
id: OBPI-0.31.0-04-test-quality
parent_adr: ADR-0.31.0-new-cli-command-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-04: Test Quality

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-04 --- "Port test-quality (495 lines) --- AST-based test quality metrics"`

## OBJECTIVE

Port opsdev's `test-quality` command (495 lines) to gzkit as `gz test-quality`. The command provides AST-based test quality analysis: assertion density, test-to-code ratio, test naming conventions, mock usage patterns, and test isolation metrics. At 495 lines, this is the second-largest command in the absorption set and requires careful porting. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `test-quality` command implementation (495 lines)
- **gzkit equivalent:** None --- gzkit has no AST-based test quality metrics capability

## ASSUMPTIONS

- AST-based test quality analysis is governance-generic --- every project benefits from test quality metrics
- The command uses Python's `ast` module for analysis --- no external dependencies for parsing
- At 495 lines, the command likely has multiple analysis modes that should be preserved
- The command should support configurable quality thresholds for exit code determination

## NON-GOALS

- Reimplementing AST analysis from scratch --- port the existing analysis logic
- Supporting test frameworks beyond unittest --- gzkit's test policy mandates unittest
- Replacing manual code review --- metrics complement, not replace, human judgment

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev implementation completely
1. Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
1. Include help text with description, usage, options, and at least one example
1. Write unit tests with >= 40% coverage
1. Create manpage documentation
1. Preserve all analysis modes from the original 495-line implementation

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
