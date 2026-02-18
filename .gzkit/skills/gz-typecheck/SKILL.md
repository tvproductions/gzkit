---
name: gz-typecheck
description: Run static type checks. Use when verifying type safety before merge or attestation.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz typecheck

## Overview

Operate the gz typecheck command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run uv run gz typecheck with the required options.
3. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-typecheck to run type checks and report failures..
