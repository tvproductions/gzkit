# SKILL.md

## gz typecheck

Run static type checks with configured toolchain.

## Trigger

When validating type safety before merge or closeout.

## Behavior

Run uv run gz typecheck and report actionable failures.

## Prerequisites

Typechecker dependencies are available.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Run type checks.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
