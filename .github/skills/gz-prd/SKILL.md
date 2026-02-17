# SKILL.md

## gz prd

Create and record Product Requirements Documents.

## Trigger

When defining or updating product-level intent before ADR planning.

## Behavior

Run uv run gz prd with the requested identifier and verify file and ledger effects.

## Prerequisites

Governance project is initialized.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Create PRD-GZKIT-2.0.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
