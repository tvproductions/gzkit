# SKILL.md

## gz init

Initialize gzkit in a repository with governance scaffolding.

## Trigger

When bootstrapping a new repository or reinitializing governance scaffolding.

## Behavior

Run uv run gz init with the requested mode and flags and summarize created surfaces.

## Prerequisites

Run in the target repository root.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Initialize this repo with heavy mode.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
