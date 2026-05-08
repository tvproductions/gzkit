# gz chores propose-ghi

File GitHub issues for unfiled cluster proposal records from a chore's `proofs/` directory.

---

## Usage

```bash
gz chores propose-ghi <slug>
```

---

## Runtime Behavior

- Reads `proposal-*.json` files from `.gzkit/chores/<slug>/proofs/`.
- In TTY mode, prompts `PROPOSE/skip` for each unfiled record and calls
  `gh issue create` on confirmation.
- In headless mode, marks records `advisory=true` without filing.
- Already-filed records (where `filed: true`) are skipped on re-run.
- Requires `gh` CLI available in `$PATH` for issue creation.

**TTY gating.** Detects `sys.stdin.isatty() and sys.stdout.isatty()` before
prompting. Non-interactive (CI) environments receive advisory-only output and
no GHI is created.

---

## Example

```bash
uv run gz chores propose-ghi eval-feedback-cluster
```
