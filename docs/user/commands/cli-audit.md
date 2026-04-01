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
- `README.md` Quick Start command examples parse against the live CLI

### Cross-Coverage (AST-driven)

Discovers all CLI commands by parsing `cli/main.py` and verifies six documentation
surfaces per command:

| Surface | Verification |
|---------|-------------|
| Manpage | `docs/user/commands/<slug>.md` exists |
| Index entry | Listed in `docs/user/commands/index.md` |
| Operator runbook | Referenced in `docs/user/runbook.md` |
| Governance runbook | Referenced in `docs/governance/governance_runbook.md` |
| Docstring | Handler function has non-empty docstring |

Also detects orphaned documentation referencing removed commands.

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
