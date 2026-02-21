---
name: gz-state
description: Query artifact relationships and readiness state. Use when reporting lineage or artifact graph status.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz state

## Overview

Operate the gz state command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz state with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-state to show current artifact graph state..
