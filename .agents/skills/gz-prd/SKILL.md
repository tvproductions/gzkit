---
name: gz-prd
description: Create product requirement artifacts. Use when defining or revising project-level intent before ADR planning.
---

# gz prd

## Overview

Operate the gz prd command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz prd with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-prd to create a PRD with the requested identifier..
