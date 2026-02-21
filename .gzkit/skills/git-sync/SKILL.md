---
name: git-sync
description: Run the guarded repository sync ritual with lint/test gates.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-21
---

# SKILL.md

## Git Sync

Run the guarded repository sync ritual with lint/test gates.

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
2. Execute git-only sync when requested:
   `uv run gz git-sync --apply`
3. Execute full ritual with quality gates:
   `uv run gz git-sync --apply --lint --test`

## Examples

### Example 1

**Input**: "git sync"

**Output**: Runs `uv run gz git-sync --apply --lint --test` (or dry-run first if safety confirmation is needed).

## Constraints

- Never use force push in this routine.
- Resolve blockers (divergence, lint/test failures) before retrying.
- Use `uv run` invocation style for project commands.

## Related Skills

- `lint`
- `test`
- `format`
