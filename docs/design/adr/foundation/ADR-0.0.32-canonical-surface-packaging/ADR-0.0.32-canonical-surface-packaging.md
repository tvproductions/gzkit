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

### Canonical-routing scope (binding)

The canonical-routing model applies uniformly to every gzkit-homegrown
authored canonical surface. The scope is operator-edited content the
wheel must ship and the agent runtime must consume:

| Surface | Authored canonical at | Wheel-shipping copy at | Vendor mirror(s) | Scaffolder | Status |
|---|---|---|---|---|---|
| skills | `.gzkit/skills/<slug>/SKILL.md` | `src/gzkit/skills/<slug>/SKILL.md` | `.claude/skills/`, `.github/skills/` | `scaffold_core_skills` (OBPI-02) | dual-surface ✓ (OBPI-01) |
| rules | `.gzkit/rules/<slug>.md` | `src/gzkit/rules/<slug>.md` | `.claude/rules/`, `.github/instructions/` | `scaffold_core_rules` (OBPI-04) | pending (OBPI-03) |
| personas | `.gzkit/personas/<slug>.md` | `src/gzkit/personas/<slug>.md` | `.claude/personas/`, `.github/personas/`, `.agents/personas/` (transformed) | `scaffold_core_personas` (OBPI-10) | pending (OBPI-09/10) |
| templates | `.gzkit/templates/<name>.md` | `src/gzkit/templates/<name>.md` | none (templates are consumed at scaffold-time, not exposed to agent runtime) | `scaffold_core_templates` (OBPI-12) | pending (OBPI-11/12 — reverse-migration from current `src/gzkit/templates/` location) |
| chores | `.gzkit/chores/<slug>/CHORE.md` + adjuncts | `src/gzkit/chores/<slug>/CHORE.md` + adjuncts | (none — chores are scaffolder/library only) | `scaffold_core_chores` (ADR-0.0.21) | dual-surface present with drift; normalize under OBPI-13 |

### Named exceptions to canonical-routing (binding)

Not every harness surface fits the canonical-routing model uniformly. The
two named exceptions below are documented gaps, not oversights. Each is
explicitly carved out of the dual-surface byte-parity invariant declared
above.

**Exception 1 — Hooks are vendor-coupled with uneven multi-vendor coverage.**

gzkit ships hooks for multiple vendors today:

- **Claude** — 12 hook scripts at `.claude/hooks/*.py` (ceremony-step-gate,
  control-surface-sync, ghi-triage-chat-silence, instruction-router,
  ledger-writer, obpi-completion-validator, pipeline-completion-reminder,
  pipeline-gate, pipeline-router, plan-audit-gate, post-edit-ruff,
  session-staleness-check). The most complete coverage.
- **Copilot** — `.github/copilot/hooks/ledger-writer.py` (1 script today)
  plus the Python adapter `src/gzkit/hooks/copilot.py`. Minimal but real.
- **Codex** — `.agents/` namespace reserved (skills + personas already
  populated); `.agents/hooks/` not yet populated; the Python `gzkit.hooks`
  package does not yet ship a `codex.py` adapter sibling to `claude.py`
  and `copilot.py`. Slot-reserved.

The design gap is **not** "Claude-only." The gap is that the three vendor
harnesses expose **non-uniform lifecycle models** — Claude's
PreToolUse / PostToolUse / SessionStart / Stop / Notification etc. has
no clean isomorphism to Copilot's event model, nor to Codex's; the
vendor-side hook contracts (signatures, I/O conventions, blocking
semantics, exit-code interpretation) differ enough that a single
gzkit-authored hook script cannot be cross-compiled to all three.

A meta-layer contract that abstracts across vendors was considered
(operator narrative, 2026-05-11) and declared currently infeasible —
even the level of specification a meta-contract would require is blocked
by vendor non-uniformity. The realistic path forward is per-vendor hook
scripts that share Python-library helpers from `src/gzkit/hooks/`
(`core.py`, `guards.py`, `obpi.py`) — which gzkit already does — without
attempting full cross-vendor parity at the script level.

Consequence: hooks are explicitly **OUT of scope** for the canonical-routing
model in this ADR. The per-vendor hook surfaces (`.claude/hooks/`,
`.github/copilot/hooks/`, `.agents/hooks/` when populated) each stay
vendor-runtime surfaces with vendor-specific shapes; `src/gzkit/hooks/`
stays a Python library API (per-vendor adapters + shared helpers)
consumed in-process; there is no `.gzkit/hooks/` authored canonical
surface that synchronizes across vendors. The wheel continues to ship
`src/gzkit/hooks/` via existing `pyproject.toml` includes; each vendor's
hook directory is maintained as that vendor's own surface, byte-coupled
to no other vendor's hook scripts.

The broader vendor-harness design framework is already captured by a
constellation of pre-existing pool ADRs that supersede the need for a
dedicated hooks-meta-layer parking artifact:

- **`ADR-pool.vendor-capability-matrix`** — the canonical machine-readable
  capability registry under `.gzkit/vendor-capabilities/<vendor>.yaml`
  with `upstream_maturity` × `gzkit_support` axes plus `source_url` +
  `source_checked_at` for surveillance. Hooks are one capability category
  in this matrix (`category: hooks`); they are not a separate scope.
- **`ADR-pool.harness-aware-execution-modes`** — the two-mode runtime
  adaptation architecture (Mode 1 universal via skill chains, Mode 2
  hook-enforced where the vendor provides lifecycle interception).
  Carries the rejection of the "lowest-common-denominator hook
  abstraction" alternative and names the triggers under which a vendor-
  neutral hook contract would become feasible.
- **`ADR-pool.vendor-alignment-{claude-code,codex,copilot,opencode}`** —
  per-vendor specialization (the subclass layer of the
  overarching-interface / per-vendor-specialization pattern).
- **`ADR-pool.vendor-scoped-chores`** — the mechanism for chores
  (and forward to hooks/skills) to declare vendor scope.
- **GHI #451** — the recurring vendor-harness-capability-surveillance
  chore that maintains the parity matrix and documents per-vendor
  lifecycle drift.

Together these surface a complete forward-design framework for the
multi-vendor hook landscape without requiring this ADR to park hooks
under a dedicated meta-layer-contract pool entry. The framework's
promotion ordering is operator-discretion; the surveillance chore (GHI
#451) keeps the per-vendor coverage status visible while the framework
remains in the pool.

**Exception 2 — Chores carry mixed file classes; byte-parity binds canonical content only.**

Chores (ADR-0.0.21) are homegrown skill/spec/ceremony/tool combos that
mix three file classes within each `<slug>/` directory:

- **Canonical authored content** — `CHORE.md`, `AGENTS.md`, doctrine
  markdown, scoring rubrics, planning prose. Operator-edited at `.gzkit/`;
  MUST be byte-equivalent at `src/gzkit/`.
- **Package-internal Python** — `__init__.py`, `__pycache__/`, library
  registries (e.g., `src/gzkit/chores/__init__.py`'s 224 lines of API).
  Package-only; never present at `.gzkit/`; EXEMPT from byte-parity.
- **Runtime-state files** — `CHORE-LOG.md`, `proofs/<artifact>`,
  `.gitkeep` markers, per-run logs. Operator-and-agent-written at
  runtime; the two surfaces diverge intentionally during chore execution;
  EXEMPT from byte-parity.

Consequence: the dual-surface byte-parity invariant applies to chores'
canonical authored content only. OBPI-13 (chores normalization)
normalizes the existing drift on canonical files (e.g.,
`.gzkit/chores/AGENTS.md` ↔ `src/gzkit/chores/AGENTS.md`) and codifies
the carve-out rules in `.claude/rules/skill-surface-sync.md` so future
chore authoring respects the class boundaries. OBPI-08's
`gz agent sync control-surfaces` MUST honor the carve-out
class-classifier — never overwrite a runtime-state file from the
`.gzkit/` side, never sync a package-only file onto the canonical side.

The runtime-state-mixed-with-canonical-instructions pattern itself is a
**design smell** (operator framing, 2026-05-11: *"keeping logs and
receipts with the instructions code [...] may be a design flaw"*). OBPI-13's
classifier is a **temporary accommodation** that preserves the
canonical-routing invariant without prejudging the deeper question of
whether runtime-state should live under the `<slug>/` directories at all.
The long-term direction — relocating runtime-state to a separate
`.gzkit/receipts/<surface>/<slug>/` tree so canonical `<slug>/` directories
carry only authored content — is parked at
**`ADR-pool.canonical-vs-runtime-separation`**. When that pool ADR is
promoted and the relocation lands, OBPI-13's classifier shrinks to a
single class (canonical authored content) and chores becomes
structurally clean under the canonical-routing model.

### Forward extension policy

Any future canonical surface added to gzkit (e.g., new agent-context
package types) MUST adopt the dual-surface model unless explicitly
declared a named exception by an attested ADR that justifies the carve-out
against this section's framing. The default is dual-surface; deviations
require attestation.

### Design gaps surfaced by this expansion

The expansion of the canonical-routing model from skills + rules to all
harness surfaces (skills, rules, personas, templates, chores) surfaced
two architectural gaps that are too large to absorb into this ADR and
are parked at pool ADRs for future promotion:

1. **`ADR-pool.canonical-vs-runtime-separation`** — runtime-state (logs,
   receipts, proofs, per-run artifacts) currently lives co-located with
   canonical instructions inside `<slug>/` directories. The chores
   class-classifier landed by OBPI-13 is a temporary accommodation; the
   structural fix is to relocate runtime-state into a separate
   `.gzkit/receipts/<surface>/<slug>/` tree. See Exception 2 above.

2. **`ADR-pool.central-config-airlineops-pattern`** — gzkit configuration
   is currently distributed across at least seven file locations
   (`pyproject.toml`, `.gzkit/manifest.json`, `data/*.json` registries,
   `.claude/settings.json`, per-surface frontmatter, etc.). Adding
   `CORE_PERSONAS` + `CORE_TEMPLATES` + further surface registries in
   this ADR's chain made the fragmentation visible. AirlineOps' pattern
   (per operator framing, 2026-05-11) provides a strong central-config
   seam gzkit should adopt; the pool ADR parks the question until
   ADR-0.0.32 closeout stabilizes the surface inventory.

Neither gap blocks ADR-0.0.32's OBPI work — they're consequences of the
expansion that justify dedicated future ADRs rather than scope-creep
into this one.

### Post-1.0 forward-look — adopter-side extensions

Adopters consume gzkit via `pip install py-gzkit && gz init` and edit
their project canonical surfaces under `.gzkit/`. The current model is
**unidirectional**: gzkit ships canonical content; adopters receive and
edit; adopters do not author their own canonical surfaces alongside
gzkit's, do not ship their own gzkit-derived wheels, and do not have
their own `src/gzkit/<surface>/` byte-equivalent shadow. The
canonical-routing invariant binds within gzkit's authoring repo and
within each adopter's project independently — not across them.

Operator framing (2026-05-11): "they adopt gzkit to do their work, it is
presently out of scope to accommodate extensions/enhancements. if they
adopt their own skills/rules, they would not mix with gzkit (hence the
prefix namespacing). maybe we can accommodate this as post release
enhancements."

The prefix-namespacing convention is already in place — gzkit's skills
use `gz-*` and `ghi-*` prefixes (`gz-prd`, `gz-plan`, `ghi-author`,
`ghi-triage`, etc.); adopters who author their own skills can use a
distinct prefix (their org or project slug) to avoid collision with
gzkit's canonical set. The same pattern can extend to rules, personas,
and templates if adopter-extension authoring becomes in scope.

What's NOT in scope for ADR-0.0.32 (deferred to post-1.0):

- A formal adopter-extension framework that lets adopter projects author
  their own dual-surface canonical content (e.g., adopter's `.gzkit/skills/`
  has both gzkit's `gz-*` skills AND the adopter's `myorg-*` skills, and
  the adopter's local `gz check` / `gz validate` honor both)
- An "adopter-publishes-gzkit-extension-wheel" workflow that lets an
  adopter ship their canonical-surface additions as a wheel that other
  consumers can install alongside gzkit
- A namespace-conflict-detection mechanism that fail-closes when an
  adopter's prefix collides with gzkit's

Future ADR (post-1.0): when adopter-extension demand emerges, the
canonical-routing model documented here should extend naturally —
adopters get the same dual-surface pattern at their authoring repo,
with prefix namespacing as the collision-avoidance discipline.

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

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 10
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 14

<!--
ORIGINAL scorecard (8 OBPIs, skills + rules + plumbing only):
  Data/State 1, Logic/Engine 2, Interface 2, Observability 1, Lineage 2 (Total 8)
  Baseline 4, Splits 1/1/1/1 = 4 (Final 8)
EXPANDED 2026-05-11 (8 → 13) to absorb personas + templates + chores
normalization per operator's canonical-routing-binds-across-all-harness-surfaces
clarification. Hooks remain a named exception (vendor-coupled, uneven
multi-vendor coverage), tracked under the pre-existing pool-ADR framework
(`ADR-pool.vendor-capability-matrix` + `ADR-pool.harness-aware-execution-modes` +
per-vendor `ADR-pool.vendor-alignment-*` ADRs) plus the surveillance
chore at GHI #451. Dimension bump: Data/State 1→2 (adds 3 more
canonical-surface families). Baseline Selected raised from 4 → 9 to absorb
the per-surface atomicity (each canonical surface gets its own migration
narrative, surface-boundary anchor, state-anchor in the ledger, and
testability ceiling — those four splits are honored by Baseline expansion,
keeping the binary split flags valid per scoring.py).
EXPANDED 2026-05-11 (13 → 14) to absorb `gz upgrade` adopter-side
surface-only refresh per GHI #450 — a CLI verb distinct from
`gz init --update` (OBPI-05). `gz init --update` is the canonical
project-refresh ceremony (all surfaces, version-aware diff/merge, manifest
mutation); `gz upgrade` is the surface-only refresh (per-`--surface`
filter, no scaffolder logic, no manifest mutation, optional `--force` and
`--dry-run` flags). Dimension bump: Observability 1→2 (adds `--dry-run`
reporting surface + idempotency exit-0 verification beyond OBPI-05's
three-state detection). Baseline Selected 9 → 10 absorbs the
surface-only-refresh narrative as distinct from the project-refresh
ceremony.

Scorecard parser contract (src/gzkit/core/scoring.py): split flags MUST
be 0 or 1; dimensions MUST be 0, 1, or 2; Baseline Range derives from
Dimension Total (≥9 → `5+`, open above); Final Target = Baseline Selected
+ Split Total. The original 2026-05-11 8 → 13 expansion encoded the
splits as 2 each (Split Total 8), which violated the parser contract;
this 13 → 14 expansion re-encoded the scorecard to a valid shape (splits
1 each + Baseline Selected 10) while preserving the same Final Target
arithmetic. The latent invalidity was discovered when `gz specify --item 14`
triggered scorecard parsing during this same authoring pass.
-->


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
- [ ] OBPI-0.0.32-08: Canonical surface sync — broaden `gz agent sync control-surfaces` so a single invocation propagates `.gzkit/<surface>/` (authored canonical) to BOTH `src/gzkit/<surface>/` (wheel-shipping byte-parity copy, dev-time only) AND `.[vendor]/<surface>/` (vendor mirrors: `.claude/skills/`, `.claude/rules/`, `.claude/personas/`, `.github/skills/`, `.github/instructions/`, `.github/personas/`, `.agents/personas/`); covers every dual-surface family (skills, rules, personas, templates, chores per § Canonical-routing scope); honors chores carve-out rules (canonical content syncs; package-only and runtime-state files exempt per § Named exceptions); idempotent on freshly-synced state; absorbs GHI #449 (`.gzkit/` → `src/gzkit/` dev-time sync) and the existing `.gzkit/` → `.[vendor]/` mirror flow into one mechanism. Depends on OBPI-03/04/09/11/13 landing first so every dual-surface family is established before the sync mechanism covers it.
- [ ] OBPI-0.0.32-09: Personas physical migration — establish dual-surface for all 6 canonical personas: retain `.gzkit/personas/<slug>.md` as authored source-of-truth AND add byte-equivalent copy at `src/gzkit/personas/<slug>.md` for wheel-shipping; create `src/gzkit/personas/__init__.py` if needed for package discovery (no public-symbol exports beyond the data surface); byte-parity test fails closed on drift. Vendor mirrors at `.claude/personas/`, `.github/personas/`, `.agents/personas/` remain a transformed shape (1-line trimmed renders distinct from full authored content) — that transformation is intentional and OUT of the byte-parity invariant for vendor mirrors. Scaffolder + init wiring deferred to OBPI-10; sync mechanism deferred to OBPI-08.
- [ ] OBPI-0.0.32-10: Personas scaffolder authoring — build `CORE_PERSONAS` registry symmetric to `CORE_SKILLS`/`CORE_RULES`/`CORE_CHORES`; author `scaffold_core_personas` that copies canonical persona content from `importlib.resources.files("gzkit.personas")` (the wheel's package surface) into the adopter's `.gzkit/personas/<slug>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). Depends on OBPI-09 landing first.
- [ ] OBPI-0.0.32-11: Templates reverse-migration — establish dual-surface for all 13+ canonical templates by REVERSE-migrating from the current single-surface location: `git mv src/gzkit/templates/*.md .gzkit/templates/*.md` to establish `.gzkit/templates/` as the new authored canonical source-of-truth; add byte-equivalent copy back at `src/gzkit/templates/*.md` for wheel-shipping; preserve `src/gzkit/templates/__init__.py` (Python package) and any non-`.md` adjuncts; existing `render_template()` consumers continue resolving through `gzkit.templates` package; byte-parity test fails closed on drift. This is a direction reversal from skills/rules/personas migrations because templates already live at the package surface today. Scaffolder + init wiring deferred to OBPI-12; sync mechanism deferred to OBPI-08.
- [ ] OBPI-0.0.32-12: Templates scaffolder authoring — build `CORE_TEMPLATES` registry symmetric to `CORE_SKILLS`/`CORE_RULES`/`CORE_PERSONAS`/`CORE_CHORES`; author `scaffold_core_templates` that copies canonical template content from `importlib.resources.files("gzkit.templates")` (the wheel's package surface) into the adopter's `.gzkit/templates/<name>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair); preserve `render_template()` resolution semantics so it consults the adopter's `.gzkit/templates/` project-first per the same project-first → package-fallback shape. Depends on OBPI-11 landing first.
- [ ] OBPI-0.0.32-13: Chores normalization — apply the § Named exceptions / Exception 2 carve-out doctrine to the existing `.gzkit/chores/` ↔ `src/gzkit/chores/` parallel structure. Bring canonical authored content (`CHORE.md`, `AGENTS.md`, doctrine markdown, scoring rubrics) into byte-parity; codify exempt classes (package-only `__init__.py`/`__pycache__`/`README.md`-when-package-only; runtime-state `CHORE-LOG.md`/`proofs/<artifact>`/`.gitkeep`) in `.claude/rules/skill-surface-sync.md` as the carve-out rule reference; teach OBPI-08's sync mechanism the class-classifier so syncs never overwrite runtime-state and never propagate package-only files onto the canonical side; add byte-parity tests scoped to canonical content classes only.
- [ ] OBPI-0.0.32-14: `gz upgrade` subcommand — adopter-side surface-only refresh of `.gzkit/<surface>/` from the installed wheel's package data via `importlib.resources.files("gzkit.<surface>")`, distinct from `gz init --update` (OBPI-05) which is the canonical project-refresh ceremony. Adds `--surface skills,rules,templates,personas,hooks` filter (comma-separated; default all), `--force` override for project-local edits (without `--force` the three-state IDENTICAL/STALE/EDITED detection from OBPI-05 reports conflicts; with `--force` overwrites), `--dry-run` reports what would change without writing. Works in a fresh `pip install py-gzkit` environment without requiring `gz init` to have been run first (bootstrap retrofit case). Idempotent: exits 0 when wheel content is already byte-identical to `.gzkit/`. Manpage at `docs/user/manpages/gz-upgrade.md`; behave coverage in `features/upgrade.feature`. Depends on OBPI-02 (scaffolder refactor wires `importlib.resources` resolution path) and OBPI-06 (wheel includes ship the canonical content) landing first.

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
ADR-0.0.31 as the cited invariant in the `parent:` frontmatter. Thirteen
OBPIs run in dependency order:

- **Migrations (parallelizable after 01):** 01 (skills dual-surface,
  completed); 03 (rules dual-surface); 09 (personas dual-surface); 11
  (templates reverse-migration); 13 (chores normalization).
- **Scaffolders (depend on respective migrations):** 02 (skills) after 01;
  04 (rules) after 03; 10 (personas) after 09; 12 (templates) after 11.
- **Adopter refresh ceremony:** 05 (`gz init --update`) after the
  scaffolders are in place.
- **T0 enforcement:** 06 (T0 smoke test + wheel includes) and 07
  (`gz validate --distribution`) after migrations + scaffolders + 05.
- **Canonical surface sync (closes the chain):** 08 (canonical surface sync
  covering every dual-surface family: skills, rules, personas, templates,
  chores; honors chores carve-out per § Named exceptions) gated on every
  migration OBPI (03/09/11/13) so all dual-surface families exist before
  the sync mechanism wires them.

Canonical-routing course corrections (2026-05-11):

- **Round 1 (mid-OBPI-01):** Brief originally specified `git mv` ("move
  into wheel-shipped package data") semantics inherited from the chores
  precedent. Operator clarified the canonical model is dual-surface —
  `.gzkit/<surface>/` retained as the authored source-of-truth,
  byte-equivalent copy at `src/gzkit/<surface>/` for wheel-shipping.

- **Round 2 (post-OBPI-01 attestation):** Clarification broadened to
  bind across the full ADR-0.0.32 chain and every future gzkit canonical
  surface: `.gzkit/<surface>/ ↔ src/gzkit/<surface>/` (dev-time
  wheel-shipping byte-parity) AND `.gzkit/<surface>/ ↔ .[vendor]/<surface>/`
  (agent-runtime vendor mirrors); both arrows originate at `.gzkit/`.

- **Round 3 (post-Round-2 ADR rewrite):** Scope expanded again to bind
  across ALL harness surfaces — skills, rules, personas, templates,
  chores — with hooks explicitly carved OUT as a documented vendor-coupled
  gap. Per-surface OBPI decomposition chosen for traceability. The
  Decomposition Scorecard bumped from Final Target 8 → 13.

- **Round 4 (post-Round-3 expansion):** Operator corrected the
  "Claude-only" framing — gzkit ships hooks across multiple vendors
  (12 Claude scripts, 1 Copilot script, Codex namespace reserved,
  OpenCode onboarding planned) but cross-vendor lifecycle standards are
  absent. Added § Post-1.0 forward-look documenting adopter-side
  extension deferral with prefix-namespacing as the collision-avoidance
  pattern.

- **Round 5 (post-Round-4 framing correction):** Discovery that the
  broader vendor-harness design framework was already captured in
  pre-existing pool ADRs (`ADR-pool.vendor-capability-matrix` parent,
  `ADR-pool.harness-aware-execution-modes` runtime adaptation,
  `ADR-pool.vendor-alignment-*` per-vendor specializations,
  `ADR-pool.vendor-scoped-chores` mechanism). The Round-3-filed
  `ADR-pool.hooks-meta-layer-contract` pool ADR was redundant with this
  framework; merged its unique slice (LCD-abstraction rejection, named
  promotion triggers, corrected multi-vendor framing) into
  `ADR-pool.harness-aware-execution-modes` § Alternatives Considered and
  deleted the redundant pool ADR. Two GHIs filed for design-intent
  tracking: GHI #451 (recurring vendor-harness-capability-surveillance
  chore — elevated scope from hooks to ALL control surfaces per
  operator framing) and GHI #452 (pool-triage skill analogous to
  ghi-triage, surfaced because the pool grew large enough to warrant
  the same triage mechanism).

Insights records at `.gzkit/insights/agent-insights.jsonl`:
2026-05-11T08:55:00Z (Round 1), 2026-05-11T09:58:00Z (Round 2),
2026-05-11T10:25:00Z (Round 3), 2026-05-11T10:55:00Z (Round 4),
and the Round 5 record appended at this reconciliation's landing time.

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

- [ ] Tests: `tests/` (unit-tier coverage for every `CORE_<SURFACE>` registry — `CORE_SKILLS`, `CORE_RULES`, `CORE_PERSONAS`, `CORE_TEMPLATES`, `CORE_CHORES` — and every `scaffold_core_<surface>` function; package-resource enumeration; init-cmd integration; per-surface byte-parity tests for skills, rules, personas, templates; chores canonical-class-only byte-parity per § Named exceptions)
- [ ] Smoke test: `features/distribution_invariant.feature` (build wheel → temp-venv install → `gz init` → byte-equivalence against `data/distribution_baseline_manifest.json` across all canonical surfaces)
- [ ] Wheel manifest: `pyproject.toml [tool.hatch.build.targets.wheel] include:` extended for `src/gzkit/skills/**/*.md`, `src/gzkit/rules/**/*.md`, `src/gzkit/personas/**/*.md`, `src/gzkit/templates/**/*.md`, `src/gzkit/hooks/scripts/**` (hooks-as-Python-library, per § Named exceptions — not dual-surface), `src/gzkit/chores/**` (canonical content only per § Named exceptions Exception 2 carve-out)
- [ ] CLI surface: `gz init --update` manpage at `docs/user/manpages/gz-init.md`; behave coverage in `features/init.feature`
- [ ] CLI surface: `gz upgrade` manpage at `docs/user/manpages/gz-upgrade.md`; behave coverage in `features/upgrade.feature` (per OBPI-14 — adopter-side surface-only refresh distinct from `gz init --update`)
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
