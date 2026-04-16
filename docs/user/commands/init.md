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
| `--force` | flag | — | Full reinitialize (overwrites config, re-scaffolds) |
| `--no-skeleton` | flag | — | Skip Python project skeleton (pyproject.toml, src/, tests/) |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Creates `.gzkit/` directory with ledger
2. Creates `.gzkit.json` configuration
3. Detects project structure (source, tests, docs paths)
4. Creates Python project skeleton (`pyproject.toml`, `src/<project>/`, `tests/`)
5. Generates `CLAUDE.md` from governance canon
6. Sets up agent hooks (Claude, Copilot)
7. Creates `design/` directories for governance artifacts
8. Scans for existing PRDs/ADRs and offers to register them

---

## Re-run (Repair Mode)

Running `gz init` on an already-initialized project enters **repair mode**:

- Detects and creates any missing artifacts (skeleton files, governance dirs, manifest)
- Re-syncs control surfaces
- Does not overwrite existing files
- Does not require `--force`

Use `--force` only when you need a full reinitialize (rewrites config, re-scaffolds everything).

---

## Project Skeleton

By default, `gz init` creates a minimal Python project skeleton:

| Artifact | Content |
|----------|---------|
| `pyproject.toml` | Project metadata, Python >=3.13, ruff config, hatchling build |
| `src/<project>/__init__.py` | Source package (name derived from directory) |
| `tests/__init__.py` | Test package |
| `.venv/` | Virtual environment (via `uv sync`) |

All skeleton files are idempotent — existing files are never overwritten.
`uv sync` only runs when `.venv` does not yet exist.
Use `--no-skeleton` to skip skeleton creation entirely (governance-only init).

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
# Initialize with defaults (governance + project skeleton)
gz init

# Initialize in heavy mode
gz init --mode heavy

# Governance-only (no pyproject.toml, src/, tests/)
gz init --no-skeleton

# Repair missing artifacts on an existing project
gz init

# Full reinitialize
gz init --force

# Dry run
gz init --dry-run
```

---

## Output

```
Initializing gzkit for my-project in lite mode...
  Created design/prd/
  Created design/constitutions/
  Created design/adr/
  Created pyproject.toml
  Created src/my_project/__init__.py
  Created tests/__init__.py
  Ran uv sync (virtualenv created)
  Scaffolded 15 skills (run gz skill list to see all)
  Scaffolded 2 default personas
  Generated CLAUDE.md
  Created .claude/settings.json
  Created .copilotignore

gzkit initialized successfully!

  Scaffolded 15 skills (run gz skill list to see all)

Next steps:
  Skill (preferred)         CLI equivalent
  /gz-prd                    gz prd <name>
  /gz-plan                   gz plan create <name>
  /gz-status                 gz status
  /gz-gates                  gz gates --adr ADR-<X.Y.Z>
```

---

## Result Tree

After `gz init --mode lite`, your project looks like this:

```text
my-project/
├── .gzkit/
│   ├── ledger.jsonl           ← Governance event log
│   ├── manifest.json          ← Project structure manifest
│   ├── personas/              ← Agent persona definitions
│   ├── rules/                 ← Canonical governance rules
│   └── skills/                ← Canonical skill definitions (15 core skills)
├── .gzkit.json                ← Project configuration
├── .claude/
│   ├── rules/                 ← Mirror of .gzkit/rules/
│   ├── skills/                ← Mirror of .gzkit/skills/
│   └── settings.json          ← Claude Code hooks
├── design/
│   ├── prd/                   ← Product Requirements Documents
│   ├── constitutions/         ← Governance constitutions
│   └── adr/                   ← Architecture Decision Records + OBPIs
├── src/my_project/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── .gitignore
├── AGENTS.md                  ← Agent governance contract
└── CLAUDE.md                  ← Claude Code instructions (generated)
```

Use `--no-skeleton` to skip `pyproject.toml`, `src/`, and `tests/` if your
project already has them.
