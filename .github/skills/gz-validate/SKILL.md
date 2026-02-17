# SKILL.md

## gz validate

Validate governance artifacts and schemas.

## Trigger

When checking manifest, ledger, documents, or control-surface validity.

## Behavior

Run uv run gz validate with requested scopes and summarize violations.

## Prerequisites

Schemas and artifact roots are present.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Validate documents and ledger.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
