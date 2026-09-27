# gz agent sync control-surfaces

Regenerate agent control surfaces from canonical governance state.

## Usage

```bash
gz agent sync control-surfaces [--dry-run]
```

## One Canonical Source, Two Derived Families (OBPI-0.0.32-08)

`gz agent sync control-surfaces` propagates `.gzkit/<surface>/` (the authored
canonical source-of-truth) to **both** derived surface families in a single
invocation:

1. **Wheel-shipping byte-parity copy** — `src/gzkit/<surface>/` for every
   dual-surface family (skills, rules, personas, templates, chores canonical
   class only). Active only in gzkit's own dev repo where
   `src/gzkit/<surface>/__init__.py` exists.

2. **Vendor mirrors** — configured delivery paths for skills, rules and personas.
   Read `.gzkit.json` for enabled vendors and paths. Skills use `claude_skills`
   and `codex_skills`; Claude rules use `claude_rules`; personas use each
   supported vendor's `surface_root`. Retired vendor directories are not current
   delivery targets.

No separate `cp` step is needed. Edit `.gzkit/<surface>/`, bump the version
marker, run sync once (closes GHI #449).

### Surface families covered

| Canonical source | Pkg copy (wheel) | Vendor mirrors |
|-----------------|------------------|----------------|
| `.gzkit/skills/<slug>/SKILL.md` | `src/gzkit/skills/<slug>/SKILL.md` | Configured `claude_skills` / `codex_skills` (defaults `.claude/skills/` / `.agents/skills/`) |
| `.gzkit/rules/<slug>.md` | `src/gzkit/rules/<slug>.md` | Configured `claude_rules` (default `.claude/rules/`) |
| `.gzkit/personas/<slug>.md` | `src/gzkit/personas/<slug>.md` | Supported vendors' configured `<surface_root>/personas/` (transformed) |
| `.gzkit/templates/<name>.md` | `src/gzkit/templates/<name>.md` | (none) |
| `.gzkit/chores/<slug>/` (canonical class) | `src/gzkit/chores/<slug>/` (canonical only) | (none) |
| `.gzkit/agents/roles.json` + registered Markdown bodies | (project-local opt-in) | `.codex/agents/*.toml` (body transformed; native metadata preserved) |
| `src/gzkit/hooks/codex.py` + repository orientation script | Python producer | `.codex/hooks.json` (native matcher groups) |

The same pass also writes the manifest, the Codex baseline `.codex/config.toml`
(only when missing or empty), `AGENTS.md` (playback of the committed
rendition), and, when Claude is enabled, `CLAUDE.md`, `.claude/settings.json`
and the Claude hook scripts, then `.github/discovery-index.json` and the
nested `AGENTS.md` files.

Re-running on freshly-synced state changes no surface bytes (idempotent). Each
real run still appends one `agent_sync_completed` ledger event; `--dry-run`
appends none.

### Codex interim delivery

For enabled Codex projects carrying `scripts/session_orientation.py`, sync
registers orientation and shared handoff advisement on startup, resume, clear,
and compaction, plus the shared verification exit-code guard on shell calls.
It migrates the old command-array hook format and preserves unrelated handlers.
The generated `statusMessage` labels identify the owned handlers for subsequent
repair. Projects without the orientation script receive no dangling registration.

Registered role bodies come from `.gzkit/agents/`; captured legacy fingerprints
permit the initial migration. Generated bodies track canonical changes while
existing TOML metadata and customized unmarked roles remain intact. No registry
means no role writes. Existing nonempty Codex configuration remains preserved,
including model, sandbox, and document-budget settings.

Native Codex hook review remains necessary after generation: `/hooks` lists each
definition and its trust status. A coherent file is not evidence of automatic
execution. See the [interim parity record](../../governance/codex-interim-parity-2026-09-12.md)
for measured support and the work still owned by the pool ADR.

## Determinism Contract

For unchanged inputs, sync emits a deterministic updated-path list and stable operator output.

The list is not a list of changes. Skill mirror files appear only when their
bytes change; the manifest, `AGENTS.md`, `CLAUDE.md`, settings, rules, hooks
and persona mirrors appear on every run. `--dry-run` renders the sync into a
capture sink and prints the same list without writing anything.

## Persona Mirroring

Sync mirrors persona files from `.gzkit/personas/` to vendor surfaces
(Claude and Codex `surface_root` plus `/personas/`), respecting
vendor enablement configuration. Persona mirroring is automatic when the
canonical persona directory exists — no additional flags are needed.

## Manifest Paths

Sync writes the manifest at `paths.manifest` (default `.gzkit/manifest.json`)
and preserves authored manifest rule settings from that same file. Its reported
write list names the configured location. Explicitly configured source, test,
documentation and design roots override structure discovery; unspecified roots
retain discovery. A stale manifest at the default location is not a fallback
for a missing configured manifest.

## Fail-Closed Canonical Preflight

Before any mirror propagation, sync validates canonical `.gzkit/skills` integrity.

Blocking preflight failures include:

- missing canonical skill directories (without a legacy bootstrap candidate),
- missing `SKILL.md`,
- missing or invalid `SKILL.md` frontmatter identity fields,
- malformed `last_reviewed` values (not `YYYY-MM-DD`),
- invalid/missing deprecation metadata for `deprecated` or `retired` skills,
- malformed `lifecycle_state`, `metadata.skill-version` or other metadata values.

On failure, sync exits 1 before writing anything and prints recovery steps.
`--dry-run` does not run the preflight, so it can print a plan the real run
refuses.

After writing, sync re-runs the skill audit and exits 1 if a blocking issue
other than a stale review remains ("Sync post-check failed"); the writes are
already on disk.

Review **age** never blocks sync. A `last_reviewed` older than the policy threshold is a maintenance signal on canon, not corruption: sync propagates it, and neither the preflight nor the post-sync audit refuses on it. `gz skill audit` and Gate 3 report it and block (GHI #1099).

## Recovery Behavior (Non-Destructive)

Sync copies canonical files into mirrors but does not auto-delete mirror-only stale content.

When stale mirror-only paths exist, sync:

1. completes successfully,
2. emits a recovery warning with stale paths,
3. prints the manual cleanup protocol.

Related policy in `gz skill audit`:

- stale mirror-only paths are reported as non-blocking warnings
  (`SKA-MIRROR-DIR-UNEXPECTED`) by default,
- `--strict` escalates those warnings to blocking failures.

Manual recovery protocol:

```bash
uv run gz skill audit --json
# remove listed stale mirror-only paths
uv run gz agent sync control-surfaces
uv run gz skill audit
```

## Local vs Repo Config

Claude Code uses two settings files:

| File | Tracked | Contents |
|------|---------|----------|
| `.claude/settings.json` | Yes | Hooks, plugins — shared policy generated by sync |
| `.claude/settings.local.json` | No | Permissions, timeouts — machine-local convenience |

**Separation model:** `settings.json` is generated and deterministic. Local
overrides (allowed commands, domain allowlists, timeouts) go in
`settings.local.json`, which is `.gitignore`-d so each workstation can
customise without polluting shared policy.

**Example file:** `.claude/settings.local.example.json` shows the
permissions-only structure. Copy it to `settings.local.json` and edit.

**Drift detection:** After sync, call `detect_claude_settings_drift()` (from
`gzkit.sync`) to compare the on-disk `settings.json` against the generator
output. Returns a list of human-readable differences (empty = no drift).

## Examples

```bash
# Preview targets only
uv run gz agent sync control-surfaces --dry-run

# Apply sync and view recovery warnings (if any)
uv run gz agent sync control-surfaces
```

Codex paths from the observed 2026-09-12 sync output (excerpt):

```text
  Updated .codex/agents/git-sync-repo.toml
  Updated .codex/agents/implementer.toml
  Updated .codex/agents/narrator.toml
  Updated .codex/agents/quality-reviewer.toml
  Updated .codex/agents/spec-reviewer.toml
  Updated .codex/config.toml
  Updated .codex/hooks.json
```

`Updated` names managed delivery paths; unchanged bytes are not rewritten.
