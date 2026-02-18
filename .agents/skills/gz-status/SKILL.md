---
name: gz-status
description: Report gate and lifecycle status across ADRs. Use when checking blockers and next governance actions.
---

# gz status

## Overview

Operate the gz status command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz status with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-status to report current gate status and pending work..
