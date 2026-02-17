---
name: gz-closeout
description: Initiate ADR closeout with evidence context. Use when preparing an ADR for attestation and audit steps.
---

# gz closeout

## Overview

Operate the gz closeout command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz closeout with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-closeout to start ADR closeout preparation..
