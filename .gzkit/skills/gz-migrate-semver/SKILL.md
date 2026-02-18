---
name: gz-migrate-semver
description: Record semver identifier migration events. Use when applying canonical ADR or OBPI renaming migrations.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz migrate-semver

## Overview

Operate the gz migrate-semver command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz migrate-semver with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-migrate-semver to apply semver migration mappings..
