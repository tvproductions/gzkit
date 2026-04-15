---
id: OBPI-0.31.0-10-interrogate
parent: ADR-0.31.0-new-cli-command-absorption
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.31.0-10: Interrogate

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-10 --- "Port interrogate (wrapper) --- docstring coverage integration"`

## OBJECTIVE

Port opsdev's `interrogate` command wrapper to gzkit as `gz interrogate`. The command wraps the `interrogate` tool to provide docstring coverage analysis with governance-standard output. As a wrapper, this is the smallest command in the absorption set, but it must still follow gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples.

## SOURCE MATERIAL

- **opsdev:** `interrogate` command wrapper implementation
- **gzkit equivalent:** None --- gzkit has no docstring coverage capability

## ASSUMPTIONS

- Docstring coverage is governance-generic --- every project benefits from documentation completeness tracking
- interrogate is the underlying tool; gzkit wraps it with governance-standard output
- The wrapper likely adds configurable thresholds, structured JSON output, and exit code mapping
- Optional dependency: interrogate must be declared as an optional dependency in pyproject.toml

## NON-GOALS

- Replacing interrogate --- this is a wrapper, not a reimplementation
- Enforcing specific docstring formats --- interrogate checks presence, not style
- Supporting docstring coverage for non-Python files

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

- [x] REQ-0.31.0-10-01: Read the opsdev implementation completely
- [x] REQ-0.31.0-10-02: Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
- [x] REQ-0.31.0-10-03: Include help text with description, usage, options, and at least one example
- [x] REQ-0.31.0-10-04: Write unit tests with >= 40% coverage
- [x] REQ-0.31.0-10-05: Create manpage documentation


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
