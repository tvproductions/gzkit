---
name: gz-validate
description: Validate governance artifacts against schema rules. Use when checking manifest, ledger, document, or surface validity.
---

# gz validate

## Overview

Operate the gz validate command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz validate with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-validate to run requested governance validations..
