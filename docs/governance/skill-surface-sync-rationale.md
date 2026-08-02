# Skill & Surface Sync — Rationale

> Expansion doc for `.gzkit/rules/skill-surface-sync.md` § Rationale (ADR-0.0.54-04 lift).
> Prose preserved verbatim; see rule file for binding bullets.

## Rationale

`.claude/` surfaces are the path of least resistance — that is what the agent reads at runtime. Editing there is the common drift mode; the next sync silently overwrites it. Rules cannot fully override the editing instinct, so the mechanical backstop is version + commit hash comparison: even when an agent edits the wrong surface, the version and git history make the conflict detectable and resolvable.

The split between frontmatter `skill-version` (skills) and body-level `<!-- rule-version: ... -->` (rules) keeps each artifact's version marker close to the surface that consumes it. The skill schema validates frontmatter strictly, so `skill-version` belongs there. The rule schema is deliberately minimal (id/paths/description) so that it can grow without breaking every rule file at once — the body-level marker preserves the version-bump invariant without requiring a schema migration every time the metadata vocabulary changes. See `chores.md` for the canonical body-marker form.

## Bootstrap semantics (`gz init`)

(Lifted from `.gzkit/rules/skill-surface-sync.md` under the 2026-08-02 diet pass; the rule keeps the binding core and a pointer here.)

On first init in an adopter project, `gz init` populates `.gzkit/skills/<slug>/SKILL.md` by copying canonical content from the wheel's package surface (`importlib.resources.files("gzkit.skills")`). The package surface is the *one-time bootstrap source*: after init, the adopter's `.gzkit/skills/` is **the project canonical source-of-truth** for that project, and the "Edit `.gzkit/` first" rule binds from that point forward.

Repair mode (re-running `gz init`) is idempotent: it adds new canonical slugs delivered by the installed gzkit version without overwriting operator-edited files (`skip_existing=True`). Use `--force` to wipe and re-copy every canonical SKILL.md from the wheel.

`scaffold_core_skills` filters skills whose canonical SKILL.md declares `lifecycle_state: retired` — retired slugs are not re-introduced on `gz init` (hard cutover invariant, enforced by `tests/commands/test_skills.py::TestSkillCommands::test_init_scaffolds_adr_create_and_removes_adr_manager`).

As of OBPI-0.0.32-04, `gz init` also populates `.gzkit/rules/<slug>.md` by copying canonical rule content from the wheel's package surface (`importlib.resources.files("gzkit.rules")`). The same editing invariant applies: after init, `.gzkit/rules/` is **the project canonical source-of-truth** for rules in that adopter project. Rules scaffolding runs after `sync_all` in the fresh init path so the initial control-surface sync uses the instruction-sync path; subsequent `gz agent sync control-surfaces` invocations render canonical rules to `.github/instructions/`. The `AGENTS.md` file in the rules package is excluded from scaffolding (it is a package-internal agent contract, not an operator-facing rule).

`gz init --update` (OBPI-0.0.32-05, not yet landed) will provide version-aware refresh semantics for the adopter's `.gzkit/<surface>/` from the wheel, with three-state IDENTICAL/STALE/EDITED detection so operator edits are preserved across gzkit upgrades.

## Retirement policy (delete-on-retire)

(Rationale lifted from the rule's § Retirement policy, 2026-08-02; the delete-on-retire invariant and the same-commit inheritance rule remain binding in the rule file.)

**Why delete:** the `package_only` classifier carve-out exists for *non-md package-machinery* (e.g. `__init__.py`, `__pycache__/**`). Routing retired SKILL.md tombstones through `package_only` is classifier scope creep that inflates the shipped wheel with `archived_into` frontmatter stubs and muddies the canonical/package_only distinction. Operator judgment (recorded under GHI #464 / ADR-0.0.32 closeout): *"tombstones not worth keeping if they are stubs."*

**Redirect UX is acceptably "skill not found."** A retired-name invocation returns the missing-skill response rather than a tombstone pointer to the successor. The discoverability cost is small enough that indefinite wheel inflation is not justified.

**Defensive backstop preserved.** The retired-frontmatter branch in `_classify_skill_file` (lines ~45–52 of `src/gzkit/skills/__init__.py`) remains as a defensive net: if a tombstone leaks back in violation of this doctrine, it is still classified `package_only` so `gz validate --distribution` does not flag it. The doctrine is the authored rule; the classifier branch is the runtime fallback.

## Class-classifier reference

(Reference tables lifted from the rule's § Canonical surface class-classifier, 2026-08-02; the three-class model and its validator/sync consumers remain in the rule file.)

### Default rules by surface

| Surface | canonical | package_only | runtime_state |
|---------|-----------|--------------|---------------|
| **chores** | `CHORE.md`, `AGENTS.md`, `*.md` outside `proofs/`, `acceptance.json`, `registry.json`, `.py` with `.gzkit/` counterpart | `__init__.py`, `__pycache__/**`, `.py` with no `.gzkit/` counterpart | `CHORE-LOG.md`, `proofs/**`, `.gitkeep` |
| **rules** | `*.md`, `*.json` with `.gzkit/rules/` counterpart, `.py` with `.gzkit/rules/` counterpart | `__init__.py`, `__pycache__/**`, `_scaffolder.py`, `.py` or `.json` with no `.gzkit/rules/` counterpart | (none) |
| **skills** | `SKILL.md` (all) | `__init__.py`, `__pycache__/**` | (none) |
| **personas** | `*.md` (all) | `__init__.py`, `__pycache__/**` | (none) |
| **templates** | `*.md` (all) | `__init__.py`, `__pycache__/**` | (none) |

### Python helpers (all signature-compatible with `_classify_chore_file`)

| Surface | Helper | Module | Tests |
|---------|--------|--------|-------|
| chores | `_classify_chore_file(path, *, project_root=None)` | `gzkit.chores` | `tests/test_chores.py::TestChoresLayoutDualSurface` |
| rules | `_classify_rule_file(path, *, project_root=None)` | `gzkit.rules` | `tests/test_rules.py::TestClassifyRuleFile` |
| skills | `_classify_skill_file(path, *, project_root=None)` | `gzkit.skills` | `tests/test_skills.py::TestClassifySkillFile` |
| personas | `_classify_persona_file(path, *, project_root=None)` | `gzkit.personas` | `tests/test_personas.py::TestClassifyPersonaFile` |
| templates | `_classify_template_file(path, *, project_root=None)` | `gzkit.templates` | `tests/test_templates.py::TestClassifyTemplateFile` |

**Long-term note (chores):** The chores classifier is a **temporary accommodation** for runtime-state co-location with canonical instructions. When `ADR-pool.canonical-vs-runtime-separation` promotes, runtime-state moves to a separate location and the chores classifier shrinks to a single class (canonical only).
