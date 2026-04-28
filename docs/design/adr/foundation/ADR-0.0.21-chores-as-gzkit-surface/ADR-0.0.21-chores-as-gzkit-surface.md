---
id: ADR-0.0.21-chores-as-gzkit-surface
status: Validated
kind: foundation
semver: 0.0.21
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-24
---

# ADR-0.0.21-chores-as-gzkit-surface: Chores as a .gzkit/ Surface

## Persona

Agents working on this ADR inherit the `main-session` persona
(`.gzkit/personas/main-session.md`): craftsperson, governance-aware,
whole-file-reasoning, direct. The work is a layout migration with a
distribution contract — incremental patching is the wrong shape. Every
change to the resolver, scaffolder, packaging, and registry must land
complete (tests with implementation, imports with usage, docs with
behavior change).

## Intent

Chores are governance surfaces — the same class as skills, rules, personas,
and ceremonies — but they drifted into `ops/chores/` at the repo root and
never picked up `.gzkit/` delivery discipline. Today a downstream
`pip install py-gzkit` yields a working CLI with zero chores: the canonical
definitions (~33 directories of `CHORE.md` + `acceptance.json` + `README.md`)
and the registry (`config/gzkit.chores.json`) are not packaged in the wheel,
and resolution in `src/gzkit/commands/chores.py:18` and
`src/gzkit/commands/chores_exec.py:138,214` is `Path.cwd()`-bound via
`get_project_root()`. This is a distribution bug wearing a layout bug's
costume. This ADR locks the layout: canonical source ships in
`src/gzkit/chores/` inside the wheel; `gz init` scaffolds into
`.gzkit/chores/` in the consumer project; resolution prefers project-local
with `importlib.resources` fallback; `proofs/` remains project-local and
writable. Chores join skills/rules/personas/ceremonies as a first-class
`.gzkit/` surface, not a gzkit-repo-only scratch directory.

**Target state:** after this ADR lands, `pip install py-gzkit && gz init &&
gz chores list` returns the canonical chore set with zero manual
intervention. After this ADR lands, an operator reading the gzkit
repository layout can predict where any governance surface lives by
pattern match alone: `src/gzkit/<surface>/` ships it, `.gzkit/<surface>/`
consumes it, `scaffold_core_<surface>()` wires the two. After this ADR
lands, `ops/chores/` is deleted and `gz validate --chores-layout` prevents
its return.

**Precedent / exemplar:** the `.gzkit/` surface doctrine already delivers
skills, rules, personas, and ceremonies. Skills are the load-bearing
exemplar — `src/gzkit/skills.py:302-338` implements
`scaffold_core_skills(project_root, config, skip_existing=...)`; the
canonical source lives under the `gzkit` package; `gz init` scaffolds
into `.gzkit/skills/`; `gz agent sync control-surfaces` propagates to
vendor mirrors. This ADR applies that same pattern to chores. Personas
follow the same shape (`scaffold_default_personas`), and rules follow
it with the additional `control-surfaces` mirror step. The pattern is
proven; the chores system is the outlier. See `.claude/rules/skill-surface-sync.md`
for the canonical+mirror doctrine that chores are joining.

**Anti-patterns this ADR forecloses:**

- **Ship-only-with-the-repo.** Treating a governance surface as "gzkit
  internal tooling, not distributable." The original `ops/chores/`
  placement fell into this trap — it optimized for in-repo authoring
  convenience and forgot that the CLI advertises a chores system to
  downstream consumers. Any new governance surface that is advertised
  by the CLI must ship.
- **Cwd-bound resolution.** Using `Path.cwd()` or `get_project_root()`
  as the sole path resolver for shipped data. The cwd is the consumer's
  working tree, not gzkit's package location. Resolvers for shipped
  data must consult `importlib.resources` (or equivalent) as fallback
  at minimum, project-first with package-fallback ideally.
- **Read/write conflation.** Treating read-only canonical definitions
  (`CHORE.md`, `acceptance.json`) and writable runtime evidence
  (`proofs/`) as one unit at one path. Canonical definitions belong
  in the wheel; runtime evidence belongs in the consumer project.
  Conflating them forces either read-only evidence (broken) or
  writable canonical (not distributable).
- **Silent fallback.** Emitting no signal when the project-local path
  misses and the package-resource fallback fires. Silent fallback
  hides partial installs and makes "scaffolder never ran" a six-month
  mystery rather than a one-command diagnosis (see pre-mortem failure
  mode (a) in the Q&A transcript).
- **Force-include without surface parity.** Shipping files via
  `[tool.hatch.build.targets.wheel.force-include]` while leaving the
  layout at `ops/` or another non-`src/gzkit/` location. This fixes
  distribution while cementing layout drift, which was rejected as
  Alternative 1.

## Decision

**Rationale for the chosen shape:** the design follows the established
`.gzkit/` surface pattern (skills/rules/personas/ceremonies) because
parity reduces cognitive load — operators and agents reason about one
delivery pattern, not five. The resolver fallback preserves correctness
when `gz init` has not yet run (first-install ergonomics), but
project-first preference preserves overlay and proofs-writability
(the reasons we scaffold into `.gzkit/` at all). The registry-merge
contract is explicit because silent overwrite on upgrade is the
most common way scaffolded registries corrupt project-local state.
The layout validator and doctor command are included because the
pre-mortem identified silent regression (failure mode (a)) and
re-emergence of `ops/chores/` (failure mode (c)) as the two highest-
probability ways this ADR fails in 18 months — both are closed by
mechanical backstops, not documentation.

1. **Canonical source location:** `src/gzkit/chores/<slug>/` containing
   `CHORE.md`, `acceptance.json`, and `README.md`. Ships inside the
   `py-gzkit` wheel via `[tool.hatch.build.targets.wheel.force-include]`
   (or equivalent non-`.py` data-shipping mechanism verified in the
   packaging OBPI).
2. **Canonical registry location:** `src/gzkit/chores/registry.json`.
   Supersedes `config/gzkit.chores.json`, which is deleted as part of
   migration.
3. **Downstream consumer surface:** `.gzkit/chores/` — scaffolded into the
   consumer project by `gz init` at first run, repaired by `gz init` on
   gzkit version upgrades. Mirrors the delivery pattern of
   `scaffold_core_skills` (`src/gzkit/skills.py:302-338`) and
   `scaffold_default_personas`.
4. **Config key:** `GzkitConfig.paths.chores = ".gzkit/chores"` — addressable,
   same shape as `paths.skills`. Enables projects to relocate chores if
   they need a non-default path (same flexibility skills already have).
5. **Resolver order:**
   - First: `project_root / config.paths.chores / <slug>/` (project-scaffolded).
   - Fallback: `importlib.resources.files("gzkit.chores") / <slug>/`
     (package-shipped canonical).
   - Same fallback order applies to the registry.
   - Error paths name both attempted locations so "scaffolder didn't run"
     is distinguishable from "slug is wrong" from "package is corrupt."
6. **Registry merge contract (on `gz init` repair):** canonical registry
   is authoritative for shipped chore slugs; local registry overlays with
   project-only chores; reconciliation is keyed by slug with
   **canonical wins on shipped slugs, local wins on unknown slugs**.
   `gz init --repair` prints a diff and, unless `--yes`, prompts before
   writing — so an operator's project-local chores are never silently
   overwritten by a canonical upgrade.
7. **Proofs:** stay project-local under `.gzkit/chores/<slug>/proofs/`.
   Already writable, already the expected shape, no change to the
   existing proof-writing path in `chores_exec.py`.
8. **Diagnostic surface:** `gz chores list --explain` shows which path
   resolved each chore (project-scaffolded / package-shipped fallback /
   missing). Fallback hits emit a structured log event so "scaffolder
   never ran" is a detectable state rather than silent success.
9. **Mechanical backstop:** `gz validate --chores-layout` fail-closes
   (exit 3) on any `CHORE.md` or `acceptance.json` discovered outside
   `src/gzkit/chores/` (canonical) or `.gzkit/chores/` (project-scaffolded).
   Prevents a future authoring drift that re-creates `ops/chores/`.
10. **Repair command:** `gz chores doctor` re-scaffolds missing
    `.gzkit/chores/<slug>/` directories from the canonical package
    without touching `proofs/`. 2am-operator recovery path when the
    normal resolver path is broken but package resources are fine.
11. **Migration artifacts deleted:** `ops/chores/` (all ~33 directories),
    `config/gzkit.chores.json`, and `ops/chores/CLAUDE.md` are removed
    from the tree after migration. The agent contract from
    `ops/chores/CLAUDE.md` migrates into `src/gzkit/chores/README.md`.
12. **Rule/doc updates:** `.gzkit/rules/chores.md` paths frontmatter and
    body; `docs/user/runbook.md`; `docs/user/manpages/`; root `CLAUDE.md`
    and `AGENTS.md` if they reference `ops/chores/` directly.
13. **Dependency gate to ADR-0.28.0:** the in-flight
    `ADR-0.28.0-chores-system-maturity-absorption` (absorbing opsdev's
    19-module executor pipeline into gzkit) has a closeout prerequisite
    that this ADR is Validated. Landing 0.28.0's decomposition on top
    of the wrong distribution model locks the bug in at deeper structural
    depth; the prerequisite prevents that.

## Consequences

### Positive

1. **`pip install py-gzkit` delivers a working chores system out of the
   box.** Operators get the canonical chore set without cloning the
   gzkit repo. This is the bug fix.
2. **Chores join the `.gzkit/` surface-parity doctrine.** Operators reason
   about skills, rules, personas, ceremonies, and chores as one class —
   same layout, same scaffolding, same resolution, same upgrade path.
   Agent instructions simplify: one pattern, applied consistently.
3. **Project-local chore overlay becomes first-class.** Projects can
   author custom chores under `.gzkit/chores/<slug>/` that the CLI
   discovers without registry edits to the package (mechanism: local
   registry overlay on unknown slugs per Decision #6).
4. **Proofs have a stable, project-local, commitable home.** Already
   true under `ops/`, still true under `.gzkit/` — the invariant
   is preserved through the migration.
5. **Mechanical backstops prevent future layout drift.** The layout
   validator (Decision #9) and the `--explain` diagnostic surface
   (Decision #8) make regressions detectable rather than silent.
6. **Unblocks `ADR-pool.vendor-scoped-chores`.** With the distribution
   layout stable, the vendor-field work can land on solid ground without
   competing migration in-flight.
7. **Reverse-compatible data shape.** `CHORE.md`, `acceptance.json`,
   `README.md` per-slug structure is unchanged. The migration is a
   location move, not a schema change.

### Negative

1. **Two registry locations exist during migration.** `config/gzkit.chores.json`
   and `src/gzkit/chores/registry.json` coexist for the duration of the
   migration OBPI. The resolver's fallback order disambiguates, but the
   window is real and must be scoped tightly to a single OBPI.
2. **`importlib.resources` semantics across install modes are a verified
   assumption, not a given.** Wheel install, editable install
   (`pip install -e .`), and pyinstaller binary build
   (`pyproject.toml:78`) all need to be tested. The resolver OBPI carries
   this verification burden.
3. **Scaffolder-never-ran is a new silent-degradation risk.** The
   `importlib.resources` fallback means `gz chores` keeps working even
   when `gz init` was never run — which is good for usability but hides
   an incomplete install. Decision #8's structured fallback-hit logging
   is the mitigation.
4. **Registry-merge contract adds semantics that need testing.**
   Decision #6 is a contract, not a detail. Edge cases: slug renamed
   canonically, slug removed canonically, local chore has same slug as
   a new canonical chore. All need explicit test coverage.
5. **ADR-0.28.0 coordination cost.** The dependency gate (Decision #13)
   adds a blocking relationship between two pending ADRs. If 0.28.0's
   absorption work is blocked waiting for this ADR's 9 OBPIs, the
   critical path lengthens.
6. **Reverse-migration has non-zero cost.** Two-way door per forcing
   function #6: ~20 lines of resolver revert, mechanical file moves,
   but any downstream project that adopted `.gzkit/chores/` in the
   adoption window has data to unwind. Landing pre-1.0 (current
   version 0.25.15) keeps the adoption surface small.
7. **Nine OBPIs is a non-trivial pipeline.** Each one gates on Gate 5
   human attestation (foundation-kind rigor per ADR-0.0.18 § Lane & Kind
   Attestation Matrix), regardless of OBPI-level lane. The attestation
   load is real.

## Decomposition Scorecard

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 9

<!--
Split rationale:
- Single-Narrative: layout migration, resolver logic, scaffolder, packaging, docs are five orthogonal narratives
- Surface Boundary: internal resolver vs external CLI surface vs packaging surface vs .gzkit/ filesystem surface
- State Anchor: project-local state (.gzkit/chores/) vs package-shipped state (src/gzkit/chores/) are different state anchors
- Testability Ceiling: BDD install-and-scaffold scenario, layout validator, doctor command each demand independent test surfaces
-->


## Checklist

- [ ] OBPI-0.0.21-01: Physical migration — move `ops/chores/<33 dirs>` → `src/gzkit/chores/`; move `config/gzkit.chores.json` → `src/gzkit/chores/registry.json`; delete origin paths including `ops/chores/CLAUDE.md`
- [ ] OBPI-0.0.21-02: Config schema — add `paths.chores` to `GzkitConfig` with default `.gzkit/chores`, mirroring `paths.skills`
- [ ] OBPI-0.0.21-03: Wheel packaging — configure `pyproject.toml` to ship chore data files in the wheel; verify across wheel, editable, and pyinstaller install modes
- [ ] OBPI-0.0.21-04: Resolver — project-first lookup with `importlib.resources` fallback in `commands/chores.py` and `commands/chores_exec.py`; `--explain` diagnostic surface; error messages naming both attempted locations
- [ ] OBPI-0.0.21-05: Scaffolder — implement `scaffold_core_chores(project_root, config, skip_existing=...)` mirroring `scaffold_core_skills`; wire into `init_cmd.py`; implement registry-merge contract on repair
- [ ] OBPI-0.0.21-06: Rule and documentation updates — `.gzkit/rules/chores.md`, `docs/user/runbook.md`, `docs/user/manpages/gz-chores.md`, root `CLAUDE.md`/`AGENTS.md`; migrate `ops/chores/CLAUDE.md` content into `src/gzkit/chores/README.md`
- [ ] OBPI-0.0.21-07: BDD scenario — install-and-scaffold feature under `features/chores_distribution.feature` proving `pip install py-gzkit` → `gz init` → `gz chores list` returns the canonical set
- [ ] OBPI-0.0.21-08: Layout validator — `gz validate --chores-layout` fail-closing (exit 3) on any `CHORE.md` or `acceptance.json` outside `src/gzkit/chores/` or `.gzkit/chores/`
- [ ] OBPI-0.0.21-09: Doctor command — `gz chores doctor` re-scaffolds missing `.gzkit/chores/<slug>/` directories from canonical package without touching `proofs/`

## Q&A Transcript

### Tier 1 — ADR Pro-Forma

**Kind:** `foundation` — chores as a `.gzkit/` surface is an identity-shaping
invariant of how gzkit delivers governance tooling to downstream projects;
it sits in the same class as skills/rules/personas/ceremonies delivery.

**Lane:** `heavy` — changes the CLI resolver contract, changes wheel
packaging (external distribution surface), introduces new scaffolding
behavior consumed by `gz init`. All three are external contracts requiring
Gate 3 docs, Gate 4 BDD, Gate 5 attestation.

**Problem:** See Intent section. In short: `pip install py-gzkit` delivers
zero chores today because `ops/chores/` and `config/gzkit.chores.json`
are not in the wheel and resolution is cwd-bound.

**Decision:** See Decision section.

**Alternatives:** See Alternatives Considered section below.

**Positive/Negative Consequences:** See Consequences section.

**Checklist items (9):** See Checklist section.

### Tier 2 — Design Forcing Functions

**1. Pre-Mortem — 18 months from now this has failed spectacularly. Why?**

Four failure scenarios named during interview (operator confirmed all
four as plausible):

- (a) The resolver fallback masked a broken installation for months;
  `gz chores` worked via package resources while the `.gzkit/chores/`
  scaffolder never ran, and nobody noticed until a proofs-writing bug
  surfaced. **Mitigation:** Decision #8 structured fallback-hit logging
  and `--explain` diagnostic.
- (b) Registry merge on upgrade wasn't designed; stale project-local
  `registry.json` diverged from canonical on each release and operators
  hand-edited it to resync. **Mitigation:** Decision #6 explicit
  registry-merge contract.
- (c) `ops/chores/` came back because no mechanical check enforced the
  canonical location; git history and a stale README pointed the next
  authoring agent at the wrong place. **Mitigation:** Decision #9
  layout validator (OBPI 8).
- (d) ADR-0.28.0 ignored the prerequisite and landed its decomposition
  work on the old layout, creating two resolvers and two registry
  locations. **Mitigation:** Decision #13 dependency gate.

**2. What Would Have to Be True — chosen path (`src/gzkit/chores/` + `.gzkit/chores/`):**

- `.gzkit/` surface-parity doctrine is genuinely load-bearing.
- Chores have a meaningful per-project overlay use case (custom chores,
  tuned lanes, project-specific acceptance thresholds).
- Proofs genuinely belong at the project level (auditable, committable).
- `importlib.resources` works reliably across wheel install, editable
  install, and pyinstaller binary build.

**— rejected Alternative 1 (`[force-include] ops/` only):**

- Chores would have to be gzkit-repo-internal by design, not a
  distributable tooling surface.
- Proofs would have to be fine in `site-packages/` (read-only) or
  redirected to a cache dir — no `.gzkit/` project surface needed.
- The `.gzkit/` surface doctrine would have to be coincidental for
  skills/rules/personas rather than a deliberate pattern.

Shakiest condition on the chosen path: the project-overlay use case.
If nobody adds project-local chores, the `.gzkit/chores/` scaffolding
is overhead for a theoretical benefit. Operator confirmed this is
acceptable — even with zero project overlays ever authored, the
scaffolding still delivers proofs-writability and registry-local
visibility, both of which are non-theoretical.

**3. Constraint Archaeology:**

- "Canonical source must live in `src/<package>/`": **real and active.**
  `[tool.hatch.build.targets.wheel] packages = ["src/gzkit"]` makes
  anything outside that tree non-distributable.
- "Chores must be writable for proofs": **real.** Inherited from
  ADR-0.8.0 executor design; proofs accumulate; accumulation needs
  a writable home.
- "Chores live beside the chore registry file at `config/`": **assumed
  and stale.** Accident of original authoring order, not a designed
  coupling. This ADR unwinds it.

**4. Assumption Surfacing:**

- Implicit: `gz init` is always run before `gz chores` — empirically
  false; counter-move is the fallback resolver.
- Implicit: project-local chores are rare; if the opposite were true,
  the registry-merge contract (Decision #6) becomes load-bearing rather
  than edge-case.
- Implicit: `importlib.resources` semantics are uniform across install
  modes — not yet verified for the pyinstaller binary path; OBPI 3
  carries this verification.
- Implicit: chore count stays roughly stable (~33). Acceptable at
  hundreds too, but `gz init` scaffold time would become visible.

**5. 2am Operator Question — `gz chores run <slug>` failing with
`FileNotFoundError: acceptance.json`:**

Operator needs: `--explain` to see which path resolved (Decision #8);
`gz chores doctor` to re-scaffold without touching proofs (OBPI 9);
human-readable registry JSON (already true); error messages naming both
attempted locations so scaffolder-not-run is distinguishable from
wrong-slug is distinguishable from corrupt-package (Decision #5).

**6. Reversibility Assessment:**

Two-way door with work. File moves are mechanical; resolver revert is
~20 lines; `paths.chores` removal is a breaking config change for any
adopter. Reversibility cost scales with adoption window. Landing
pre-1.0 (current version 0.25.15) keeps the adoption surface small and
the reverse migration bounded. A reverse-migration script belongs with
closeout evidence if reversal ever fires.

**7. Scope Minimization — half-time cut:**

Must-have: OBPIs 1-3 (migration, config, packaging). Essential:
OBPIs 4-5 (resolver, scaffolder) + OBPI 6 (docs). Cuttable under time
pressure: OBPIs 7 (BDD), 8 (layout validator), 9 (doctor). **Cut not
taken** — the pre-mortem failure modes (a), (c) are directly closed
by OBPIs 8 and 9, and skipping BDD reintroduces the silent-distribution-
bug class. The hardening OBPIs are the point; omitting them reintroduces
the class of defect this ADR closes.

**Closing — Subsequent ADRs forced:**

1. **Registry merge semantics for scaffolded surfaces** — generalizable
   to skills, rules, personas, any `.gzkit/` surface with a registry.
   Foundation follow-up likely.
2. **`ADR-pool.vendor-scoped-chores`** — unblocked; vendor field work
   lands on the new layout without competing migration.
3. **ADR-0.28.0 dependency resolution** — how absorption OBPIs
   coordinate with this ADR's layout becomes its own design increment.
4. **Chore execution sandboxing (pool)** — chores are now distributed
   tooling; `gz chores run` becomes a supply-chain surface where
   shipped code executes in user projects. Not immediate, pool-worthy.

## Evidence

- [ ] Gate 1 — ADR recorded: this file; OBPI briefs in `obpis/`;
  registries synced (`docs/design/adr/adr_index.md`,
  `docs/design/adr/adr_status.md`,
  `docs/governance/GovZero/adr-status.md`).
- [ ] Gate 2 — Tests pass: `uv run gz test`.
- [ ] Gate 3 — Docs updated: rules, runbook, manpages per OBPI 6;
  `uv run mkdocs build --strict`.
- [ ] Gate 4 — BDD verified: `features/chores_distribution.feature` per
  OBPI 7; `uv run behave features/chores_distribution.feature`.
- [ ] Gate 5 — Human attests: per-OBPI attestation at brief completion
  (foundation-kind rigor per ADR-0.0.18); ADR-level attestation at
  closeout.

## Alternatives Considered

1. **Keep `ops/chores/` + packaging `[force-include]`:** packaging
   works, but cements the wrong location and breaks the `.gzkit/`
   surface-parity doctrine. Downstream projects get no scaffolded
   `.gzkit/chores/` overlay; proofs have no project-local home unless
   a separate mechanism is added. Rejected because it fixes the
   distribution symptom while preserving the layout defect.
2. **Ship registry only, resolve chores via HTTP on first use:**
   rejected. Offline-hostile; violates hermetic-install expectation;
   introduces a network dependency for a baseline governance surface;
   incompatible with the pyinstaller binary build path.
3. **Keep current `ops/` layout, document chores as gzkit-repo-only:**
   rejected. Contradicts the tooling contract — `py-gzkit` advertises
   a chores system and delivering nothing is the bug, not the design.
4. **Symlink `.gzkit/chores/` → `site-packages/gzkit/chores/`:**
   rejected. Windows-hostile (symlink semantics unreliable on
   non-admin shells); breaks when gzkit upgrades (dangling symlink
   after wheel replacement); can't host writable `proofs/` inside
   a read-only target.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.21 | Validated | g0 (agent-relayed) | 2026-04-28 | All 9 OBPIs attested_completed; agent audit pass over evidence (3703 tests OK, mkdocs strict, BDD 4/4, layout validator clean, wheel ships 110 chores entries); operator verbal `attest completed`; agent-relayed Gate-5 emit via `gz adr audit-begin/audit-end` ceremony marker (GHI #292; sub-scope of GHI #354) |
