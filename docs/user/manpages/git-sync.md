# gz git-sync

Sync ritual for gzkit repositories: fetch, stage, commit, rebase and push, with
the repository's hooks as the gates.

---

## Usage

```bash
gz git-sync [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--branch` | string | Branch to sync (defaults to current branch) |
| `--remote` | string | Remote name (default: `origin`) |
| `--apply` | flag | Execute actions (dry-run by default) |
| `--lint/--no-lint` | flag | `--lint` runs whole-tree `gz lint` before the commit (a failure blocks) and again at the end (a failure warns). Default `--no-lint` |
| `--test/--no-test` | flag | `--test` runs the full unit suite (`gz test`) before the commit; a failure blocks. No hook runs the full suite; without it, CI runs it after the push. Default `--no-test` |
| `--auto-add/--no-auto-add` | flag | `--auto-add` (default) stages every change with `git add -A`, refused when it would stage `src/` or `tests/`; `--no-auto-add` stages nothing and commits whatever is already staged, with no `src/`/`tests/` refusal |
| `--push/--no-push` | flag | `--push` (default) pushes when the branch is ahead; `--no-push` commits and rebases but does not push, so no pre-push hook runs |
| `--json` | flag | Output JSON summary |
| `--skill` | flag | Print the paired skill file's path and exit, before any check |

---

## What It Does

Without `--apply`, it runs the refusals and the fetch, prints the plan, and
changes nothing; `--lint` and `--test` run nothing. With `--apply` it runs, in
order:

0. **Refusals:** `SKIP` that would bypass the complexity gates, a current branch
   other than `--branch`, a merge commit at HEAD, or a failing `git status`.
1. **Fetch:** `git fetch --prune <remote>`; under `--apply` a failure blocks.
2. **Merge driver:** registers the append-only JSONL merge driver.
3. **Stage:** `git add -A` on a dirty tree (skipped by `--no-auto-add`).
4. **Hook check:** refuses when a gating hook type the config installs is not
   installed or is not the pre-commit shim; a missing recording hook only warns.
   A missing or unreadable config, one with no pre-push `gz check` hook, and a
   linked worktree are not checked here.
5. **Pre-check:** `--lint` runs whole-tree `gz lint`; `--test` runs the full unit
   suite. Neither runs by default.
6. **Commit:** when something is staged, refuses on a stranded
   `.git/COMMIT_EDITMSG`; otherwise commits it, and the pre-commit hooks run.
7. **Rebase:** `git pull --ff-only` when behind, `git pull --rebase` when
   diverged.
8. **Push:** `git push` when ahead (skipped by `--no-push`); the pre-push hooks
   run.
9. **Post-check:** `--lint` runs whole-tree `gz lint` again; a failure warns.

A blocker stops every later step and exits `1`, except step 2, which runs under
`--apply` whatever blocked. Nothing already done is undone.
The flags are independent, so any combination runs the union of their steps.
The git-sync skill (`.gzkit/skills/git-sync/SKILL.md`) states each step in full,
what each hook stage runs, and which command each moment (routine, OBPI Stage 5,
ADR closeout, release) uses.

The pull and push steps read `ahead`/`behind` **after** the ceremony's own
auto-commit, not from the plan computed before it. A dirty tree that is behind
the remote becomes diverged the moment that commit lands, so the ceremony
rebases rather than attempting a fast-forward that cannot succeed. The dry-run
plan projects the same post-commit shape, so the preview matches what `--apply`
runs (GHI #720).

For OBPI pipeline closeout in gzkit, this is the canonical sync step:

- run `uv run gz git-sync --apply` after attestation
- then emit the final completed OBPI receipt/accounting
- then update brief/ADR reconciliation artifacts

This ordering prevents completion receipts from being anchored to an obviously
unsynced repository state.

---

## Governed-scope sweep guard

The ceremony commits under an auto-generated `chore: … (gz git-sync)` subject
carrying `Task: TASK-gz-git-sync`. That attribution is correct for what the
ceremony produces — generated mirrors, `.gzkit/` state, the ledger — and wrong
for `src/**` / `tests/**` work, which
[`.gzkit/rules/tests.md` § TASK-Driven Workflow](https://github.com/tvproductions/gzkit/blob/main/.gzkit/rules/tests.md)
scopes a real `Task:` trailer to.

So before `git add -A`, sync reads the three sets that sweep would stage — the
index, tracked-but-unstaged changes, and untracked files — and **refuses** if any
path lands in `src/` or `tests/`. Scope is exactly those two roots: guarding the
generated surfaces would disarm the verb rather than defend it. The guard fails
**open** on a git error, so an unreadable worktree never strands a sync.

Recovery is what the message says: commit the governed work under its own typed
subject, then re-run sync.

```console
$ uv run gz git-sync --apply
Git sync execution
  Branch: main
  Remote: origin
  ahead=0 behind=0 diverged=False dirty=True
  Actions:
    - git add -A
    - git fetch --prune origin
    - git push origin main
  Blockers:
    - Refusing `git add -A`: the sweep would stage changes in trailer-governed
scope:
    src/gzkit/commands/sync.py
    tests/commands/test_sync_sweep_guard.py
...
Next step: commit the governed work under its own message — `git commit -m
'fix(<scope>): <summary> (GHI #N)'` with a `Task:` trailer, confirming it
succeeded — then re-run `gz git-sync --apply`.
```

Exit code `1`; nothing is staged, committed, or pushed.

---

## Examples

```bash
# Dry-run plan
gz git-sync

# Routine sync, OBPI Stage 5 and ADR closeout
gz git-sync --apply

# Full unit suite and lint before the push, as well as the hooks
gz git-sync --apply --lint --test

# Commit and rebase now, push later
gz git-sync --apply --no-push

# Governed work present — commit it first, then sync the ceremony surfaces
git commit -m 'fix(sync): <summary> (GHI #N)'
gz git-sync --apply
```
