# gz git-sync

Guarded git sync ritual for gzkit repositories.

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
| `--lint/--no-lint` | flag | Run `gz lint` before and after sync |
| `--test/--no-test` | flag | Run `gz test` before sync |
| `--auto-add/--no-auto-add` | flag | Auto stage changed files with `git add -A` |
| `--push/--no-push` | flag | Push if branch is ahead |
| `--json` | flag | Output JSON summary |

---

## What It Does

1. Validates git repo + branch state.
2. Plans sync actions (fetch, pull/rebase, push).
3. Optionally stages/commits local changes.
4. Runs lint/test guardrails when requested.
5. Executes sync operations when `--apply` is set.

The pull and push steps read `ahead`/`behind` **after** the ceremony's own
auto-commit, not from the plan computed before it. A dirty tree that is behind
the remote becomes diverged the moment that commit lands, so the ceremony
rebases rather than attempting a fast-forward that cannot succeed. The dry-run
plan projects the same post-commit shape, so the preview matches what `--apply`
runs (GHI #720).

For OBPI pipeline closeout in gzkit, this is the canonical guarded sync step:

- run `uv run gz git-sync --apply --lint --test` after attestation
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
[`.gzkit/rules/tests.md` § TASK-Driven Workflow](../../../.gzkit/rules/tests.md)
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

# Full ritual with guardrails
gz git-sync --apply --lint --test

# Governed work present — commit it first, then sync the ceremony surfaces
git commit -m 'fix(sync): <summary> (GHI #N)'
gz git-sync --apply --lint --test
```
