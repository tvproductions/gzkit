# SKILL.md

## gz attest

Record human attestation with gate prerequisite enforcement.

## Trigger

When a human is ready to attest ADR completion, partial, or dropped outcome.

## Behavior

Run uv run gz attest with status and rationale options, then confirm ledger event.

## Prerequisites

Required gates have passed or force override is explicit.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Attest ADR-0.4.0 as completed.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
