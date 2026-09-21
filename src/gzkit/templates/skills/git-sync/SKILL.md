---
name: git-sync
persona: main-session
description: Run the guarded repository sync ritual; the hooks your pre-commit config declares enforce the quality gates.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
model: haiku
last_reviewed: 2026-04-19
metadata:
  skill-version: "1.2.2"
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
2. Execute the standard ritual:
   `uv run gz git-sync --apply`
3. Explicit redundant-gate invocation (edge cases only, e.g. verifying
   pre-commit config drift):
   `uv run gz git-sync --apply --lint --test`

> Read your own `.pre-commit-config.yaml` for which gates run at commit
> and which at push — gzkit ships no pre-commit config, so this skill
> cannot state your roster. gzkit's own convention is cheap gates at
> commit (ruff, ty, xenon) with the unit suite reached only at push,
> through a hook that runs `gz check`. `--lint` and `--test` re-run those
> gates at the `gz` level — redundant when the hooks already cover them,
> and multi-minute pain. Defaults are `False` to match that (airlineops
> parity evolution).

## Examples

### Example 1

**Input**: "git sync"

**Output**: Runs `uv run gz git-sync --apply` (or dry-run first if safety confirmation is needed). Pre-commit hook handles lint/test automatically.

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
- Lint or test failures bypassed instead of fixed
- Divergence resolved by reset/force instead of investigation
- Dry-run run without follow-through apply
- Sync run on a tree with uncommitted control-surface drift

> The hooks your `.pre-commit-config.yaml` declares are the mandatory
> gate; explicit `--lint --test` flags are redundant when those hooks
> already cover the ritual (see Steps § 3). Omitting them is not a red
> flag — skipping the hooks via `--no-verify` is.

## Related Skills

- `lint`
- `test`
- `format`
