# gz personas list

Enumerate persona files from `.gzkit/personas/` (read-only).

---

## Usage

```bash
gz personas list [--json]
```

---

## Runtime Behavior

- Discovers persona YAML files in `.gzkit/personas/`.
- Prints a table with persona name, role, and file path.
- With `--json`, emits a JSON array of persona data to stdout.
- If the personas directory does not exist, prints an empty table (or empty JSON array).

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON array |

---

## Example

```bash
uv run gz personas list
uv run gz personas list --json
```
