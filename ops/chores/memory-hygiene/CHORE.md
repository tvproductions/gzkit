# Memory Hygiene

- **Version:** 1.0.0
- **Lane:** Lite
- **Slug:** `memory-hygiene`
- **Vendor:** `claude` (Claude Code only)

## Overview

Claude Code auto-memory is machine-local and cannot be made project-portable. In a governed
project like gzkit, this creates a shadow persistence layer that competes with version-controlled
artifacts (skills, rules, CLAUDE.md).

The failure mode: corrections arise, the model writes a memory instead of fixing the governed
source. The memory is not portable, not shared, and not auditable.

## Policy

- `user` and `reference` memories are legitimate — leave them alone
- `feedback` and `project` memories that encode process are migration candidates for skills/rules/CLAUDE.md
- Stale memories (references to nonexistent files/functions, outdated dates) should be removed

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
| `feedback` | Review — if it encodes process, migrate to skill/rule/CLAUDE.md |
| `project` | Review — if outdated or encoded in code, remove |

### 3. Migrate or Remove

For each migration candidate:

1. Identify the governed artifact that should hold the correction (skill, rule, CLAUDE.md)
2. Apply the correction to the governed artifact
3. Remove the memory file
4. Update MEMORY.md index

### 4. Validate

```bash
uv run -m unittest -q
```

## Acceptance Criteria

| # | Criterion | Command |
|---|-----------|---------|
| 1 | Tests pass | `uv run -m unittest -q` |
| 2 | MEMORY.md exists and is valid | `test -f ~/.claude/projects/-Users-jeff-Documents-Code-gzkit/memory/MEMORY.md` |

## Evidence Commands

```bash
uv run -m unittest -q
ls -la ~/.claude/projects/-Users-*/memory/
wc -l ~/.claude/projects/-Users-*/memory/MEMORY.md
```
