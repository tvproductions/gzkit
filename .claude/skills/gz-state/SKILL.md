# SKILL.md

## gz state

Query artifact graph state and lineage relationships.

## Trigger

When reporting readiness, parent linkage, or artifact inventory.

## Behavior

Run uv run gz state and summarize results.

## Prerequisites

Governance ledger exists.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Show current artifact graph as JSON.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
