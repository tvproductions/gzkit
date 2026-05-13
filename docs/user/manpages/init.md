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
| `--force` | flag | — | Full reinitialize (overwrites config, re-scaffolds). Mutually exclusive with `--update` |
| `--update` | flag | — | Version-aware refresh of canonical surfaces from the installed wheel; preserves operator edits via marker detection. Mutually exclusive with `--force` |
| `--no-skeleton` | flag | — | Skip Python project skeleton (pyproject.toml, src/, tests/) |
| `--yes` | flag | — | Auto-accept registry-merge prompts during repair |
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

## Update Mode (Version-Aware Refresh)

`gz init --update` is the **third** init mode, distinct from default (repair-missing) and `--force` (wipe-and-recreate). It refreshes canonical surfaces in the adopter's `.gzkit/<surface>/` from the installed wheel's package data while **preserving operator-edited files** via marker detection.

### Three modes — when to use which

| Mode | When to use | Behavior on existing canonical files |
|------|-------------|--------------------------------------|
| **default** (`gz init`) | First init, or repair missing artifacts on an existing project | Skip-existing: never overwrites |
| **`--update`** | Cross-version upgrade after `pip install py-gzkit==X.Y.Z` brings new canonical content | Refresh STALE entries in place; preserve EDITED entries; report conflicts |
| **`--force`** | Full reinitialize; willing to lose operator edits | Wipe and re-copy every canonical surface |

### Three-state detection (REQ-0.0.32-05-02)

Per artifact under `.gzkit/<surface>/`, `--update` classifies the project copy against the wheel canonical:

| State | Condition | Action |
|-------|-----------|--------|
| `IDENTICAL` | bytes match wheel canonical | skip; no write |
| `STALE` | bytes differ; no canonical-version marker present | refresh in place (overwrite with wheel canonical) |
| `EDITED` | bytes differ; canonical-version marker present | **conflict — never overwrite**; record in summary |

### Operator-edit marker (REQ-0.0.32-05-04)

The marker is a body-level HTML comment:

```html
<!-- gzkit-canonical-version: X.Y.Z -->
```

The scaffolder writes this marker when it copies canonical content into `.gzkit/<surface>/`. `--update` rewrites it on a STALE refresh. The marker's presence in a file whose bytes differ from the current wheel canonical is the positive signal that the scaffolder previously stamped this copy and the operator (or a prior `--update`) has since edited it.

The marker composes with — and does **not** replace — the existing surface-author version markers per `.claude/rules/skill-surface-sync.md`:

- Skills retain `skill-version:` in YAML frontmatter
- Rules retain body-level `<!-- rule-version: X.Y.Z -->`
- The canonical-version marker tracks "version of canonical content delivered by the wheel" — a distinct dimension from surface-author version semantics.

### Dry-run

```bash
gz init --update --dry-run
```

Reports the per-surface `IDENTICAL`/`STALE`/`EDITED` count and lists every artifact that would be refreshed or conflicted, **without writing**. Use to preview an upgrade before committing.

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success: refresh complete or dry-run reported; no unresolved conflicts |
| `1` | Usage error: e.g. `--update` combined with `--force`, or `--update` on an uninitialized project |
| `3` | Policy breach: at least one `EDITED` conflict remains unresolved at end-of-run |

### Conflict resolution (exit 3)

When `gz init --update` exits 3, review each `EDITED` conflict listed in the summary. Two operator actions resolve a conflict:

1. **Accept the canonical version** — delete the project copy and re-run `gz init --update`. The next run sees the file as missing, copies the wheel canonical, and stamps a fresh marker.
2. **Keep the project edits** — no action required. The conflict persists across runs; `--update` will continue to surface it until the operator either accepts the canonical or rewrites the project copy to match.

### Surface coverage

`--update` iterates every canonical surface that ships in the wheel:

- `gzkit.skills` → `.gzkit/skills/<slug>/SKILL.md`
- `gzkit.rules` → `.gzkit/rules/<slug>.md`
- `gzkit.chores` → `.gzkit/chores/<slug>/` (canonical-class files only per chores class-classifier)
- `gzkit.personas` → `.gzkit/personas/<slug>.md`
- `gzkit.templates` → `.gzkit/templates/<name>.md`

Package-internal entries (`__init__.py`, `_scaffolder.py`, `__pycache__/`) are excluded by the leading-underscore filter. Chore `proofs/` and runtime-state files are excluded by the chores class-classifier.

---

## Skills Scaffolding

As of OBPI-0.0.32-02, `gz init` copies canonical `SKILL.md` content from the
wheel's package surface (`importlib.resources.files("gzkit.skills")`) into the
project's `.gzkit/skills/<slug>/SKILL.md`. Every active canonical slug is
scaffolded; entries whose canonical SKILL.md declares
`lifecycle_state: retired` are skipped.

Once written, `.gzkit/skills/` is the **project canonical source-of-truth** —
the same editing invariant binds in every gzkit-or-adopter repo. Edit files
under `.gzkit/skills/`; run `gz agent sync control-surfaces` to propagate to
vendor mirrors (`.claude/skills/`, `.github/skills/`).

Re-running `gz init` (repair mode) adds any new canonical skills delivered by
the installed gzkit version without overwriting operator-edited files
(`skip_existing=True` semantics).

Use `--force` to wipe and re-copy all canonical SKILL.md content from the
wheel's package surface (replaces any operator edits).

---

## Rules Scaffolding

As of OBPI-0.0.32-04, `gz init` copies canonical rule `.md` content from the
wheel's package surface (`importlib.resources.files("gzkit.rules")`) into the
project's `.gzkit/rules/<slug>.md`. Every canonical rule slug is scaffolded;
`AGENTS.md` (a package-internal agent contract) is excluded.

Once written, `.gzkit/rules/` is the **project canonical source-of-truth** —
operators edit there. Run `gz agent sync control-surfaces` to propagate to
vendor mirrors (`.claude/rules/`, `.github/instructions/`).

Re-running `gz init` (repair mode) adds any new canonical rules delivered by
the installed gzkit version without overwriting operator-edited files
(`skip_existing=True` semantics). Rules scaffolding runs after `sync_all` in
the fresh init path so that the initial control-surface sync uses the
instruction-sync path; subsequent syncs render canonical rules to instructions.

---

## Personas Scaffolding

As of OBPI-0.0.32-10, `gz init` copies canonical persona `.md` content from the
wheel's package surface (`importlib.resources.files("gzkit.personas")`) into the
project's `.gzkit/personas/<slug>.md`. The 6 canonical persona slugs are:
`implementer`, `main-session`, `narrator`, `pipeline-orchestrator`,
`quality-reviewer`, `spec-reviewer`.

Once written, `.gzkit/personas/` is the **project canonical source-of-truth** for
that project — operators customize personas there. The `CORE_PERSONAS` registry
(in `gzkit.personas`) enumerates the canonical slugs; `scaffold_core_personas`
is the scaffolding function.

Personas are treated as operator identity files and are **never overwritten** by
`gz init` when they already exist — even with `--force`. Re-running `gz init`
(repair mode) adds any new canonical personas delivered by the installed gzkit
version without overwriting existing ones (`skip_existing=True` semantics always).

---

## Templates Scaffolding

As of OBPI-0.0.32-12, `gz init` copies canonical template `.md` content from the
wheel's package surface (`importlib.resources.files("gzkit.templates")`) into the
project's `.gzkit/templates/<name>.md`. The 11 canonical template slugs are:
`adr`, `adr_pool`, `agents`, `audit`, `audit_plan`, `claude`, `closeout`,
`constitution`, `copilot`, `obpi`, `prd`.

Once written, `.gzkit/templates/` is the **project canonical source-of-truth** —
`render_template()` consults the project copy first when present
(project-first → package-fallback resolution). Operators customize templates there.

Re-running `gz init` (repair mode) adds any new canonical templates delivered by
the installed gzkit version without overwriting existing ones (`skip_existing=True`
semantics). Operator edits to `.gzkit/templates/<name>.md` are preserved.

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

# Version-aware refresh after pip install py-gzkit==<newer> (preserves operator edits)
gz init --update

# Preview what --update would refresh, without writing
gz init --update --dry-run
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
