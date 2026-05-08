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

- Reads chore definitions via the project-first → package-fallback resolver
  (ADR-0.0.21): `<project_root>/.gzkit/chores/registry.json` first, then
  `importlib.resources.files("gzkit.chores")` as the package fallback.
- Checks whether each chore has a log file at the deterministic
  `.gzkit/chores/<slug>/proofs/CHORE-LOG.md` path.
- Prints a summary table with lane and log status.

---

## Example

```bash
uv run gz chores audit --all
```
