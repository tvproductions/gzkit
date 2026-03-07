# gz chores list

List all chores declared in `config/gzkit.chores.json`.

---

## Usage

```bash
gz chores list
```

---

## Runtime Behavior

- Loads the registry from `config/gzkit.chores.json`.
- Fails closed if the registry is missing or malformed.
- Prints one row per chore with `slug`, `lane`, step count, and title.

---

## Example

```bash
uv run gz chores list
```
