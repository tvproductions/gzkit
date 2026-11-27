---
name: git-sync
persona: main-session
description: Run the guarded repository sync ritual; commit-time hooks enforce the cheap gates and the pre-push hook runs gz check.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
last_reviewed: 2026-11-08
metadata:
  skill-version: "1.6.8"
model: haiku
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

## Commit messages (binding)

Every commit's subject says what changed. Operator feedback: *"Every commit must
describe what actually changed."* It was moved into this skill from auto memory
on 2026-11-08 (operator: *"A: skill plus GHI"*). `gz git-sync` has no message
flag. When it commits staged work it writes the generic subject
`chore: update <areas> (gz git-sync)`, so commit the change yourself first, with
a descriptive subject and the trailers `gz validate --commit-trailers` requires,
and run `gz git-sync --apply` on a clean tree to fetch, rebase and push.
GHI #1313 tracks changing the generic default.

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
| 2. Merge driver | registers the append-only JSONL merge driver (§ Append-only JSONL conflicts) | — | — | — | — |
| 3. Stage | on a dirty tree, `git add -A`; refused when it would stage a path under `src/` or `tests/`, which you commit yourself first (the refusal fails open on a git error) | — | — | stages nothing, and the `src/`/`tests/` refusal does not run: whatever is already staged, governed work included, is committed at step 6 under the generic subject; when an unstaged or untracked change exists, or git cannot say, the run, dry or not, warns that it stays uncommitted | — |
| 4. Hook check | refuses when a gating hook type `.pre-commit-config.yaml` installs (such as `pre-commit` or `pre-push`) is not installed in the hooks directory (a `core.hooksPath` in the repository's own `.git/config` is honoured; a global or included one is not) or is not the pre-commit shim; a missing recording hook (`prepare-commit-msg`, `post-commit`) only warns. Nothing is checked and nothing refuses here when the config is missing, unreadable or declares no pre-push `gz check` hook, or in a linked worktree, where `.git` is a file | — | — | — | — |
| 5. Pre-check | nothing | whole-tree `gz lint`; a failure blocks | the full unit suite (`gz test`); a failure blocks | — | — |
| 6. Commit | when something is staged: refuses when `.git/COMMIT_EDITMSG` holds a stranded commit attempt; otherwise commits it, under `chore: update <areas> (gz git-sync)`, and the pre-commit-stage hooks run | — | — | — | — |
| 7. Rebase | when behind, `git pull --ff-only`; when diverged, `git pull --rebase` | — | — | — | — |
| 8. Push | when ahead, `git push`; the pre-push-stage hooks run | — | — | — | skipped, so no pre-push hook runs |
| 9. Post-check | nothing | whole-tree `gz lint` again, after the push or, under `--no-push`, after the rebase; a failure warns and does not block | — | — | — |

A blocker at any step stops every later step and exits 1, except step 2, which
runs under `--apply` whatever blocked, and step 4, which still runs its check
when `git add -A` itself fails (not when step 3 refuses) and adds any finding to
the report. Nothing already done is undone, so a tree
step 3 staged stays staged. `--lint` and `--test` call
`gz lint` and `gz test` directly rather than through a hook, so safe mode never
turns them off.

The other flags change no step: `--branch` names the branch to sync (default:
the current one, and step 0 refuses any other); `--remote` names the remote
(default `origin`); `--json` prints the same result as JSON; `--skill` prints
this skill's path and exits before step 0.

What the hooks run (the roster is `.pre-commit-config.yaml`; read it, not this list):

- **At the commit (step 6):** the cheap gates, such as ruff, ty, the complexity
  ceiling, the guards, gitleaks and authorship. No unit test runs: `unittest` is
  `stages: [manual]`.
- **At the push (step 8):** whole-tree `gz lint`, the closing-keyword check, and
  `gz check --reuse-verified`, which runs every validator and the tests the
  change touches.
- **In safe mode** (`.gzkit/mx.json` open, either level), most guards report an
  `[MX advisory]` line instead of blocking (`.gzkit/rules/mx-mode.md`);
  `gate5_invariants` still block. **At the drydock level,** in addition, every
  hook the config routes through `gzkit.mx.alarms` does not run: at the commit `validator-reachability-ratchet`
  and `ledger-vocabulary-inertness`, at the push `gz check`. The rest run,
  `gz lint` and the closing-keyword check at the push included.
- **After the push:** CI runs `gz check --full` on the pushed commit: the full
  unit suite, Behave and the docs build.

So `--lint` repeats the pre-push `gz lint`, earlier. Within the sync, `--test` is
the only run of the full unit suite before the push; without it, CI runs it
after. A release runs it itself, as `gz check --full` before the sync.

## Which command each moment uses

| Moment | Command | Prescribed by |
|---|---|---|
| Routine sync | `uv run gz git-sync --apply` | this skill |
| OBPI pipeline Stage 5, both syncs | `uv run gz git-sync --apply` | `gz-obpi-pipeline`, `references/stage-5-sync-and-account.md` |
| ADR closeout, both syncs | `uv run gz git-sync --apply` | `gz-adr-closeout-ceremony` |
| Release | `git add -A`, `uv run gz check --full`, commit the release yourself (`release: vX.Y.Z` with its `Task:` trailer), because the bump changes `src/gzkit/__init__.py`, which step 3 refuses to sweep, then `uv run gz git-sync --apply`, then, for a non-Foundation release, `gh release create` | `gz-patch-release` Step 4c |
| The full suite must pass before the push (CI unavailable, or checking that the hooks still cover the gates) | `uv run gz git-sync --apply --lint --test` | this skill |
| Commit and rebase now, push later | `uv run gz git-sync --apply --no-push` | this skill |
| Commit only what you staged yourself, when it is not `src/` or `tests/` work | `uv run gz git-sync --apply --no-auto-add` | this skill |

No moment requires `--lint` or `--test`, and leaving them off is not a skipped
gate. Bypassing a hook with `--no-verify` is (§ Red Flags).

## Examples

### Example 1

**Input**: "git sync"

**Output**: Runs `uv run gz git-sync` to preview, then `uv run gz git-sync --apply`. The pre-commit hooks run at the commit and the pre-push hooks at the push (§ What each flag runs).

## Append-only JSONL conflicts

The runtime appends to `.gzkit/ledger.jsonl` (and `agent-insights.jsonl`,
`corpus/*.jsonl`) during every session, so two clones in flight conflict over
disjoint tail additions. `uv run gz git-sync --apply` registers a git merge
driver — `uv run gz ledger merge-driver` — that reconciles them as a
**timestamp-ordered union**. Registration is idempotent and per-clone, because
git reads a driver command from local config, which cannot be committed.

**Never hand-edit `.gzkit/ledger.jsonl` to clear a conflict.** That is the
action `AGENTS.md` § Behavior Rules prohibits (the ledger is written only through `gz` commands), and the driver exists so you do not
have to. If the driver exits 1, a side did more than add rows — an ancestor row
was edited or removed, a row carries no sortable `ts`, or the ancestor was
already out of ts order — and it left the conflict for you deliberately. An
addition never lands there, wherever in the file it sits (GHI #1075). Resolve as
a timestamp-ordered union; never append one side to the other, which is what
git's built-in `merge=union` would do and why it is not used here (the ledger is
strictly ts-ordered — `gz validate --ledger`).

## Constraints

- Never use force push in this routine.
- Resolve blockers (divergence, lint/test failures) before retrying.
- Use `uv run` invocation style for project commands.

## Common Rationalizations

These thoughts mean STOP — you are about to skip the sync, or push without its guards:

| Thought | Reality |
|---------|---------|
| "Force push, it's just my branch" | The constraint is explicit: never use force push in this routine. "Just my branch" still rewrites history and can desync local clones. Resolve divergence the long way. |
| "Lint is failing on something cosmetic — ship it" | The hooks' gates exist because cosmetic failures often hide real ones. The whole point of the ritual is that you don't get to triage at sync time. Fix or revert. |
| "Divergence with remote — just rebase and force" | Investigate first. Divergence may mean another agent or another machine pushed work you don't have. Force-pushing destroys it. |
| "Dry-run looks fine, no need to actually run --apply" | Dry-run shows the plan; apply executes it. Walking away after dry-run leaves the local tree out of sync, which the next session inherits. |
| "Pre-commit hook failed — `--no-verify` it" | Hooks are part of the contract. Skipping them with `--no-verify` removes the only gates a sync runs (§ What each flag runs). Diagnose, don't bypass. |
| "I committed; the sync can wait" | Commit first with a descriptive subject (§ Commit messages), then run `gz git-sync --apply`. A commit left unpushed is work the remote lacks, and the branch diverges if the remote moves on before the push. |

## Red Flags

- Force push appearing anywhere in the routine
- `--no-verify` used on the commit
- Lint or test failures bypassed instead of fixed
- Divergence resolved by reset/force instead of investigation
- Dry-run run without follow-through apply
- Sync run on a tree with uncommitted control-surface drift

> The hooks are the mandatory gate (§ What each flag runs). Omitting `--lint`
> or `--test` is not a red flag; bypassing a hook with `--no-verify` is.

## Related Skills

- `gz-check`
