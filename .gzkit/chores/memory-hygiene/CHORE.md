# Memory Hygiene

- **Version:** 1.1.0
- **Lane:** Lite
- **Slug:** `memory-hygiene`
- **Vendor:** `claude` (Claude Code only)

## Overview

Claude Code auto-memory is machine-local and cannot be made project-portable. In a governed
project like gzkit, this creates a shadow persistence layer that competes with version-controlled
artifacts (skills, rules, the agent contract).

The failure mode: corrections arise, the model writes a memory instead of fixing the governed
source. The memory is not portable, not shared, and not auditable.

## Policy

- `user` and `reference` memories are legitimate — leave them alone
- `feedback` and `project` memories that encode process are migration candidates for a governed
  source — see § Migration targets for which source, because the agent-contract surfaces are
  rendered and are never the edit target
- Stale memories (references to nonexistent files/functions, outdated dates) should be removed

## Migration targets (binding — never edit a rendered surface)

`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` and everything under
`.claude/**` are **generated**: `gz agent sync control-surfaces` composes them from
the sources below (`src/gzkit/sync_surfaces.py`). An edit applied to the render is
reverted by the next sync and leaves no trace of the correction it was meant to
carry — the same defect GHI #817 found in `instructions-files-diet`.

| Correction kind | Edit this source | Then |
|---|---|---|
| Operator canon / durable behavioral rule | the corpus, via `uv run gz content remember` | `gz content compose` → operator attests at Gate 5 |
| Project-local agent-contract prose | `.gzkit/agents.local.md` | `uv run gz agent sync control-surfaces` |
| Scoped rule | `.gzkit/rules/<name>.md` (canonical) — **never** `.claude/rules/` | `uv run gz agent sync control-surfaces` |
| Skill procedure | `.gzkit/skills/<name>/SKILL.md` (canonical) — **never** `.claude/skills/` | `uv run gz agent sync control-surfaces` |

## Workflow

### 1. Scan

```bash
ls ~/.claude/projects/-Users-*/memory/*.md
```

### 2. Classify

Read each memory file and classify by frontmatter `type`:

| Type | Action |
|------|--------|
| `user` | Keep (legitimate personalization) |
| `reference` | Keep (external system pointers) |
| `feedback` | Review — if it encodes process, migrate per § Migration targets |
| `project` | Review — if outdated or encoded in code, remove |

### 3. Migrate or Remove

For each migration candidate:

1. Identify the governed **source** that should hold the correction, per § Migration targets
2. Apply the correction to that source — never to a rendered surface
3. Re-render if the source feeds one (`uv run gz agent sync control-surfaces`)
4. Remove the memory file
5. Update MEMORY.md index

### 4. Validate

```bash
uv run gz validate --invariant-coherence
uv run -m unittest -q
```

`--invariant-coherence` re-renders and byte-compares against the committed surfaces
(ADR-0.0.37). It is the check that fails when a correction was applied to a render
instead of its source, so it runs first.

## Acceptance Criteria

| # | Criterion | Command |
|---|-----------|---------|
| 1 | No memory postdates the last hygiene pass | `uv run python .gzkit/chores/memory-hygiene/check_memory_drift.py` |
| 2 | Tests pass (precondition, not this chore's discriminator) | `uv run -m unittest -q` |

Criterion 1 is the chore's own witness: it resolves the memory directory from the
checkout path, then fails when any memory file is newer than `proofs/CHORE-LOG.md`.
A memory written after the last pass is the shadow-persistence this chore exists to
catch. An absent memory directory passes — the surface is vendor-specific and
machine-local, so its absence is not a finding.

Two earlier shapes were green by construction and are retired (GHI #743):
`test -f .../MEMORY.md` witnessed that an index was written once, never that it still
described the surface — and it hardcoded one maintainer's absolute path, so every
adopter's copy checked a file on a machine they do not own. The criterion that
replaced it observed the instructions-files budget, a different surface entirely.

## Evidence Commands

```bash
uv run python .gzkit/chores/memory-hygiene/check_memory_drift.py
uv run -m unittest -q
```
