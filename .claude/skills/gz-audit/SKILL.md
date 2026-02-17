# SKILL.md

## gz audit

Run strict post-attestation audit reconciliation.

## Trigger

When attestation is complete and audit artifacts must be generated.

## Behavior

Run uv run gz audit for the target ADR and report findings and artifacts.

## Prerequisites

Attestation prerequisites are satisfied.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Run audit for ADR-0.4.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
