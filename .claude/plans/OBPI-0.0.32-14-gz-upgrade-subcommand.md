# Plan: OBPI-0.0.32-14-gz-upgrade-subcommand

**OBPI:** OBPI-0.0.32-14-gz-upgrade-subcommand
**Parent ADR:** ADR-0.0.32-canonical-surface-packaging
**Lane:** Heavy
**Date:** 2026-05-13

## Context

`gz upgrade` is a new CLI subcommand that provides adopter-side surface-only
refresh of `.gzkit/<surface>/` from the installed wheel's package data via
`importlib.resources.files("gzkit.<surface>")`. It is distinct from
`gz init --update` (which is the canonical project-refresh ceremony: all
surfaces, manifest mutation, scaffolder hooks). `gz upgrade` is the narrower
verb: per-surface filter, no manifest mutation, no scaffolder hooks.

The three-state IDENTICAL/STALE/EDITED detection infrastructure already exists
in `src/gzkit/commands/init_cmd.py` (functions `_detect_refresh_state`,
`_refresh_surface`, `_refresh_resource_surface`). This implementation MUST
import and reuse these helpers — not duplicate them.

Registration pattern: `init` is registered in `src/gzkit/cli/parser_governance.py`
via `_LAZY_HANDLERS` dict + `add_parser`. `upgrade` follows the same pattern
in the same file.

## Allowed Files

- `src/gzkit/commands/upgrade.py` (new)
- `src/gzkit/cli/parser_governance.py` (modify)
- `tests/commands/test_upgrade.py` (new)
- `tests/commands/test_upgrade_resources.py` (new)
- `features/upgrade.feature` (new)
- `docs/user/manpages/gz-upgrade.md` (new)
- `docs/user/runbook.md` (modify)

## Implementation Steps

### Step 1: Write red tests for upgrade_cmd semantics (TDD red phase)

File: `tests/commands/test_upgrade.py`

Write tests derived from the brief REQs (not from an implementation run):

- `TestUpgradeRegistered` — `gz upgrade --help` exits 0; verb resolves via `gz cli audit`
  (REQ-0.0.32-14-01) — test as import check + parser construction test
- `TestUpgradeSurfaceFilter` — unknown surface name exits 1 with token-naming error;
  known subset processes only those surfaces; default processes all (REQ-0.0.32-14-02)
- `TestUpgradeConflictDetection` — EDITED artifacts reported, left unchanged, exit non-zero
  when conflicts remain; exit 0 when zero conflicts (REQ-0.0.32-14-03)
- `TestUpgradeForce` — EDITED artifacts overwritten; per-file overwrite line printed;
  exit 0 on success (REQ-0.0.32-14-04)
- `TestUpgradeDryRun` — zero bytes written; same classification as non-dry-run;
  exit code matches non-dry-run (REQ-0.0.32-14-05)
- `TestUpgradeBootstrapRetrofit` — works when `.gzkit/<surface>/` absent;
  scaffolds from package data (REQ-0.0.32-14-06)
- `TestUpgradeIdempotent` — second invocation immediately after first exits 0,
  zero STALE/EDITED (REQ-0.0.32-14-07)
- `TestUpgradeManifestIsolation` — `.gzkit/manifest.json` not mutated by upgrade;
  `gz agent sync control-surfaces` NOT invoked (REQ-0.0.32-14-08)

Use `unittest.mock.patch` on `importlib.resources.files` to isolate from real
package data for unit-tier tests. Use `tempfile.TemporaryDirectory` for
filesystem isolation.

### Step 2: Write red tests for resource resolution (TDD red phase)

File: `tests/commands/test_upgrade_resources.py`

- `TestUpgradeResourceResolution` — `importlib.resources.files("gzkit.skills")` returns
  a Traversable; same for gzkit.rules, gzkit.templates, gzkit.personas
- `TestUpgradeCoreRegistries` — each CORE_SKILLS/CORE_RULES/CORE_PERSONAS/CORE_TEMPLATES
  entry is resolvable via `importlib.resources.files`

### Step 3: Implement `src/gzkit/commands/upgrade.py`

Import from `init_cmd`: `RefreshState`, `_detect_refresh_state`, `_refresh_surface`,
`_refresh_resource_surface` (or the equivalent helper that iterates a surface package).

Implement `upgrade_cmd(args: argparse.Namespace) -> None`:

```
REGISTERED_SURFACES = ("skills", "rules", "templates", "personas", "hooks")
SURFACE_PKG_MAP = {
    "skills": "gzkit.skills",
    "rules": "gzkit.rules",
    "templates": "gzkit.templates",
    "personas": "gzkit.personas",
    "hooks": None,  # hooks surface: skip if no package data
}

1. Parse --surface (comma-split, validate each token against REGISTERED_SURFACES;
   exit 1 on unknown token naming the token)
2. For each surface to process:
   a. Resolve resource package via SURFACE_PKG_MAP
   b. Enumerate entries via importlib.resources.files(pkg)
   c. For each entry:
      - Determine project path: <project_root>/.gzkit/<surface>/<slug>
      - If project path absent: write from package data (bootstrap-retrofit)
      - Else: call _detect_refresh_state(project_bytes, canonical_bytes)
      - IDENTICAL: skip (count identical)
      - STALE and not dry_run and (force or True): overwrite; if force: print per-file line
      - STALE and dry_run: report would-update (no write)
      - EDITED and force: overwrite; print per-file line
      - EDITED and not force: record conflict (do NOT write)
3. After all surfaces: if any EDITED conflicts remain and not force: exit 3
4. Exit 0 otherwise
5. NEVER touch .gzkit/manifest.json; NEVER call gz agent sync
```

Guard: do NOT import or call scaffold_core_* functions — those are scaffolder
paths that modify other state. Only use the three-state detection + raw file
write.

### Step 4: Register upgrade in parser_governance.py

In `src/gzkit/cli/parser_governance.py`:

1. Add `"upgrade_cmd": "gzkit.commands.upgrade"` to `_LAZY_HANDLERS`
2. Add upgrade subparser after the init parser:
   ```python
   p_upgrade = commands.add_parser(
       "upgrade",
       help="Surface-only refresh of .gzkit/<surface>/ from installed wheel package data.",
       epilog=build_epilog([...])
   )
   p_upgrade.add_argument(
       "--surface",
       default=None,
       help="Comma-separated subset of surfaces (skills,rules,templates,personas,hooks). Default: all.",
   )
   add_force_flag(p_upgrade)
   add_dry_run_flag(p_upgrade)
   p_upgrade.set_defaults(func=lambda a: _lazy("upgrade_cmd")(a))
   ```

### Step 5: Write `docs/user/manpages/gz-upgrade.md`

Follow the shape of `docs/user/manpages/init.md`:
- `# gz upgrade`
- `## Usage` with synopsis
- `## Options` table (--surface, --force, --dry-run)
- `## What It Does` section
- `## Three-State Detection` section (IDENTICAL/STALE/EDITED)
- `## Bootstrap Retrofit` section
- `## Relationship to gz init --update` section
- `## Exit Codes` table
- `## Examples` section (dry-run preview, surface subset, force overwrite, bootstrap)
- `## Related Commands` section

### Step 6: Update `docs/user/runbook.md`

Add an entry under the Surface Management section (or create one) distinguishing:
- `gz init --update` — project-refresh ceremony (manifest, scaffolder hooks, all surfaces)
- `gz upgrade` — surface-only refresh (no manifest, no hooks, --surface filter)

### Step 7: Write `features/upgrade.feature`

Author behave scenarios covering each REQ with `@covers` tags:

```gherkin
Feature: gz upgrade surface-only refresh

  @covers REQ-0.0.32-14-01
  Scenario: gz upgrade is a registered subcommand
    ...
  @covers REQ-0.0.32-14-02
  Scenario: --surface filter rejects unknown surface name
    ...
  @covers REQ-0.0.32-14-02
  Scenario: --surface filter processes only named surfaces
    ...
  @covers REQ-0.0.32-14-03
  Scenario: EDITED artifacts reported and left unchanged without --force
    ...
  @covers REQ-0.0.32-14-04
  Scenario: --force overwrites EDITED artifacts with audit trail
    ...
  @covers REQ-0.0.32-14-05
  Scenario: --dry-run reports changes but writes nothing
    ...
  @covers REQ-0.0.32-14-06
  Scenario: bootstrap retrofit scaffolds surfaces when .gzkit/surface absent
    ...
  @covers REQ-0.0.32-14-07
  Scenario: idempotent second run exits 0 with zero STALE/EDITED
    ...
  @covers REQ-0.0.32-14-08
  Scenario: manifest.json is not mutated by gz upgrade
    ...
```

### Step 8: Verify

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz cli audit
uv run gz upgrade --help
uv run gz covers OBPI-0.0.32-14-gz-upgrade-subcommand --json
```

## Pre-Execution Notes

**Destination-in-mind disclosure:** Before writing this plan, the intended
approach was: reuse init_cmd's three-state helpers, register upgrade alongside
init in parser_governance.py, and avoid duplicating detection logic. This
was determined by reading init_cmd.py first.

**Rejected alternatives:**
1. Duplicate the three-state detection into upgrade.py — rejected because the
   brief's Discovery Checklist explicitly says "factor shared helpers into a
   module both commands can import; do NOT duplicate the three-state logic."
2. Register in parser_maintenance.py instead of parser_governance.py — rejected
   because `gz upgrade` is semantically adjacent to `gz init` (both are
   adopter-side surface management verbs), so governance parser is the right
   home.
3. Re-use scaffold_core_* functions — rejected because those functions run
   scaffolder hooks and modify other state beyond surface content copy.
   `gz upgrade` must stay narrower.

## Acceptance Check

Plan covers all 9 REQs from OBPI brief. All touched files are within the
corrected Allowed Paths. No denied paths are touched. Three-state detection
reused from init_cmd.py (not duplicated).
