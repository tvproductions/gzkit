---
name: gz-status
description: Report gate and lifecycle status across ADRs. Use when checking blockers and next governance actions.
category: governance-infrastructure
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-06-07
metadata:
  skill-version: "1.1.0"
model: haiku
---

# gz status

## Overview

Operate the gz status command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run `uv run gz status` with the required options.
3. For a focused single-OBPI runtime view, run `uv run gz obpi status <id>` to
   inspect one brief's lifecycle state, gate completion, and lock status.
4. Summarize results, including evidence and any follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with `uv run gz status` or `uv run gz state`.

## Example

```bash
# ADR-level gate status summary
uv run gz status

# Focused single-OBPI view (runtime state, gates, locks)
uv run gz obpi status OBPI-0.0.67-02-wire-orphan-verbs-into-skills
```
