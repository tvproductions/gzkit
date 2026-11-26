---
name: git-sync
persona: main-session
description: Run the guarded repository sync ritual; the hooks your pre-commit config declares enforce the quality gates.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
model: haiku
last_reviewed: 2026-11-26
metadata:
  skill-version: "1.3.0"
---

# SKILL.md

## Git Sync

Run the repository sync ritual: stage, commit, fetch, rebase and push, with the
repository's hooks as the gates.

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

1. Preview: `uv run gz git-sync`. It runs `git fetch --prune <remote>`, prints
   the plan, and changes nothing and runs no gate.
2. Execute the command § Which command each moment uses names for your moment.

## What each flag runs

`gz git-sync --apply` runs these steps in order. The defaults are `--no-lint
--no-test --auto-add --push`, so `--apply` alone is the first column. Each other
column changes only the cells it fills; a dash means "as `--apply`". Flags
combine: `--apply --lint --test` runs both columns' cells, and so on for any
combination.

| Step | `--apply` | `--lint` | `--test` | `--no-auto-add` | `--no-push` |
|---|---|---|---|---|---|
| 1. Stage | on a dirty tree, `git add -A`; refused when it would stage a path under `src/` or `tests/`, which you commit yourself first | — | — | stages nothing | — |
| 2. Hook check | refuses when a hook your `.pre-commit-config.yaml` declares is not installed | — | — | — | — |
| 3. Pre-check | nothing | whole-tree `gz lint`; a failure blocks | the full unit suite (`gz test`); a failure blocks | — | — |
| 4. Commit | commits what is staged, under `chore: update <areas> (gz git-sync)`; your pre-commit-stage hooks run | — | — | — | — |
| 5. Rebase | when behind, `git pull --ff-only`; when diverged, `git pull --rebase` | — | — | — | — |
| 6. Push | when ahead, `git push`; your pre-push-stage hooks run | — | — | — | skipped, so no pre-push hook runs |
| 7. Post-check | nothing | whole-tree `gz lint` again; a failure warns and does not block | — | — | — |

Which gates run at steps 4 and 6 is whatever your `.pre-commit-config.yaml`
declares for its `pre-commit` and `pre-push` stages; gzkit ships no pre-commit
config, so this skill cannot state your roster. Read your config to know whether
`--lint` or `--test` repeats a hook or is the only run of that gate before the
push.

## Which command each moment uses

| Moment | Command | Prescribed by |
|---|---|---|
| Routine sync | `uv run gz git-sync --apply` | this skill |
| OBPI pipeline Stage 5, both syncs | `uv run gz git-sync --apply` | `gz-obpi-pipeline` |
| ADR closeout, both syncs | `uv run gz git-sync --apply` | `gz-adr-closeout-ceremony` |
| Release | `git add -A`, `uv run gz check --full`, then `uv run gz git-sync --apply`, then `gh release create` | `gz-patch-release` Step 4c |
| The full suite must pass before the push | `uv run gz git-sync --apply --lint --test` | this skill |
| Commit and rebase now, push later | `uv run gz git-sync --apply --no-push` | this skill |
| Commit only what you staged yourself | `uv run gz git-sync --apply --no-auto-add` | this skill |

No moment requires `--lint` or `--test`, and leaving them off is not a skipped
gate. Bypassing a hook with `--no-verify` is (§ Red Flags).

## Examples

### Example 1

**Input**: "git sync"

**Output**: Runs `uv run gz git-sync` to preview, then `uv run gz git-sync --apply`. Your hooks run at the commit and at the push (§ What each flag runs).

## Constraints

- Never use force push in this routine.
- Resolve blockers (divergence, lint/test failures) before retrying.
- Use `uv run` invocation style for project commands.

## Common Rationalizations

These thoughts mean STOP — you are about to push without the guards:

| Thought | Reality |
|---------|---------|
| "Force push, it's just my branch" | The constraint is explicit: never use force push in this routine. "Just my branch" still rewrites history and can desync local clones. Resolve divergence the long way. |
| "Lint is failing on something cosmetic — ship it" | The hooks' gates exist because cosmetic failures often hide real ones. The whole point of the ritual is that you don't get to triage at sync time. Fix or revert. |
| "Divergence with remote — just rebase and force" | Investigate first. Divergence may mean another agent or another machine pushed work you don't have. Force-pushing destroys it. |
| "Dry-run looks fine, no need to actually run --apply" | Dry-run shows the plan; apply executes it. Walking away after dry-run leaves the local tree out of sync, which the next session inherits. |
| "Pre-commit hook failed — `--no-verify` it" | Hooks are part of the contract. Skipping them with `--no-verify` removes the gates a sync runs (§ What each flag runs). Diagnose, don't bypass. |
| "I'll commit and sync separately" | The ritual includes the sync step deliberately. Committing without syncing leaves the branch behind on the remote, which is exactly the divergence trap. |

## Red Flags

- Force push appearing anywhere in the routine
- `--no-verify` used on the commit
- Lint or test failures bypassed instead of fixed
- Divergence resolved by reset/force instead of investigation
- Dry-run run without follow-through apply
- Sync run on a tree with uncommitted control-surface drift

> The hooks your `.pre-commit-config.yaml` declares are the mandatory gate
> (§ What each flag runs). Omitting `--lint` or `--test` is not a red flag;
> bypassing a hook with `--no-verify` is.

## Related Skills

- `gz-check`
