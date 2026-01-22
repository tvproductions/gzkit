# gz init

Initialize gzkit in the current project.

---

## Usage

```bash
gz init [OPTIONS]
```

---

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--mode` | `lite` \| `heavy` | `lite` | Governance mode |
| `--force` | flag | — | Overwrite existing initialization |

---

## What It Does

1. Creates `.gzkit/` directory with ledger
2. Creates `.gzkit.json` configuration
3. Detects project structure (source, tests, docs paths)
4. Generates `CLAUDE.md` from governance canon
5. Sets up agent hooks (Claude, Copilot)
6. Creates `design/` directories for governance artifacts
7. Scans for existing PRDs/ADRs and offers to register them

---

## Modes

### Lite (default)

Gates 1 and 2:

- ADR required
- Tests required

Use for internal changes that don't affect external contracts.

### Heavy

All five gates:

- ADR required
- Tests required
- Documentation required
- BDD acceptance tests required
- Human attestation required

Use when changing CLI, API, or schema contracts.

---

## Example

```bash
# Initialize with defaults
gz init

# Initialize in heavy mode
gz init --mode heavy

# Reinitialize (overwrites existing)
gz init --force
```

---

## Output

```
Initializing gzkit for my-project in lite mode...
  Created design/prd/
  Created design/constitutions/
  Created design/briefs/
  Created design/adr/
  Generated CLAUDE.md
  Created .claude/settings.json
  Created .copilotignore
  Scaffolded 3 core skills

gzkit initialized successfully!

Next steps:
  gz prd <name>       Create a PRD
  gz status           Check gate status
  gz validate         Validate artifacts
```
