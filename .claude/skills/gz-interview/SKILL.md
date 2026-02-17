---
name: gz-interview
description: Run interactive governance interviews. Use when gathering structured inputs for governance artifacts.
---

# gz interview

## Overview

Operate the gz interview command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz interview with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-interview to run an interview flow for artifact capture..
