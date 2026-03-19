# CHORE: Skill Manifest Sync

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `skill-manifest-sync`

---

## Overview

Sync skill manifests across `.github/skills/`, `.claude/skills/`, and skill listings in `AGENTS.md`. Ensures skill count and naming consistency.

## Policy and Guardrails

- **Lane:** Lite — manifest synchronization, no contract changes
- `.github/skills/` is the reference directory
- `.claude/skills/` mirrors must stay in sync
- Use `gz agent sync control-surfaces` to regenerate mirrors

## Workflow

### 1. Audit

Check skill counts and naming across directories.

### 2. Sync

```bash
uv run gz agent sync control-surfaces
```

### 3. Validate

```bash
uv run gz validate --surfaces
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uv run gz validate --surfaces` | 0 |

## Evidence Commands

```bash
uv run gz validate --surfaces > ops/chores/skill-manifest-sync/proofs/validate-surfaces.txt
```

---

**End of CHORE: Skill Manifest Sync**
