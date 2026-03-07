# gz chores audit

Audit chore log presence for one chore or all chores.

---

## Usage

```bash
gz chores audit --all
gz chores audit --slug <slug>
```

---

## Runtime Behavior

- Reads chore definitions from `config/gzkit.chores.json`.
- Checks whether each chore has a log file at the deterministic `CHORE-LOG.md` path.
- Prints a summary table with lane and log status.

---

## Example

```bash
uv run gz chores audit --all
```
