---
id: skill-surface-sync
paths:
  - ".claude/**"
  - ".gzkit/skills/**"
  - ".gzkit/rules/**"
  - ".github/skills/**"
  - ".github/instructions/**"
description: Version-disciplined editing and sync for skill and rule surfaces
---

<!-- rule-version: 0.4.0 -->

# Skill & Surface Sync (gzkit)

> **Rule version:** `0.4.0` — bumped under OBPI-0.0.32-13 to add § Chores
> class-classifier, codifying the three-class chores surface model per
> ADR-0.0.32 § Named exceptions / Exception 2. Prior `0.3.0` content
> (OBPI-0.0.32-02 — bootstrap-from-wheel semantics) preserved.

## Non-negotiable rules

1. **Edit `.gzkit/` first.** The canonical source for skills is `.gzkit/skills/` and for rules is `.gzkit/rules/`. Always make changes there.
2. **Bump the version on every edit.** Increment the version marker before saving. The marker differs by surface:
   - **Skills** carry `skill-version:` in YAML frontmatter (validated by the skill schema).
   - **Rules** carry a body-level `<!-- rule-version: X.Y.Z -->` HTML comment immediately after the frontmatter, plus a visible `> **Rule version:** \`X.Y.Z\`` block quote with a one-sentence rationale. The rule frontmatter schema (`RuleFrontmatter` in `src/gzkit/rules.py`) is `extra="forbid"` and rejects a `skill-version:` key on rule files — that is intentional. The "skill-version" name on a non-skill artifact was a doctrine smell; the body-level marker resolves it.
3. **Run sync after every edit.** `uv run gz agent sync control-surfaces` propagates canonical state to all vendor mirrors.
4. **Never edit vendor mirrors directly.** `.claude/skills/`, `.claude/rules/`, `.github/skills/`, and `.github/instructions/` are generated outputs.

## Surface layout

| Canonical (edit here) | Vendor mirrors (generated, do not edit) | Version marker |
|-----------------------|-----------------------------------------|----------------|
| `.gzkit/skills/`      | `.claude/skills/`, `.github/skills/`    | Frontmatter `skill-version:` |
| `.gzkit/rules/`       | `.claude/rules/`, `.github/instructions/` | Body `<!-- rule-version: X.Y.Z -->` + visible block quote |

## Procedure

1. Edit the canonical file under `.gzkit/skills/` or `.gzkit/rules/`
2. Bump the version marker for the surface:
   - Skill: increment `skill-version:` in frontmatter
   - Rule: increment both the `<!-- rule-version: X.Y.Z -->` HTML comment and the visible `> **Rule version:** \`X.Y.Z\`` block quote
3. Run `uv run gz agent sync control-surfaces`
4. Verify sync output shows no stale or divergent mirrors
5. If sync reports stale mirror-only paths, follow the recovery in `/gz-agent-sync` skill documentation

## Version discipline

| Change type | Bump | Example |
|-------------|------|---------|
| GovZero framework major release | Major | 6.0.0 -> 7.0.0 |
| Governance rule or procedure change | Minor | 6.0.0 -> 6.1.0 |
| Tooling, template, or wording fix | Patch | 6.0.0 -> 6.0.1 |

The same bump table applies to both skills (frontmatter version) and rules (body-level version). The marker location differs; the semver semantics do not.

## Conflict resolution

When sync detects a version mismatch between canonical and a mirror, resolve via:

| Signal | What it tells you | How to check |
|--------|-------------------|--------------|
| Version marker (semver) | Intentional edit sequence | Skill: parse frontmatter `skill-version`. Rule: parse body `<!-- rule-version: ... -->` |
| Git commit hash / timestamp | Physical edit recency | `git log -1 --format=%H -- <path>` |

**Resolution rules:**

- **Mirror version > canonical version:** An agent edited the mirror directly. Promote the mirror content to canonical, then sync. The higher version wins.
- **Mirror version == canonical version, content differs:** An agent edited the mirror without bumping the version. Use git commit timestamp to determine recency; flag for human review.
- **Canonical version > mirror version:** Normal state — sync propagates canonical to mirrors.

Version is the primary signal (intentional semantic ordering). Commit hash is the tiebreaker (physical recency when versions match but content diverges).

## Anti-patterns

- Do not edit a skill without bumping its `skill-version` frontmatter
- Do not edit a rule without bumping its body-level `<!-- rule-version: ... -->` marker (and the visible block quote)
- Do not add `skill-version:` to rule frontmatter — the schema rejects it (GHI #307); use the body-level marker instead
- Do not edit `.claude/rules/` directly — sync overwrites it from `.gzkit/rules/`
- Do not edit `.claude/skills/` directly — edit `.gzkit/skills/` and sync
- Do not manually copy skill files between surfaces — use the sync command
- Do not skip sync because "both files look the same" — sync also updates manifests, registrations, and vendor-specific rendering

## Bootstrap semantics (`gz init`)

On first init in an adopter project, `gz init` populates
`.gzkit/skills/<slug>/SKILL.md` by copying canonical content from the wheel's
package surface (`importlib.resources.files("gzkit.skills")`). The package
surface is the *one-time bootstrap source*: after init, the adopter's
`.gzkit/skills/` is **the project canonical source-of-truth** for that
project, and the "Edit `.gzkit/` first" rule binds from that point forward.

Repair mode (re-running `gz init`) is idempotent: it adds new canonical
slugs delivered by the installed gzkit version without overwriting
operator-edited files (`skip_existing=True`). Use `--force` to wipe and
re-copy every canonical SKILL.md from the wheel.

`scaffold_core_skills` filters skills whose canonical SKILL.md declares
`lifecycle_state: retired` — retired slugs are not re-introduced on `gz init`
(hard cutover invariant, enforced by `tests/commands/test_skills.py::TestSkillCommands::test_init_scaffolds_adr_create_and_removes_adr_manager`).

As of OBPI-0.0.32-04, `gz init` also populates `.gzkit/rules/<slug>.md` by
copying canonical rule content from the wheel's package surface
(`importlib.resources.files("gzkit.rules")`). The same editing invariant
applies: after init, `.gzkit/rules/` is **the project canonical
source-of-truth** for rules in that adopter project. Rules scaffolding runs
after `sync_all` in the fresh init path so the initial control-surface sync
uses the instruction-sync path; subsequent `gz agent sync control-surfaces`
invocations render canonical rules to `.github/instructions/`. The
`AGENTS.md` file in the rules package is excluded from scaffolding (it is a
package-internal agent contract, not an operator-facing rule).

`gz init --update` (OBPI-0.0.32-05, not yet landed) will provide
version-aware refresh semantics for the adopter's `.gzkit/<surface>/` from
the wheel, with three-state IDENTICAL/STALE/EDITED detection so operator
edits are preserved across gzkit upgrades.

## Chores class-classifier

This section codifies the three-class chores surface model per ADR-0.0.32 § Named exceptions / Exception 2 (OBPI-0.0.32-13). Every file under `.gzkit/chores/<slug>/` or `src/gzkit/chores/<slug>/` falls into exactly one class:

| Class | Examples | Byte-parity | Notes |
|---|---|---|---|
| **canonical** | `CHORE.md`, `AGENTS.md`, `*.md` (outside `proofs/`), `acceptance.json`, `registry.json`, `scan.py` (authored tool scripts present at `.gzkit/` surface), `mapping.json`, `*.schema.json` | Required | `.gzkit/chores/` is direction-of-truth; sync propagates `.gzkit/ → src/gzkit/` |
| **package_only** | `__init__.py`, `__pycache__/**`, `README.md` (when no `.gzkit/` counterpart), `eval_feedback_cluster_lib.py`, `check_evidence.py` (Python modules with no `.gzkit/` counterpart) | Exempt | Package surface only; NEVER sync onto canonical side |
| **runtime_state** | `CHORE-LOG.md`, `proofs/<artifact>`, `.gitkeep` | Exempt | Each surface owns runtime-state independently; NEVER sync either direction |

**Default rules:**
- Unmatched `.md` files outside `proofs/` → **canonical**
- Files under `proofs/` → **runtime_state**
- `.py` files present at `.gzkit/chores/<slug>/` surface → **canonical** (authored tool scripts)
- `.py` files in `src/gzkit/chores/<slug>/` with no `.gzkit/` counterpart → **package_only**

**Conflict resolution** (mirror version > canonical version): promote mirror content to canonical, then re-sync. Apply § Conflict resolution above.

**Python helper:** `_classify_chore_file(path, *, project_root=None)` in `src/gzkit/chores/__init__.py` implements this classifier for OBPI-08's sync mechanism. See tests at `tests/test_chores.py::TestChoresLayoutDualSurface`.

**Long-term note:** This classifier is a **temporary accommodation**. The deeper design concern — runtime-state (logs/receipts/proofs) co-located with canonical instructions — is parked at `ADR-pool.canonical-vs-runtime-separation`. When that ADR is promoted, runtime-state moves to a separate location and this classifier shrinks to a single class (canonical only).

## Rationale

`.claude/` surfaces are the path of least resistance — that is what the agent reads at runtime. Editing there is the common drift mode; the next sync silently overwrites it. Rules cannot fully override the editing instinct, so the mechanical backstop is version + commit hash comparison: even when an agent edits the wrong surface, the version and git history make the conflict detectable and resolvable.

The split between frontmatter `skill-version` (skills) and body-level `<!-- rule-version: ... -->` (rules) keeps each artifact's version marker close to the surface that consumes it. The skill schema validates frontmatter strictly, so `skill-version` belongs there. The rule schema is deliberately minimal (id/paths/description) so that it can grow without breaking every rule file at once — the body-level marker preserves the version-bump invariant without requiring a schema migration every time the metadata vocabulary changes. See `chores.md` for the canonical body-marker form.
