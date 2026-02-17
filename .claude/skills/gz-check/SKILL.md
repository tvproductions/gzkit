# SKILL.md

## gz check

Run all quality checks in one command.

## Trigger

When performing full pre-merge quality verification.

## Behavior

Run uv run gz check and summarize lint, format, type, and test results.

## Prerequisites

Project dependencies and test surfaces are available.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Run full quality check.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
