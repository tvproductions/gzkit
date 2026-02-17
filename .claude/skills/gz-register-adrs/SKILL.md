---
name: gz-register-adrs
description: Register existing ADR files missing from ledger state. Use when reconciling on-disk ADRs with governance state.
---

# gz register-adrs

## Overview

Operate the gz register-adrs command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz register-adrs with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-register-adrs to register pool or full ADR sets..
