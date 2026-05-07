---
id: ADR-0.0.32-canonical-surface-packaging
status: Draft
kind: foundation
semver: 0.0.32
lane: heavy
parent: ADR-0.0.31-distribution-invariant-doctrine
date: 2026-04-25
---

# ADR-0.0.32-canonical-surface-packaging: Canonical Surface Packaging

## Persona

Governance-aware implementer who treats package data as a first-class
deliverable. Sees that "the wheel ships what the canonical surface contains"
is a contract, not an artifact of `pyproject.toml`'s include-list happening
to be correct. Mirrors the proven ADR-0.0.21 chores precedent: two-surface
layout (canonical `src/gzkit/<surface>/` + project overlay
`.gzkit/<surface>/`), project-first → package-fallback resolution, doctor
repair surface, validate-layout mechanical check. Refuses the "we'll just
extend the include list" shortcut because the include list alone does not
make the scaffolders shipped-content-aware.

## Intent

Mechanically satisfy the T0 distribution invariant authored by ADR-0.0.31
across every canonical surface that today exists only in this repo's
`.gzkit/` tree: skills (61), rules (14), hooks, templates, personas. The
goal is that `pip install py-gzkit && gz init` in a fresh greenfield
project yields canonical surfaces byte-equivalent (modulo project-name
substitution) to a frozen baseline manifest, with `gz init --update`
providing version-aware refresh for existing projects.

This ADR is the mechanical counterpart to ADR-0.0.31's doctrine surface.
ADR-0.0.21 (chores-as-gzkit-surface) is the canonical precedent: every
mechanical pattern in this ADR's scope already worked through chores
(two-surface layout, importlib.resources enumeration, doctor-repair, layout
validate). The reason chores got the right packaging treatment and skills/
rules did not is purely temporal: chores was promoted *after* the
self-hosting blindness was already entrenched and someone (correctly)
recognized chores would have downstream consumers; skills and rules were
promoted earlier, when there were no external consumers to expose the gap.

## Decision

Promote `.gzkit/skills/<slug>/SKILL.md` and `.gzkit/rules/<slug>.md`
content into wheel-shipped package data under `src/gzkit/skills/<slug>/`
and `src/gzkit/rules/<slug>.md`, mirroring the chores two-surface layout.
Build a `CORE_RULES` registry symmetric to `CORE_SKILLS` and
`CORE_CHORES`. Wire `scaffold_core_rules` into `init_cmd._scaffold_project_skeleton`
and `_repair_missing_artifacts`. Refactor `scaffold_core_skills` to copy
canonical content from package resources rather than rendering one-line
stubs through `templates/skill.md`. Extend the wheel `include:` list to
ship the new surface trees. Add `gz init --update` for version-aware
refresh that preserves project-local edits. Author a build-then-install
T0 smoke test that proves byte-equivalence against a frozen baseline
manifest. Extend `gz validate --surfaces` (or add a dedicated
`--distribution` scope) with a T0 check that exits 3 on any unshipped
canonical surface.

The package layout:

```
src/gzkit/skills/
    __init__.py        # current src/gzkit/skills.py contents (preserves `from gzkit.skills import X`)
    <slug>/
        SKILL.md       # canonical content (was .gzkit/skills/<slug>/SKILL.md)

src/gzkit/rules/
    __init__.py        # current src/gzkit/rules.py contents (preserves `from gzkit.rules import X`)
    <slug>.md          # canonical content (was .gzkit/rules/<slug>.md)
```

The module-to-package conversion is unavoidable: `src/gzkit/skills.py` and
`src/gzkit/skills/<slug>/SKILL.md` cannot coexist; converting the file to
`src/gzkit/skills/__init__.py` keeps `from gzkit.skills import X` working
because Python resolves the symbol through the package's `__init__.py`
re-exports. Same for `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py`.
This mirrors chores exactly: `src/gzkit/chores/` is a package with
`__init__.py` (224 lines of library API) plus per-slug subdirectories.

Resolution order (project-first → package-fallback) follows the chores
contract: `gz init` and the scaffolders look for `.gzkit/<surface>/<slug>/`
first; if absent, fall back to the package canonical content via
`importlib.resources.files("gzkit.<surface>")`. This preserves operator
edits to project-local copies while letting fresh installs receive
canonical content from the wheel.

## Comparator Uplift (2026-05-07)

Tessl/BMAD/GSD package context so agents can enter a workflow quickly. gzkit's
packaging bar is higher: packages are canonical source plus generated mirrors,
versioned metadata, trust boundary, load budget, and validation result. This ADR
should make that package shape the default for skills, rules, personas, and
future context packages so portability never means hand-copied markdown.

## Consequences

### Positive

- Closes the GHI #318 class: `pip install py-gzkit && gz init` in a fresh
  project yields canonical content byte-equivalent to the baseline manifest,
  not one-line stubs.
- Makes future canonical-surface promotions follow a single proven pattern
  (the chores precedent extended to skills/rules and forward to hooks/
  templates/personas).
- Enables version-aware upgrades via `gz init --update` rather than the
  current binary "leave alone or `--force` wipe."
- Provides the mechanical enforcement T0 needs to be more than advisory:
  the smoke test fails the build if a canonical surface stops shipping,
  and `gz validate --distribution` fails any commit that adds a canonical
  surface without wheel coverage.
- Makes the in-repo `.gzkit/` content auditable as project overlay, not as
  the only place canonical content exists. Doctor-repair semantics from
  chores extend cleanly: `gz skills doctor` and `gz rules doctor` can
  refill missing canonical files without clobbering project edits.

### Negative

- 75 file moves (61 skills + 14 rules) plus two module-to-package
  conversions. Cross-references to `from gzkit.rules import X` /
  `from gzkit.skills import X` (~25 sites in src/, tests/) must continue
  resolving — package `__init__.py` re-exports preserve the API, but the
  conversion itself is a structural change that must be done correctly.
- The wheel grows: 75 new content files plus eventual hooks/templates/
  personas additions. Build time and install time both increase modestly.
- The two-surface layout discipline now binds for all canonical content.
  Authoring a new skill or rule means committing to the canonical-source
  → package-resource → scaffolder integration chain, not just dropping a
  file under `.gzkit/`.
- The T0 smoke test must build a wheel and install into a temp venv on
  every CI run — substantially slower than unit tests. Lives in `features/`
  per the test-runner contract; budgeted accordingly.
- Heavy-lane attestation rigor applies (foundation-kind + heavy lane =
  brief-level Gate 5 attestation per § Lane & Kind Attestation Matrix).
  Each of the six OBPIs gates on a human witness.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 2
- Dimension Total: 8
- Baseline Range: 4-4
- Baseline Selected: 4
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 8

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps.
     Mirrors the ADR-0.0.21 chores precedent — physical migration is its own OBPI,
     separate from the scaffolder/resolver work that depends on it. -->

- [ ] OBPI-0.0.32-01: Skills physical migration — `git mv .gzkit/skills/<slug>/SKILL.md src/gzkit/skills/<slug>/SKILL.md` for all 61 canonical skills; convert `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` preserving every public symbol re-export. Scaffolder refactor explicitly deferred to OBPI-02.
- [ ] OBPI-0.0.32-02: Skills scaffolder refactor — refactor `scaffold_core_skills` to copy canonical SKILL.md content from `importlib.resources.files("gzkit.skills")`; implement project-first → package-fallback resolution; delete (or document repurposing of) `src/gzkit/templates/skill.md`. Depends on OBPI-01 landing first.
- [ ] OBPI-0.0.32-03: Rules physical migration — `git mv .gzkit/rules/<slug>.md src/gzkit/rules/<slug>.md` for all 14 canonical rules; convert `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserving every public symbol re-export. Registry + scaffolder + init wiring explicitly deferred to OBPI-04.
- [ ] OBPI-0.0.32-04: Rules scaffolder authoring — build `CORE_RULES` registry symmetric to `CORE_SKILLS`/`CORE_CHORES`; author `scaffold_core_rules` mirroring `scaffold_core_chores` semantics; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). Depends on OBPI-03 landing first.
- [ ] OBPI-0.0.32-05: Add `gz init --update` flag with version-aware refresh + three-state detection (IDENTICAL/STALE/EDITED) + manpage + behave coverage
- [ ] OBPI-0.0.32-06: Author T0 smoke test (build wheel, install into temp venv, run `gz init`, assert byte-equivalence against frozen baseline manifest); audit and extend `pyproject.toml [tool.hatch.build.targets.wheel] include:`; author `data/distribution_baseline_manifest.json`
- [ ] OBPI-0.0.32-07: Extend `gz validate --surfaces` (or add `--distribution`) with T0 enforcement — verify every canonical surface in manifest is wheel-deliverable; fail-closed exit 3 on any package-data omission; flip T0 scorecard Promotable→Mechanical
- [ ] OBPI-0.0.32-08: Sync mirrors after surfaces promote: `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` regenerated from new package surface; verify `gz agent sync control-surfaces` no-ops cleanly post-promotion

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Design content sourced from GHI #318 amendment authored by ahuimanu on
2026-04-25T14:00:48Z, "ADR-0.0.27 — Canonical Surface Packaging" section
plus "OBPI decomposition sketch for ADR-0.0.27" table. The amendment
proposed slug ADR-0.0.27; that slug was reused by unrelated foundation work
(exemplar-corpus-doctrine) between amendment authoring and ADR creation, so
this ADR is booked at the next available foundation slug, ADR-0.0.32. No
design intent changed in the slug shift; the substantive scope is the
amendment text. The OBPI numbering preserves the amendment's 01–06 sketch.

Sequencing: ADR-0.0.31 (T0 doctrine) lands first; ADR-0.0.32 opens with
ADR-0.0.31 as the cited invariant in the `parent:` frontmatter. Six OBPIs
run in dependency order: 01 (skills) and 02 (rules) in parallel; 03
(`--update`) and 04 (smoke test + wheel includes) and 05 (`validate
--distribution`) after 01+02; 06 (mirror sync) last.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/` (unit-tier coverage for `CORE_RULES`, `scaffold_core_rules`, package-resource enumeration, init-cmd integration)
- [ ] Smoke test: `features/distribution_invariant.feature` (build wheel → temp-venv install → `gz init` → byte-equivalence against `data/distribution_baseline_manifest.json`)
- [ ] Wheel manifest: `pyproject.toml [tool.hatch.build.targets.wheel] include:` extended for `src/gzkit/skills/**/*.md`, `src/gzkit/rules/**/*.md`, `src/gzkit/templates/*.md`, `src/gzkit/hooks/scripts/**`, `src/gzkit/personas/**`
- [ ] CLI surface: `gz init --update` manpage at `docs/user/manpages/gz-init.md`; behave coverage in `features/init.feature`
- [ ] Validation surface: `gz validate --distribution` (or extended `--surfaces`) manpage + tests
- [ ] Mirror parity: `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/` regenerated cleanly from new package surface; `gz agent sync control-surfaces` no-ops post-promotion
- [ ] Docs: `docs/governance/trust-doctrine.md` cross-link to T0 (authored by ADR-0.0.31); `docs/user/runbook.md` updated with `--update` workflow

## Alternatives Considered

**A. Extend `pyproject.toml` `include:` only, leave scaffolders untouched.**
Rejected because the include extension alone ships the content but does not
make the scaffolders shipped-content-aware. `scaffold_core_skills` would
still render one-line stubs from `templates/skill.md` instead of copying
canonical content from the package. The wheel would carry the right files;
`gz init` would still produce stubs. Closes the *symptom* (files in wheel)
without closing the *class* (canonical surfaces don't reach fresh
installs). Per `AGENTS.md` § DO IT RIGHT #1, fix the class.

**B. Ship skills/rules under a separate `src/gzkit/_canonical/` namespace
that doesn't collide with the existing `gzkit.skills` and `gzkit.rules`
modules.** Rejected because asymmetry with the chores precedent
(`src/gzkit/chores/<slug>/`) is a doctrine smell. The module-to-package
conversion is the right shape and is reversible if a future ADR finds a
better layout; the asymmetric namespace would entrench a different layout
for skills/rules than for chores forever.

**C. Single ADR covering both T0 doctrine and canonical-surface mechanics.**
Rejected at ADR-0.0.31 authoring time per the amendment's own analysis: the
two concerns have different change cadences and different attestation
evidence shapes. Splitting them mirrors the proven ADR-0.0.18 ↔ ADR-0.0.17
(taxonomy) and AGENTS.md § Defect-fix routing ↔ § DO IT RIGHT (#6c)
patterns where doctrine and mechanism live in dedicated artifacts.

**D. Defer `gz init --update` to a follow-up ADR.** Rejected because
without `--update`, the only upgrade path on existing projects is `--force`
(full wipe). Cross-version upgrades silently leave stale artifacts in
place; the operator has explicitly named this as defect class D in the GHI
#318 body. Including `--update` in this ADR closes class D in the same
patch set as classes A–C.

**E. Skip the build-then-install smoke test; trust unit tests of the
scaffolders.** Rejected because the entire failure mode (self-hosting
blindness) was that unit tests against in-repo `.gzkit/` content silently
covered for the missing wheel content. The only way to falsify that mode is
a test that builds a real wheel and installs it into a real fresh venv. The
smoke test budget cost is the price of having T0 be more than advisory.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.32 | Pending | | | |
