# CHORE: Skill Authoring Quality (Anthropic Best Practices)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `skill-authoring-quality`

---

## Overview

Audit SKILL.md files against Anthropic's published skill authoring best practices. Detect frontmatter drift, description quality issues, verbosity, content duplication with AGENTS.md, and mirror sync drift.

## Policy and Guardrails

- **Lane:** Lite — audit and analysis, fixes are behavior-preserving
- Only `name` + `description` are loaded at startup; SKILL.md body is on-demand
- Descriptions are the "search index" — quality directly impacts skill selection
- Fixes must preserve skill behavior (same commands, same procedures)

## Workflow

### 1. Frontmatter Compliance

Check required fields (`name`, `description`) and flag non-standard fields.

### 2. Description Quality

- Third-person voice (not "I can" or "you should")
- Length <1024 chars (flag >800)
- Must include "when to use" triggers (Use when/Use to/Use for)

### 3. Body Size Audit

Flag SKILL.md files exceeding 400 lines (500-line ceiling).

### 4. Content Duplication

Identify skills re-embedding governance doctrine from AGENTS.md.

### 5. Mirror Sync

Verify `.github/skills/` and `.claude/skills/` are in sync.

### 6. Validate

```bash
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run gz validate --surfaces > ops/chores/skill-authoring-quality/proofs/validate-surfaces.txt
```

---

**End of CHORE: Skill Authoring Quality**
