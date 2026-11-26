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
  skill-version: "1.3.1"
---

# SKILL.md

## Git Sync

Run the repository sync ritual: fetch, stage, commit, rebase and push, with the
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

1. Preview: `uv run gz git-sync`. It runs steps 0 and 1 of § What each flag
   runs and nothing else: it prints the plan and changes nothing, and `--lint`
   and `--test` run nothing without `--apply`. A fetch failure here warns and the
   plan uses cached refs (GHI #343); under `--apply` it blocks.
2. Execute the command § Which command each moment uses names for your moment.

## What each flag runs

`gz git-sync --apply` runs these steps in order (dry run: § Steps). The defaults are `--no-lint
--no-test --auto-add --push`, so `--apply` alone is the first column. Each other
column changes only the cells it fills; a dash means "as `--apply`". Flags
combine: `--apply --lint --test` runs both columns' cells, and so on for any
combination.

| Step | `--apply` | `--lint` | `--test` | `--no-auto-add` | `--no-push` |
|---|---|---|---|---|---|
| 0. Refusals | refuses when `SKIP` would bypass the complexity gates (before any other step), or when the current branch is not `--branch`, HEAD is a merge commit, or `git status` fails (then only step 2, a local git-config write, still runs) | — | — | — | — |
| 1. Fetch | `git fetch --prune <remote>`; a failure blocks | — | — | — | — |
| 2. Merge driver | registers gzkit's append-only JSONL merge driver in local git config | — | — | — | — |
| 3. Stage | on a dirty tree, `git add -A`; refused when it would stage a path under `src/` or `tests/`, which you commit yourself first | — | — | stages nothing, and the `src/`/`tests/` refusal does not run: whatever is already staged, governed work included, is committed at step 6 under the generic subject | — |
| 4. Hook check | refuses when a gating hook type your `.pre-commit-config.yaml` installs (such as `pre-commit` or `pre-push`) is not installed in the hooks directory (`core.hooksPath` is honoured) or is not the pre-commit shim; a missing recording hook (`prepare-commit-msg`, `post-commit`) only warns. When the config is missing, unreadable or declares no pre-push `gz check` hook, nothing is checked and nothing refuses here | — | — | — | — |
| 5. Pre-check | nothing | whole-tree `gz lint`; a failure blocks | the full unit suite (`gz test`); a failure blocks | — | — |
| 6. Commit | when something is staged: refuses when `.git/COMMIT_EDITMSG` holds a stranded commit attempt; otherwise commits it, under `chore: update <areas> (gz git-sync)`, and the pre-commit-stage hooks run | — | — | — | — |
| 7. Rebase | when behind, `git pull --ff-only`; when diverged, `git pull --rebase` | — | — | — | — |
| 8. Push | when ahead, `git push`; the pre-push-stage hooks run | — | — | — | skipped, so no pre-push hook runs |
| 9. Post-check | nothing | whole-tree `gz lint` again, after the push or, under `--no-push`, after the rebase; a failure warns and does not block | — | — | — |

A blocker at any step stops every later step and exits 1, except step 2, which
runs under `--apply` whatever blocked. Nothing already done is undone, so a tree
step 3 staged stays staged. `--lint` and `--test` call
`gz lint` and `gz test` directly rather than through a hook, so safe mode never
turns them off.

The other flags change no step: `--branch` names the branch to sync (default:
the current one, and step 0 refuses any other); `--remote` names the remote
(default `origin`); `--json` prints the same result as JSON; `--skill` prints
this skill's path and exits before step 0.

Which gates run at steps 6 and 8 is whatever your `.pre-commit-config.yaml`
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
| Release | `git add -A`, `uv run gz check --full`, commit the release yourself (`release: vX.Y.Z` with its `Task:` trailer: the bump stages `src/`), then `uv run gz git-sync --apply`, then, for a non-Foundation release, `gh release create` | `gz-patch-release` Step 4c |
| The full suite must pass before the push | `uv run gz git-sync --apply --lint --test` | this skill |
| Commit and rebase now, push later | `uv run gz git-sync --apply --no-push` | this skill |
| Commit only what you staged yourself, when it is not `src/` or `tests/` work | `uv run gz git-sync --apply --no-auto-add` | this skill |

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
