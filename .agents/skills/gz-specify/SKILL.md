---
name: gz-specify
description: Create OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz specify

## Overview

Operate the gz specify command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz specify with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-specify to create an OBPI brief for a specific parent and checklist item..
