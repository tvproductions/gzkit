# SKILL.md

## gz implement

Run Gate 2 tests and record gate results.

## Trigger

When validating implementation progress before closeout.

## Behavior

Run uv run gz implement for target ADR and summarize Gate 2 result.

## Prerequisites

Tests are available and verification.test is valid.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Run implement for ADR-0.4.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
