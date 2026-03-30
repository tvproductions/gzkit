# CHORE: Skill Authoring Quality (Agent-First Best Practices)

**Version:** 2.0.0
**Lane:** Lite
**Slug:** `skill-authoring-quality`

---

## Overview

Audit SKILL.md files against agent-first skill authoring best practices. Skills are now primarily agent-called infrastructure — descriptions are routing signals, bodies encode domain reasoning, and outputs are contracts. This chore detects structural, semantic, and functional quality gaps.

## Policy and Guardrails

- **Lane:** Lite — audit and analysis, fixes are behavior-preserving
- Only `name` + `description` are loaded at startup; SKILL.md body is on-demand
- Descriptions are **routing signals** — they determine whether agents select the skill
- Skills that only wrap a CLI command with no added reasoning should be classified as **aliases**, not skills
- Fixes must preserve skill behavior (same commands, same procedures)

## Workflow

### 1. Frontmatter Compliance

Check required fields (`name`, `description`) and flag non-standard fields.

### 2. Description Quality (Routing Signal Assessment)

Descriptions are 80% of skill quality — they determine agent selection accuracy.

**Structural checks:**

- Single-line value (no YAML block scalars `|` or `>`)
- Third-person voice (not "I can" or "you should")
- Length <1024 chars (flag >800)

**Agent-contract checks:**

- Must include trigger phrases (Use when/Use to/Use for/Triggers on)
- Must declare what the skill produces (flag descriptions that name no artifact or outcome)
- Must not be a bare label — "Run X with Y" alone is insufficient; descriptions should state *when* to use and *what the agent gets*

**Classification:**

| Pattern | Classification |
|---------|---------------|
| Has triggers + output declaration + domain context | **Contract** (good) |
| Has triggers but no output/outcome declaration | **Partial** (needs output contract) |
| Names only the tool/command with no triggers | **Label** (needs rewrite) |

### 3. Body Quality (Domain Reasoning Assessment)

**Size thresholds:**

| Lines | Classification | Action |
|-------|---------------|--------|
| <30 | **Alias** — too thin to encode reasoning | Flag: evaluate whether this should be a skill or just a CLI help alias |
| 30–200 | **Normal** — expected range | Pass |
| 201–300 | **Heavy** — acceptable for orchestrators | Flag for review |
| >300 | **Oversized** — must decompose | Fail: extract reference material into companion files |

**Reasoning checks:**

- Has a reasoning/principles section (not just numbered steps)
- Has edge cases or failure modes documented
- Has output format specification for artifact-producing skills
- Has anti-patterns or "when NOT to use" section

**Classification:**

| Pattern | Classification |
|---------|---------------|
| Has reasoning + edge cases + output contract | **Domain-rich** (good) |
| Has some reasoning but missing edge cases or output | **Moderate** (needs enrichment) |
| Only has numbered steps or CLI commands | **Procedure-only** (needs reasoning) |

### 4. Stub Detection

Flag skills containing placeholder patterns:

- `Step 1` / `Step 2` / `Step 3` without substantive content
- `Example input` / `Example output`
- `Constraint 1` / `Constraint 2`
- `Skill 1` / `Skill 2`
- `TODO` / `TBD` / `FIXME` in body

Any stub detection is a **fail** — stubs fire in production with incomplete instructions.

### 5. Content Duplication

Identify skills re-embedding governance doctrine from AGENTS.md.

### 6. Mirror Sync

Verify `.github/skills/` and `.claude/skills/` are in sync.

### 7. Validate

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

## Scoring Summary

After audit, produce a table:

```
| Skill | Lines | Desc Class | Body Class | Stubs | Action Needed |
|-------|-------|-----------|-----------|-------|---------------|
```

Where:
- **Desc Class**: Contract / Partial / Label
- **Body Class**: Domain-rich / Moderate / Procedure-only / Alias
- **Stubs**: Y/N
- **Action Needed**: None / Enrich description / Add reasoning / Fix stub / Decompose

---

**End of CHORE: Skill Authoring Quality**
