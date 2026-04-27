---
id: OBPI-0.31.0-02-complexity-check
parent: ADR-0.31.0-new-cli-command-absorption
item: 2
status: pending
lane: heavy
date: 2026-03-21
withdrawn_date: 2026-04-25
withdrawn_by: complexity-doctrine-cluster
withdrawn_reason: subsumed-by-ADR-0.0.29
---

# OBPI-0.31.0-02: Complexity Check (WITHDRAWN — subsumed by ADR-0.0.29)

> **Status:** WITHDRAWN on 2026-04-25 — subsumed by [ADR-0.0.29 (Complexity Advisor)](../../../foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md) and the broader four-ADR complexity-doctrine cluster (0.0.27 corpus / 0.0.28 thresholds / 0.0.29 advisor / 0.0.30 authoring-guidance).
>
> **Why withdrawn:** This OBPI was scoped as a literal port of opsdev's 122-line `complexity-check` wrapper around xenon. The complexity-doctrine cluster supersedes it with empirically-grounded doctrine (corpus → thresholds → advisor → authoring-guidance) and a proper `gz complexity-advise` CLI verb (ADR-0.0.29 OBPI-03) that auto-chains from xenon-as-gate failure rather than re-wrapping xenon. Re-implementing a thin xenon wrapper here would create a competing surface to the cluster and violate the single-canonical-home invariant ADR-0.0.28 codifies.
>
> **Replacement surfaces:**
> - Trigger-time complexity diagnosis: `gz complexity-advise` (ADR-0.0.29 OBPI-03)
> - Authoring-time complexity hints: `gz complexity-guide` (ADR-0.0.30 OBPI-01)
> - Xenon-as-gate enforcement: continues to live in the existing `complexity-reduction-xenon` chore, strengthened to consume ADR-0.0.28's `ThresholdTable` (separate work item)
>
> **Original brief content retained below for historical reference; do not implement.**

## ADR ITEM --- Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.31.0-new-cli-command-absorption/ADR-0.31.0-new-cli-command-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.31.0-02 --- "Port complexity-check (122 lines) --- xenon cyclomatic complexity"` → subsumed by ADR-0.0.29

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

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.31.0-02-01: Read the opsdev implementation completely
- [x] REQ-0.31.0-02-02: Port to gzkit with argparse, exit codes 0/1/2/3, --json/--plain output
- [x] REQ-0.31.0-02-03: Include help text with description, usage, options, and at least one example
- [x] REQ-0.31.0-02-04: Write unit tests with >= 40% coverage
- [x] REQ-0.31.0-02-05: Create manpage documentation


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

### Closing Argument

*To be authored at completion from delivered evidence.*
