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

---

## Examples

```bash
# Dry-run plan
gz git-sync

# Full ritual with guardrails
gz git-sync --apply --lint --test
```
