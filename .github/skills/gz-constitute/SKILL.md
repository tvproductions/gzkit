---
name: gz-constitute
description: Create constitution artifacts. Use when governance constitutions must be created or refreshed.
---

# gz constitute

## Overview

Operate the gz constitute command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz constitute with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-constitute to create a constitution document for this project..
