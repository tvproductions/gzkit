---
name: gz-tidy
description: Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz tidy

## Overview

Operate the gz tidy command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz tidy with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-tidy to run tidy maintenance workflows..
