---
id: OBPI-0.0.32-01-skills-canonical-promotion
parent: ADR-0.0.32-canonical-surface-packaging
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.32-01-skills-canonical-promotion: Skills Canonical Promotion

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #1 — "Promote `.gzkit/skills/<slug>/SKILL.md` → `src/gzkit/skills/<slug>/SKILL.md` two-surface layout; convert `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py`; refactor `scaffold_core_skills` to copy canonical package content (eliminate stub-template path)"

**Status:** Draft

## Objective

Move 61 hand-authored canonical SKILL.md files from `.gzkit/skills/<slug>/` into wheel-shipped package data at `src/gzkit/skills/<slug>/SKILL.md`, mirroring the ADR-0.0.21 chores precedent layout. Convert the existing `src/gzkit/skills.py` module (438 lines) into `src/gzkit/skills/__init__.py` so `from gzkit.skills import X` import sites continue to resolve. Refactor `scaffold_core_skills` to copy canonical package content via `importlib.resources.files("gzkit.skills")` rather than rendering one-line stubs through `templates/skill.md`. After this OBPI lands, `pip install py-gzkit && gz init` produces full canonical SKILL.md content in `.gzkit/skills/<slug>/`, not stubs — closing failure class B from GHI #318.

## Lane

**Heavy** — restructures Python package layout (module → package conversion), changes the runtime contract of `scaffold_core_skills`, and changes what the wheel ships. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/skills.py` — convert to package (move contents to `src/gzkit/skills/__init__.py`); delete the file
- `src/gzkit/skills/__init__.py` — receives the contents of the former `src/gzkit/skills.py` plus the new `_iter_canonical_skill_slugs()` enumerator and the refactored `scaffold_core_skills`
- `src/gzkit/skills/<slug>/SKILL.md` — destination of `git mv` from `.gzkit/skills/<slug>/SKILL.md` (61 files)
- `src/gzkit/skills/<slug>/` — per-slug subdirectories created by the move
- `.gzkit/skills/<slug>/SKILL.md` — source of `git mv`; per chores precedent, the project-overlay layer remains valid for project-local skills but the canonical content moves to the package
- `pyproject.toml` — extend `[tool.hatch.build.targets.wheel] include:` with `src/gzkit/skills/**/*.md`
- `tests/test_skills.py`, `tests/commands/test_init.py` (or equivalents) — add unit tests for `_iter_canonical_skill_slugs`, scaffolder copy semantics, project-first → package-fallback resolution
- `src/gzkit/templates/skill.md` — DELETE or repurpose; the stub-template path is eliminated by Decision

## Denied Paths

- `src/gzkit/rules.py`, `src/gzkit/rules/**` — rules promotion is OBPI-0.0.32-02; do not bundle
- `src/gzkit/commands/init_cmd.py` — wiring CHANGES limited to scaffolder API consumption only; init_cmd updates that touch the rules surface belong to OBPI-0.0.32-02
- `src/gzkit/hooks/**`, `src/gzkit/personas/**`, `src/gzkit/templates/*.md` (other than `skill.md`) — not in scope for this OBPI; future surface promotions belong to follow-up OBPIs
- `features/distribution_invariant.feature` — the T0 smoke test belongs to OBPI-0.0.32-04
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-0.0.32-05
- `.claude/skills/`, `.github/skills/` — mirror regeneration belongs to OBPI-0.0.32-06; this OBPI may leave mirrors stale temporarily
- `docs/governance/trust-doctrine.md` — T0 doctrine paragraph belongs to OBPI-0.0.31-01

## Requirements (FAIL-CLOSED)

1. `git mv .gzkit/skills/<slug>/SKILL.md src/gzkit/skills/<slug>/SKILL.md` MUST be used for every one of the 61 canonical skills so git history is preserved. A bulk `cp` + `rm` is NEVER acceptable.
2. After the moves, `src/gzkit/skills/<slug>/SKILL.md` MUST be byte-identical to the pre-move `.gzkit/skills/<slug>/SKILL.md` (no content edits in this OBPI; content authoring is out of scope).
3. `src/gzkit/skills.py` MUST NOT exist after this OBPI. Its contents MUST move to `src/gzkit/skills/__init__.py` such that every `from gzkit.skills import X` import site in `src/` and `tests/` continues to resolve without modification.
4. `src/gzkit/skills/__init__.py` MUST add `_iter_canonical_skill_slugs()` mirroring `src/gzkit/chores/__init__.py:_iter_canonical_chore_slugs()` exactly: enumerate via `importlib.resources.files("gzkit.skills")`, skip `__pycache__`-style entries, require `SKILL.md` presence per slug.
5. `scaffold_core_skills` MUST copy canonical SKILL.md content from package resources rather than rendering through `templates/skill.md`. The stub-template path MUST be removed (delete `src/gzkit/templates/skill.md` or document its repurposing in the same commit).
6. Project-first → package-fallback resolution MUST hold: if `.gzkit/skills/<slug>/SKILL.md` exists in the destination project, the scaffolder leaves it alone (per `skip_existing=True` semantics); if absent, it copies from `importlib.resources.files("gzkit.skills")`.
7. `pyproject.toml [tool.hatch.build.targets.wheel] include:` MUST grow to include `src/gzkit/skills/**/*.md`. The exclude list MUST not strip the new content.
8. Unit tests MUST cover: (a) canonical-slug enumeration returns all 61 slugs, (b) scaffolder copies byte-identical content from package, (c) project-first resolution preserves operator edits, (d) `from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills` (and every other current public symbol) continues to work after the package conversion.
9. `from gzkit.skills_audit import …` import sites MUST continue to work; the audit module is a sibling, not a child.
10. `uv run gz check` (lint + format + test + typecheck) MUST exit 0 after the conversion lands.
11. The 61 moved files MUST appear in the built wheel: `python -m build && unzip -l dist/py_gzkit-*.whl | grep "gzkit/skills/.*SKILL\.md" | wc -l` MUST return 61.

> STOP-on-BLOCKERS:
> - If `git mv` reports a name collision (a `src/gzkit/skills/<slug>/` already exists), STOP and investigate.
> - If any `.gzkit/skills/<slug>/` contains files OTHER than `SKILL.md` (e.g. `assets/`, `examples/`), STOP and decide per-skill whether the auxiliary content is canonical (move with) or project-local (leave behind). The chores precedent (per-slug `CHORE.md` + `acceptance.json` + `README.md` + `proofs/`) suggests per-slug auxiliary content is canonical when it predates the project; verify per-slug.
> - If any current `from gzkit.skills import X` site fails to resolve after the package conversion, STOP and add the missing re-export in `__init__.py` before continuing.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary.
- [ ] Parent ADR § Intent — names the chores precedent and the temporal-promotion-gap rationale
- [ ] Parent ADR § Decision — package layout block, project-first → package-fallback resolution
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix (heavy + foundation requires brief-level Gate 5)
- [ ] `AGENTS.md` § DO IT RIGHT #1 (fix the class — the class here is "canonical surfaces don't reach fresh installs")
- [ ] `.gzkit/rules/skill-surface-sync.md` — current skill-version semantics; package promotion must preserve the version-bump invariant
- [ ] `.gzkit/rules/tests.md` — RGR discipline; the unit tests in this OBPI start RED
- [ ] `.gzkit/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding rules apply to file copies

**Context — chores precedent (read closely; this OBPI mirrors it):**

- [ ] `src/gzkit/chores/__init__.py` — full file, especially `_iter_canonical_chore_slugs`, `_CANONICAL_RESOURCE = "gzkit.chores"`, `scaffold_core_chores` semantics
- [ ] `pyproject.toml` current `[tool.hatch.build.targets.wheel] include:` block (the chores entries are the template to extend)
- [ ] ADR-0.0.21-chores-as-gzkit-surface and OBPI-0.0.21-01 (physical migration), OBPI-0.0.21-04 (resolver with fallback) — full pattern playbook

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/skills.py` exists at 438 lines (sanity-check it hasn't been touched out from under this OBPI)
- [ ] 61 directories under `.gzkit/skills/` each containing `SKILL.md` (`ls .gzkit/skills/ | wc -l` returns 61)
- [ ] `src/gzkit/skills/` does NOT yet exist as a directory (greenfield destination)
- [ ] `src/gzkit/chores/__init__.py` exists (the precedent we mirror)
- [ ] Git working tree is clean before starting

**Existing Code (understand current state):**

- [ ] Every public symbol in `src/gzkit/skills.py` enumerated (e.g. `__all__` or grep for top-level `def` / `class` / module-level constants) — these all need re-export from the new `__init__.py`
- [ ] Every `from gzkit.skills import X` and `import gzkit.skills` site in `src/` and `tests/` enumerated (`grep -rn "from gzkit.skills\|import gzkit.skills" src/ tests/`) — sanity-check the imports the new package must preserve
- [ ] `src/gzkit/templates/skill.md` read end-to-end before deletion (so its content is preserved in commit history if anyone needs it later)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #1 quoted verbatim above

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for `_iter_canonical_skill_slugs` and scaffolder-copies-from-package fail before implementation lands
- [ ] GREEN: tests pass after package conversion + scaffolder refactor
- [ ] Coverage maintained above the 40% floor
- [ ] `uv run gz test` passes

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/gz-init.md` updated if scaffolder behavior surface changed (likely yes — `--force` semantics around copied vs templated content)
- [ ] `.claude/rules/skill-surface-sync.md` updated to reflect canonical-content-from-package (current rule assumes hand-authored canonical files at `.gzkit/skills/`)
- [ ] `docs/user/runbook.md` skills section reviewed for stale references
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] `features/init.feature` (or `features/skills.feature` if exists) extended with a scenario asserting fresh-init produces canonical SKILL.md content (one full file, not a stub)

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded; foundation-kind heavy-lane OBPIs gate on Gate 5 at brief level

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test ! -f src/gzkit/skills.py
test -f src/gzkit/skills/__init__.py
ls src/gzkit/skills/ | grep -v __init__.py | grep -v __pycache__ | wc -l
find src/gzkit/skills/ -name SKILL.md | wc -l
python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills; print('imports OK')"
python -c "import importlib.resources; r=importlib.resources.files('gzkit.skills'); print(sum(1 for e in r.iterdir() if e.is_dir() and not e.name.startswith('__')))"

uv build
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/skills/.*SKILL\.md"
```

## Acceptance Criteria

- [ ] REQ-0.0.32-01-01: All 61 SKILL.md files moved via `git mv` from `.gzkit/skills/<slug>/SKILL.md` to `src/gzkit/skills/<slug>/SKILL.md`; git history preserved per file
- [ ] REQ-0.0.32-01-02: `src/gzkit/skills.py` does not exist post-OBPI; its contents live at `src/gzkit/skills/__init__.py`
- [ ] REQ-0.0.32-01-03: Every public symbol previously importable from `gzkit.skills` (e.g. `CORE_SKILLS`, `scaffold_core_skills`, `audit_skills`, `SkillAuditIssue`, `_parse_frontmatter`, `DEFAULT_MAX_REVIEW_AGE_DAYS`) remains importable
- [ ] REQ-0.0.32-01-04: `_iter_canonical_skill_slugs()` exists in `src/gzkit/skills/__init__.py`, mirrors `_iter_canonical_chore_slugs`, and yields all 61 canonical slugs
- [ ] REQ-0.0.32-01-05: `scaffold_core_skills` copies canonical SKILL.md content from `importlib.resources.files("gzkit.skills")` rather than templating
- [ ] REQ-0.0.32-01-06: Project-first → package-fallback resolution holds: a project-local `.gzkit/skills/<slug>/SKILL.md` is preserved by `skip_existing=True`; a missing one is filled from package canonical
- [ ] REQ-0.0.32-01-07: `pyproject.toml` wheel `include:` covers `src/gzkit/skills/**/*.md`; built wheel contains 61 SKILL.md files under `gzkit/skills/`
- [ ] REQ-0.0.32-01-08: `src/gzkit/templates/skill.md` is deleted (or its repurposing documented in the same commit)
- [ ] REQ-0.0.32-01-09: `uv run gz check` exits 0 with the new layout

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed; test counts and coverage recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + skill-surface-sync rule updated; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Fresh-init scenario added and passing
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output (RED then GREEN), coverage delta
```

### Code Quality

```text
# Paste lint, format, ty output
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)

```text
# Paste behave scenario output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: `pip install py-gzkit && gz init` in a fresh project produced 12 one-line skill stubs from `templates/skill.md` while this repo's 61 canonical SKILL.md files (multi-section operator-facing artifacts) lived only at `.gzkit/skills/` and never shipped. After this OBPI: the canonical content is wheel-shipped package data; fresh installs produce the same SKILL.md content this repo uses to govern itself. Closes failure class B from GHI #318.

### Key Proof

```bash
unzip -l dist/py_gzkit-*.whl | grep -c "gzkit/skills/.*SKILL\.md"
# Expected: 61
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure class B addressed by this OBPI (closure deferred to ADR-0.0.32 closeout)

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
