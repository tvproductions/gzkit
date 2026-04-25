# gz chores plan

Show deterministic execution plan details for one chore.

---

## Usage

```bash
gz chores plan <slug>
```

---

## Runtime Behavior

- Loads and validates `registry.json` via the project-first → package-fallback
  resolver (ADR-0.0.21): `<project_root>/.gzkit/chores/registry.json` first,
  then `importlib.resources.files("gzkit.chores")` as the package fallback.
- Resolves `<slug>` and prints lane, steps, evidence commands, acceptance checks, and log path.
- Does not execute any command.

---

## Example

```bash
uv run gz chores plan quality-check
```
