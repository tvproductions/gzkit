# SKILL.md

## gz adr emit-receipt

Emit ADR receipt events with optional scoped evidence.

## Trigger

When recording completed or validated accounting events or OBPI-scoped receipts.

## Behavior

Run uv run gz adr emit-receipt with event, attestor, and evidence JSON.

## Prerequisites

Target ADR exists and receipt intent is explicit.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Emit an OBPI-scoped completed receipt under ADR-0.4.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
