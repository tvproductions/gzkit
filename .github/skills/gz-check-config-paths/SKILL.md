# SKILL.md

## gz check-config-paths

Validate config and manifest path coherence.

## Trigger

When config or manifest path issues are suspected.

## Behavior

Run uv run gz check-config-paths and report mismatches.

## Prerequisites

Repository is initialized with config and manifest.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Check config path coherence.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
