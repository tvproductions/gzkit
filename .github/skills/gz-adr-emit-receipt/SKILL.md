---
name: gz-adr-emit-receipt
description: Emit ADR receipt events with scoped evidence payloads. Use when recording completed or validated accounting events.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz adr emit-receipt

## Overview

Operate the gz adr emit-receipt command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz adr emit-receipt with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-adr-emit-receipt to emit a receipt event with evidence JSON..
