# SKILL.md

## gz plan

Create ADR artifacts for planned changes.

## Trigger

When capturing architecture intent and checklist scope for a new change.

## Behavior

Run uv run gz plan with semver and lane options and validate ADR creation.

## Prerequisites

PRD and parent context is established.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Plan ADR 0.4.0 in heavy lane.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
