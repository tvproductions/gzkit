# gz chores list

List all chores declared in the chores registry (`registry.json`).

---

## Usage

```bash
gz chores list [--explain]
```

---

## Runtime Behavior

- Loads `registry.json` using the project-first → package-fallback resolver
  (ADR-0.0.21): `<project_root>/.gzkit/chores/registry.json` is consulted
  first, then `importlib.resources.files("gzkit.chores")` as the package
  fallback.
- Fails closed if the registry is missing or malformed in both surfaces.
- Prints one row per chore with `slug`, `lane`, step count, and title.
- `--explain` adds a resolution-source column labeling each row `project`,
  `package`, or `missing`.
- Validates each chore's class declaration (`class`, `rung`, `idempotent`,
  `staleness`, `remediation`, `nonAuthority`, `governingRule`; see
  `src/gzkit/chores/README.md`). A partial or malformed declaration fails
  closed with a `chores[<slug>].<field>` blocker; an absent one does not.
- After the table, announces how many chores carry no class declaration
  (GHI #999), e.g. `40 of 40 chores carry no class declaration (GHI #999).`

---

## Example

```bash
uv run gz chores list
```
