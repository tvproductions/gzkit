# gz check-config-paths

Validate that `.gzkit.json` and manifest path declarations match on-disk repo structure.

---

## Usage

```bash
gz check-config-paths [--json]
```

---

## What It Checks

- Required configured directories and files exist
- Manifest artifact paths exist
- Manifest control-surface paths exist with expected type (file vs directory)

---

## Example

```bash
uv run gz check-config-paths
```

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
