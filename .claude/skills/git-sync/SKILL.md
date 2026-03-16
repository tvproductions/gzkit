---
name: git-sync
description: Run the guarded repository sync ritual. Lint/test gates run via pre-commit hooks.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-21
---

# SKILL.md

## Git Sync

Run the guarded repository sync ritual. Lint and test gates are enforced by pre-commit hooks, so `--lint --test` flags are redundant.

## Trigger

- User asks to "git sync" or "push with guards"
- End-of-task reconciliation before handoff
- Branch drift recovery after remote updates

## Behavior

Use the `gz git-sync` command flow (dry-run first, then apply as requested).

## Prerequisites

- Repository is initialized with `gz init`
- Current directory is a git worktree

## Steps

1. Preview planned actions:
   `uv run gz git-sync`
2. Execute sync:
   `uv run gz git-sync --apply`

## Examples

### Example 1

**Input**: "git sync"

**Output**: Runs `uv run gz git-sync --apply` (or dry-run first if safety confirmation is needed).

## Constraints

- Never use force push in this routine.
- Resolve blockers (divergence, lint/test failures) before retrying.
- Use `uv run` invocation style for project commands.

## Related Skills

- `lint`
- `test`
- `format`
