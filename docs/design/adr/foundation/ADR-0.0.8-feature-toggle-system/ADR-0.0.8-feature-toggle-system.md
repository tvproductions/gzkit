---
id: ADR-0.0.8-feature-toggle-system
status: Draft
semver: 0.0.8
parent: PRD-GZKIT-1.0.0
lane: heavy
---

# ADR-0.0.8: Feature Flag System for GZKit

## Status

Draft

## Date

2026-03-29

---

## 1. Context

GZKit is a governance and specification toolkit that helps humans and AI agents
collaborate across a project lifecycle. It initializes projects (`gz init`),
synchronizes control surfaces (`gz agent sync`), manages ADR and OBPI
lifecycles, runs quality gates, and orchestrates closeout ceremonies. Its
architecture is hexagonal (ports/adapters), its config is typed Pydantic, and
its quality stack is deterministic.

GZKit evolves continuously. New commands appear. Existing commands gain new
behavior. Internal representations change (e.g., `briefs/` renamed to
`obpis/`). Rendering paths are replaced. Quality gates are added. Each of these
changes creates a moment where old behavior and new behavior must coexist. Today,
GZKit has no mechanism for managing that coexistence.

The immediate trigger is the product proof gate incident (GHI #49). ADR-0.23.0
introduced a closeout quality check that retroactively blocked all 25
previously-validated ADRs. There was no phased rollout, no migration window, no
way for operators to run the old closeout path while the new check stabilized.
The only options were "enforce everywhere immediately" or "don't ship."

This is not an isolated incident. It is a structural problem. GZKit will
continue to evolve, and every evolution that changes behavior needs a transition
mechanism. Without one, every improvement is a breaking change.

### What GZKit Is Not

GZKit is not a SaaS product with user tiers. It is not an analytics platform.
It has no concept of "users" in the multi-tenant sense. It runs locally for
one project operator at a time, with AI agents working under governance
constraints. Feature flags here are not about conversion funnels, paid
entitlements, or A/B experiments. They are **transition controls**: mechanisms
for routing between old and new behavior during migration, with the explicit
expectation that the old path and the toggle will be removed.

---

## 2. Problem

GZKit needs to introduce new behavior without immediately breaking or rewriting
all legacy behavior. Specifically:

1. New governance checks must ship without retroactive enforcement. Old
   closeout path and new closeout path must coexist until operators confirm
   the new path works.

2. Init and scaffold behavior must be evolvable. When `gz init` gains new
   vendor surfaces (Gemini, OpenCode), the new scaffold path must be
   activatable without disrupting projects that initialized under the prior
   shape.

3. Sync and rendering paths must be replaceable incrementally. When `sync_all`
   adopts a new manifest structure or a new rule-rendering pipeline, the old
   pipeline must remain available as a fallback during transition.

4. Risky internal behavior must have kill switches. If a new hook script or
   pipeline stage causes failures in the field, operators must be able to
   disable it without reverting code.

5. Transition controls must not accumulate as permanent debt. Every flag that
   exists is a fork in the code. Forks that persist past their purpose are
   maintenance hazards. The system must make this debt visible and enforce
   cleanup.

6. AI agents must not be able to silently bypass governance by toggling flags.
   Flag state is set by operators. Agents consume decisions; they do not
   make them.

---

## 3. Decision Drivers

- **Transition safety.** The primary job is routing between old and new
  behavior during migration. The system must make it safe to ship new behavior
  alongside old behavior and switch between them.

- **Human intent is primary.** Operators set flag state. Agents receive
  resolved decisions. No flag may be evaluated or changed by agent action
  without operator configuration.

- **Inspectability.** An operator must be able to answer "what flags exist,
  what are their current values, and where did those values come from" at
  any moment.

- **Explicit defaults.** Every flag declares a default. Evaluating an
  undeclared flag is a hard error. No silent fallbacks.

- **Lifecycle discipline.** Every flag has an intended lifetime. Transient
  flags carry removal dates. Stale flags are surfaced as debt. The system
  makes it harder to leave old toggles in place than to clean them up.

- **Proportionality.** GZKit is a small typed Python CLI. The flag system
  must be small, typed, deterministic, and local-first. No vendor SDKs, no
  distributed coordination, no analytics.

---

## 4. Toggle Taxonomy for GZKit

Martin Fowler identifies four toggle categories, positioned on a matrix of
longevity (transient vs long-lived) and dynamism (static vs per-request). We
analyze each against GZKit's actual needs, plus a fifth category (migration
toggles) that Fowler discusses as a subcategory but that GZKit needs as a
primary concern.

### Release Toggles

**Fowler's definition.** Allow incomplete or risky features to deploy as latent
code. Trunk-based development enablers. Transient (days to weeks). Static
decision per deployment.

**GZKit fit: IN SCOPE (v1).**

GZKit ships from trunk. New commands and new quality checks need a way to land
as latent code before full activation. Concrete examples:

- A new `gz drift` command is implemented but gated behind a release toggle
  until its BDD scenarios stabilize.
- A new init scaffold behavior (Gemini vendor surface) ships disabled until
  the adapter is production-ready.
- A new closeout quality check (product proof) ships as non-enforcing before
  promoting to enforcing.

**Characteristics:** Short-lived (days to weeks). Static (resolved once at
process start from config). Must carry a `remove_by` date. Convention: OFF
means legacy/absent behavior; ON means new behavior. This convention is
mandatory for testability — "all flags OFF" means "legacy behavior" and is
always a valid fallback configuration.

### Experiment Toggles

**Fowler's definition.** Support A/B testing. Require consistent per-user
cohort assignment. Transient.

**GZKit fit: OUT OF SCOPE. Not appropriate.**

GZKit has no user population to segment. It runs locally for one operator.
There is no population to assign cohorts to, no metrics to measure statistical
significance against, and no analytics infrastructure to collect results.
Experiment toggles require a fundamentally different evaluation model
(per-request, context-dependent, probabilistic) that is architecturally
incompatible with GZKit's static, deterministic nature.

This category is not "out of scope for v1." It is structurally inappropriate
for GZKit and should not be designed for.

### Ops Toggles

**Fowler's definition.** Operational controls for runtime behavior. Allow
graceful degradation. Some short-lived (incident response), some long-lived
(kill switches). Dynamic — must support fast reconfiguration.

**GZKit fit: IN SCOPE (v1).**

GZKit has operations that are expensive, environment-dependent, or
occasionally broken. Operators need kill switches. Concrete examples:

- `ops.mkdocs_gate`: Disable the mkdocs build gate in environments where
  mkdocs is unavailable (CI, offline development, lightweight containers).
- `ops.bdd_gate`: Disable behave scenarios when behave is not installed.
- `ops.hook_enforcement`: Kill switch for hook execution when hooks are
  causing failures during a development session.
- `ops.product_proof`: Control whether the product proof check blocks
  closeout or only warns. (The GHI #49 case.)

**Characteristics:** Variable lifetime. Some are incident-response (hours).
Some are long-lived environmental controls (months). Must carry a `review_by`
date — not necessarily a `remove_by`, because a kill switch for an optional
dependency may be permanent. Static resolution (from config/env at process
start). Fowler notes ops toggles ideally support sub-second reconfiguration
for incident response; in GZKit's CLI context, re-running a command with
different config is sufficient.

### Permissioning Toggles

**Fowler's definition.** Restrict features to specific user groups. Premium
tiers, beta programs, internal dogfooding. Long-lived. Per-user dynamic.

**GZKit fit: OUT OF SCOPE. Not appropriate.**

GZKit has no user tiers, no premium features, no beta programs. It is a
single-operator local tool. Permissioning toggles assume a multi-tenant
authorization model that does not exist and must not be invented. If GZKit
ever needs "this feature is only available in paid mode," that is a product
architecture decision, not a feature flag.

Like experiment toggles, this category is structurally inappropriate, not
merely deferred.

### Migration Toggles

**Fowler discusses** migration toggles as a use of release toggles during
system-level transitions. GZKit elevates this to a primary category because
migration is the dominant use case for toggles in a governance toolkit that
evolves its own internal representations.

**GZKit fit: IN SCOPE (v1). Primary use case.**

GZKit regularly changes its internal file layouts, config schemas, command
behaviors, and rendering pipelines. Each change needs a transition period
where old and new coexist. Concrete examples:

- `migration.obpi_folder_name`: During the `briefs/` to `obpis/` rename, the
  scanner must accept both folder names. The toggle controls which name is
  canonical. After migration completes, the toggle and the `briefs/` code
  path are removed.
- `migration.closeout_product_proof`: Bridge between the old closeout path
  (no product proof check) and the new path (product proof enforced). The
  toggle controls enforcement level during transition.
- `migration.config_gates_to_flags`: Bridge the temporary `config.gates`
  dict to the proper flag service during this ADR's own implementation.
  A flag that manages the migration of the flag system itself.
- `migration.legacy_pipeline_marker`: Control whether the pipeline reads
  the legacy `.plan-audit-receipt.json` marker format or the new per-OBPI
  marker format.

**Characteristics:** Medium-lived (weeks to a release cycle). Static. Must
carry a `remove_by` date. Migration toggles that outlive their migration are
defects, not features. They should be the most aggressively retired category.
Convention: OFF means old/legacy path; ON means new path.

---

## 5. Options Considered

### Option A: Config-Backed Toggle Dictionary

The `config.gates` prototype shipped during GHI #49. Open-ended string keys,
three string-valued enforcement levels, `gate()` lookup defaulting to
`"enforce"` for unknown keys.

**Assessment.** This is a dressed-up if-statement. It has no registry
(any string key is valid), no categories (all toggles are alike), no metadata
(no owner, no expiry, no description), no lifecycle enforcement (stale
toggles are invisible), no centralized decision logic (consumers call
`config.gate("some.string")` with magic strings scattered through the
codebase), and it silently returns a default for undeclared flags (hiding
typos). It solves the immediate product proof problem but creates the
structural conditions for toggle debt.

**Verdict:** Insufficient. Must be replaced, not extended.

### Option B: Full Feature Flag Platform

A centralized flag management service with SDK, targeting rules, percentage
rollouts, analytics collection, and admin UI. The LaunchDarkly/Statsig model.

**Assessment.** Architecturally wrong for a local CLI tool. Every design
assumption of these platforms (per-request evaluation, user cohorts,
server-side state, analytics pipelines) is inapplicable to GZKit. The
complexity and dependency cost is indefensible.

**Verdict:** Inappropriate. Wrong domain, wrong scale, wrong model.

### Option C: Source-Controlled Registry with Centralized Decision Layer

A source-controlled JSON registry declares every known flag with typed
metadata. A `FlagService` resolves values through a defined precedence chain.
A `FeatureDecisions` object translates raw flag state into named decision
methods that commands and workflows consume. Commands receive decisions, not
flag service handles. Business logic never knows flags exist.

**Assessment.** Proportional to GZKit's needs. Source-controlled (auditable,
reviewable, moves through CI). Typed (errors at load time). Category-aware
(different lifecycle rules per category). The three-layer architecture —
router, decisions, toggle points — follows Fowler's prescription for keeping
toggle infrastructure out of business logic. Named decision methods prevent
magic-string coupling. Lifecycle metadata and stale detection prevent debt
accumulation.

**Verdict:** Selected.

---

## 6. Decision

GZKit adopts Option C. The following sections specify the architecture.

### 6.1 Three-Layer Architecture

Fowler's central architectural lesson is that toggle points (the places in
code where behavior branches) must be decoupled from toggle routers (the
infrastructure that resolves flag values). He further recommends a
**feature decisions** layer between them: an object with named methods that
translate flag state into domain-meaningful decisions. GZKit adopts this
three-layer structure:

```text
Layer 1: FlagService (toggle router)
  - Loads registry, resolves precedence, returns raw boolean values.
  - The only code that knows about flag keys, config files, env vars.
  - Singleton per process. Initialized at CLI startup.

Layer 2: FeatureDecisions (decision layer)
  - A typed object with named methods: use_new_init_scaffold(),
    product_proof_enforced(), accept_legacy_obpi_folder(), etc.
  - Each method calls FlagService internally. Flag keys live HERE
    and nowhere else.
  - The single place where a flag key string appears in the codebase.
  - If a flag's semantics change (different key, compound logic),
    only this class changes. No toggle points are touched.

Layer 3: Toggle points (consumers)
  - Command functions, rendering paths, sync orchestrators.
  - Receive FeatureDecisions (or individual resolved booleans) at
    their boundary. Branch on named decisions, not flag keys.
  - Never import FlagService. Never see a flag key string.
```

**Example flow:**

```text
CLI startup
  → FlagService loads registry + config + env
  → FeatureDecisions(flag_service) constructed
  → closeout_cmd receives decisions.product_proof_enforced()
  → closeout_cmd passes the boolean to the proof check
  → quality.py receives a plain bool, not a flag handle
```

**Why this matters.** Without the decisions layer, flag key strings scatter
across the codebase (Fowler's anti-pattern). With it, the mapping from "flag
key" to "what this means for behavior" is centralized, named, typed, and
testable. When a flag is retired, you change one method in FeatureDecisions
and remove the branch from the toggle point. The flag key string appears in
exactly two places: the registry file and the FeatureDecisions class.

### 6.2 Where Toggle Points Are Allowed

Toggle points — locations where a feature decision influences behavior — are
permitted at well-chosen boundaries:

| Location | Example | Rationale |
|----------|---------|-----------|
| Command entry functions | `closeout_cmd` checks `decisions.product_proof_enforced()` | Natural injection boundary. Decisions are resolved before business logic runs. |
| Sync orchestrators | `sync_all` checks `decisions.use_new_manifest_structure()` | Migration routing between old and new sync pipelines. |
| Init/scaffold flows | `init` checks `decisions.use_new_init_scaffold()` | Staged rollout of new project initialization behavior. |
| Rendering/output paths | Reporter checks `decisions.use_new_report_layout()` | Alternative display modes during transition. |
| Diagnostic surfaces | `gz status` includes `decisions.product_proof_enforced()` in output | Operators need to see which path is active. |

### 6.3 Where Toggle Points Are Forbidden

Flags must never influence the following. These are governance invariants, not
behaviors that can be toggled.

| Location | Rationale |
|----------|-----------|
| Lifecycle state-machine transition rules | ADR authority is absolute. A flag cannot make `Pool → Completed` a valid transition. The transition table in `core/lifecycle.py` is canon. |
| Attestation semantics | Human attestation either happened or it did not. A flag cannot redefine what attestation means. |
| Ledger event schema | The ledger is an append-only audit trail. Event structure is a contract. Flags cannot alter what events mean or which fields they carry. |
| Canon meaning | What an ADR, OBPI, constitution, or PRD *is* cannot be toggled. An ADR is still an ADR regardless of flag state. |
| Closeout validity | Closeout either completed or it did not. A flag can control whether a *check within* closeout runs (product proof), but cannot redefine whether closeout itself is valid. |
| Gate identity | Gate 1 is ADR, Gate 2 is TDD, Gate 3 is Docs, Gate 4 is BDD, Gate 5 is Attestation. Flags cannot redefine this model. They can control enforcement of a check *within* a gate, but the gate structure is governance doctrine. |

### 6.4 Source of Truth and Precedence

Flag values resolve through a defined precedence chain. Later sources override
earlier ones.

| Priority | Source | Mutability | Purpose |
|----------|--------|------------|---------|
| 1 (lowest) | Registry default | Immutable (source-controlled) | Canonical default. The value a flag has when nobody has overridden anything. |
| 2 | Environment variable (`GZKIT_FLAG_<KEY>`) | Per-process | CI/CD overrides, container configuration, operator environment tuning. Key format: dots replaced with underscores, uppercased. `ops.product_proof` → `GZKIT_FLAG_OPS_PRODUCT_PROOF`. |
| 3 | Project config (`.gzkit.json` `flags` section) | Per-project | Operator project-level customization. This is where a project says "product proof is advisory for us." |
| 4 | Test override (in-memory) | Per-test | Unittest isolation. `flag_service.set_override("ops.product_proof", False)`. Cleared between tests. |
| 5 (highest) | Runtime override (in-memory) | Per-invocation | Development debugging only. Not persisted. Not available to agents in normal operation. |

**Unknown flags fail explicitly.** Evaluating a key not in the registry raises
`UnknownFlagError`. This prevents typos, undeclared ad-hoc flags, and stale
references to removed flags.

**Malformed values fail explicitly.** A non-boolean string in env or config
(e.g., `"maybe"`) raises `InvalidFlagValueError` at service initialization,
not silently at evaluation time.

### 6.5 Flag Metadata

Every flag in the registry carries:

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `key` | str | Yes | Dotted identifier: `{category}.{name}` (e.g., `migration.obpi_folder_name`) |
| `category` | enum | Yes | `release`, `ops`, `migration`, `development` |
| `default` | bool | Yes | Explicit default value. Convention: `false` = legacy/off, `true` = new/on. |
| `description` | str | Yes | Human-readable purpose. Not a label — a sentence explaining what this flag controls and why. |
| `owner` | str | Yes | Responsible party. A person or team name, not "system." |
| `introduced_on` | date | Yes | When the flag was added to the registry. |
| `review_by` | date | Conditional | Required for `ops` flags. When the flag should be reviewed for continued relevance. |
| `remove_by` | date | Conditional | Required for `release`, `migration`, and `development` flags. When the flag and its old code path must be removed. |
| `linked_adr` | str | No | ADR that introduced or motivated this flag. |
| `linked_issue` | str | No | GitHub issue tracking this flag. |

**Category-specific rules:**

- **Release** flags MUST have `remove_by`. They are transient by definition.
  A release toggle without a removal date is not a release toggle.
- **Migration** flags MUST have `remove_by`. Migrations that never complete
  are defects. Migration toggles should be the most aggressively retired.
- **Ops** flags MUST have `review_by`. Some ops flags are long-lived (kill
  switches for optional dependencies), but they must be periodically reviewed.
  An ops flag without periodic review becomes invisible debt.
- **Development** flags MUST have `remove_by` and MUST default to `false`.
  Development flags gate incomplete work on trunk. They are never active in
  production. They exist so developers can merge partial work without
  activating it.

### 6.6 Lifecycle Discipline

**Creation.** Add a flag to `data/flags.json` with all required metadata. No
flag may be referenced in code without a registry entry. The `FeatureDecisions`
class must have a corresponding named method. Both additions happen in the
same commit.

**ON/OFF convention.** OFF (`false`) means legacy, absent, or old behavior.
ON (`true`) means new behavior. This is mandatory. It ensures that "all flags
OFF" is always a valid fallback configuration representing the pre-flag
baseline.

**Stale detection.** `gz flags --stale` reports flags past their `review_by`
or `remove_by` dates. `gz check` includes flag staleness in its output.

**Time-bomb tests.** A standing test (`test_no_expired_flags`) loads the
registry and fails if any flag is past its `remove_by` date. This runs in
CI. It makes it harder to ignore an expired flag than to remove it.

**Removal.** When a flag is ready for removal:
1. Delete the method from `FeatureDecisions`.
2. Replace the toggle point with the permanent behavior (the winning branch).
3. Delete the old code path.
4. Remove the flag entry from `data/flags.json`.
5. Remove any `.gzkit.json` or env overrides.
6. Run tests. Any `UnknownFlagError` from stale references surfaces immediately.
7. Commit. The flag is gone. No tombstones, no compatibility shims, no
   deprecation period for already-expired flags.

**Inventory visibility.** `gz flags` lists all active flags with current
value, source, category, owner, and days until review/removal. This is the
toggle inventory that Fowler says teams must manage like work-in-progress.

---

## 7. Boundaries and Non-Goals

**Explicitly out of scope for all versions:**

- Experiment toggles (no cohorts, no A/B, no analytics)
- Permissioning toggles (no user tiers, no authorization model)
- Percentage rollouts (no population to roll out across)
- Per-request evaluation (all flags are static per process)
- Non-boolean flag values in v1 (enums, strings, integers — may revisit)
- Vendor SDK integration
- Admin UI (CLI is the operator interface)
- Dynamic reconfiguration within a running process (restart is fine for a CLI)

**Explicitly not a rename of governance gates.** The existing five-gate model
(ADR, TDD, Docs, BDD, Attestation) is governance doctrine. Feature flags can
control enforcement *within* a gate (e.g., whether product proof blocks or
warns inside the closeout pipeline). Feature flags cannot redefine, disable,
or bypass the gate model itself. The `commands/gates.py` module and `gz gates`
command are unrelated to feature flags and must not be confused with them.

---

## 8. Consequences

- GZKit gains a `src/gzkit/flags/` subpackage.
- `data/flags.json` becomes a source-controlled registry reviewed like any
  governance artifact.
- `FeatureDecisions` becomes the single class in the codebase that maps flag
  keys to named decisions. No other module references flag keys.
- The `config.gates` prototype is removed. The `.gzkit.json` `gates` key is
  migrated to `flags`. This migration is itself managed by a migration toggle.
- New governance checks must register a flag before shipping enforcement.
  The ON/OFF convention and advisory-first pattern become standard.
- `gz flags` becomes a new CLI command group.
- `gz check` gains flag health validation (stale flags).
- A standing `test_no_expired_flags` test enforces removal discipline in CI.
- Every flag is visible debt with a declared expiry. The system makes debt
  visible rather than hiding it.

---

## 9. v1 Scope

### In scope

- Flag categories: release, ops, migration, development
- Boolean flags only
- Source-controlled registry (`data/flags.json`) with JSON Schema validation
- `FlagService`: registry loading, precedence resolution, override API
- `FeatureDecisions`: named decision methods, the only place flag keys appear
- Environment variable overrides (`GZKIT_FLAG_<KEY>`)
- Project config overrides (`.gzkit.json` `flags` section)
- Test and runtime override APIs for unittest isolation
- Unknown flag detection (explicit `UnknownFlagError`)
- Malformed value detection (explicit `InvalidFlagValueError`)
- Stale flag reporting (`gz flags --stale`)
- CLI: `gz flags`, `gz flags --stale`, `gz flag explain <key>`
- Integration with `gz check` for flag health
- Time-bomb test: `test_no_expired_flags`
- Initial flags: `ops.product_proof` as first real flag
- Migration of `config.gates` prototype via `migration.config_gates_to_flags`
- unittest coverage for registry validity, evaluation precedence,
  config/env parsing, override behavior, unknown flag failure, stale reporting

### Out of scope for v1

- Non-boolean flag values
- Flag dependency graphs
- Automatic retirement (manual removal; CI test enforces deadline)
- Ledger audit events for flag state changes
- BDD scenarios for flag CLI (defer to v2 when surface stabilizes)
- Strategy-pattern based toggle points (if/else at command boundary is
  sufficient for v1's transient toggles; strategy injection for long-lived
  ops toggles can be introduced when a concrete need arises)

---

## 10. Follow-On Implementation Implications

### Recommended Module Layout

```text
src/gzkit/flags/
  __init__.py          — Public API: get_flag_service(), get_decisions()
  models.py            — FlagSpec, FlagCategory, FlagEvaluation, errors
  registry.py          — Load and validate data/flags.json against schema
  service.py           — FlagService: precedence resolution, override API
  decisions.py         — FeatureDecisions: named decision methods

data/flags.json        — Source-controlled flag registry
data/schemas/flags.schema.json — JSON Schema for registry validation
```

Five modules. `decisions.py` is the architectural keystone — the only file
that maps flag key strings to named methods. When a flag is added, one method
is added here. When a flag is removed, one method is removed here.

### Recommended Precedence Model

```text
registry default (lowest)
  ↓ overridden by
GZKIT_FLAG_OPS_PRODUCT_PROOF=false (env var)
  ↓ overridden by
.gzkit.json { "flags": { "ops.product_proof": true } } (project config)
  ↓ overridden by
flag_service.set_test_override("ops.product_proof", false) (test)
  ↓ overridden by
flag_service.set_runtime_override("ops.product_proof", true) (runtime)
```

### Example Flag Definitions

```json
{
  "flags": [
    {
      "key": "ops.product_proof",
      "category": "ops",
      "default": true,
      "description": "When enabled, the product proof check blocks closeout for OBPIs without operator-facing documentation. When disabled, the check warns but does not block. Introduced because the check retroactively blocked 25 validated ADRs that predated it.",
      "owner": "governance",
      "introduced_on": "2026-03-29",
      "review_by": "2026-06-29",
      "linked_adr": "ADR-0.23.0",
      "linked_issue": "GHI-49"
    },
    {
      "key": "migration.config_gates_to_flags",
      "category": "migration",
      "default": false,
      "description": "When enabled, the flag service replaces config.gates as the authority for gate enforcement levels. When disabled, config.gates is still consulted (backward compatibility). Remove after all consumers migrate to FeatureDecisions.",
      "owner": "governance",
      "introduced_on": "2026-03-29",
      "remove_by": "2026-05-01",
      "linked_adr": "ADR-0.0.8"
    },
    {
      "key": "release.drift_command",
      "category": "release",
      "default": false,
      "description": "When enabled, the gz drift command is available in the CLI. When disabled, the command is hidden. Gate for incomplete feature development.",
      "owner": "cli",
      "introduced_on": "2026-03-29",
      "remove_by": "2026-04-30",
      "linked_adr": "ADR-0.20.0"
    }
  ]
}
```

### Example: Centralized Feature Decision Usage

```python
# --- flags/decisions.py ---
class FeatureDecisions:
    """Named feature decisions. The ONLY place flag keys appear."""

    def __init__(self, service: FlagService) -> None:
        self._svc = service

    def product_proof_enforced(self) -> bool:
        """Whether the product proof check blocks closeout."""
        return self._svc.is_enabled("ops.product_proof")

    def use_new_init_scaffold(self) -> bool:
        """Whether gz init uses the new vendor-aware scaffold."""
        return self._svc.is_enabled("release.new_init_scaffold")

    def accept_legacy_obpi_folder(self) -> bool:
        """Whether the scanner accepts briefs/ as an alias for obpis/."""
        return not self._svc.is_enabled("migration.obpi_folder_name")


# --- commands/closeout.py ---
def closeout_cmd(adr: str, as_json: bool, dry_run: bool) -> None:
    decisions = get_decisions()
    enforce_proof = decisions.product_proof_enforced()
    # ...
    # At the proof gate:
    if not proof_result.success:
        if enforce_proof:
            _block_closeout(proof_result, as_json)
        else:
            _warn_closeout(proof_result, as_json)
    # quality.py never imports flags. It receives a bool.
```

**What this achieves:**
- `"ops.product_proof"` appears in exactly two places: `data/flags.json`
  and `decisions.py`.
- `closeout_cmd` calls `decisions.product_proof_enforced()` — a named
  method, not a magic string.
- `quality.py` never knows flags exist. It receives a boolean.
- When the flag is retired, delete the method from `decisions.py`, replace
  the branch in `closeout_cmd` with the permanent behavior, delete the
  registry entry. Three files touched. Done.

### Testing Strategy

Following Fowler's specific recommendations:

1. **Test current production config.** Load the actual `data/flags.json` with
   no overrides. Verify the system behaves correctly with current defaults.
2. **Test fallback config.** All flags OFF. This is the legacy baseline and
   must always be a valid, working configuration.
3. **Test target config.** Flags set to their intended future state (new
   toggles ON, about-to-be-removed toggles OFF). Verify the future works.
4. **Test all flags ON.** Optional regression detection. May catch hidden
   interactions.
5. **Per-flag unit tests.** Each `FeatureDecisions` method tested with flag
   ON and OFF. Verify the named decision returns the correct boolean.
6. **Precedence tests.** For each layer in the precedence chain, set a value
   and confirm it overrides lower layers.
7. **Error tests.** Unknown flag raises `UnknownFlagError`. Malformed env/config
   value raises `InvalidFlagValueError`.
8. **Registry validity.** Load `data/flags.json`, validate all entries parse,
   required metadata present, category-specific rules enforced (`remove_by`
   for release/migration, `review_by` for ops).
9. **Time-bomb test.** `test_no_expired_flags` fails if any flag is past
   `remove_by`. Runs in CI. Forces cleanup.

### Removal Strategy

Fowler warns that toggles multiply and accumulate as debt. GZKit's removal
strategy:

1. **At creation:** `remove_by` or `review_by` is required in the registry.
   No undated flags.
2. **In CI:** `test_no_expired_flags` fails the build if a flag is past its
   `remove_by` date. This is the time bomb. It makes ignoring an expired
   flag harder than removing it.
3. **In diagnostics:** `gz flags --stale` and `gz check` surface stale flags.
   Operators see the debt.
4. **At removal:** Delete the `FeatureDecisions` method. Replace the toggle
   point branch with permanent behavior. Delete the old code path. Delete the
   registry entry. Remove config/env references. Run tests —
   `UnknownFlagError` catches any stale references. Commit.
5. **No tombstones.** Removed flags are gone. No `# removed: was ops.foo`
   comments, no compatibility shims, no re-export stubs. The flag existed,
   served its purpose, and was cleaned up. Git history is the record.

---

## OBPI Decomposition -- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.8-01-flag-models-and-registry | FlagSpec, FlagCategory, FlagEvaluation models; registry loader with schema validation; error types | Heavy | Pending |
| 2 | OBPI-0.0.8-02-flag-service | FlagService with precedence chain, override API, unknown/malformed flag errors | Heavy | Pending |
| 3 | OBPI-0.0.8-03-feature-decisions | FeatureDecisions class with named methods; initial decisions for ops.product_proof | Heavy | Pending |
| 4 | OBPI-0.0.8-04-diagnostics-and-staleness | Stale detection, flag health, explain output, gz check integration, time-bomb test | Heavy | Pending |
| 5 | OBPI-0.0.8-05-cli-surface | gz flags, gz flags --stale, gz flag explain commands | Heavy | Pending |
| 6 | OBPI-0.0.8-06-closeout-migration | Migrate closeout product proof from config.gates to FeatureDecisions | Lite | Pending |
| 7 | OBPI-0.0.8-07-config-gates-removal | Remove config.gates prototype, migrate .gzkit.json schema, clean up | Heavy | Pending |
| 8 | OBPI-0.0.8-08-operator-docs | Runbook section, command manpage, flag system documentation | Heavy | Pending |

### Dependency Graph and Parallelization

```text
Stage 1:  [OBPI-01] Flag Models & Registry
              │
Stage 2:  [OBPI-02] Flag Service
              │
         ┌────┴────┐
Stage 3:  [OBPI-03] │ [OBPI-04]       ← parallel
         Feature    │ Diagnostics
         Decisions  │ & Staleness
              │     │
         ┌────┴─────┤
Stage 4:  [OBPI-06] │ [OBPI-05]       ← parallel
         Closeout   │ CLI Surface
         Migration  │ (depends 01,02,04)
              │     │
Stage 5:  [OBPI-07] │                 ← sequential (depends 06)
         Config     │
         Gates      │
         Removal    │
              │     │
         └────┬─────┘
Stage 6:  [OBPI-08] Operator Docs     ← depends all
```

**Critical path:** 01 → 02 → 03 → 06 → 07 → 08 (6 stages).
**Maximum parallelism:** Stage 3 (OBPI-03 ∥ OBPI-04), Stage 4 (OBPI-05 ∥ OBPI-06).

### Feature Checklist (Capability Inventory)

Every item below maps to a testable deliverable. If removed, the named capability is absent.

| # | Capability | Lost if removed | Delivered by |
|---|-----------|-----------------|-------------|
| 1 | Typed flag models with category rules | No schema validation, no metadata enforcement | OBPI-01 |
| 2 | Source-controlled registry with JSON Schema | Flags are ad-hoc magic strings | OBPI-01 |
| 3 | Precedence resolution (registry → env → config → test → runtime) | No override mechanism; flags are hardcoded | OBPI-02 |
| 4 | Unknown/malformed flag detection | Typos and bad values are silent | OBPI-02 |
| 5 | Named decision methods (FeatureDecisions) | Flag keys scatter across codebase | OBPI-03 |
| 6 | Stale flag detection and health reporting | Expired flags accumulate invisibly | OBPI-04 |
| 7 | Time-bomb CI test for expired flags | No forcing function for cleanup | OBPI-04 |
| 8 | `gz flags` / `gz flags --stale` / `gz flag explain` CLI | Operator cannot inspect flag state | OBPI-05 |
| 9 | Closeout migration to FeatureDecisions | GHI #49 problem remains unsolved | OBPI-06 |
| 10 | config.gates removal and .gzkit.json migration | Legacy prototype persists as tech debt | OBPI-07 |
| 11 | Operator docs (runbook, manpage, system docs) | Feature ships without operator guidance | OBPI-08 |

**Briefs location:** `obpis/OBPI-0.0.8-*.md`

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.8 | Completed | Jeff | 2026-03-30 | completed |
