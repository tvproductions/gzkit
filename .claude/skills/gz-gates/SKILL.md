# SKILL.md

## gz gates

Run lane-required gates or a specific gate and record events.

## Trigger

When checking governance gate compliance for an ADR.

## Behavior

Run uv run gz gates with adr or gate options and report pass or fail per gate.

## Prerequisites

Target ADR is resolved and verification commands are configured.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Run Gate 3 for ADR-0.4.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
