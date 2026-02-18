---
name: gz-agent-sync
description: Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz agent sync control-surfaces

## Overview

Operate the gz agent sync control-surfaces command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz agent sync control-surfaces with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-agent-sync to sync control surfaces and mirrors..
