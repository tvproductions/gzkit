---
name: gz-agent-sync
persona: main-session
description: Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-09-27
metadata:
  skill-version: "1.3.0"
model: haiku
---

# gz agent sync control-surfaces

## Overview

`gz agent sync control-surfaces` (`_run_agent_control_sync` in
`src/gzkit/commands/tidy.py`) regenerates every derived control surface from
canon through `sync_all` in `src/gzkit/sync_surfaces.py`:

- the manifest at `paths.manifest`, and the Codex baseline `.codex/config.toml`
  when it is missing or empty;
- when Codex is enabled, or `.gzkit.json` declares no vendors, `.codex/hooks.json`
  and `.codex/agents/*.toml` (see § Codex delivery);
- in gzkit's own repository only, the wheel copies under `src/gzkit/<surface>/`
  for skills, rules, personas, templates and canonical-class chores;
- `AGENTS.md`, played back byte-for-byte from its committed rendition, or
  bootstrapped from the `agents` template when none is committed. Sync never
  recomposes it: changing that canon goes through the content skills;
- when Claude is enabled, `CLAUDE.md`, the rules under `paths.claude_rules`,
  `.claude/settings.json` (gzkit hook phases merged into operator-added ones)
  and the Claude hook scripts;
- `.github/discovery-index.json` and the nested `AGENTS.md` files;
- skill mirrors at `paths.claude_skills` and `paths.codex_skills`, and persona
  mirrors under each enabled Claude and Codex `surface_root`. `vendor_skill_map`
  in `src/gzkit/sync_skills.py` is the authority for which vendors get a skill
  mirror; OpenCode has none.

A real run first runs the canonical preflight (`refuse_on_sync_blockers`,
`src/gzkit/commands/sync_guard.py`) and exits 1 before writing anything when a
canonical skill is corrupt: a missing `SKILL.md` or frontmatter, a bad
identity field, a malformed date, version or lifecycle value. A stale
`last_reviewed` never blocks (GHI #1099). After writing, it appends an
`agent_sync_completed` ledger event, then re-runs the skill audit and exits 1
if any blocking audit issue other than a stale review remains; the mirrors
are already written by then. Mirror copying only adds and updates files:
mirror-only paths are listed under "Recovery required" and left in place.

Every run prints an `Updated <path>` line for each surface that always
reports, such as the manifest, `AGENTS.md`, `CLAUDE.md`, settings, rules,
hooks and personas, whether its bytes changed or not. Skill mirror files are
listed only when they change.

`--dry-run` renders the same sync into a capture sink (`plan_sync_all`) and
writes nothing, the ledger included. It lists the same paths a real run would
report, not only the changed ones. It skips the preflight, so a plan it prints
can still be refused by the real run.

## Workflow

1. Edit canon only: `.gzkit/skills/`, `.gzkit/rules/`, `.gzkit/personas/`,
   `.gzkit/templates/`, `.gzkit/chores/`, `.gzkit/agents/`. Never edit a mirror
   or `src/gzkit/<surface>/`.
2. Preview with `uv run gz agent sync control-surfaces --dry-run`, then run it
   without the flag.
3. On a preflight refusal (exit 1, "Sync preflight failed"), fix each listed
   canonical skill, then run `uv run gz skill audit --json` and re-run the sync.
4. On a post-check failure (exit 1, "Sync post-check failed"), fix each listed
   error and re-sync.
5. When sync reports stale mirror-only paths, follow the recovery it prints:
   - `uv run gz skill audit --json`
   - remove the listed stale mirror-only paths
   - `uv run gz agent sync control-surfaces`
   - `uv run gz skill audit`
6. Report the exit code, the changed paths, and any recovery done.

## Validation

- `uv run gz validate --surfaces` reports no drift after the sync.
- `uv run gz skill audit` shows no mirror-parity error.

## Codex delivery

When Codex is enabled, sync recovers native `.codex/hooks.json` registrations in
projects carrying `scripts/session_orientation.py`, and renders registered
`.gzkit/agents/roles.json` role bodies into `.codex/agents/*.toml`. Edit the
canonical role body or `src/gzkit/hooks/codex.py` producer, then preview and sync.
Preserve operator-owned hooks and native role metadata. The generated hook status
labels identify owned handlers; customized unmarked role bodies remain user-owned.

Verify `uv run gz validate --surfaces --orientation-freshness`. This proves
delivery coherence, not native dispatch: Codex requires review of each new or
changed hook through `/hooks` before it runs. Report registration, trust, and
observed execution separately. The full parity design remains
`ADR-pool.vendor-alignment-codex`; syncing does not initiate its parked OBPIs.

## Common Rationalizations

These thoughts mean STOP — you are about to create canon/derived drift:

| Thought | Reality |
|---------|---------|
| "I edited `.claude/skills/foo/SKILL.md` directly — it's the runtime path anyway" | `.claude/` is a vendor mirror. The next sync overwrites it. Edit `.gzkit/skills/foo/SKILL.md` (canonical) and run sync. The instinct to edit the mirror is the bug. |
| "The mirrors look identical to canon — skip sync" | Only a sync regenerates the surfaces from canon, and running it on a synced tree changes no surface bytes. Skipping it after a skill edit leaves the drift in place. |
| "Sync will see my edit through the `skill-version` bump" | Sync copies canon bytes over every mirror and never compares versions; it only checks that the value is `X.Y.Z`. Bump the version anyway: `gz-skill-review` requires it, and it is how a reader tells the edit happened. |
| "Sync reported stale mirror-only paths — I'll deal with them next time" | Stale mirror paths mean the canonical source was deleted, renamed or retired. Leaving them means the old skill keeps loading. Run the recovery sequence now. |
| "I can skip `--dry-run`, this edit was small" | The dry-run lists every path the sync would report, before anything is written. It lists unchanged always-reported surfaces too, so read it for the unexpected paths. |
| "Manual copy from canonical to mirror is faster than sync" | Sync also writes the manifest, settings, hooks, nested `AGENTS.md` files and vendor-specific renderings. A manual copy gets the file and leaves the rest stale. |

## Red Flags

- Direct edits to any mirror: `.claude/`, `.agents/` (`paths.claude_skills`,
  `paths.codex_skills` and each vendor's `surface_root` in `.gzkit.json`), or
  `src/gzkit/<surface>/` in gzkit's own repository
- Skill edits without a `skill-version` bump
- Canonical files changed but the sync lists none of their mirrors (something
  is broken)
- Stale mirror-only paths reported and not cleaned up
- A mirror that differs from canon after a sync that exited 0
- Skipping sync because "the mirrors are fine"

## Example

```bash
uv run gz agent sync control-surfaces --dry-run
uv run gz agent sync control-surfaces
uv run gz validate --surfaces
```
