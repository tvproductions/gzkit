# Chores Package — Agent Contract

**STOP. Read this entire file before authoring or modifying any chore.**

This directory is the **canonical, packaged source** of gzkit chores
(`src/gzkit/chores/`). It ships in the wheel and is discoverable at runtime via
`importlib.resources.files("gzkit.chores")`. Project repositories receive
project-local overlays at `.gzkit/chores/<slug>/`; canonical templates here are
read-only at runtime.

---

## Two-Surface Layout (ADR-0.0.21)

| Surface | Path | Role | Shipped in wheel? |
|---------|------|------|-------------------|
| Canonical (package) | `src/gzkit/chores/<slug>/` | Authoritative templates and registry | **Yes** |
| Project overlay | `.gzkit/chores/<slug>/` | Project-local copies + execution evidence (`proofs/`) | No |

`gz chores` resolves each slug **project-first → package-fallback**: it looks
under `<project_root>/.gzkit/chores/<slug>/` first; if that path is absent or
incomplete, it falls back to the canonical package resource. The same order
applies to the `registry.json` file (REQ-0.0.21-04-05).

`gz chores list --explain` prints one row per chore labeling the resolution
source as `project`, `package`, or `missing`.

**`proofs/` is always project-local, never canonical.** Canonical templates
under `src/gzkit/chores/<slug>/` MUST NOT ship `proofs/` content. Execution
evidence is generated at run time under `.gzkit/chores/<slug>/proofs/`.

---

## Slug Directory Contract

Each subdirectory (canonical OR project overlay) is a self-contained chore
package containing:

| File | Purpose | Required |
|------|---------|----------|
| `CHORE.md` | Definition, workflow, acceptance criteria | Yes |
| `acceptance.json` | Machine-readable criteria for automation | Yes |
| `README.md` | Human-readable summary | Yes |
| `proofs/` | Execution evidence directory (project-local only) | Yes (project-local) |

The package surface ships `CHORE.md`, `acceptance.json`, and `README.md` for
every canonical slug. `proofs/` is never canonical.

---

## MANDATORY: Consult Before Acting

Before executing or modifying any chore, read:

1. **The chore's `CHORE.md`** — Contains the authoritative procedure
2. **The registry** at `src/gzkit/chores/registry.json` (canonical) — for
   discovery; `gz chores list` is the operator-facing surface

---

## Chore Execution Protocol

### Step 1: Discover and read the CHORE.md

```bash
uv run gz chores list --explain
uv run gz chores show <chore_slug>
```

The `--explain` flag tells you whether each slug resolves from `project`,
`package`, or is `missing`.

### Step 2: Dry-run criteria

```bash
uv run gz chores advise <chore_slug>
```

### Step 3: Execute and log

```bash
uv run gz chores run <chore_slug>
```

This validates acceptance criteria and writes a dated log entry to
`.gzkit/chores/<slug>/proofs/CHORE-LOG.md`. Per-slug evidence is project-local.

### Step 4: Audit log presence

```bash
uv run gz chores audit --all
```

---

## Health Check and Layout Discipline

### `gz chores doctor` — Restore canonical scaffold (REQ-0.0.21-09)

```bash
uv run gz chores doctor                 # Repair missing canonical files
uv run gz chores doctor --dry-run       # Report-only; no file changes
uv run gz chores doctor --json          # One JSON record per slug
```

`doctor` re-creates any missing canonical file (`CHORE.md`, `acceptance.json`,
`README.md`) inside `.gzkit/chores/<slug>/` from the package source, byte-for-byte
matching the canonical scaffold output. It never touches `proofs/` content
(REQ-0.0.21-09-05) and never modifies project-local-only slugs that are absent
from the canonical set (REQ-0.0.21-09-06).

### `gz validate --chores-layout` — Layout enforcement (REQ-0.0.21-08)

```bash
uv run gz validate --chores-layout
```

Fails closed (exit 3) on any unwaived `CHORE.md` or `acceptance.json` outside
`src/gzkit/chores/`, `.gzkit/chores/`, or the configured `paths.chores`.
Waivers are explicit entries in `data/chores_layout_waivers.json`; silent skips
are not permitted.

---

## What You MUST NOT Do

1. **DO NOT skip the CHORE.md** — It contains the authoritative procedure.
2. **DO NOT put proofs in `artifacts/` or any path outside the slug overlay.**
   Proofs go in `.gzkit/chores/<slug>/proofs/`.
3. **DO NOT modify acceptance criteria** without updating both `CHORE.md` and
   `acceptance.json` in the canonical package.
4. **DO NOT create a chore without all required files** (`CHORE.md`,
   `acceptance.json`, `README.md`, plus a `proofs/` directory in the project
   overlay).
5. **DO NOT add `proofs/` content to the canonical package surface.** Proofs are
   execution evidence, not canon.
6. **DO NOT introduce a `CHORE.md` or `acceptance.json` outside the two canonical
   roots.** `gz validate --chores-layout` will fail closed; layout drift is the
   re-emergence pattern ADR-0.0.21 exists to prevent.

---

## What You SHOULD Do

1. **Follow the established pattern** — Study existing chores under
   `src/gzkit/chores/` before creating new ones.
2. **Keep proofs atomic** — One file per evidence artifact.
3. **Use descriptive filenames** — `ruff-report-2026-04-25.txt`, not
   `output.txt`.
4. **Commit project-local proofs** — They are tracked, not gitignored, and
   live under `.gzkit/chores/<slug>/proofs/`.

---

## Adding a New Chore (Canonical)

Use an existing canonical chore as a template. Required structure for a
canonical addition:

```text
src/gzkit/chores/<slug>/
├── CHORE.md          # Definition, workflow, acceptance criteria
├── acceptance.json   # Machine-readable criteria
└── README.md         # Brief human summary
```

After creating, register the slug in `src/gzkit/chores/registry.json`. Project
overlays (`.gzkit/chores/<slug>/`) are scaffolded by `gz init` or `gz chores
doctor` from the canonical surface.

---

## Acceptance Criteria Format

The `acceptance.json` file uses this schema:

```json
{
  "criteria": [
    {
      "type": "exitCodeEquals",
      "command": "uv run -m unittest -q",
      "expected": 0
    },
    {
      "type": "outputNotContains",
      "command": "uvx ruff check src/gzkit --select E722",
      "notContains": "E722",
      "description": "No bare except clauses"
    }
  ]
}
```

Supported types:

- `exitCodeEquals` — Command must exit with specific code
- `outputContains` — Command output must contain string
- `outputNotContains` — Command output must not contain string
- `fileExists` — File must exist at path

Commands must not contain shell operators (`&&`, `||`, `|`, `<`, `>`).
Split compound commands into separate criteria.

---

## If You're Unsure

**ASK THE HUMAN:**

- "Should I create a new chore or add to an existing one?"
- "Should this chore live in canonical (`src/gzkit/chores/`) or only as a
  project overlay (`.gzkit/chores/`)?"
- "What lane should this chore be?"
- "Where should I store this proof artifact?"

---

## Related

- ADR-0.0.21 — `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/`
- Rule — `.gzkit/rules/chores.md`
- Manpage — `docs/user/manpages/gz-chores.md`
- Runbook — `docs/user/runbook.md` § Chores Commands
