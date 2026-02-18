---
name: gz-check
description: Run full quality checks in one pass. Use for pre-merge or pre-attestation quality verification.
---

# gz check

## Overview

Operate the gz check command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz check with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-check to run all quality checks for the repository..
