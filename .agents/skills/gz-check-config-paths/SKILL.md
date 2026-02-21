---
name: gz-check-config-paths
description: Validate configured and manifest path coherence. Use when diagnosing control-surface or path drift.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz check-config-paths

## Overview

Operate the gz check-config-paths command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz check-config-paths with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-check-config-paths to validate config and manifest paths..
