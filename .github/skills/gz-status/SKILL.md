# SKILL.md

## gz status

Report gate and lifecycle status across ADRs.

## Trigger

When checking pending gates, completion state, and closeout progress.

## Behavior

Run uv run gz status and extract blockers and next required gates.

## Prerequisites

Governance ledger exists.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Show current gate status.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
