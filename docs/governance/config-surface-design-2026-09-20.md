# gzkit-internal config surface — design record

> **Status: PROPOSAL. Nothing here is built.** This record exists so
> `ADR-0.39.0` is a transcription rather than a fresh design when ADR order
> permits it. It is not an ADR, initiates no OBPI, and moves no file. Operator
> ruling required before any of it lands.
>
> Figures are a dated observation of the 2026-09-20 tree and are ILLUSTRATIVE
> (`AGENTS.md` § Governance doctrine surfaces). Re-run
> [`config-derivation-2026-09-20-evidence/census.py`](config-derivation-2026-09-20-evidence/census.py).

## Why

Operator, 2026-09-20, verbatim:

> gzkit lacks a comprehensive and all-encompassing config system like airlineops
> had, we need to adopt this as a pre-requisite for 1.0. this is inexcusable.
> there are so many janky and undocumented rules, thresholds and pseudo-settings
> handing around gzkit. it is a travesty

And, scoping it:

> I want a single configuration surface for the whole project. implementers would
> develop their own, so this is a 'gzkit-interal' config.

**That second sentence is the load-bearing one.** This surface is what gzkit
reads *about itself*. It is not what an adopter gets: `gz init` scaffolds an
adopter's own config, and an adopter's instance is theirs to own. The two must
not be conflated, because gzkit is simultaneously a product and its own first
consumer — the confusion this whole campaign exists to unwind.

## Operator rulings this record implements

| # | Ruling |
|---|---|
| 1 | Scope is the `data/` registries and module constants **plus `.gzkit.json`** — everything gzkit reads about itself |
| 2 | Shape is **entry point + categorical subdirectories**, the `../airlineops/config` model |
| 3 | The waiver / grandfather / baseline rosters are a **separate class — debt state, not settings** |
| 4 | **Migrate readers once**, after the surface lands — not before |

## The shape (ruling 2)

`../airlineops/config/README.md` states five principles; they are adopted
verbatim as this surface's contract:

1. **Single Entry Point** — one file is THE config; code calls one loader.
2. **Categorical Subdirectories** — every file belongs to a category; no loose files at root.
3. **No Parallel Systems** — one loader, one source of truth.
4. **Config != Documentation** — if no code imports it, it belongs in `docs/`.
5. **No Duplication** — each value has ONE authoritative location.

```text
config/
├── settings.json          <- THE entry point: scalars inline, categories indexed
├── settings.local.json    <- optional operator overrides, gitignored
├── catalogs/              <- reference data gzkit reads
├── governance/            <- campaign identity, check scopes, dispatch
├── surfaces/              <- what gzkit writes and delivers
└── thresholds/            <- tunable numbers

debt/                      <- SEPARATE CLASS (ruling 3), not config
├── ratchet.json           <- the index, today data/waiver_ratchet_registry.json
└── <29 roster files>
```

**Merge order:** packaged defaults → `config/settings.json` →
`config/settings.local.json` (optional). Same as airlineops. A local override
never enters git and never satisfies a gate.

## The mapping — 48 files placed

### Debt class — 29 files, OUT of the settings surface (ruling 3)

These record *measured debt* under shrink-only ratchets. Nobody tunes them; they
shrink as debt is repaid, and every one is already indexed by
`waiver_ratchet_registry.json` with a declared honesty mechanism. Treating them
as settings would invite editing them as settings, which is precisely the
laundering `ADR-0.0.73` Boundary Invariant #8 forbids.

`adversarial_validation_grandfather` · `advisory_scorecard_grandfather` ·
`behave_coverage_waivers` · `chores_layout_waivers` ·
`config_derivation_grandfather` · `direct_data_reach_grandfather` ·
`distribution_baseline_manifest` · `exemption_control_grandfather` ·
`fidelity_presence_grandfather` · `foundation_grandfather` ·
`ghi_cross_reference_baseline` · `handoff_section_grandfather` ·
`historical_self_close_waivers` · `interview_transcript_waivers` ·
`ledger_vocabulary_grandfather` · `mechanical_witness_grandfather` ·
`module_constant_grandfather` · `module_size_grandfather` ·
`persona_grandfather` · `population_control_grandfather` ·
`release_tag_reachability_grandfather` · `req_kind_grandfathering` ·
`sensitivity_floor_grandfather` · `support_proof_grandfather` ·
`surface_weight_waivers` · `tautological_test_baseline` ·
`tautological_test_waivers` · `uncalled_gate_grandfather` ·
`validator_reachability_grandfather`

### Settings surface — 19 files in four categories

| Category | Files |
|---|---|
| `governance/` | `active_campaign` · `check_scope_membership` · `check_step_scopes` · `check_step_concurrency` · `mandated_tier1_dispatch` |
| `thresholds/` | `audit_thresholds` · `eval_feedback_thresholds` · `instructions_files_budget` · `surface_weight_floor` |
| `surfaces/` | `agents_md_survival_declaration` · `vendor-manifest` · `transcribed_count_surfaces` · `security_surfaces` |
| `catalogs/` | `frontier_model_cards` · `exemplar_corpus` · `advisor_archetype_rules` · `flags` |

Two are **indexes rather than settings** and become part of the entry point
itself: `config_registry.json` (which registry is owned by whom) and
`waiver_ratchet_registry.json` (which roster carries which honesty mechanism —
moves to `debt/ratchet.json` with its class).

### `.gzkit.json` (ruling 1)

`GzkitConfig` — `VendorConfig`, `PathConfig`, `ArbConfig`, `AuthorshipConfig`,
`SmokeConfig` — is the adopter-facing **schema**, and it stays that. What folds
in is **gzkit's own instance** of it: gzkit reads its own vendors, paths and
authorship from the one surface like everything else. An adopter's `.gzkit.json`
is untouched, because an adopter's config is theirs.

### The 56 module constants

Not enumerated here, because deciding 56 rows individually is the work, not the
design. The triage rule:

- **A value an operator could reasonably want different → settings.** Budgets,
  ceilings, review ages, cadences.
- **A value that would break correctness if changed → code, with a comment.**
  Parser depths, fence widths, buffer sizes.
- **A timeout → settings**, because every timeout is environment-dependent and
  `DEFAULT_TIMEOUT_SECONDS` already disagrees with itself across two modules
  (30.0 and 3.0) with nothing reconciling them.

`data/module_constant_grandfather.json` already rosters all 56 shrink-only, so
the triage can proceed one constant at a time against a list that cannot grow.

## Addressing — the one open question this record does not settle

`gzkit.registries.load_registry(project_root, name)` exists and 1 of 50 readers
uses it. When files move into categories, `name` must mean something.

**Option A — logical keys.** `load_registry(root, "thresholds.audit")`; the entry
point maps key → path. Files can move forever without touching a caller. Costs a
rename of every call site at migration time, which ruling 4 already schedules.

**Option B — filenames forever.** `load_registry(root, "audit_thresholds.json")`;
the entry point maps filename → path. Callers never change again, but the
surface's addresses stay the filenames of a layout it is meant to replace.

**Recommendation: A.** Ruling 4 already has every reader migrating once, so the
rename is free at exactly the moment it is cheapest, and B permanently encodes
the pre-config layout in the post-config API.

## Migration plan (ruling 4)

1. Land this design as `ADR-0.39.0` when ADR order permits, or by operator
   exception. **This record is the input, not the decision.**
2. Build the entry point and extend `load_registry` to resolve through it.
3. Move the 19 settings files into categories; move the 29 debt files out.
4. Migrate the 49 remaining readers **once**, to whichever addressing wins.
5. Triage the 56 constants against the roster, which may only shrink.
6. Retire `data/` or leave it for genuine data — a decision this record defers.

## What is already fenced, so the surface is not racing decay

Three shrink-only ratchets landed 2026-09-20 and hold the line while this waits:
derivation (GHI #1066), module constants (#1066), and direct reads (#1067). New
unsourced registries, new hardcoded thresholds and new parallel readers all fail
closed today. **The surface is owed; the bleeding is stopped.**

## What this record does not claim

- It does not claim the 19/29 split is correct at the row level. Two files are
  indexes rather than settings and are called out; others may be miscategorised,
  and category membership is cheap to change before anything moves.
- It does not decide whether `data/` survives.
- It does not estimate effort. The campaign's § 7 arithmetic covers OBPI work,
  and no OBPI has been authored for this.
