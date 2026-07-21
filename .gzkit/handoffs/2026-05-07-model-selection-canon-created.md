---
mode: CREATE
branch: main
timestamp: "2026-05-07T00:00:00Z"
agent: claude-code
---

<!-- Frontmatter added under GHI #709. This handoff predates the YAML
     frontmatter convention; its metadata lived in the bold body lines and
     the filename, so the validator that governs it could not parse it.
     Every field below is derived from this document or its filename —
     `adr_id` is omitted where the parent is not named, which is legal now.
     Body content is unchanged. -->

# Forward Hydration: Model Selection Canon

**Date:** 2026-05-07
**Status:** Integrated — all 67 skills declare model tier; 9 opus skills self-escalate
**Token constraint:** 20x max subscription hitting walls; model routing is now a core resource allocation strategy.

## What was done

Created `.gzkit/rules/model-selection.md` (0.1.0) with:
- Routing matrix (read-only → Haiku, design → Opus, etc.)
- Skill frontmatter directive: `model: {haiku,sonnet,opus}`
- Subagent effort levels: `light` → Haiku, `high` → Sonnet, `xhigh/max` → Opus
- Anti-patterns and rationale

**Why:** You need explicit guidance on when to use lower models across skills, rules, and subagents. Without it, you default to high/max everywhere and burn tokens.

## What's next (priority order)

1. **Skill frontmatter integration** — add `model:` directive to skill schema (`src/gzkit/schemas/skill.json`) and update all existing skills in `.gzkit/skills/` to declare their model tier.
   - Most routine skills (gz-register-adrs, gz-validate, gz-tidy) → `haiku`
   - Design/planning skills (gz-design, gz-plan, gz-adr-create) → `opus`
   - Search/explore skills (gz-adr-map, gz-complexity-distill) → `haiku`

2. **Sync mirrors** — run `uv run gz agent sync control-surfaces` after all skill edits to propagate `model:` to `.claude/skills/`, `.github/skills/`, etc.

3. **Update docs** — reference model-selection rule in:
   - `docs/governance/opus-tuning.md` (add "Model Selection" section linking to rule)
   - `AGENTS.md` § Behavior Rules (add "Use model-selection rule for all decision routing")
   - `.gzkit/rules/` index if one exists

4. **Audit subagent usage** — grep for `Agent(` calls in active skills and AGENTS.md; ensure all specify effort levels, not hardcoded models.

## Decision points for next session

- Should `model:` be required or optional in skill frontmatter? (Currently: required per rule.)
- Does skill SKILL.md need a `max-effort:` variant for when the skill can scale to harder problems?
- Should the routing matrix live in AGENTS.md as a reference section, or stay isolated in rules/?

## Current state

- Rule file: `.gzkit/rules/model-selection.md` (0.1.0)
- Schema update: **not yet done** (needs skill.json edit + validation)
- Skills frontmatter: **not yet updated** (100+ skills need `model:` added)
- Mirrors: **will sync after skills are updated**
- Docs: **reference only; not updated yet**

## Token economy impact (estimate)

- Each skill using Haiku instead of Opus for read-only/validation work: ~3k tokens/session saved
- Rough estimate: 30-40 skills could downgrade → **100-120k tokens/session freed** (or ~2-3 additional full design dialogues per session)

## Caveats

- Effort levels are heuristic, not mechanical. A "light" task that needs Opus reasoning should still use Opus.
- The routing matrix is initial canon (0.1.0). Adjust based on observed failure patterns.
- This rule does not apply to user-facing CLI commands (those should always use the best model available); it applies to internal automation (skills, subagents, validation gates).
