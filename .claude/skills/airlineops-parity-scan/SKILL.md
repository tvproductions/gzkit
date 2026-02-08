# SKILL.md

## AirlineOps Parity Scan

Run a repeatable governance parity scan between `../airlineops` (canon) and gzkit (extraction).

## Trigger

- Weekly parity check cadence.
- Before promoting any pool ADR into active implementation.
- Any time a canonical GovZero skill/doc changes in AirlineOps.

## Behavior

Produce a dated parity report with explicit gaps, severity, and required ADR/OBPI follow-up.

## Prerequisites

- `../airlineops` exists and is readable.
- gzkit repo is initialized with `docs/` and `docs/design/`.
- Use canonical references in `docs/lodestar/govzero-doctrine.md`.

## Steps

1. Confirm both repos are present:
   `test -d ../airlineops && test -d .`
2. Read canonical source declarations:
   `docs/lodestar/govzero-doctrine.md`, `docs/lodestar/README.md`, `AGENTS.md`.
3. Compare canonical governance surfaces:
   - AirlineOps: `.github/skills/gz-*`, `docs/governance/GovZero/*`
   - gzkit: `.github/skills/*`, `docs/user/*`, `docs/design/*`
4. Classify each item as:
   - `Parity`
   - `Partial`
   - `Missing`
   - `Divergent`
5. Write a dated report:
   `docs/proposals/REPORT-airlineops-parity-YYYY-MM-DD.md`
   Use `docs/proposals/REPORT-TEMPLATE-airlineops-parity.md`.
6. For every `Missing` or `Divergent` finding:
   - Propose target SemVer minor
   - Identify parent ADR and OBPI linkage
   - Add an explicit next action
7. Summarize risk:
   - What blocks 1.0 readiness
   - What can wait
   - What must be done next cycle

## Examples

### Example 1

**Input**: "Run the weekly AirlineOps parity scan."

**Output**: `docs/proposals/REPORT-airlineops-parity-2026-02-07.md` with matrix, severity, and action list.

## Constraints

- Do not modify anything in `../airlineops`.
- Do not claim parity without path-level evidence.
- Do not use patch versions for new feature sequencing.
- Keep findings actionable: each gap must map to ADR/OBPI follow-up.

## Related Skills

- gz-adr-manager
- gz-adr-audit
