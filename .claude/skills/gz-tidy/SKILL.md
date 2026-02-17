# SKILL.md

## gz tidy

Run maintenance checks and cleanup routines.

## Trigger

When performing repository hygiene or governance maintenance operations.

## Behavior

Run uv run gz tidy with requested flags and summarize changes and findings.

## Prerequisites

Repository is initialized with governance config.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Run tidy maintenance checks.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
