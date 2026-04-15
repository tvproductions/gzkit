---
id: OBPI-0.27.0-10-arb-paths
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-10: ARB Paths

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-10 — "Evaluate and absorb arb/paths.py (43 lines) — ARB path resolution and directory layout"`

## OBJECTIVE

Evaluate `opsdev/arb/paths.py` (43 lines) against gzkit's current path resolution patterns and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing path resolution is sufficient), or Exclude (environment-specific). The opsdev module centralizes ARB directory layout: receipt storage paths, schema paths, archive paths, and directory creation. gzkit currently has path resolution in `config.py` and scattered across modules. The comparison must determine whether a dedicated ARB paths module provides cleaner architecture than integrating ARB paths into gzkit's existing path resolution.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/paths.py` (43 lines)
- **gzkit equivalent:** Path resolution in `src/gzkit/config.py` and module-level constants

## ASSUMPTIONS

- The governance value question governs: does a dedicated paths module improve architecture over inline path constants?
- At 43 lines, this is the smallest ARB module — likely a utility that other modules depend on
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- This module is foundational — if the receipt system is adopted, paths must be resolved somewhere

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Redesigning gzkit's entire path resolution strategy — scope is ARB-specific paths

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: path resolution strategy, directory creation, cross-platform safety
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's existing path resolution is sufficient
1. If Exclude: document why the module is environment-specific

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.27.0-10-01: Read both implementations completely
- [x] REQ-0.27.0-10-02: Document comparison: path resolution strategy, directory creation, cross-platform safety
- [x] REQ-0.27.0-10-03: Record decision with rationale: Absorb / Confirm / Exclude
- [x] REQ-0.27.0-10-04: If Absorb: adapt to gzkit conventions and write tests
- [x] REQ-0.27.0-10-05: If Confirm: document why gzkit's existing path resolution is sufficient
- [x] REQ-0.27.0-10-06: If Exclude: document why the module is environment-specific


## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Decision: Absorb (executed under OBPI-0.25.0-33)

**Decision:** Absorb.

**Executed under:** `OBPI-0.25.0-33-arb-analysis-pattern` (closed 2026-04-14). Cross-referenced to preserve per-module audit trail.

**Gzkit implementation:**

- `src/gzkit/arb/paths.py` — port of `opsdev/arb/paths.py` (43L source). Replaces airlineops's `Settings + registry` pattern with gzkit's typed `GzkitConfig` approach: adds `ArbConfig` to `src/gzkit/config.py` with `receipts_root: str = "artifacts/receipts"` and `default_limit: int = 20`, wires `arb: ArbConfig = Field(default_factory=ArbConfig)` into `GzkitConfig`. The `receipts_root()` function accepts an optional `config` and `project_root` for test injection, honors a `GZKIT_ARB_RECEIPTS_ROOT` environment variable override, and creates the directory on demand.
- `tests/arb/test_paths.py` — 4 Red→Green tests: default path from config, custom receipts_root, env override, auto-load config when not provided.
- `tests/test_config.py::TestArbConfig` — 5 additional tests: defaults, frozen, GzkitConfig exposes arb, roundtrip through GzkitConfig.

**Comparison evidence:** See OBPI-0.25.0-33-arb-analysis-pattern.md § Comparison Evidence — "Storage architecture — Per-run receipt files under `arb.receipts_root` (config-driven)" — parity between opsdev and gzkit post-absorption, with gzkit's typed Pydantic config as the upgrade.

**Dog-fooding proof:** All 4 dog-food receipts (ruff, typecheck step, unittest step, mkdocs step) were written to `artifacts/receipts/` via `receipts_root()`, demonstrating the path resolution works end-to-end in the real project.

**Foundational-module note:** The brief correctly noted "This module is foundational — if the receipt system is adopted, paths must be resolved somewhere." That "somewhere" ended up being `src/gzkit/arb/paths.py` + `ArbConfig` in `src/gzkit/config.py`, executed atomically with the rest of the absorption.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
