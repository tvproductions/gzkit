---
id: ADR-0.0.61-harness-factoring-minimal-init
status: Draft
kind: foundation
semver: 0.0.61
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-25
inspired_by: "Andy Dev Dan — five-pillar agentic engineering framework (agent harness, software factory, extensible software, always-on agents, agentic access)"
complements:
  - ADR-0.0.31-distribution-invariant
  - ADR-0.0.32-canonical-surfaces
  - ADR-0.0.60-harness-fitness-report
---

# ADR-0.0.61-harness-factoring-minimal-init: Harness-Factoring with gz init --minimal

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats governance not as overhead but as the discipline that keeps work honest. The harness-factoring problem is a doctrine problem first, an ergonomics problem second: the wrong shape ships adoption-friction as a feature, the right shape ships incremental adoption as a primitive.

## Why foundation tier?

**Invariance test:** Without this ADR, would the project still be the project? **Yes** — gzkit remains a governance kit. But the *adoption-as-monolithic-PR* failure mode is itself a foundation-level constraint: a governance kit that cannot be adopted incrementally is structurally inert in established codebases. The invariance is *adoption-shape neutrality*: the kit must offer both from-scratch and incremental-adoption paths through the same canonical surface contract.

**Port-vs-adapter framing:** This ADR is a **port** — it defines the abstract contract that the canonical-surface scaffolders (skills, rules, personas, templates, chores, control surfaces, hooks) are individually addressable and idempotently composable through a single CLI noun (`gz harness install <component>`). The existing `scaffold_core_*` functions are the **adapters** behind that port; this ADR factors the port out of the monolithic `gz init` adapter.

## Intent

**Before (today):** `gz init` lands ~150+ files in one shot — `.gzkit/` (skills, rules, personas, templates, chores, manifest, ledger, config), `.claude/` mirror, `.github/` mirror, AGENTS.md, CLAUDE.md, hooks, pyproject.toml, src/ skeleton, .gitignore, audit_thresholds.json. For an established project considering gzkit adoption, that is a 150-file PR that no engineering team is going to land in a single review. The adoption friction is *higher* than the from-scratch friction, which is backwards for a governance kit.

**After (this ADR):** `gz init --minimal` lands ~5–10 files (`.gzkit/{ledger.jsonl, manifest.json}`, `.gzkit.json`, empty canonical-surface dirs, governance dir tree). Subsequent `gz harness install <component>` calls layer skills, rules, personas, templates, chores, control surfaces, and hooks as individual reviewable PRs. The full-flavor `gz init` remains the default; `--minimal` is the adoption-friendly path.

**Scope (inaugural shape):** Two profiles only — `default` (today's behavior, byte-identical) and `minimal` (the new bootstrap-isolation profile). One new CLI noun (`gz harness install`) wrapping seven component scaffolders that already exist in the codebase. One new status indicator, one new ledger event, one validator-dispatcher policy change. No new scaffolders; no new validators; no removal of existing behavior.

**Anti-vibing constraint (binding):** `--minimal` does not lower any gate. It postpones the *installation* of the surfaces that gates validate against. The validator dispatcher emits structured SKIP receipts (`arb-step-skip-<scope>-`) for absent surfaces on minimal projects so the skipped gates remain *legible* in every ceremony. A minimal project that never installs surfaces accumulates SKIP receipts at every closeout — the visibility is the discipline.

**Factory metric:** files-in-first-adoption-PR. Today ~150. Target ≤10 on `gz init --minimal`. Each subsequent `gz harness install <component>` is a separately reviewable PR.

## Decision

### Architectural precedents and exemplars

This ADR composes three established gzkit patterns rather than inventing new ones; the implementation OBPIs are pure factoring of existing capability.

- **Precedent — canonical-surface scaffolders ([ADR-0.0.32](../ADR-0.0.32-canonical-surfaces-bytewise-byparity/ADR-0.0.32-canonical-surfaces-bytewise-byparity.md)).** The seven `scaffold_core_*` functions (skills, rules, personas, templates, chores, plus `setup_*_hooks` and `sync_all`) are the **exemplar contract** this ADR factors into individually addressable CLI verbs. Every `gz harness install <component>` wraps a function whose semantics, idempotency contract, and EDITED-detection mechanism are already locked by ADR-0.0.32. The CLI surface is new; the underlying capability is byte-identical to today's `gz init` repair-mode invocation.
- **Precedent — `--update` refresh-and-marker mechanism ([init_cmd.py:66–93](../../../../src/gzkit/commands/init_cmd.py#L66-L93)).** The `_detect_refresh_state` IDENTICAL/STALE/EDITED classifier and the `<!-- gzkit-canonical-version: X.Y.Z -->` marker are the **exemplar conflict-handling pattern** this ADR reuses for `gz harness install <component> --force`. EDITED detection on canonical content goes through the existing marker mechanism; no new conflict-resolution doctrine is introduced.
- **Precedent — `gz harness` noun namespace ([ADR-0.0.60](../ADR-0.0.60-harness-fitness-report/ADR-0.0.60-harness-fitness-report.md)).** ADR-0.0.60 established `gz harness report` as the first verb in the `gz harness` namespace. This ADR adds `gz harness install` as the second, sharing the noun's semantic anchor: *capability operations on the gzkit harness itself, distinct from `gz status` (project state) and `gz check` (gate evaluation)*. The namespace is a deliberate composition target, not an accidental one.
- **Anti-precedent — multi-mode init alternatives.** This ADR explicitly rejects the multi-profile patterns common in adjacent toolchains (cookiecutter's template variants, Yeoman's generator sub-types, Cargo's `--lib`/`--bin`). Those exemplars segment users by use-case at scaffold time; gzkit's two-profile choice (`default` + `minimal`) intentionally rejects user-segmentation in favor of a single profile-upgrade path. Named in Alternatives Considered §3.

The seven decisions below are ordered by dependency: data shape (1) before CLI surface (2, 3) before behavior (4, 5, 6) before architectural assertion (7). Each item is independently testable per the OBPI decomposition in the Checklist.

1. Add `gz init --minimal` flag and `gz harness install <component>` CLI surface (Decision 1, below) **because** the existing `gz init` lands ~150 files in one shot and adoption-PR friction is the named factory failure mode this ADR addresses.
2. Compose canonical surfaces (skills, rules, personas, templates, chores) as independent peers; derive `surfaces` from them; chain `hooks` last (Decision 2) **because** the dependency graph reflects what each component reads and writes — operator-chosen ordering on individual installs respects operator agency, aggregate ordering on `install all` avoids generating empty mirrors.
3. Map every `gz harness install <component>` to an existing `scaffold_core_*` function (Decision 3) **because** the OBPI is pure CLI factoring — no new scaffolders, no new validators, no rewrite of canonical-surface logic. The rationale for pure factoring is risk minimization: every wrapped function is already locked by ADR-0.0.32 byte-parity invariants.
4. Add `installation_profile` to `GzkitConfig` and stamp it in the manifest; emit `HarnessComponentInstalledEvent` per install call (Decision 4) **because** without per-install ledger events, the ADR-0.0.60 fitness surface cannot measure files-per-adoption-PR or time-from-minimal-to-default. The data shape is the seed for the factory metric.
5. Render profile-aware output: `gz init --minimal` post-init text lists `gz harness install` next steps; `gz status` adds a profile indicator with per-component counts (Decision 5) **because** discoverability of the layered-adoption path must equal the discoverability of full-flavor `gz init` — otherwise operators default back to the monolithic path.
6. Exit codes follow the canonical 4-code map; EDITED conflicts exit 3 (Decision 6) **because** `.claude/rules/cli.md` already binds the 4-code contract — this ADR introduces no new exit semantics.
7. Assert that all derived caches (status profile indicator, manifest profile field, component counts) are Layer-3 derived views regenerable from `.gzkit/<surface>/` contents (Decision 7) **because** doctrine drift starts when a derived view becomes source-of-truth (Architectural Boundary 6, `docs/governance/state-doctrine.md`). The directory contents are the canon; the profile is observational.

### Decision 1 — CLI surface

```bash
gz init --minimal                        # minimal scaffold (5–10 files)
gz init --minimal --dry-run

gz harness install skills                # canonical skills only
gz harness install rules                 # canonical rules only
gz harness install personas              # canonical personas only
gz harness install templates             # canonical templates only
gz harness install chores                # canonical chores + registry merge
gz harness install surfaces              # AGENTS.md, CLAUDE.md, vendor mirrors
gz harness install hooks                 # Claude + Copilot hook configs
gz harness install all                   # all of above in dependency order

# Flags applying to every install component
--dry-run
--force            # overwrite existing canonical content; discard EDITED conflicts
--json             # machine-readable result to stdout, diagnostics to stderr
```

`gz harness install` slots into the `gz harness` noun namespace alongside `gz harness report` (ADR-0.0.60).

### Decision 2 — Component dependency graph

```
                    skills, rules, personas, templates, chores   ← canonical surfaces
                    (independent peers, wheel-sourced)
                                     │
                                     ▼  (reads to render)
                              surfaces                            ← derived
                    (AGENTS.md, CLAUDE.md, .claude/, .github/, .agents/)
                                     │
                                     ▼  (references)
                                hooks                             ← derived
            (.claude/settings.json, .claude/hooks/*.py, copilot)
```

**Individual install ordering: operator-chosen.** No ordering enforcement on individual `gz harness install <component>` calls — operators may install in any sequence. **Aggregate `install all` ordering: canonicals → surfaces → hooks** to avoid generating empty-shell mirrors.

### Decision 3 — Component → scaffolder mapping (pure factoring, no new code)

| Component | Wraps existing function | Source |
|-----------|-------------------------|--------|
| `skills` | `scaffold_core_skills(project_root, config, skip_existing=not force)` | `gzkit.skills` |
| `rules` | `scaffold_core_rules(project_root, config, skip_existing=not force)` | `gzkit.rules` |
| `personas` | `scaffold_core_personas(project_root, config, skip_existing=not force)` | `gzkit.personas` |
| `templates` | `scaffold_core_templates(project_root, config, skip_existing=not force)` | `gzkit.templates` |
| `chores` | `scaffold_core_chores(...)` + `merge_chores_registry(...)` | `gzkit.chores` |
| `surfaces` | `sync_all(project_root, config)` | `gzkit.sync` |
| `hooks` | `setup_claude_hooks(...)` + `setup_copilot_hooks(...)` + `setup_copilotignore(...)` | `gzkit.hooks.claude`, `gzkit.hooks.copilot` |

### Decision 4 — Data flow

**`installation_profile` field** added to `GzkitConfig` (`src/gzkit/config.py`) as `Literal["default", "minimal"] = "default"`. Written by `gz init --minimal` (value `"minimal"`); default `gz init` writes `"default"`. The field is **observational, not authoritative** — it tracks adoption *intent at init time*, not current installation state. Current state is always computed fresh by inspecting `.gzkit/<surface>/` contents.

**Manifest stamping:** `generate_manifest()` in `src/gzkit/sync.py` reads `config.installation_profile` and includes it in `.gzkit/manifest.json` for downstream readers that do not load full `GzkitConfig`.

**Ledger events:** new `HarnessComponentInstalledEvent` in `src/gzkit/ledger_events.py` emitted per `gz harness install <component>` call with `extra={component, profile, items_added, force, dry_run}`. New `HarnessProfileUpgradedEvent` emitted by `install all` on successful full-install when profile auto-upgrades from `minimal` to `default`.

**`gz status --table`** adds a profile indicator line above the existing ADR tables, reading `config.installation_profile` and counting items per canonical surface via a `_count_installed()` helper. `gz status --json` adds a sibling `installation_profile` field and `harness_components` block (additive, schema-versioned, no breaking changes).

**`gz check` skip-absent-surface policy:** validator-scope registry annotated with `required_surfaces`. Dispatcher in `src/gzkit/trust_audits.py` checks surface presence; on a minimal-profile project with an absent surface, the scope emits a structured SKIP receipt (`arb-step-skip-<scope>-`) with `reason: "surface_not_installed"` and exits 0 for that scope. On a default-profile project with an absent surface, existing FAIL behavior is preserved (a default project missing its surfaces is broken). SKIP receipts surface in ceremony narrator output, `gz obpi complete` evidence, and `gz closeout` audit reports — the visibility is the anti-vibing backstop.

### Decision 5 — Output rendering

`gz init --minimal` post-init text replaces the default "Next steps" block with profile-aware adoption guidance (every `gz harness install <component>` form listed; SKIP-receipt behavior named). `gz harness install <component>` renders per-component progress (items scaffolded, items skipped, EDITED conflicts); `--json` mode returns a `HarnessInstallReport` model. `install all` renders a 7-step progress table and writes a `Profile upgraded: minimal -> default` line on full success. Default mode is human-first prose + counts; `--json` mode is parseable JSON to stdout with diagnostics on stderr (per `.claude/rules/cli.md`).

### Decision 6 — Exit codes

- `0` — success (install, dry-run, repair, skip-on-minimal)
- `3` — policy breach: EDITED canonical-surface conflict without `--force`; `--minimal` invoked on already-initialized project without `--force`

### Decision 7 — Layer-3 assertion

The cache surfaces this ADR creates (status profile indicator, manifest profile field, harness component counts) are **Layer-3 derived views** per `docs/governance/state-doctrine.md`. They are regenerable from `.gzkit/<surface>/` contents (canonical) and the ledger (truth). They are never source-of-truth for installation state — the directory contents are.

## Consequences

### Positive

- **Adoption-PR friction collapses.** Files-in-first-adoption-PR drops from ~150 to ≤10; each subsequent `gz harness install <component>` is a separately reviewable PR. Established codebases can adopt gzkit incrementally.
- **No tradeoff on anti-vibing doctrine.** `--minimal` does not lower a single gate; the SKIP-receipt policy makes deferred gates explicit at every ceremony.
- **Pure factoring, no new scaffolders or validators.** Every `gz harness install <component>` wraps an existing `scaffold_core_*` function. The OBPI is a CLI-surface and dispatcher-policy change, not a rewrite of canonical-surface logic.
- **Schema-stable contract.** Manifest, status JSON, and ledger event additions are additive. No breaking changes to existing surfaces. Default `gz init` behavior is byte-identical to today.
- **Telemetry seed for ADR-0.0.60.** `HarnessComponentInstalledEvent` events become inputs to a future ADR-0.0.60 fitness surface measuring "time-from-minimal-to-default" and "files-per-adoption-PR" — the Andy Dev Dan factory metric materialized as a measurable signal.

### Negative

- **CLI surface grows.** One new noun (`gz harness install`) with seven component subverbs, one new flag (`--minimal`), one new status indicator. All seven components require manpage entries (Gate 3 docs surface) and BDD scenarios (Gate 4).
- **Validator dispatcher policy is the delicate piece.** The skip-absent-surface contract concentrates anti-vibing risk at one code site (`src/gzkit/trust_audits.py`). Wrong implementation = silent passes on minimal projects = doctrine drift. Mitigated by structured SKIP receipts and dedicated test coverage in OBPI-06.
- **Two-profile state to reason about.** `gz status`, `gz check`, ceremony narrators, and audit reports all gain awareness of `installation_profile`. Edge cases (default profile with missing surface = DRIFT; minimal profile fully installed = functionally default) require careful reading by operators.
- **Profile auto-upgrade is operator-judgment-sensitive.** `install all` automatically rewrites `installation_profile: "minimal" -> "default"` in config + manifest. Alternative (explicit `gz harness profile set default`) would be more anti-vibing but adds CLI surface. Auto-upgrade is the simpler choice; if it becomes a doctrine smell, a future ADR can introduce explicit attestation.
- **7-OBPI implementation commitment on top of ADR-0.0.60's 6 OBPIs.** Combined surgical-win backlog is now 13 OBPIs across two ADRs. Sequencing matters: ADR-0.0.60 spine (01→02→03) and ADR-0.0.61 spine (01→02→03) can interleave; ADR-0.0.61 OBPI-06 (check skip) coordinates with ADR-0.0.60 OBPI-05 (telemetry validator) at the `trust_audits.py` dispatcher.

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
- Baseline Selected: 7
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 7

Baseline-selected uplift from 5 to 7 is justified by surface diversity (config + CLI flag + new CLI subcommand + aggregate orchestrator + status renderer + validator dispatcher policy + documentation/attestation cluster). Each surface is a distinct testability concern with its own coverage shape; bundling would violate the OBPI right-sizing matrix (single-narrative-split criterion).

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.61-01: **harness-install-config-and-models** — Extend `GzkitConfig` with `installation_profile: Literal["default", "minimal"]`; add `HarnessComponentInstalledEvent` + `HarnessProfileUpgradedEvent` to `src/gzkit/ledger_events.py`; add `installation_profile` to manifest schema (`src/gzkit/schemas/manifest.json`); define the `INSTALL_COMPONENT_REGISTRY` constant in `src/gzkit/harness/install.py` mapping component name → wrapped scaffolder callable.
- [ ] OBPI-0.0.61-02: **gz-init-minimal-flag** — Wire `--minimal` flag into `init_cmd.init()`; minimal-mode writes `.gzkit/{ledger.jsonl, manifest.json}`, `.gzkit.json`, empty canonical-surface dirs with `.gitkeep`, governance dir tree; emit `project_init` event with `extra.installation_profile: "minimal"`; replace post-init text per profile; preserve full-flavor default behavior byte-identical.
- [ ] OBPI-0.0.61-03: **gz-harness-install-command** — New `gz harness install <component>` CLI subcommand wrapping `INSTALL_COMPONENT_REGISTRY` entries (skills, rules, personas, templates, chores, surfaces, hooks); per-call `HarnessComponentInstalledEvent` emission; `--dry-run`, `--force`, `--json`; EDITED-conflict reuse of `_detect_refresh_state` marker mechanism; exit-code 3 on unresolved conflicts.
- [ ] OBPI-0.0.61-04: **gz-harness-install-all-aggregate** — `gz harness install all` orchestrator; canonicals → surfaces → hooks ordering; per-component progress rendering; profile auto-upgrade to `"default"` on full success (both `.gzkit.json` and manifest rewritten); `HarnessProfileUpgradedEvent` ledger emission.
- [ ] OBPI-0.0.61-05: **gz-status-profile-indicator** — Profile + per-component count line in `gz status --table`; `installation_profile` + `harness_components` block in `gz status --json` (additive, schema-versioned); `_count_installed()` helper in `src/gzkit/commands/status_cmd.py`; default-profile DRIFT detection.
- [ ] OBPI-0.0.61-06: **gz-check-skip-absent-surface** — Validator-scope registry annotated with `required_surfaces`; dispatcher in `src/gzkit/trust_audits.py` checks surface presence; minimal-profile + absent surface → structured SKIP receipt (`arb-step-skip-<scope>-`) with reason `"surface_not_installed"`, scope exits 0; default-profile + absent surface → existing FAIL behavior preserved; SKIP receipts surfaced in ceremony narrator, `gz obpi complete` evidence, and `gz closeout` audit.
- [ ] OBPI-0.0.61-07: **harness-install-docs-and-attestation** — Operator runbook section "Incremental adoption with `--minimal`"; manpage entries for `gz init --minimal` and every `gz harness install <component>` form; Gate 4 BDD scenarios (`features/harness_install.feature`); profile doc at `docs/governance/harness/installation-profiles.md`; Gate 5 attestation evidence bundle.

## Q&A Transcript

Design dialogue 2026-05-25 (main-session persona, operator-attested):

**Operator:** Asked for the surgical-win shape — answered "unknown… suggest."

**Agent recommendation:** Bootstrap-isolation profile (B), tightened with a concrete factory-engineering metric — files-in-first-adoption-PR. Today ~150; target ≤10 on `gz init --minimal`. Each subsequent `gz harness install <component>` is a separately reviewable PR. Direct map to Andy Dev Dan's *extensible-software* pillar: gzkit's harness becomes a modular extension, not a monolithic scaffold. Preserves anti-vibing mantra: `--minimal` postpones gate installation, never lowers a gate.

**Operator:** Ratified B.

**Section 1 (CLI surface):** Operator ratified. "Keep vibing." Two top edits considered (collapsing surfaces+hooks; splitting surfaces further) — both rejected to preserve simplicity.

**Section 2 (component dependency graph):** Operator ratified — and named the anti-vibing checkpoint: *"make sure you don't overly vibe code it."* Open question on `hooks:claude` vs `hooks:copilot` vendor split parked; current draft keeps monolithic per existing `_setup_init_hooks` convention.

**Section 3 (data flow):** Operator ratified. Skip-absent-surface policy concentrated at dispatcher; structured SKIP receipts as the anti-vibing backstop. `installation_profile` declared observational-not-authoritative.

**Section 4 (output & rendering):** Operator ratified. Profile auto-upgrade on `install all` chosen (simpler); explicit-attestation alternative noted for future ADR if doctrine smell emerges.

**Section 5 (OBPI decomposition):** Operator ratified — 7 OBPIs across config/models, init flag, install command, install aggregate, status indicator, check dispatcher policy, docs/attestation cluster. Sequencing: 01 → (02, 03, 05, 06 parallel) → 04 → 07.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/commands/test_init_minimal.py`, `tests/harness/test_install.py`, `tests/harness/test_install_all.py`, `tests/commands/test_status_profile.py`, `tests/governance/test_check_skip_absent_surface.py`
- [ ] Docs: `docs/user/runbook.md` (Incremental Adoption section), `docs/governance/harness/installation-profiles.md`, `docs/user/manpages/gz_init.md` (--minimal entry), `docs/user/manpages/gz_harness_install.md`
- [ ] BDD: `features/harness_install.feature`
- [ ] Receipts: `arb-step-skip-*` receipts on minimal-profile `gz check` runs

## Alternatives Considered

**Routing alternatives (3 rejected):**

1. **Faster init / skip "unnecessary" content (Option A in dialogue).** *Rejected* — "unnecessary" is operator-judgment; embedding taste into the kit violates anti-vibing doctrine. The kit must not assume which canonical surfaces an operator does not need.
2. **Skeleton + layer-on commands without minimal profile (Option C in dialogue).** *Rejected as standalone* — strict subset of bootstrap-isolation. Folded in as the `gz harness install` layering primitive within Option B. Not lost; absorbed.
3. **Multi-mode init (`--starter`, `--full`, `--minimal`, `--enterprise`).** *Rejected* — doctrine surface inflation. Two profiles (`default`, `minimal`) is sufficient and well-defined by what each omits. More profiles invent operator-segmentation distinctions the kit has no business making.

**Component-shape alternatives (2 rejected):**

4. **Collapse `surfaces` + `hooks` into one component.** *Rejected* — surfaces is a canonical-surface render (consumes skills/rules/personas/templates); hooks is a vendor-integration step (consumes ledger paths). Distinct concerns; bundling would obscure the dependency graph.
5. **Split `surfaces` into `agents-md` + `vendor-mirrors`.** *Rejected* — AGENTS.md and vendor mirrors are generated by the same `sync_all` invocation; splitting at the CLI would expose internal implementation seams without operator-visible benefit.

**Vendor-isolation alternatives (1 rejected):**

6. **Vendor-split components (`hooks:claude`, `hooks:copilot`).** *Rejected* — existing `_setup_init_hooks` convention bundles both. Andy Dev Dan's framework treats vendor as orthogonal, but gzkit's canon already chose bundled. A future ADR can split if vendor-isolated install becomes a real operator need.

**Profile-management alternatives (2 rejected):**

7. **Explicit `gz harness profile set default` to upgrade profile.** *Rejected for v1* — more anti-vibing but adds CLI surface. Auto-upgrade on `install all` is the simpler choice; if it becomes a doctrine smell, a future ADR can introduce explicit attestation. Named tradeoff acknowledged in Consequences § Negative.
8. **Permanent `--minimal` flag with no upgrade path.** *Rejected* — would make `minimal` a forever-escape-hatch from full gate coverage. Auto-upgrade on full install closes that loophole structurally.

**Validator-policy alternatives (3 rejected):**

9. **Silent no-op for validators on minimal projects.** *Rejected* — exactly the anti-vibing failure mode this ADR is engineered against. SKIP receipts are non-negotiable.
10. **Fail-closed every validator regardless of profile.** *Rejected* — would force operators to install full harness before any `gz check` succeeds, defeating incremental adoption. The structured-SKIP design preserves discipline without forcing adoption all-at-once.
11. **Per-validator runtime opt-in flags (`gz check --skip-instructions-budget`).** *Rejected* — pushes profile state into per-invocation flags instead of the config; would require operators to know which scopes their installation surface enables. The dispatcher-level policy is single-source-of-truth.

**Telemetry-shape alternatives (1 rejected):**

12. **No new ledger events; rely on directory inspection alone.** *Rejected* — `HarnessComponentInstalledEvent` seeds the ADR-0.0.60 fitness surface (files-per-adoption-PR, time-from-minimal-to-default). Without per-install events, the factory metric cannot be measured.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.61 | Pending | | | |
