# SKILL.md

## gz closeout

Initiate ADR closeout with evidence context.

## Trigger

When preparing an ADR for attestation and audit sequence.

## Behavior

Run uv run gz closeout and verify closeout initiation event.

## Prerequisites

Target ADR and evidence surfaces exist.

## Steps

1. Confirm target context and IDs.
2. Run the command with the correct flags.
3. Report outcome and any follow-up actions.

## Examples

### Example 1

**Input**: Start closeout for ADR-0.4.0.

**Output**: Command executed and summarized with pass/fail details.

## Constraints

- Use uv run for command execution.
- Do not claim completion without checking command output.

## Related Skills

- gz-adr-create
- gz-adr-audit
