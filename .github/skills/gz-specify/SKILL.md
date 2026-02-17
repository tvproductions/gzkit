# SKILL.md

## gz specify

Create OBPI briefs for scoped implementation items.

## Trigger

When breaking ADR work into OBPI units with explicit parent linkage.

## Behavior

Run uv run gz specify with parent and item context and verify brief placement.

## Prerequisites

Parent ADR exists and checklist item is known.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Create an OBPI for checklist item 3 under ADR-0.4.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
