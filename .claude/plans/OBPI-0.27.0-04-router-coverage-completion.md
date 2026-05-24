# Plan: OBPI-0.27.0-04-router-coverage-completion

**OBPI:** OBPI-0.27.0-04-router-coverage-completion
**Parent ADR:** ADR-0.27.0-namespace-router-product-surface
**Lane:** Lite
**Date:** 2026-05-24

## Context

OBPIs 01-03 implemented the six namespace routers and the `gz validate --router-tables`
validator. During that work, 16 previously-unrouted skills were pre-emptively routed
into existing routers — but in the wrong places, creating duplicates and misplacements
that violate REQ-04 (uniqueness invariant). The validator currently returns exit 0 only
because skills are "reachable" (Direction 2 is advisory for unrouted, not for
duplicates); it does not check uniqueness.

This OBPI: (1) creates the 7th gz-chores router, (2) corrects all skill placements to
match the ADR's router table, (3) removes all duplicates.

**Current duplicates and misplacements detected:**
- `gz-justify` + `gz-plan-audit`: in gz-governance (wrong) → must move to gz-workflow
- `gz-competitor-radar`: in gz-governance (wrong) → must move to gz-project
- `gz-foundation-triage`: in gz-governance (wrong) → must move to gz-chores
- `gz-chore-runner` + `gz-cli-audit` + `gz-pythonic-pattern-detect` + `gz-pythonic-pattern-apply`: in gz-quality (wrong) → must move to gz-chores
- `gz-check-config-paths` + `gz-deps-upgrade`: in gz-project (wrong) → must move to gz-chores
- `gz-state`: in BOTH gz-context and gz-project (duplicate) → remove from gz-project
- `gz-adr-closeout-ceremony`: in BOTH gz-governance and gz-workflow (duplicate) → remove from gz-workflow
- `gz-patch-release`: in BOTH gz-workflow and gz-manage (duplicate) → remove from gz-workflow
- `gz-migrate-semver`: in BOTH gz-governance and gz-manage (duplicate) → remove from gz-manage

## Files

**Create:**
- `.gzkit/skills/gz-chores/SKILL.md` — new 7th router (all 7 chore skills)

**Modify:**
- `.gzkit/skills/gz-workflow/SKILL.md` — add gz-justify + gz-plan-audit; remove gz-adr-closeout-ceremony (dup) + gz-patch-release (dup); bump skill-version + last_reviewed
- `.gzkit/skills/gz-project/SKILL.md` — add gz-competitor-radar; remove gz-state (dup) + gz-check-config-paths (→chores) + gz-deps-upgrade (→chores); bump
- `.gzkit/skills/gz-governance/SKILL.md` — remove gz-justify + gz-plan-audit (→workflow) + gz-competitor-radar (→project) + gz-foundation-triage (→chores); bump
- `.gzkit/skills/gz-quality/SKILL.md` — remove gz-chore-runner + gz-cli-audit + gz-pythonic-pattern-detect + gz-pythonic-pattern-apply (all →chores); bump
- `.gzkit/skills/gz-manage/SKILL.md` — remove gz-migrate-semver (dup; stays in gz-governance); bump

**Brief evidence:**
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-04-router-coverage-completion.md`

## Steps

1. **Create gz-chores/SKILL.md** — new router with YAML frontmatter (name, description,
   category: agent-operations, lifecycle_state: active, owner: gzkit-governance,
   last_reviewed: 2026-05-24, model: haiku, skill-version: 0.1.0) and `| Intent | Skill |`
   table routing: gz-chore-runner, gz-deps-upgrade, gz-foundation-triage,
   gz-pythonic-pattern-detect, gz-pythonic-pattern-apply, gz-check-config-paths, gz-cli-audit.

2. **Update gz-workflow/SKILL.md** — add `| justify | \`gz-justify\`` and
   `| plan audit | \`gz-plan-audit\`` rows; remove `gz-adr-closeout-ceremony` and
   `gz-patch-release` rows (duplicates: both already in gz-governance and gz-manage
   respectively). Bump skill-version minor (0.1.0 → 0.2.0 or current+minor).
   Set last_reviewed: 2026-05-24.

3. **Update gz-project/SKILL.md** — add `| competitor radar | \`gz-competitor-radar\``
   row; remove gz-state (stays in gz-context), gz-check-config-paths (→gz-chores),
   gz-deps-upgrade (→gz-chores) rows. Bump skill-version minor. Set last_reviewed: 2026-05-24.

4. **Update gz-governance/SKILL.md** — remove gz-justify, gz-plan-audit,
   gz-competitor-radar, gz-foundation-triage rows. Bump skill-version minor.
   Set last_reviewed: 2026-05-24.

5. **Update gz-quality/SKILL.md** — remove gz-chore-runner, gz-cli-audit,
   gz-pythonic-pattern-detect, gz-pythonic-pattern-apply rows. Bump skill-version minor.
   Set last_reviewed: 2026-05-24.

6. **Update gz-manage/SKILL.md** — remove gz-migrate-semver row (stays in gz-governance
   per REQ-02). Bump skill-version minor. Set last_reviewed: 2026-05-24.

7. **Run sync** — `uv run gz agent sync control-surfaces` to propagate all canonical
   edits to pkg copy and vendor mirrors.

8. **Verify uniqueness** — programmatically scan all 7 routers' intent tables and
   confirm no skill slug appears in more than one router.

9. **Verify validator** — `uv run gz validate --router-tables` must return exit 0
   with 0 errors (already passes; must stay passing after reorganization).

10. **Run quality gates** — `uv run gz arb ruff`, `uv run gz arb typecheck`,
    `uv run gz arb step --name unittest -- uv run -m unittest -q`.

## Verification

```bash
# Validator: 0 errors
uv run gz validate --router-tables

# Canonical file created
test -f .gzkit/skills/gz-chores/SKILL.md

# All 7 chore skills in gz-chores
for s in gz-chore-runner gz-deps-upgrade gz-foundation-triage gz-pythonic-pattern-detect gz-pythonic-pattern-apply gz-check-config-paths gz-cli-audit; do
  grep -q "$s" .gzkit/skills/gz-chores/SKILL.md || echo "MISSING: $s"
done

# Target routers have correct skills
grep -q gz-justify .gzkit/skills/gz-workflow/SKILL.md
grep -q gz-plan-audit .gzkit/skills/gz-workflow/SKILL.md
grep -q gz-competitor-radar .gzkit/skills/gz-project/SKILL.md
grep -q gz-adr-evaluate .gzkit/skills/gz-governance/SKILL.md
grep -q gz-migrate-semver .gzkit/skills/gz-governance/SKILL.md
grep -q gz-obpi-lock .gzkit/skills/gz-governance/SKILL.md
grep -q gz-obpi-simplify .gzkit/skills/gz-quality/SKILL.md
grep -q gz-issue-file .gzkit/skills/gz-manage/SKILL.md

# No duplicates (uniqueness invariant)
# scan all routers and count per-slug appearances — must all be 1

# Quality
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Notes

- gz-context/SKILL.md is in Denied Paths — no changes needed (gz-state stays there)
- The validator does NOT check uniqueness (only reachability); uniqueness is verified
  manually in step 8
- Byte budget: GSD reference 696–1131 bytes; gz-chores should fall within this range
  (~7 skills × ~60 bytes/skill + frontmatter ≈ ~600-900 bytes total)
- skill-version bump is minor (governance procedure change per skill-surface-sync.md)
