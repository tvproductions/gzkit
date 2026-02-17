---
name: gz-plan
description: Create ADR artifacts for planned change. Use when recording architecture intent and lane-specific scope.
---

# gz plan

## Overview

Operate the gz plan command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz plan with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-plan to plan a new ADR with semver and lane options..
