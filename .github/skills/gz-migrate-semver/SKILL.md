# SKILL.md

## gz migrate-semver

Record semver ID rename migrations in governance state.

## Trigger

When migrating historical ADR and OBPI IDs to canonical naming.

## Behavior

Run uv run gz migrate-semver and verify migration events.

## Prerequisites

Migration mapping is defined and reviewed.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Apply semver ID migration.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
