---
id: OBPI-0.31.0-01-sloc-scan
parent: ADR-0.31.0-new-cli-command-absorption
item: 1
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-01: SLOC Scan

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-01 --- "Port sloc-scan (159 lines) --- radon-based SLOC analysis"`

## OBJECTIVE

Port opsdev's `sloc-scan` command (159 lines) to gzkit as `gz sloc-scan`. The command provides radon-based source lines of code analysis with per-module and aggregate reporting. It must be adapted to gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `sloc-scan` command implementation (159 lines)
- **gzkit equivalent:** None --- gzkit has no SLOC analysis capability

## ASSUMPTIONS

- SLOC analysis is governance-generic --- every project benefits from code size tracking
- radon is the underlying tool; gzkit wraps it with governance-standard output
- The command should support configurable thresholds for exit code determination
- Optional dependency: radon must be declared as an optional dependency in pyproject.toml

## NON-GOALS

- Replacing radon --- this is a wrapper, not a reimplementation
- Supporting languages beyond Python (radon is Python-only)
- Real-time monitoring --- this is a point-in-time scan

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
