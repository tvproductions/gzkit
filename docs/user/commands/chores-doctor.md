# gz chores doctor

Re-scaffold missing or damaged canonical chores from the package source.
Project-local slugs and `proofs/` content are never modified.

---

## Usage

```bash
gz chores doctor
gz chores doctor --dry-run
gz chores doctor --json
```

---

## Runtime Behavior

- Enumerates canonical chore slugs from the `gzkit.chores` package and the
  project-local set under `.gzkit/chores/`.
- Classifies each slug as `MISSING`, `DAMAGED`, `HEALTHY`, or `PROJECT-LOCAL`.
- Repairs `MISSING` slugs by delegating to
  `scaffold_core_chores(skip_existing=True)`; repairs `DAMAGED` slugs by
  restoring missing or differing canonical files in
  `(CHORE.md, acceptance.json, README.md)` only.
- `proofs/` directories under `.gzkit/chores/<slug>/` are never touched.
- `PROJECT-LOCAL` slugs (in the project but absent from canonical) are
  reported and never modified.
- `--dry-run` reports what would be repaired without writing any file.
- `--json` emits one record per slug with `slug`, `before_status`, and
  `after_status` to stdout.

---

## Example

```bash
uv run gz chores doctor
uv run gz chores doctor --dry-run
uv run gz chores doctor --json
```
