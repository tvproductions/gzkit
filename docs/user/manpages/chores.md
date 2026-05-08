# gz chores

Discover, plan, execute, and audit repository chores using the two-surface
chores layout introduced by ADR-0.0.21.

## Synopsis

```bash
gz chores <subcommand> [OPTIONS]
```

## Description

`gz chores` is the operator surface for gzkit's chore system. Chores are
declarative maintenance, refactoring, or quality work items packaged as
self-contained directories. Each chore ships a `CHORE.md` (procedure),
`acceptance.json` (machine-readable criteria), and `README.md` (human summary).

**Two-surface resolution.** Chores resolve project-first → package-fallback:
`<project_root>/.gzkit/chores/<slug>/` is consulted before the canonical package
resource at `importlib.resources.files("gzkit.chores")`. The same order applies
to the `registry.json` file. Use `gz chores list --explain` to see which
surface answers each slug. `proofs/` directories are project-local only;
canonical templates do not ship execution evidence.

## Subcommands

### list

Enumerate declared chores from the registry.

```bash
gz chores list [--explain] [--json]
```

`--explain` prints one row per chore with its resolution source: `project`,
`package`, or `missing`.

### show

Display the `CHORE.md` for one chore.

```bash
gz chores show <slug>
```

### plan

Show plan details for one chore.

```bash
gz chores plan <slug> [--replace]
```

### advise

Dry-run criteria and report status without mutating disk.

```bash
gz chores advise <slug>
```

### run

Execute one chore by slug. Validates acceptance criteria and writes a dated
log to `.gzkit/chores/<slug>/proofs/CHORE-LOG.md`.

```bash
gz chores run <slug>
```

### audit

Audit log presence across all chores.

```bash
gz chores audit --all
```

### doctor

Restore missing canonical files (`CHORE.md`, `acceptance.json`, `README.md`)
inside `.gzkit/chores/<slug>/` from the package source. Never modifies
`proofs/` content (REQ-0.0.21-09-05). Never modifies project-local-only slugs
that are absent from canonical (REQ-0.0.21-09-06).

```bash
gz chores doctor [--dry-run] [--json]
```

`--dry-run` produces the full summary without modifying any file.
`--json` emits one record per slug to stdout with `slug`, `before_status`,
and `after_status` fields.

### propose-ghi

File GitHub issues for unfiled cluster proposal records found in a chore's
`proofs/` directory.

```bash
gz chores propose-ghi <slug>
```

Reads `proposal-*.json` files from `.gzkit/chores/<slug>/proofs/`. In TTY
mode, prompts `PROPOSE/skip` for each unfiled record and calls `gh issue create`
on confirmation. In headless mode, marks records `advisory=true` without filing.
Already-filed records (where `filed: true`) are skipped on re-run. Requires
`gh` CLI available in `$PATH` for issue creation.

**TTY gating.** The command detects `sys.stdin.isatty() and sys.stdout.isatty()`
before prompting. Non-interactive (CI) environments receive advisory-only output
and no GHI is created.

**Example:**

```bash
# File proposals from the eval-feedback-cluster chore
uv run gz chores propose-ghi eval-feedback-cluster
```

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--explain` | list | Label each row with resolution source (project/package/missing) |
| `--json` | list, doctor | Output as JSON to stdout |
| `--dry-run` | doctor | Report-only; no file changes |
| `--replace` | plan | Replace any cached plan file |
| `--all` | audit | Audit every registered chore |
| `--quiet`, `-q` | global | Suppress non-error output |
| `--verbose`, `-v` | global | Enable verbose output |
| `--debug` | global | Enable debug mode with full tracebacks |
| `--help`, `-h` | global | Show help and exit |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error (missing slug, malformed `acceptance.json`, etc.) |
| 2 | System/IO error |
| 3 | Policy breach (acceptance criterion failed; layout violation; missing canonical chore not waived) |

## Examples

```bash
# Discover what's available, with resolution source
uv run gz chores list --explain

# Inspect a chore before running it
uv run gz chores show coverage-40pct

# Dry-run criteria
uv run gz chores advise coverage-40pct

# Execute the chore (writes evidence to .gzkit/chores/coverage-40pct/proofs/)
uv run gz chores run coverage-40pct

# Audit log presence across the registry
uv run gz chores audit --all

# Repair a missing canonical scaffold
uv run gz chores doctor

# Health-check without writing files
uv run gz chores doctor --dry-run

# Machine-readable doctor output
uv run gz chores doctor --json

# File GHI proposals from the eval-feedback-cluster chore (TTY mode)
uv run gz chores propose-ghi eval-feedback-cluster
```

## Files

| Path | Role |
|------|------|
| `src/gzkit/chores/<slug>/` | Canonical, packaged chore source (shipped in wheel) |
| `src/gzkit/chores/registry.json` | Canonical chore registry |
| `.gzkit/chores/<slug>/` | Project-local overlay (optional; created by `gz init` and `gz chores doctor`) |
| `.gzkit/chores/<slug>/proofs/` | Project-local execution evidence (never canonical) |
| `importlib.resources.files("gzkit.chores")` | Package resource fallback used when the project-local path is absent |
| `data/chores_layout_waivers.json` | Explicit waiver list for `gz validate --chores-layout` |

## Related

- [`gz validate --chores-layout`](validate.md) — fail-closed (exit 3) on stray
  `CHORE.md` or `acceptance.json` outside the canonical roots.
- [`gz-chore-runner`](../skills/gz-chore-runner.md) — guided workflow for
  end-to-end chore execution.
- ADR-0.0.21 — `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/`
- Rule — `.gzkit/rules/chores.md`
- Agent contract — [`src/gzkit/chores/README.md`](../../../src/gzkit/chores/README.md)

## See Also

- [chores-list](../commands/chores-list.md)
- [chores-show](../commands/chores-show.md)
- [chores-plan](../commands/chores-plan.md)
- [chores-advise](../commands/chores-advise.md)
- [chores-run](../commands/chores-run.md)
- [chores-audit](../commands/chores-audit.md)
- [chores-propose-ghi](../commands/chores-propose-ghi.md)
