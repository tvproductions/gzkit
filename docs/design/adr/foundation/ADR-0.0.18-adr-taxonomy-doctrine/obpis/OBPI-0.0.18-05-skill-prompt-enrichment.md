---
id: OBPI-0.0.18-05-skill-prompt-enrichment
parent: ADR-0.0.18
item: 5
lane: Lite
status: Draft
---

# OBPI-0.0.18-05-skill-prompt-enrichment: skill prompt updates for --kind

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #5 — "Skill prompt enrichment"

**Status:** Draft

## Objective

Update `.gzkit/skills/gz-plan/SKILL.md` and `.gzkit/skills/gz-adr-create/SKILL.md` so their interview prompts ask for `--kind` explicitly, show the concise decision heuristic inline, and link to the concepts page (OBPI-01). Skill versions are bumped per `.gzkit/rules/skill-surface-sync.md`; mirrors (`.claude/skills/`, `.github/skills/`) are regenerated via `gz agent sync control-surfaces`.

## Lane

**Lite** — skill-layer updates, no CLI contract change.

## Allowed Paths

- `.gzkit/skills/gz-plan/SKILL.md`
- `.gzkit/skills/gz-adr-create/SKILL.md`
- `.claude/skills/gz-plan/SKILL.md` (mirror — regenerated via sync)
- `.claude/skills/gz-adr-create/SKILL.md` (mirror — regenerated via sync)
- `.github/skills/gz-plan/SKILL.md` (mirror)
- `.github/skills/gz-adr-create/SKILL.md` (mirror)
- `.agents/skills/gz-plan/SKILL.md` (mirror)
- `.agents/skills/gz-adr-create/SKILL.md` (mirror)

## Denied Paths

- Any other skill — scope is strictly `gz-plan` and `gz-adr-create`
- CLI command implementations (ADR-0.0.17 scope)
- Concept/runbook/policy pages (OBPI-01, 02, 03 of this ADR)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Both skills' interview sections prompt for `--kind` with the concise heuristic: "foundation (app/system invariant, always 0.0.x) / feature (release-carrying capability) / pool (noted, not committed)".
2. REQUIREMENT: Both skills cite `docs/user/concepts/adr-taxonomy.md` by path at the prompt for operators wanting deeper context.
3. REQUIREMENT: `skill-version` in frontmatter is bumped (minor, per governance-rule-change classification in `.gzkit/rules/skill-surface-sync.md` § Version discipline).
4. REQUIREMENT: `uv run gz agent sync control-surfaces` runs clean after edits — no drift between canonical `.gzkit/skills/` and mirrors.
5. REQUIREMENT: The skill prompts NEVER embed a default for `--kind`. The whole point of the no-default CLI design (ADR-0.0.17 OBPI-02 REQ-01) is to force an informed choice; skills must preserve that forcing function.
6. REQUIREMENT: Body language in the skill respects the vocabulary locked in ADR-0.0.17 — `pool`, `foundation`, `feature` only. No residual informal terms like "normal ADR", "work ADR", "versioned ADR".

## Verification

```bash
uv run gz agent sync control-surfaces
# Confirm no drift output; diff shows frontmatter version bump + prompt updates
uv run gz validate --skill-alignment  # skill must still have a wielded CLI verb
```

## Evidence

- Skill diff showing prompt additions + version bump
- Sync transcript showing no drift
- `gz validate --skill-alignment` clean output
- ARB receipts

## REQ Coverage

- REQ-0.0.18-05-01 through REQ-0.0.18-05-06
