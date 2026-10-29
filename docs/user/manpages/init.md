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
| `--update` | flag | — | Version-aware refresh of canonical surfaces from the installed wheel; leaves any file that matches no version gzkit shipped (an operator edit) untouched. Mutually exclusive with `--force` |
| `--no-skeleton` | flag | — | Skip Python project skeleton (pyproject.toml, src/, tests/) |
| `--project-type` | `lib` \| `package` \| `app` | `lib` | Shape `uv init` builds for a new project: `lib` ships `py.typed` and no entry point; `package` and `app` declare a `[project.scripts]` entry. Ignored when `pyproject.toml` already exists |
| `--yes` | flag | — | Auto-accept registry-merge prompts during repair or `--update` |
| `--attestor-handle` | string | — | Record `authorship.attestor_handle` in `.gzkit.json`: the handle an omitted `--attestor` records on the verbs that default it. A handle with no spaces, never a real name. On first init without the flag, an interactive terminal is asked; otherwise none is set, and gzkit's own handle is never scaffolded. Mutually exclusive with `--update` (GHI #1036) |
| `--dry-run` | flag | — | Show actions without writing |

---

## What It Does

1. Creates `.gzkit/` directory with ledger
2. Creates `.gzkit.json` configuration
3. Detects project structure (source, tests, docs paths)
4. Builds the Python project through uv when there is no `pyproject.toml` (`uv init --<project-type>`, then `uv add --dev ruff ty`), adds `tests/` and a CI workflow, and runs `uv sync` when `.venv` is absent; see [Project Skeleton](#project-skeleton)
5. Seeds `data/astral_discipline_baseline.json` from the violations of the Astral discipline the project carries now, when it has no baseline; `gz validate --astral-discipline` then fails on any new one, and the list only shrinks
6. Copies the wheel's canonical skills, chores, personas, templates and rules into `.gzkit/`, runs the sync preflight, and syncs every control surface (`AGENTS.md`, `CLAUDE.md`, vendor mirrors, manifest, Codex files); see [`gz agent sync control-surfaces`](agent-sync-control-surfaces.md)
7. Sets up agent hooks (Claude)
8. Creates `design/` directories for governance artifacts
9. Scans for existing PRDs/ADRs and offers to register them
10. Writes `.pre-commit-config.yaml` declaring the pre-push `gz check` gate
    (ADR-0.0.68), preserving any config already present
11. Runs `pre-commit install` for every hook type the config declares
    (`default_install_hook_types`, plus `pre-push`), so the gate is actually
    delivered into `.git/hooks/`, not merely declared
12. When the config declares `post-commit`, installs the commit-locus ledger
    recorder as `.git/hooks/post-commit.legacy`. pre-commit runs that file
    before it stashes unstaged changes; run as an ordinary post-commit hook,
    the recorder's ledger row was rolled back whenever the ledger had
    unstaged rows (GHI #1092). An existing `post-commit.legacy` that is not
    gzkit's is left in place and reported
13. Writes `.gitignore` and `data/audit_thresholds.json` when absent and, in a
    git worktree, registers the `gzkit-jsonl` append-only merge driver in
    local git config
14. Appends `project_init` to the ledger, plus one `agent_sync_completed` per
    sync it runs

Steps 10 and 11 are separate on purpose. A declared-but-uninstalled gate
enforces nothing while every surface reports green, so `gz check` verifies the
hook is on disk rather than trusting the declaration (GHI #715). When
installation cannot complete — `pre-commit` unavailable, or `core.hooksPath`
set, which makes `pre-commit install` refuse — `gz init` reports the reason and
continues; the `gz check` gate is the fail-closed half.

---

## Codex Project Configuration

Initialization and `gz agent sync control-surfaces` create the configured
Codex project file, `.codex/config.toml` by default, when it is missing or
empty. The managed baseline is:

```toml
# gzkit-managed-codex-config: v1
sandbox_mode = "workspace-write"
project_doc_max_bytes = 65536
[features]
hooks = true

[sandbox_workspace_write]
network_access = true
```

The `paths.codex_config` value in `.gzkit.json` changes both the generated
location and the path published in `.gzkit/manifest.json`. Sync writes only the
configured target; transition handling for a prior default is described below.

The marker identifies content that began as the gzkit baseline. Sync never
overwrites a non-empty Codex config: both unmarked operator files and marked
baselines with added settings are preserved byte-for-byte across init, repair,
and sync. `gz validate --surfaces` reports marked content whose bytes drift from
the baseline so ownership changes remain visible. Remove the complete marker
line after adding persistent model, approval, MCP, or other local settings to
accept operator ownership and silence that managed-drift diagnostic.

When `paths.codex_config` moves away from the default, sync removes the old
default only when it is empty or its bytes still exactly match the generated baseline. A
customized old default is preserved and reported as a conflicting duplicate by
surface and sync-parity validation, preventing silent operator-data loss.

To replace a drifted managed baseline, delete the configured file and run:

```bash
gz agent sync control-surfaces
gz validate --surfaces
```

Hook registration is delivered separately; enabling `[features].hooks` here
does not make a malformed or untrusted project hook authoritative.

---

## Re-run (Repair Mode)

Running `gz init` on an already-initialized project enters **repair mode**:

- Detects and creates any missing artifacts (skeleton files, governance dirs, manifest)
- Re-syncs control surfaces, listing each file the sync changes; a tree already in sync is left untouched
- Refuses to sync when canonical skills fail the sync preflight: it reports what it already repaired, then exits 1 with the blockers and leaves every mirror unchanged. `gz init --force` runs the same preflight, because it re-copies the wheel's skills but keeps local ones (GHI #1100)
- With `--attestor-handle`, sets `authorship.attestor_handle` in `.gzkit.json` and changes no other key (listed like every other repair write)
- Does not overwrite existing files, except that in a git worktree with a pre-commit config it re-runs `pre-commit install` and rewrites gzkit's `post-commit.legacy` recorder on every run, so repair always reports those two lines
- Does not require `--force`

Every file repair writes appears in its output and in the `Repaired N artifact(s)` count. `gz init --dry-run` lists the same writes and makes none. The one limit: a dry run renders the sync plan against the tree as it stands, so for an artifact it would newly scaffold, its `Would scaffold` line stands in for that artifact's mirrors (GHI #1098).

Use `--force` only when you need a full reinitialize (rewrites config, re-copies the wheel's canonical surfaces except personas; deletes nothing).

---

## Update Mode (Version-Aware Refresh)

`gz init --update` is the **third** init mode, distinct from default (repair-missing) and `--force` (re-copy from the wheel). It refreshes canonical surfaces in the adopter's `.gzkit/<surface>/` from the installed wheel's package data, overwriting a file only when it holds a version gzkit shipped, never an operator's edit (below). It does nothing else: no manifest write, no control-surface sync, no ledger event. Run `gz agent sync control-surfaces` afterwards so the mirrors carry the refreshed canon.

What it refreshes is what delivery defines (GHI #1123):

- **skills, rules, templates, personas** — the files `gz upgrade` refreshes, selected by the same per-surface classifiers, so package-only files such as `templates/author_prompts.py` and `templates/skills/**` never reach `.gzkit/`;
- **chores** — the files first init delivers: the surface-root documents and each shipped slug's canonical files, new slugs included;
- **`chores/registry.json`** — merged, never copied: shipped entries are added or updated, and entries only the project has (`projectLocal` chores, adopter chores) are kept. `--yes` accepts the merge without the prompt. A missing registry is delivered whole.

### Three modes — when to use which

| Mode | When to use | Behavior on existing canonical files |
|------|-------------|--------------------------------------|
| **default** (`gz init`) | First init, or repair missing artifacts on an existing project | Skip-existing: never overwrites |
| **`--update`** | Cross-version upgrade after `uv tool install py-gzkit==X.Y.Z` brings new canonical content | Refresh STALE entries in place; preserve EDITED entries; report conflicts |
| **`--force`** | Full reinitialize; willing to lose operator edits | Re-copy the wheel's skills, rules, templates and chores over the project's copies; deletes nothing (project-local files remain) and never overwrites personas |

### Three-state detection (REQ-0.0.32-05-02)

Per artifact under `.gzkit/<surface>/`, `--update` classifies the project copy against the wheel canonical:

| State | Condition | Action |
|-------|-----------|--------|
| `IDENTICAL` | bytes match wheel canonical | skip; no write |
| `STALE` | bytes differ, and equal a version of this file gzkit has shipped; also a file missing from the project | refresh in place (overwrite with wheel canonical) |
| `EDITED` | bytes differ, and match no version gzkit has shipped | **conflict — never overwrite**; record in summary |

### Edit detection (content-hash history)

The wheel ships `canonical_history.json`: the sha256 of every version of every canonical-surface file gzkit has ever shipped, keyed by `<surface>/<path>` (OBPI-0.0.32-05 requirement 4(b), ruled on GHI #1122). A project copy whose hash is in that history is one gzkit delivered and nobody changed, so refreshing it loses nothing. Any other difference is treated as the operator's edit, including a copy of a path the history has never seen. Nothing is written into the files themselves.

The history is appended by `gz agent sync control-surfaces` every time a canonical file changes, and entries are never removed, so a project scaffolded by any earlier release is recognized. The first entries were backfilled from gzkit's git history on 2026-09-27.

Because the hash covers the whole file, detection composes with the surface-author version markers in `.claude/rules/skill-surface-sync.md` without reading them: a copy whose `skill-version:` or `<!-- rule-version: X.Y.Z -->` differs from the wheel's is `STALE` when that copy shipped, and `EDITED` when the operator changed it.

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

1. **Accept the canonical version** — delete the project copy and re-run `gz init --update`. The next run sees the file as missing and copies the wheel canonical.
2. **Keep the project edits** — no action required. The conflict persists across runs; `--update` will continue to surface it until the operator either accepts the canonical or rewrites the project copy to match.

### Surface coverage

`--update` iterates every canonical surface that ships in the wheel:

- `gzkit.skills` → `.gzkit/skills/<slug>/SKILL.md`
- `gzkit.rules` → `.gzkit/rules/<slug>.md`
- `gzkit.chores` → `.gzkit/chores/<slug>/` (canonical-class files only per chores class-classifier)
- `gzkit.personas` → `.gzkit/personas/<slug>.md`
- `gzkit.templates` → `.gzkit/templates/<name>.md`

Package-internal entries (`__init__.py`, `_scaffolder.py`, `__pycache__/`) are excluded by the leading-underscore filter, and each surface's class-classifier excludes its package-only and runtime-state files (see What it refreshes, above).

In gzkit's own repository the installed package is the editable `src/gzkit/`, itself a copy synced from `.gzkit/`. A `.gzkit/` edit not yet synced matches no shipped version, so `--update` reports it `EDITED` and leaves it alone.

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
vendor mirrors (`paths.claude_skills` and `paths.codex_skills`, default `.claude/skills/` and `.agents/skills/`).

Re-running `gz init` (repair mode) adds any new canonical skills delivered by
the installed gzkit version without overwriting operator-edited files
(`skip_existing=True` semantics).

Use `--force` to re-copy all canonical SKILL.md content from the wheel's
package surface over the project's copies (replaces any operator edits;
project-local skills are kept).

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
project's `.gzkit/templates/<name>.md`. The canonical template slugs are whatever `gzkit.templates` ships — that package
directory is the authority, never a count transcribed here. Measured 2026-08-31:
`adr`, `adr_pool`, `agents`, `audit`, `audit_plan`, `changelog`, `claude`,
`closeout`, `constitution`, `obpi`, `prd`, `release_notes`.

Once written, `.gzkit/templates/` is the **project canonical source-of-truth** —
`render_template()` consults the project copy first when present
(project-first → package-fallback resolution). Operators customize templates there.

Re-running `gz init` (repair mode) adds any new canonical templates delivered by
the installed gzkit version without overwriting existing ones (`skip_existing=True`
semantics). Operator edits to `.gzkit/templates/<name>.md` are preserved.

---

## Project Skeleton

When the directory has no `pyproject.toml`, `gz init` builds the project
through uv rather than writing a manifest of its own:

```bash
uv init --<project-type> --name <package> --python <gzkit's floor> \
  --no-workspace --vcs none --author-from none .
uv add --dev --frozen ruff ty
```

The Python floor is read from the installed gzkit's `Requires-Python`, never
restated, and `--author-from none` keeps your git identity out of the
manifest. gzkit then adds what uv does not write:

| Artifact | Content |
|----------|---------|
| `pyproject.toml` | uv's manifest (uv_build backend, `dev` dependency group with `ruff` and `ty`), plus a Ruff configuration that bans `from __future__ import annotations` |
| `src/<package>/__init__.py` | Source package (name derived from directory); `lib` adds `py.typed` |
| `README.md` | Governance README, unless one already exists |
| `tests/__init__.py` | Test package |
| `.github/workflows/ci.yml` | CI on `astral-sh/setup-uv` pinned to a commit: `uv sync --locked`, Ruff, ty and `gz check`, with `UV_MALWARE_CHECK` on |
| `.venv/`, `uv.lock` | Virtual environment and lockfile (via `uv sync`) |

A project whose detected source root is not `src/` gets its package moved
there and `[tool.uv.build-backend] module-root` set to match.

An existing `pyproject.toml` is left exactly as it is; only `tests/` is
repaired. Every other skeleton file is idempotent too. `uv sync` only runs when
`.venv` does not yet exist. Use `--no-skeleton` to skip skeleton creation
entirely (governance-only init).

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

# Build a runnable package rather than a library
gz init --project-type package

# Repair missing artifacts on an existing project
gz init

# Full reinitialize
gz init --force

# Dry run
gz init --dry-run

# Version-aware refresh after uv tool install py-gzkit==<newer> (preserves operator edits)
gz init --update

# Preview what --update would refresh, without writing
gz init --update --dry-run
```

---

## Output

A dated record, observed 2026-10-29: `gz init --project-type package
--attestor-handle g0` in an empty git repository, excerpt. The counts are what
that installed wheel shipped, not a contract; `gz skill list` shows the current
set. Most of the first sync's `Generated <path>` lines are elided. With
`--no-skeleton`, the two `uv` lines, the `tests/__init__.py` line and `Ran uv
sync` are absent.

```text
Initializing gzkit for demo-proj in lite mode...
  Recorded attestor handle: g0
  Created design/prd/
  Created design/constitutions/
  Created design/adr/
  Created the project with uv init --package --author-from none, uv add --dev ruff ty
  Created src/demo_proj/ and .github/workflows/ci.yml
  Created tests/__init__.py
  Ran uv sync (virtualenv created)
  Created .gitignore
  Seeded data/astral_discipline_baseline.json (0 violation row(s); it only shrinks)
  Created .pre-commit-config.yaml (pre-push gz check gate)
  Installed pre-commit, pre-push hooks (session-green gate active)
  Registered git merge driver 'gzkit-jsonl' for append-only JSONL
  Scaffolded 72 core skills
  Scaffolded 31 core chores
  Scaffolded 7 core personas
  Scaffolded 14 core templates
  ...
  Generated AGENTS.md
  Generated CLAUDE.md
  Scaffolded 28 core rules
  Created .claude/hooks/post-edit-ruff.py
  ...
  Created .claude/settings.json
  (No existing artifacts to register)

gzkit initialized successfully!

  Scaffolded 72 skills (run gz skill list to see all)

Next steps:
  Skill (preferred)         CLI equivalent
  /gz-prd                    gz prd <name>
  /gz-plan                   gz plan create <name>
  /gz-status                 gz status
  /gz-check                  gz check

Skills add interview logic, forcing functions, and governance
validation that bare CLI commands do not. Use them when available.
See: /user/skills/ in the docs or run gz skill list.
```

---

## Result Tree

After `gz init --mode lite` with the skeleton:

```text
my-project/
├── .gzkit/
│   ├── ledger.jsonl           ← Governance event log
│   ├── manifest.json          ← Project structure manifest
│   ├── chores/                ← Canonical chores and registry
│   ├── personas/              ← Agent persona definitions
│   ├── rules/                 ← Canonical governance rules
│   ├── skills/                ← Canonical skill definitions
│   └── templates/             ← Canonical artifact templates
├── .gzkit.json                ← Project configuration
├── .claude/
│   ├── hooks/                 ← Claude Code hook scripts
│   ├── personas/              ← Mirror of .gzkit/personas/
│   ├── rules/                 ← Mirror of .gzkit/rules/
│   ├── skills/                ← Mirror of .gzkit/skills/
│   └── settings.json          ← Claude Code hooks
├── .agents/
│   ├── personas/              ← Codex persona mirror
│   └── skills/                ← Codex skill mirror
├── .codex/config.toml         ← Codex project baseline
├── .github/
│   ├── discovery-index.json
│   └── workflows/ci.yml       ← CI on setup-uv, uv sync --locked
├── data/
│   ├── astral_discipline_baseline.json  ← Seeded at init; only shrinks
│   └── audit_thresholds.json
├── design/
│   ├── prd/                   ← Product Requirements Documents
│   ├── constitutions/         ← Governance constitutions
│   └── adr/                   ← Architecture Decision Records + OBPIs
├── src/my_project/
│   ├── __init__.py
│   └── py.typed               ← lib only
├── tests/
│   └── __init__.py
├── .python-version
├── pyproject.toml             ← Built by uv init
├── uv.lock
├── README.md
├── .gitignore
├── .pre-commit-config.yaml    ← Pre-push gz check gate
├── AGENTS.md                  ← Agent governance contract (plus nested AGENTS.md files)
└── CLAUDE.md                  ← Claude Code instructions (generated)
```

Use `--no-skeleton` to skip `pyproject.toml`, `src/`, and `tests/` if your
project already has them.
