---
name: gz-agent-sync
description: Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-21
---

# gz agent sync control-surfaces

## Overview

Operate the gz agent sync control-surfaces command surface as a reusable governance workflow.

## Workflow

1. Confirm target context, IDs, and lane assumptions.
2. Run `uv run gz agent sync control-surfaces` (or `--dry-run` first when staging changes).
3. If sync preflight fails, repair canonical `.gzkit/skills` state before retrying.
4. If sync reports stale mirror-only paths, follow manual recovery:
   - `uv run gz skill audit --json`
   - remove stale mirror-only paths listed by sync
   - `uv run gz agent sync control-surfaces`
   - `uv run gz skill audit`
5. Summarize deterministic output, recovery actions, and follow-up gates.

## Validation

- Verify command output reflects the requested scope.
- If governance state changed, confirm with uv run gz status or uv run gz state.

## Example

Use $gz-agent-sync to sync control surfaces and mirrors..
