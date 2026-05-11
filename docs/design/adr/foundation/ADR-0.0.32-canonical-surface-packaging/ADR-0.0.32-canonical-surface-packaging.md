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
to be correct. Adopts the proven ADR-0.0.21 chores precedent's mechanical
arms (importlib.resources enumeration, doctor repair surface, validate-layout
check, wheel-include discipline) while diverging from chores on the surface
authoring model: `.gzkit/<surface>/` is the authored canonical source-of-truth
in every gzkit-or-adopter repo (operators always edit there); `src/gzkit/<surface>/`
carries byte-equivalent copies for wheel-shipping; `.[vendor]/` carries
vendor mirrors. Both `src/gzkit/` and `.[vendor]/` sync FROM `.gzkit/`. Refuses
the "we'll just extend the include list" shortcut because the include list
alone does not make the scaffolders shipped-content-aware, and refuses the
chores-pure "single canonical at `src/gzkit/`, project-overlay if operator
wants edits" framing because skills/rules/templates/personas are themselves
authored at `.gzkit/` in this very repo and cannot be moved without
displacing the authoring surface.

## Intent

Mechanically satisfy the T0 distribution invariant authored by ADR-0.0.31
across every canonical surface that today exists only in this repo's
`.gzkit/` tree: skills (~70), rules (14), hooks, templates, personas. The
goal is that `pip install py-gzkit && gz init` in a fresh greenfield
project yields canonical surfaces under the adopter's `.gzkit/<surface>/`
tree byte-equivalent (modulo project-name substitution) to a frozen
baseline manifest, with `gz init --update` providing version-aware refresh
for existing projects.

This ADR is the mechanical counterpart to ADR-0.0.31's doctrine surface.
ADR-0.0.21 (chores-as-gzkit-surface) supplies every mechanical arm of this
ADR's scope (importlib.resources enumeration, doctor-repair, layout
validate, wheel-include discipline). What this ADR does *not* adopt from
the chores precedent is its single-canonical-at-`src/gzkit/` framing:
chores was promoted *into* the package because there was nowhere else
chores content lived; skills and rules were authored *at* `.gzkit/` from
the start, and `.gzkit/` remains the authored source-of-truth in every
gzkit-or-adopter repo. The chores precedent's gap that this ADR closes is
purely about packaging plumbing — wheel-shipping content, scaffolder
canonical resolution, fresh-install closure — not about which surface
operators edit. `.gzkit/` is the editing surface; `src/gzkit/` is its
wheel-shipping shadow; `.[vendor]/` is its agent-runtime shadow.

The canonical-routing invariant is binding across every gzkit surface,
present and future: `.gzkit/<surface>/` ↔ `src/gzkit/<surface>/` (dev-time
byte-parity for wheel-shipping) and `.gzkit/<surface>/` ↔ `.[vendor]/<surface>/`
(agent-runtime vendor mirrors). Both arrows originate at `.gzkit/`; reads
in this repo always resolve from `.gzkit/`; writes from `gz agent sync
control-surfaces` always derive from `.gzkit/`. In adopter projects, the
identical invariant holds once `gz init` has populated `.gzkit/` from the
wheel's package data.

## Decision

Establish the dual-surface canonical-routing model across skills (and
forward to rules, templates, personas, hooks) — `.gzkit/<surface>/` retained
as the authored canonical source-of-truth; byte-equivalent copies added at
`src/gzkit/<surface>/` so the wheel ships the canonical content; vendor
mirrors at `.[vendor]/<surface>/` regenerated from `.gzkit/<surface>/` by
`gz agent sync control-surfaces`. Convert `src/gzkit/skills.py` →
`src/gzkit/skills/__init__.py` and `src/gzkit/rules.py` →
`src/gzkit/rules/__init__.py` so the package surfaces can coexist with the
existing public-symbol API. Build a `CORE_RULES` registry symmetric to
`CORE_SKILLS` and `CORE_CHORES`. Wire `scaffold_core_rules` into
`init_cmd._scaffold_project_skeleton` and `_repair_missing_artifacts`.
Refactor `scaffold_core_skills` to copy canonical SKILL.md content from
`importlib.resources.files("gzkit.skills")` (the wheel's package surface)
into the adopter's `.gzkit/skills/<slug>/` rather than rendering one-line
stubs through `templates/skill.md`. Extend the wheel `include:` list to
ship the new surface trees. Add `gz init --update` for version-aware
refresh of the adopter's `.gzkit/` that preserves project-local edits.
Author a build-then-install T0 smoke test that proves byte-equivalence
against a frozen baseline manifest. Extend `gz validate --surfaces` (or
add a dedicated `--distribution` scope) with a T0 check that exits 3 on
any unshipped canonical surface. Broaden `gz agent sync control-surfaces`
so a single invocation propagates `.gzkit/<surface>/` to both
`src/gzkit/<surface>/` (dev-time wheel-shipping byte-parity) and
`.[vendor]/<surface>/` (agent-runtime vendor mirrors).

The package layout:

```
.gzkit/skills/
    <slug>/
        SKILL.md       # AUTHORED canonical source-of-truth (edited here)

src/gzkit/skills/
    __init__.py        # current src/gzkit/skills.py contents (preserves `from gzkit.skills import X`)
    <slug>/
        SKILL.md       # byte-equivalent copy of .gzkit/skills/<slug>/SKILL.md (ships in the wheel)

.gzkit/rules/
    <slug>.md          # AUTHORED canonical source-of-truth (edited here)

src/gzkit/rules/
    __init__.py        # current src/gzkit/rules.py contents (preserves `from gzkit.rules import X`)
    <slug>.md          # byte-equivalent copy of .gzkit/rules/<slug>.md (ships in the wheel)

.claude/skills/, .github/skills/, .github/instructions/, .claude/rules/
                       # VENDOR mirrors regenerated from .gzkit/ by gz agent sync
```

The module-to-package conversion is unavoidable: `src/gzkit/skills.py` and
`src/gzkit/skills/<slug>/SKILL.md` cannot coexist; converting the file to
`src/gzkit/skills/__init__.py` keeps `from gzkit.skills import X` working
because Python resolves the symbol through the package's `__init__.py`
re-exports. Same for `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py`.

Canonical-routing direction (binding):

1. **In this repo (gzkit dev):** operators edit `.gzkit/<surface>/`; `gz agent
   sync control-surfaces` propagates byte-equivalent content to
   `src/gzkit/<surface>/` (the wheel-shipping copy) and to
   `.[vendor]/<surface>/` (the agent-runtime mirrors). Runtime reads in this
   repo (any tool that consults a canonical artifact) resolve from
   `.gzkit/<surface>/` directly — no fallback chain.
2. **In an adopter repo (post `gz init`):** `gz init` reads canonical content
   from the installed wheel's package data via
   `importlib.resources.files("gzkit.<surface>")` and writes it into the
   adopter's `.gzkit/<surface>/`. From that point forward the adopter's
   `.gzkit/` is *their* project canonical surface; the same propagation
   invariant binds (adopter's `gz agent sync control-surfaces` regenerates
   `.[vendor]/`; `gz init --update` and `gz upgrade` refresh `.gzkit/` from
   the wheel; the adopter's `src/gzkit/` is not in scope because adopter
   projects do not re-ship the wheel).
3. **Scaffolder project-first → package-fallback** is a write-time semantic
   for the adopter-side init path only: when scaffolding into the adopter's
   `.gzkit/<surface>/<slug>/`, if a project-local file already exists it
   is preserved (`skip_existing=True`); if absent, it is copied from the
   wheel's package surface. The "fallback" word names the *source of the
   first write*, not a runtime resolution chain — once written, the adopter's
   `.gzkit/` is canonical for that project.

## Comparator Uplift (2026-05-07)

Tessl/BMAD/GSD package context so agents can enter a workflow quickly. gzkit's
packaging bar is higher: packages are canonical source plus generated mirrors,
versioned metadata, trust boundary, load budget, and validation result. This ADR
should make that package shape the default for skills, rules, personas, and
future context packages so portability never means hand-copied markdown.

## Consequences

### Positive

- Closes the GHI #318 class: `pip install py-gzkit && gz init` in a fresh
  project yields canonical content under the adopter's `.gzkit/` tree
  byte-equivalent to the baseline manifest, not one-line stubs.
- Establishes the canonical-routing model as binding for every gzkit
  surface — present and future. `.gzkit/<surface>/` is the authored
  source-of-truth; `src/gzkit/<surface>/` and `.[vendor]/<surface>/` sync
  from it. Single mental model across skills, rules, templates, personas,
  hooks, and any future canonical surface.
- Enables version-aware upgrades via `gz init --update` rather than the
  current binary "leave alone or `--force` wipe."
- Provides the mechanical enforcement T0 needs to be more than advisory:
  the smoke test fails the build if a canonical surface stops shipping,
  and `gz validate --distribution` fails any commit that adds a canonical
  surface without wheel coverage.
- Preserves `.gzkit/` as the authoring surface in this very repo. Operators
  and agents continue editing where they already edit; the byte-parity
  test (`tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity`,
  landed under OBPI-01) fails closed on any drift between `.gzkit/<surface>/`
  and `src/gzkit/<surface>/`, making the dual-surface invariant mechanical.
- `gz agent sync control-surfaces` becomes a single unified surface for
  propagating `.gzkit/` to every derived surface — wheel-shipping copy at
  `src/gzkit/` and vendor mirrors at `.[vendor]/` — closing the manual-`cp`
  gap that GHI #449 surfaced.

### Negative

- ~84 byte-equivalent file copies (~70 skills + 14 rules) added under
  `src/gzkit/` while the authored originals stay at `.gzkit/`, plus two
  module-to-package conversions. Cross-references to
  `from gzkit.rules import X` / `from gzkit.skills import X` (~25 sites in
  src/, tests/) must continue resolving — package `__init__.py` re-exports
  preserve the API, but the conversion itself is a structural change that
  must be done correctly.
- The wheel grows: ~84 new content files plus eventual hooks/templates/
  personas additions. Build time and install time both increase modestly.
- The dual-surface byte-parity discipline now binds for all canonical
  content. Authoring a new skill or rule means editing at `.gzkit/` AND
  running `gz agent sync control-surfaces` so the wheel-shipping copy and
  vendor mirrors stay byte-equivalent. The byte-parity test fails closed
  on drift, so any forgotten sync run is detected at `gz check` time.
- The T0 smoke test must build a wheel and install into a temp venv on
  every CI run — substantially slower than unit tests. Lives in `features/`
  per the test-runner contract; budgeted accordingly.
- Heavy-lane attestation rigor applies (foundation-kind + heavy lane =
  brief-level Gate 5 attestation per § Lane & Kind Attestation Matrix).
  Each of the eight OBPIs gates on a human witness.

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
     Establishes the dual-surface canonical-routing model: .gzkit/ is authored
     source-of-truth; src/gzkit/ is the byte-equivalent wheel-shipping copy;
     .[vendor]/ is the agent-runtime mirror. Both src/gzkit/ and .[vendor]/
     sync FROM .gzkit/. -->

- [x] OBPI-0.0.32-01: Skills physical migration — establish dual-surface for all ~70 canonical skills: retain `.gzkit/skills/<slug>/SKILL.md` as authored source-of-truth AND add byte-equivalent copy at `src/gzkit/skills/<slug>/SKILL.md` for wheel-shipping; convert `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` preserving every public symbol re-export; byte-parity test fails closed on drift. Scaffolder refactor deferred to OBPI-02; sync mechanism deferred to OBPI-08.
- [ ] OBPI-0.0.32-02: Skills scaffolder refactor — refactor `scaffold_core_skills` to copy canonical SKILL.md content from `importlib.resources.files("gzkit.skills")` (the wheel's package surface) into the adopter's `.gzkit/skills/<slug>/`; preserve operator edits via `skip_existing=True`; delete (or document repurposing of) `src/gzkit/templates/skill.md`. Depends on OBPI-01 landing first.
- [ ] OBPI-0.0.32-03: Rules physical migration — establish dual-surface for all 14 canonical rules: retain `.gzkit/rules/<slug>.md` as authored source-of-truth AND add byte-equivalent copy at `src/gzkit/rules/<slug>.md` for wheel-shipping; convert `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserving every public symbol re-export; byte-parity test fails closed on drift. Registry + scaffolder + init wiring deferred to OBPI-04; sync mechanism deferred to OBPI-08.
- [ ] OBPI-0.0.32-04: Rules scaffolder authoring — build `CORE_RULES` registry symmetric to `CORE_SKILLS`/`CORE_CHORES`; author `scaffold_core_rules` that copies canonical rule content from `importlib.resources.files("gzkit.rules")` (the wheel's package surface) into the adopter's `.gzkit/rules/<slug>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). Depends on OBPI-03 landing first.
- [ ] OBPI-0.0.32-05: Add `gz init --update` flag — version-aware refresh of the adopter's `.gzkit/<surface>/` from the wheel's package data, with three-state detection (IDENTICAL/STALE/EDITED), manpage, behave coverage.
- [ ] OBPI-0.0.32-06: Author T0 smoke test (build wheel, install into temp venv, run `gz init`, assert byte-equivalence of the resulting `.gzkit/` tree against frozen baseline manifest); audit and extend `pyproject.toml [tool.hatch.build.targets.wheel] include:`; author `data/distribution_baseline_manifest.json`.
- [ ] OBPI-0.0.32-07: Extend `gz validate --surfaces` (or add `--distribution`) with T0 enforcement — verify every canonical surface in manifest is wheel-deliverable from `src/gzkit/`; fail-closed exit 3 on any package-data omission; flip T0 scorecard Promotable→Mechanical.
- [ ] OBPI-0.0.32-08: Canonical surface sync — broaden `gz agent sync control-surfaces` so a single invocation propagates `.gzkit/<surface>/` (authored canonical) to BOTH `src/gzkit/<surface>/` (wheel-shipping byte-parity copy, dev-time only) AND `.[vendor]/<surface>/` (vendor mirrors: `.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/`); idempotent on freshly-synced state; absorbs GHI #449 (`.gzkit/` → `src/gzkit/` dev-time sync) and the existing `.gzkit/` → `.[vendor]/` mirror flow into one mechanism. Depends on OBPI-03/04 landing first so rules are dual-surface before the sync mechanism covers them.

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
ADR-0.0.31 as the cited invariant in the `parent:` frontmatter. Eight OBPIs
run in dependency order: 01 (skills dual-surface, completed); 02 (skills
scaffolder), 03 (rules dual-surface), 04 (rules scaffolder) in parallel
after 01; 05 (`init --update`), 06 (T0 smoke test + wheel includes), 07
(`validate --distribution`) after 03/04; 08 (canonical surface sync —
`.gzkit/` to `src/gzkit/` AND `.[vendor]/`) last, gated on 03/04 so the
sync mechanism covers skills + rules + (forward) templates + personas +
hooks in one pass.

Canonical-routing course correction (2026-05-11): OBPI-01 was authored
with `git mv` ("move into wheel-shipped package data") semantics inherited
from the chores precedent. Mid-implementation, operator clarified the
canonical model is dual-surface — `.gzkit/<surface>/` retained as the
authored source-of-truth, byte-equivalent copy at `src/gzkit/<surface>/`
for wheel-shipping. The clarification was subsequently broadened to bind
across the full ADR-0.0.32 chain and every future gzkit canonical surface:
`.gzkit/<surface>/ ↔ src/gzkit/<surface>/` (dev-time wheel-shipping
byte-parity) AND `.gzkit/<surface>/ ↔ .[vendor]/<surface>/` (agent-runtime
vendor mirrors); both arrows originate at `.gzkit/`. ADR-0.0.32's narrative
sections (Persona, Intent, Decision, Consequences, Alternatives) and the
checklist items for OBPI-01/02/03/04/08 were rewritten to reflect this.
Insights record at `.gzkit/insights/agent-insights.jsonl`
(2026-05-11T08:55:00Z + 2026-05-11T09:58:00Z).

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/` (unit-tier coverage for `CORE_RULES`, `scaffold_core_rules`, package-resource enumeration, init-cmd integration)
- [ ] Smoke test: `features/distribution_invariant.feature` (build wheel → temp-venv install → `gz init` → byte-equivalence against `data/distribution_baseline_manifest.json`)
- [ ] Wheel manifest: `pyproject.toml [tool.hatch.build.targets.wheel] include:` extended for `src/gzkit/skills/**/*.md`, `src/gzkit/rules/**/*.md`, `src/gzkit/templates/*.md`, `src/gzkit/hooks/scripts/**`, `src/gzkit/personas/**`
- [ ] CLI surface: `gz init --update` manpage at `docs/user/manpages/gz-init.md`; behave coverage in `features/init.feature`
- [ ] Validation surface: `gz validate --distribution` (or extended `--surfaces`) manpage + tests
- [ ] Canonical surface sync: `gz agent sync control-surfaces` propagates `.gzkit/<surface>/` (authored canonical) to BOTH `src/gzkit/<surface>/` (wheel-shipping byte-parity copy) AND `.[vendor]/<surface>/` (`.claude/skills/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/`); sync is idempotent (no-op on freshly-synced state); byte-parity test passes post-sync
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

**F. Single-canonical at `src/gzkit/` with `.gzkit/` as project overlay
(pure chores precedent).** Rejected because skills/rules/templates/personas
are themselves *authored* at `.gzkit/` in this very repo — operators and
agents edit there, the test suite reads from there, the byte-parity test
landed under OBPI-01 enforces `.gzkit/` as authored source-of-truth. The
chores precedent's single-canonical-at-`src/gzkit/` framing works for
chores specifically because chores authoring lives nowhere else; reusing
that framing for skills/rules would either delete the existing `.gzkit/`
authoring surface (breaking 200+ agent and runbook references) or
preserve `.gzkit/` as a redundant copy with an undefined precedence rule.
The chosen dual-surface model — `.gzkit/` authored source-of-truth,
`src/gzkit/` byte-equivalent wheel-shipping copy synced from `.gzkit/` —
keeps the authoring surface intact while satisfying the T0 distribution
invariant.

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
