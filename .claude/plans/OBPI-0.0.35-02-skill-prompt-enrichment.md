# Plan: OBPI-0.0.35-02-skill-prompt-enrichment

## OBPI Reference

`OBPI-0.0.35-02-skill-prompt-enrichment` — parent ADR: `ADR-0.0.35-foundation-feature-invariance-test`

## Context

OBPI-01 (concept page) has landed at `docs/user/concepts/foundation-feature-invariance-test.md`.
OBPI-02 enriches the four kind-deciding skills so every kind-prompt section cites the invariance test inline alongside the existing heuristic, the hexagonal-ports lens, and a link to the OBPI-01 concept page.

## Pre-Implementation Disclosures (Plan-Before-Exploration Ordering)

**Destination-in-mind:** Before planning, I had already read the four skill files and identified the exact kind-prompt sections in each. My intended approach was to surgically enrich each section with three additions: verbatim test quote, hexagonal-ports lens one-liner, and forward link to the concept page.

**Rejected alternatives:**
- Replacing the existing heuristic text with the invariance test: rejected — the OBPI explicitly requires that both coexist (the test is a sharper resolution rule, not a replacement).
- Adding a new dedicated section in each skill instead of enriching the existing kind-prompt section: rejected — the OBPI requires enrichment at the section that prompts for or describes `--kind`, not a standalone section elsewhere.
- Using a shared include/macro so the test wording is DRYed: rejected — skills are standalone markdown; no DRY mechanism exists.

## Files Touched

- `.gzkit/skills/gz-plan/SKILL.md` — Step 6 kind-prompt enrichment; skill-version 1.1.1 → 1.2.0
- `.gzkit/skills/gz-adr-create/SKILL.md` — Tier 1 kind question enrichment; skill-version 6.2.0 → 6.3.0
- `.gzkit/skills/gz-design/SKILL.md` — Step 5 canonical ADR kind confirmation enrichment; skill-version 1.2.1 → 1.3.0
- `.gzkit/skills/gz-adr-promote/SKILL.md` — Options section kind enrichment; skill-version 1.2.0 → 1.3.0
- Generated mirrors (do not edit directly):
  - `.claude/skills/gz-plan/SKILL.md`
  - `.claude/skills/gz-adr-create/SKILL.md`
  - `.claude/skills/gz-design/SKILL.md`
  - `.claude/skills/gz-adr-promote/SKILL.md`
  - `.github/skills/gz-plan/SKILL.md`
  - `.github/skills/gz-adr-create/SKILL.md`
  - `.github/skills/gz-design/SKILL.md`
  - `.github/skills/gz-adr-promote/SKILL.md`

## Steps

1. Verify OBPI-01 deliverable exists: `docs/user/concepts/foundation-feature-invariance-test.md`
2. Read each canonical skill to identify kind-decision section locations
3. For each skill, add the three enrichment elements:
   - Verbatim test: "Foundation = without it, we wouldn't be doing the project."
   - Hexagonal-ports lens: "ports point to invariance; plugs are features"
   - Link forward to `docs/user/concepts/foundation-feature-invariance-test.md`
4. Bump each skill's `skill-version` (minor bump per `.claude/rules/skill-surface-sync.md`)
5. Run `uv run gz agent sync control-surfaces` to propagate to mirrors
6. Verify enrichment is in canonical and mirrors; verify skill-versions bumped
7. Run `uv run gz lint` to confirm lint clean

## Verification

```bash
# Verbatim test present in each canonical skill
for skill in gz-design gz-plan gz-adr-create gz-adr-promote; do
  grep -F "Foundation = without it, we wouldn't be doing the project" \
    ".gzkit/skills/$skill/SKILL.md" \
    || echo "MISSING in $skill"
done

# Concept-page link present in each
for skill in gz-design gz-plan gz-adr-create gz-adr-promote; do
  grep -F "foundation-feature-invariance-test" \
    ".gzkit/skills/$skill/SKILL.md" \
    || echo "MISSING link in $skill"
done

# Mirror sync clean
uv run gz agent sync control-surfaces

# ARB receipts (foundation-kind brief-level attestation)
uv run gz arb ruff
```

## Notes

- Scope collisions with ADR-0.0.43/OBPI-0.0.43-09, ADR-0.0.18/OBPI-0.0.18-05, and ADR-0.0.42/OBPI-0.0.42-04 are advisory (not fail-closed); those OBPIs are in-flight for different enrichment angles; this OBPI's edits are purely additive within the kind-decision sections and do not conflict.
- ADR-0.0.18's existing link in gz-plan and gz-adr-create is preserved per REQ-04 (the test coexists with the heuristic, it does not replace it).
