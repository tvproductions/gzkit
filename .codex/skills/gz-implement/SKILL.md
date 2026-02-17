---
name: gz-implement
description: Run Gate 2 verification and record result events. Use when validating implementation progress for an ADR.
---

# gz implement

## Overview

Operate the gz implement command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz implement with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-implement to run Gate 2 implementation checks..
