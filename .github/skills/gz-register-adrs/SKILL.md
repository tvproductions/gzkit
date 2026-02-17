# SKILL.md

## gz register-adrs

Register existing ADR files missing from ledger state.

## Trigger

When ADR files exist on disk but are absent from governance state.

## Behavior

Run uv run gz register-adrs with scope flags and confirm created events.

## Prerequisites

ADR files are discoverable in design roots.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Register pool ADRs only.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
