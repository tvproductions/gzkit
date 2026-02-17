# SKILL.md

## gz cli audit

Audit CLI docs and manpage coverage for command surfaces.

## Trigger

When validating command documentation coverage and heading consistency.

## Behavior

Run uv run gz cli audit and report missing or mismatched command docs.

## Prerequisites

Command docs index and pages are present.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Audit CLI docs coverage.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
