# gz chores plan

Show deterministic execution plan details for one chore.

---

## Usage

```bash
gz chores plan <slug>
```

---

## Runtime Behavior

- Loads and validates `config/gzkit.chores.json`.
- Resolves `<slug>` and prints lane, steps, evidence commands, acceptance checks, and log path.
- Does not execute any command.

---

## Example

```bash
uv run gz chores plan quality-check
```
