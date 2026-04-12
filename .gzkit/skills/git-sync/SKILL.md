---
name: git-sync
persona: main-session
description: Run the guarded repository sync ritual with lint/test gates.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-12
metadata:
  skill-version: "1.1.1"
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

## Common Rationalizations

These thoughts mean STOP — you are about to push without the guards:

| Thought | Reality |
|---------|---------|
| "Force push, it's just my branch" | The constraint is explicit: never use force push in this routine. "Just my branch" still rewrites history and can desync local clones. Resolve divergence the long way. |
| "Lint is failing on something cosmetic — ship it" | The lint/test gates exist because cosmetic failures often hide real ones. The whole point of the ritual is that you don't get to triage at sync time. Fix or revert. |
| "I'll skip `--lint --test` to be quick" | The bare `--apply` exists for git-only operations. Skipping the quality gates on a code change is the failure mode the ritual was designed to prevent. |
| "Divergence with remote — just rebase and force" | Investigate first. Divergence may mean another agent or another machine pushed work you don't have. Force-pushing destroys it. |
| "Dry-run looks fine, no need to actually run --apply" | Dry-run shows the plan; apply executes it. Walking away after dry-run leaves the local tree out of sync, which the next session inherits. |
| "Pre-commit hook failed — `--no-verify` it" | Hooks are part of the contract. Skipping them with `--no-verify` is the same anti-pattern as skipping `--lint --test`. Diagnose, don't bypass. |
| "I'll commit and sync separately" | The ritual includes the sync step deliberately. Committing without syncing leaves the branch behind on the remote, which is exactly the divergence trap. |

## Red Flags

- Force push appearing anywhere in the routine
- `--no-verify` used on the commit
- `--apply` run without `--lint --test` on a code-bearing change
- Lint or test failures bypassed instead of fixed
- Divergence resolved by reset/force instead of investigation
- Dry-run run without follow-through apply
- Sync run on a tree with uncommitted control-surface drift

## Related Skills

- `lint`
- `test`
- `format`
