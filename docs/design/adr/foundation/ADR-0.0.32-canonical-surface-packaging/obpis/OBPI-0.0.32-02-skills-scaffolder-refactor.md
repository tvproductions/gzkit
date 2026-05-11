---
id: OBPI-0.0.32-02-skills-scaffolder-refactor
parent: ADR-0.0.32-canonical-surface-packaging
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.32-02-skills-scaffolder-refactor: Skills Scaffolder Refactor

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #2 — "Skills scaffolder refactor — refactor `scaffold_core_skills` to copy canonical SKILL.md content from `importlib.resources.files(\"gzkit.skills\")` (the wheel's package surface) into the adopter's `.gzkit/skills/<slug>/`; preserve operator edits via `skip_existing=True`; delete (or document repurposing of) `src/gzkit/templates/skill.md`. Depends on OBPI-01 landing first."

**Status:** Draft

## Objective

After OBPI-01 has landed the skills dual-surface (~70 SKILL.md files retained at `.gzkit/skills/<slug>/SKILL.md` as authored canonical source-of-truth AND byte-equivalent copies at `src/gzkit/skills/<slug>/SKILL.md` for wheel-shipping, `src/gzkit/skills.py` converted to `src/gzkit/skills/__init__.py`), refactor `scaffold_core_skills` so it COPIES canonical SKILL.md content from `importlib.resources.files("gzkit.skills")` (the wheel's package surface — `src/gzkit/skills/` in the gzkit dev repo, the installed-wheel package data on adopter machines) into the adopter project's `.gzkit/skills/<slug>/SKILL.md` rather than rendering one-line stubs through `src/gzkit/templates/skill.md`. Author `_iter_canonical_skill_slugs()` mirroring `src/gzkit/chores/__init__.py:_iter_canonical_chore_slugs()`. Implement project-first → package-fallback resolution (project-first = preserve any existing `.gzkit/skills/<slug>/SKILL.md` in the adopter project; package-fallback = copy from wheel package data when a file is missing). The scaffolder writes into adopter's `.gzkit/<surface>/`; once written, that adopter's `.gzkit/` becomes their project canonical source-of-truth — the same canonical-routing invariant ADR-0.0.32 § Decision binds across every gzkit-or-adopter repo. Delete `src/gzkit/templates/skill.md` (or document its repurposing, but the stub-template scaffolding path MUST be eliminated). After this OBPI lands, `gz init` produces full canonical SKILL.md content in any adopter project's `.gzkit/skills/<slug>/SKILL.md`. T0-class B closure depends on this OBPI + OBPI-06 (wheel includes) jointly.

## Lane

**Heavy** — changes the runtime contract of `scaffold_core_skills` (a public scaffolder API), removes the stub-template path. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/skills/__init__.py` — add `_iter_canonical_skill_slugs()` enumerator and refactor `scaffold_core_skills` body
- `src/gzkit/templates/skill.md` — DELETE, OR keep with a documented repurposing comment (the stub-template scaffolding path is eliminated either way)
- `tests/test_skills.py`, `tests/commands/test_init.py` (or equivalents) — unit tests for `_iter_canonical_skill_slugs`, copy-from-package behavior, project-first resolution
- `docs/user/manpages/init.md` — document the new copy-from-package behavior if it surfaces operator-facing change (likely yes — `--force` semantics shift from "wipe and re-template" to "wipe and re-copy")
- `.gzkit/rules/skill-surface-sync.md` — re-affirm "Edit `.gzkit/` first" canon; document that fresh-init adopter projects receive their `.gzkit/skills/` canonical content from the wheel's package surface (`importlib.resources`), after which the adopter's `.gzkit/` is their project canonical

## Denied Paths

- Physical migration (file moves, module-to-package conversion) — owned by OBPI-01
- `src/gzkit/rules/**` — rules belong to OBPI-03 / -04
- `pyproject.toml` — wheel includes belong to OBPI-06; this OBPI's scaffolder works at runtime against the package, but until OBPI-06 lands, `importlib.resources.files("gzkit.skills")` from a fresh install will not find the canonical content. Until OBPI-06 lands, this OBPI achieves the in-repo dev behavior but not the fresh-install closure — that is the expected intermediate state
- `src/gzkit/commands/init_cmd.py` — call sites stay unchanged (the API of `scaffold_core_skills` is stable)
- `features/**` — behave belongs to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/skills/`, `.github/skills/` — mirror regen belongs to OBPI-08

## Requirements (FAIL-CLOSED)

1. `_iter_canonical_skill_slugs()` MUST be added to `src/gzkit/skills/__init__.py`, mirroring `src/gzkit/chores/__init__.py:_iter_canonical_chore_slugs()` exactly: enumerate via `importlib.resources.files("gzkit.skills")`, skip `__pycache__`-style entries, require `SKILL.md` presence per slug, yield each canonical-slug `Traversable`.
2. `scaffold_core_skills` MUST copy canonical SKILL.md content from package resources via `importlib.resources` rather than rendering through `templates/skill.md` or any other template path. The template-render path MUST be removed.
3. `src/gzkit/templates/skill.md` MUST be deleted, OR retained only with a comment documenting why the file is still present and what consumes it (no consumer should remain after this OBPI; if any does, it is a defect to surface in a follow-up GHI).
4. Project-first → package-fallback resolution MUST hold: if `.gzkit/skills/<slug>/SKILL.md` exists in the destination project, the scaffolder leaves it alone (per `skip_existing=True` semantics); if absent, it copies from `importlib.resources.files("gzkit.skills")`.
5. `scaffold_core_skills` public API surface (function name, parameter list, return type) MUST remain compatible with the pre-OBPI version so existing call sites do not change. Only the body changes.
6. Unit tests MUST cover: (a) `_iter_canonical_skill_slugs()` returns the expected number of slugs (70 as of OBPI-01, matching `importlib.resources.files("gzkit.skills")` enumeration), (b) scaffolder writes byte-identical canonical content to a tempdir, (c) `skip_existing=True` preserves operator-edited project copies, (d) scaffolder is robust to a missing canonical surface (graceful degradation, not crash).
7. `uv run gz check` MUST exit 0 after the refactor.
8. `mkdocs build --strict` MUST pass; manpage updates MUST land in the same patch as scaffolder behavior changes per `.claude/rules/gate5-runbook-code-covenant.md`.

> STOP-on-BLOCKERS:
> - If OBPI-01 has not landed (skills not yet at `src/gzkit/skills/<slug>/SKILL.md`), STOP — there is no canonical surface for the scaffolder to copy from.
> - If `src/gzkit/templates/skill.md` is referenced by anything OTHER than `scaffold_core_skills` (e.g. tests, other scaffolders), STOP and surface the dependency before deletion.
> - If `importlib.resources.files("gzkit.skills")` does not resolve at runtime (sanity check via `python -c "import importlib.resources; print(importlib.resources.files('gzkit.skills'))"`), STOP — the package-conversion in OBPI-01 may have left an issue.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — project-first → package-fallback resolution paragraph
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/skill-surface-sync.md` — current canonical-vs-mirror semantics; this OBPI updates the rule
- [ ] `.gzkit/rules/tests.md` — RGR discipline

**Context — chores precedent + sibling OBPIs:**

- [ ] `src/gzkit/chores/__init__.py` — `_iter_canonical_chore_slugs`, `scaffold_core_chores` semantics; this OBPI mirrors them
- [ ] OBPI-0.0.21-04-resolver-with-fallback — the chores resolver-with-fallback precedent
- [ ] OBPI-0.0.32-01 (sibling) — physical migration; must land first
- [ ] OBPI-0.0.32-04 (sibling) — same pattern applied to rules

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.32-01 landed (70 SKILL.md files at `src/gzkit/skills/<slug>/`, `src/gzkit/skills/__init__.py` exists)
- [ ] `src/gzkit/templates/skill.md` exists (sanity check before deletion)
- [ ] `src/gzkit/chores/__init__.py` exists (precedent)

**Existing Code:**

- [ ] Read `scaffold_core_skills` body in the post-OBPI-01 `src/gzkit/skills/__init__.py` end-to-end
- [ ] Read `scaffold_core_chores` body for the copy-from-package pattern to mirror
- [ ] Read `src/gzkit/templates/skill.md` end-to-end before deletion (so its content is preserved in commit history)
- [ ] Grep for every reference to `templates/skill.md` and to `render_template("skill.md", ...)` across `src/` and `tests/`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #2 quoted verbatim above

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: tests for `_iter_canonical_skill_slugs` and copy-from-package behavior fail before implementation
- [ ] GREEN: tests pass after refactor
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/init.md` updated for the copy-from-package behavior change
- [ ] `.gzkit/rules/skill-surface-sync.md` re-affirmed — "Edit `.gzkit/` first" remains canon; section added explaining that `gz init` populates adopter's `.gzkit/skills/` from the wheel's package surface as the bootstrap source
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] Existing `gz init`-related scenarios in `features/` continue to pass; no new scenarios in this OBPI (OBPI-06 owns the build-install-init smoke)

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

python -c "from gzkit.skills import _iter_canonical_skill_slugs; print(sum(1 for _ in _iter_canonical_skill_slugs()))"  # expect 70
python -c "import importlib.resources; r=importlib.resources.files('gzkit.skills'); print(sum(1 for e in r.iterdir() if e.is_dir() and not e.name.startswith('__')))"  # expect 70

# Smoke: scaffolder copies canonical to a temp project
mkdir /tmp/gz-skills-scaffold-smoke && cd /tmp/gz-skills-scaffold-smoke && uv run gz init && head -5 .gzkit/skills/gz-prd/SKILL.md
# Expected: full multi-section canonical content, NOT a one-line stub
```

## Acceptance Criteria

- [ ] REQ-0.0.32-02-01: `_iter_canonical_skill_slugs()` exists in `src/gzkit/skills/__init__.py` and mirrors `_iter_canonical_chore_slugs` exactly
- [ ] REQ-0.0.32-02-02: `scaffold_core_skills` copies canonical SKILL.md content via `importlib.resources` rather than templating
- [ ] REQ-0.0.32-02-03: `src/gzkit/templates/skill.md` is deleted (or its retention with a documented repurposing comment is justified in this OBPI's evidence)
- [ ] REQ-0.0.32-02-04: Project-first → package-fallback resolution holds; `skip_existing=True` preserves operator edits
- [ ] REQ-0.0.32-02-05: `scaffold_core_skills` public API surface (signature + return type) is unchanged
- [ ] REQ-0.0.32-02-06: A fresh `gz init` in a tempdir produces full canonical SKILL.md content (NOT one-line stubs) — visible via `head -5` of any scaffolded SKILL.md
- [ ] REQ-0.0.32-02-07: `.gzkit/rules/skill-surface-sync.md` re-affirms "Edit `.gzkit/` first" and documents that `gz init` populates adopter's `.gzkit/skills/` from the wheel's package surface
- [ ] REQ-0.0.32-02-08: `docs/user/manpages/init.md` updated for behavior change; `mkdocs build --strict` passes
- [ ] REQ-0.0.32-02-09: `uv run gz check` exits 0

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Manpage + skill-surface-sync rule updated; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing scenarios still pass
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste unittest output, coverage delta
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
# Paste regression scenario output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: `gz init` rendered 12 one-line skill stubs from `templates/skill.md` regardless of how rich the in-repo `.gzkit/skills/<slug>/SKILL.md` content was. After this OBPI: `gz init` copies canonical SKILL.md content from the wheel's package surface (`importlib.resources.files("gzkit.skills")`) into the adopter's `.gzkit/skills/<slug>/SKILL.md`, so a fresh-init project receives the same multi-section operator-facing artifacts this repo authors. Once written, the adopter's `.gzkit/` becomes their project canonical source-of-truth — the canonical-routing invariant ADR-0.0.32 § Decision declares binding across every gzkit-or-adopter repo. Closure of T0-class B remains contingent on OBPI-06 (wheel includes) — this OBPI delivers the runtime semantics; OBPI-06 makes them work for `pip install` consumers.

### Key Proof


Smoke run scaffolding into a tempdir against the refactored API:

```bash
uv run python -c "
import tempfile
from pathlib import Path
from gzkit.config import GzkitConfig
from gzkit.skills import scaffold_core_skills
with tempfile.TemporaryDirectory() as tmp:
    cfg = GzkitConfig(mode='lite', project_name='smoke')
    created = scaffold_core_skills(Path(tmp), cfg, skip_existing=False)
    print(f'scaffolded {len(created)} canonical skills')
    print(f'sample: {created[0].parent.name} = {len(created[0].read_text().splitlines())} lines')
"
# scaffolded 52 canonical skills
# sample: gz-adr-map = 47 lines
```

70 canonical slugs in `importlib.resources.files("gzkit.skills")`; 52 active after retired-skill filtering; each output is canonical multi-line SKILL.md content (not the pre-refactor stub). ARB receipts: `arb-step-unittest-0363c95b86b244d892ca70a8a739df1e` (4800/4800 pass), `arb-ruff-2c2e9f372d2a479f8a2091b10a5a4cc2` (lint clean), `arb-step-typecheck-6923f4c182dd4f20ae9d9345b62567c0` (type check clean), `arb-step-mkdocs-29b3a415a7ba49778bca7c01d741ea65` (docs build strict clean).

### Implementation Summary


- Files created/modified: `src/gzkit/skills/__init__.py` (added `_iter_canonical_skill_slugs()` enumerator, refactored `scaffold_core_skills` body to copy bytes from `importlib.resources.files("gzkit.skills")` with `lifecycle_state: retired` filter); `src/gzkit/templates/skill.md` (added repurposing comment; retained for residual `scaffold_skill` consumer per GHI #453); `tests/test_skills.py` (added `TestSkillsScaffolderRefactor` class with 10 REQ-covered tests); `tests/commands/test_skills.py` and `tests/commands/test_sync_cmds.py` (lint→gz-status/gz-prd fixture migration); `docs/user/manpages/init.md` (Skills Scaffolding section); `.gzkit/rules/skill-surface-sync.md` (rule-version 0.2.0 → 0.3.0; Bootstrap semantics section); brief allowed-paths and stale-count fixes (pre-pipeline authoring correction); `data/behave_coverage_waivers.json` (waiver under `adr-0.0.32-bdd-deferred-to-obpi-06`).
- Tests added: 10 (REQ-01..09 covered, 100% parity per `gz covers OBPI-0.0.32-02 --json`).
- Date completed: 2026-05-11
- Attestation status: operator attested via "attest completed" in Stage 4
- Defects noted: GHI #453 — residual `scaffold_skill` dependency on `templates/skill.md` + stale `CORE_SKILLS["lint"]` entry; deferred per REQ-03 follow-up clause.

## Tracked Defects

- GHI #318 — failure class B addressed (jointly with OBPI-01 + OBPI-06)

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.32-02 skills-scaffolder-refactor verified by 4800-test unittest sweep (arb-step-unittest-0363c95b86b244d892ca70a8a739df1e), lint clean (arb-ruff-2c2e9f372d2a479f8a2091b10a5a4cc2), type check clean (arb-step-typecheck-6923f4c182dd4f20ae9d9345b62567c0), mkdocs strict clean (arb-step-mkdocs-29b3a415a7ba49778bca7c01d741ea65), 9/9 REQ coverage (gz covers OBPI-0.0.32-02 --json), and smoke run scaffolding 52 active canonical skills (from 70 total slugs, 18 retired filtered by lifecycle_state). Residual scaffold_skill dependency tracked at GHI #453.
- Date: 2026-05-11

---

**Brief Status:** Completed

**Date Completed:** 2026-05-11

**Evidence Hash:** -
