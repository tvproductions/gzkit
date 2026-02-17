---
name: gz-gates
description: Run lane-required gates or specific gate checks. Use when verifying governance gate compliance for an ADR.
---

# gz gates

## Overview

Operate the gz gates command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz gates with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-gates to run required gates for an ADR..
