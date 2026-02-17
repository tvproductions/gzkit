# SKILL.md

## gz agent sync control-surfaces

Sync AGENTS and CLAUDE control surfaces from governance canon.

## Trigger

When skills or control-surface content changes and mirrors must be regenerated.

## Behavior

Run uv run gz agent sync control-surfaces and confirm updated surfaces.

## Prerequisites

Manifest and config paths are valid.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Sync control surfaces after adding skills.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
