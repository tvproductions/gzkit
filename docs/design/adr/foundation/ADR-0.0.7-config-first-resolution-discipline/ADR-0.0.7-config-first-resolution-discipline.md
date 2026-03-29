<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.7 — Config-First Resolution Discipline

## Tidy First Plan

Behavior-preserving tidyings required before any behavior change:

1. Inventory all module-level `Path(__file__).parents[N]` derivations and their
   downstream constants (`_PROJECT_ROOT`, `_DATA_DIR`, `_CONFIG_PATH`, etc.)
1. Inventory all hardcoded path literals, threshold values, and structural
   assumptions in `src/gzkit/` that bypass the config system
1. Map each finding to its correct manifest section (`data`, `ops`, `thresholds`,
   or existing `structure`/`artifacts` keys)

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If a hardcoded value has no natural home in the manifest schema, stop and
  propose a new manifest section before proceeding.
- If removing a constant would require changing the manifest loading bootstrap
  itself (the `.gzkit/` anchor points), stop and classify it as an architectural
  invariant.

**Date Added:** 2026-03-29
**Date Closed:**
**Status:** Draft
**SemVer:** 0.0.7
**Area:** Governance Foundation — Config Resolution
**Lane:** Lite

## Agent Context Frame — MANDATORY

**Role:** Infrastructure architect extending the config schema and establishing
enforcement rules for config-first discipline.

**Purpose:** When this ADR is complete, every path, threshold, and structural
assumption in gzkit source code resolves from the manifest — never from
module-level constants or `Path(__file__).parents[N]`. The manifest is the single
resolved config layer that code reads from, and enforcement tooling catches
violations at edit-time, gate-time, and during periodic sweeps.

**Goals:**

- Manifest v2 schema covers all resource paths currently hardcoded in source
- Resolution helpers make manifest-driven path lookup ergonomic for callers
- Lint rule catches `Path(__file__).parents[` patterns at edit-time
- `gz check-config-paths` validates source code paths trace to manifest keys
- Zero hardcoded root derivations remain in `src/gzkit/`

**Critical Constraint:** Implementations MUST resolve all paths and configurable
values from the manifest at the call site, never at module import time. The
manifest is loaded once by the CLI entry point and threaded to consumers.
Module-level constants that derive from `__file__` position are prohibited.

**Anti-Pattern Warning:** A failed implementation adds the new manifest sections
but leaves existing module-level constants in place with "fallback" logic that
reads from the constant when no manifest is provided. This produces code that
passes tests (because the fallback works) but defeats the entire purpose —
the hardcoded constant is still the actual source of truth, and the manifest
key is dead config that nobody reads.

**Integration Points:**

- `src/gzkit/config.py` — `GzkitConfig`, `PathConfig` models
- `src/gzkit/commands/common.py` — `load_manifest()`, `ensure_initialized()`
- `src/gzkit/sync_surfaces.py` — `generate_manifest()`
- `src/gzkit/commands/config_paths.py` — `check_config_paths_cmd()`
- `.gzkit/manifest.json` — the resolved config artifact
- `data/schemas/` — manifest JSON schema (if one exists)

---

## Checklist

- [ ] Manifest v2 schema — add `data`, `ops`, `thresholds` sections to `generate_manifest()` and schema validation; bump schema version
- [ ] Resolution helpers — create `manifest_path()` helper; establish parameter-threading pattern from CLI entry point to consumers
- [ ] Eval module migration — remove `_PROJECT_ROOT` from `eval/datasets.py`, `eval/delta.py`, `eval/regression.py`; thread manifest paths
- [ ] Hooks module migration — remove `Path(__file__).parents[3]` from `hooks/guards.py`; thread manifest paths
- [ ] Lint rule and check expansion — add `Path(__file__).parents` detection to `gz lint`; expand `check-config-paths` to scan source for unmapped path literals
- [ ] Chore integration — update `hardcoded-root-eradication` chore with manifest-aware acceptance criteria; wire into `gz check`

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 3-3
- Baseline Selected: 3
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 0
- Split Total: 3
- Final Target OBPI Count: 6

## Intent

Establish config-first resolution discipline as a foundation-level constraint
in gzkit. Every resource path, threshold value, and structural assumption must
resolve from the manifest (`manifest.json`) — the single comprehensive config
layer that code reads from. This is motivated by 12-factor principle #3 (config
separate from code), implemented via config files (not environment variables),
and exists to counter the recurring problem of agents hardcoding constants that
bypass the config system.

## Decision

- Extend `manifest.json` schema from v1 to v2 with three new top-level sections:
  `data` (eval datasets, baselines, schemas), `ops` (chores, receipts, proofs),
  and `thresholds` (coverage floor, eval regression delta, size limits)
- All configurable values live inline in the manifest — no external threshold
  files pointed to by the manifest (single resolved config, single source of truth)
- Code resolves paths and thresholds from the manifest at the call site via
  explicit parameters; module-level `_PROJECT_ROOT` constants are prohibited
- Enforcement is layered: lint rule (edit-time) + expanded `check-config-paths`
  (gate-time) + recurring chore (periodic sweep)
- Architectural invariants remain fixed and are not configurable: `.gzkit/` root,
  `.gzkit.json`, `.gzkit/manifest.json`, `.gzkit/ledger.jsonl`, `get_project_root()`

## Interfaces

- **Config (manifest v2 schema):** New sections `data`, `ops`, `thresholds` in
  `.gzkit/manifest.json`
- **CLI (expanded):** `gz check-config-paths` gains source-code path validation
- **Lint (new):** `gz lint` detects `Path(__file__).parents[` patterns
- **Config keys consumed:** `manifest.data.*`, `manifest.ops.*`,
  `manifest.thresholds.*` by eval, hooks, chores, and quality modules

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.7-01 | Manifest v2 schema — add `data`, `ops`, `thresholds` sections to `generate_manifest()` and schema validation; bump schema version | Lite | Pending |
| 2 | OBPI-0.0.7-02 | Resolution helpers — create `manifest_path(manifest, section, key)` helper; establish parameter-threading pattern | Lite | Pending |
| 3 | OBPI-0.0.7-03 | Eval module migration — remove `_PROJECT_ROOT` from `eval/datasets.py`, `eval/delta.py`, `eval/regression.py`; thread manifest paths | Lite | Pending |
| 4 | OBPI-0.0.7-04 | Hooks module migration — remove `Path(__file__).parents[3]` from `hooks/guards.py`; thread manifest paths | Lite | Pending |
| 5 | OBPI-0.0.7-05 | Lint rule and check expansion — add `Path(__file__).parents` detection to `gz lint`; expand `check-config-paths` to scan source for unmapped path literals | Lite | Pending |
| 6 | OBPI-0.0.7-06 | Chore integration — update `hardcoded-root-eradication` chore with manifest-aware acceptance criteria; wire into `gz check` | Lite | Pending |

**Briefs location:** `obpis/OBPI-0.0.7-*.md` (each brief is a **Level 2 WBS** element)

---

## Rationale

Agents trained on open-source codebases reflexively hardcode module-level
constants that derive paths from their physical position in the source tree.
This creates three problems:

1. **Untestable coupling** — functions silently depend on the real project root,
   breaking test isolation when called from temp directories
2. **Config bypass** — the manifest declares paths that nothing reads, while
   module constants are the actual source of truth
3. **Silent drift** — as the manifest evolves, hardcoded constants diverge
   without any enforcement catching the mismatch

The 12-factor methodology's core insight is that config must be strictly
separated from code. gzkit implements this via config files (manifest.json)
rather than environment variables, following the config-file-first philosophy
that favors structured, version-controlled, self-documenting configuration
over flat key-value env vars.

Thresholds live inline in the manifest (not in separate config files) to
maintain a single resolved config — one file to read, one source of truth,
following the pattern established in AirlineOps.

## Consequences

- `manifest.json` becomes the single comprehensive config layer for all
  resource paths, thresholds, and structural assumptions
- Schema version bumps from v1 to v2; v1 manifests remain forward-compatible
  (new sections have defaults)
- Module-level `_PROJECT_ROOT` and derived constants are removed from all
  source modules in `src/gzkit/`
- `generate_manifest()` gains responsibility for populating `data`, `ops`,
  and `thresholds` sections with sensible defaults
- `gz check-config-paths` becomes a more comprehensive enforcement gate
- The `hardcoded-root-eradication` chore gains manifest-aware acceptance
  criteria for periodic sweeps

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_config.py`, `tests/test_manifest_v2.py`
- **BDD:** not applicable (Lite lane, no external contract change)
- **Docs:** manifest schema documentation; config-first rule in `.gzkit/rules/`

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each checklist item maps to one OBPI brief. Record a one-line acceptance
  note in the brief once Gates 1-2 are green.
- Verification command:

```bash
grep -rn "Path(__file__).*parents" src/gzkit/
uv run gz check-config-paths
uv run -m unittest -q
```

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.0.7`
- **Related issues:** none yet

### Inputs & Config

- Manifest schema: `.gzkit/manifest.json` (v1 -> v2)
- Config model: `src/gzkit/config.py`

### Source & Contracts

- Manifest generation: `src/gzkit/sync_surfaces.py`
- Config validation: `src/gzkit/commands/config_paths.py`
- Eval modules: `src/gzkit/eval/datasets.py`, `src/gzkit/eval/delta.py`,
  `src/gzkit/eval/regression.py`
- Hooks: `src/gzkit/hooks/guards.py`

### Tests

- Unit: `tests/test_config.py`, `tests/test_manifest_v2.py`

### Docs

- Config-first rule: `.gzkit/rules/config-first.md`
- Manifest v2 schema docs

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD
- Notes: manifest v2 schema; module constant removal; enforcement tooling

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `.gzkit/manifest.json` | M | Schema v2 with `data`, `ops`, `thresholds` sections | Diff link | |
| `src/gzkit/sync_surfaces.py` | M | `generate_manifest()` populates v2 sections | Unit tests | |
| `src/gzkit/eval/*.py` | M | Zero `_PROJECT_ROOT` constants; manifest-driven | grep proof | |
| `src/gzkit/hooks/guards.py` | M | Zero `Path(__file__).parents` | grep proof | |
| `src/gzkit/commands/config_paths.py` | M | Source-code path validation | Unit tests | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. ...

1. ...
