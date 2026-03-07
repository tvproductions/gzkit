# gz chores run

Execute one chore and append a dated log entry.

---

## Usage

```bash
gz chores run <slug>
```

---

## Runtime Behavior

- Executes only `steps[*].argv` arrays declared in `config/gzkit.chores.json`.
- Refuses shell-string command definitions (`command`) to keep execution deterministic.
- Writes a dated entry to:
  `docs/design/briefs/chores/CHORE-<slug>/logs/CHORE-LOG.md`
  when the active `design_root` is `docs/design`.
- Returns non-zero on command failure, timeout, or missing executable.

---

## Example

```bash
uv run gz chores run quality-check
```
