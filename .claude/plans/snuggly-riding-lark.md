# Plan: OBPI-0.0.18-05 — skill prompt enrichment for `--kind`

## Context

ADR-0.0.18 locks a three-kind taxonomy (`pool` / `foundation` / `feature`) and
binds each kind to a semver convention. ADR-0.0.17 landed the CLI side:
`gz plan create` and `gz adr promote` now require an explicit `--kind` with no
default — operators must make an informed choice. This OBPI updates the two
skill files that operators interact with when authoring ADRs (`gz-plan` and
`gz-adr-create`) so their interview prompts explicitly ask for `--kind`, show
the concise decision heuristic inline, and link to the concepts page for
deeper context. Without this, skills still ask for `--lane` and `--semver` but
leave the operator to discover `--kind` from the CLI error message — which
defeats the structured-interview pattern.

Brief: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/obpis/OBPI-0.0.18-05-skill-prompt-enrichment.md`
Lane: Lite.

## Files to modify

### 1. `.gzkit/skills/gz-plan/SKILL.md`

**Frontmatter:**

- Add a `metadata:` block with `skill-version: "1.0.0"` (gz-plan is currently
  unversioned; establishing the first tagged version satisfies the
  `.gzkit/rules/skill-surface-sync.md` "bump on every edit" rule for the
  initial case, and places gz-plan in the same shape as
  `gz-adr-promote`/`gz-design`).

**Body — `## Workflow` section:**

- Between existing step 3 ("confirm target context, IDs, and lane assumptions")
  and step 4 (`uv run gz plan`), insert a `--kind` interview prompt step
  requiring the operator to explicitly choose `foundation` / `feature` / `pool`
  with the concise heuristic inline and a pointer to
  `docs/user/concepts/adr-taxonomy.md`.
- Renumber the subsequent steps (duplicate 3/4 numbering already present in the
  file is pre-existing; fix incidentally only if an adjacent line is touched).
- Ensure the prompt surfaces `--kind` as required-no-default. Never embed a
  default value (REQ-05 forcing function).

### 2. `.gzkit/skills/gz-adr-create/SKILL.md`

**Frontmatter:**

- Bump `metadata.skill-version` from `"6.0.3"` → `"6.1.0"` (minor — governance
  rule / procedure change per the skill's own versioning covenant and
  `.gzkit/rules/skill-surface-sync.md`).

**Body — `### Step 0: Interview` → `#### Question Protocol` → `**Tier 1 — ADR Pro-Forma**` list:**

- Add a new Tier 1 question "**What kind of ADR is this?**" that:
  - Forces a choice between `foundation` / `feature` / `pool`
  - Shows the heuristic inline: `foundation (app/system invariant, always 0.0.x) / feature (release-carrying capability) / pool (noted, not committed)`
  - Points to `docs/user/concepts/adr-taxonomy.md` for deeper context
  - Notes that `--kind` has no default — the operator must choose (REQ-05)
- Update the surrounding prose about "deducible fields" (currently listing `id, title, semver, lane, parent`) so `--kind` is NOT listed as deducible — kind is a substantive design question, not a mechanical field.

**Vocabulary sweep (REQ-06):**

- Grep both edited files for informal terms (`normal ADR`, `work ADR`,
  `versioned ADR`) and replace with `foundation` / `feature` / `pool`. Current
  reading of both files shows no occurrences, so this is a belt-and-suspenders
  check done during the edit pass, not a separate step.

## Mirrors

The Allowed Paths list in the brief includes mirrors under `.claude/skills/`,
`.github/skills/`, and `.agents/skills/`. Per
`.gzkit/rules/skill-surface-sync.md`: never edit mirrors directly. The sync
step below regenerates them from canonical.

## Post-edit sync and verification

```bash
uv run gz agent sync control-surfaces
uv run gz validate --skill-alignment
uv run gz arb ruff                               # lint-clean
uv run gz arb step --name unittest -- uv run -m unittest -q   # tests green
```

Expected: sync reports no drift after edits; skill-alignment passes; lint and
unittest receipts produced for Stage 4 evidence citations.

## Verification (brief-derived)

Each REQ maps to a mechanical check:

- REQ-0.0.18-05-01 (both skills prompt for `--kind` with heuristic): grep both
  canonical skill files for the heuristic string fragments.
- REQ-0.0.18-05-02 (both skills cite `docs/user/concepts/adr-taxonomy.md`):
  grep both canonical skill files for the path.
- REQ-0.0.18-05-03 (`skill-version` bumped): diff frontmatter.
- REQ-0.0.18-05-04 (sync clean): `uv run gz agent sync control-surfaces`
  output shows no divergent mirrors after edits.
- REQ-0.0.18-05-05 (no default for `--kind`): grep both canonical files — no
  line proposes a default kind value.
- REQ-0.0.18-05-06 (vocabulary respected): grep for `normal ADR`, `work ADR`,
  `versioned ADR` in both files — zero hits.

REQ → `@covers` parity: this OBPI is skill-file-only; no unit tests are
changed or added. The skill-alignment validator (`uv run gz validate
--skill-alignment`) is the mechanical test. REQ-0.0.18-05-01 through -06 are
documentation REQs covered by a single `@covers` anchor on an existing
skill-alignment test if one exists, or recorded as "verified by
`gz validate --skill-alignment` and grep" in the Stage 4 evidence table if not.
Stage 3 Phase 1b will surface any gap mechanically; handle it there rather
than inventing coverage up-front.

## Out of scope

- CLI implementation changes (ADR-0.0.17 scope, already landed)
- Concepts page edits (OBPI-01 scope)
- Runbook or policy page edits (OBPI-02/03 scope)
- Any other skill
