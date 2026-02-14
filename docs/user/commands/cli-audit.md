# gz cli audit

Audit CLI command documentation coverage and headings.

---

## Usage

```bash
gz cli audit [--json]
```

---

## What It Checks

- Required command manpages exist under `docs/user/commands/`
- Each page heading matches the command surface (`# gz ...`)
- `docs/user/commands/index.md` links to each required page

---

## Example

```bash
uv run gz cli audit
```

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable output |
