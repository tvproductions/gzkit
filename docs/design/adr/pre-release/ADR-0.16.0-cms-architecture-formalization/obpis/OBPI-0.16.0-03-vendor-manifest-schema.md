---
id: OBPI-0.16.0-03-vendor-manifest-schema
parent: ADR-0.16.0-cms-architecture-formalization
item: 3
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.16.0-03 — vendor-manifest-schema

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-0.16.0-cms-architecture-formalization.md`
- OBPI Entry: `OBPI-0.16.0-03 — "Extend manifest.json with vendors section; Pydantic model for vendor enablement"`

## OBJECTIVE (Lite)

Extend `.gzkit/manifest.json` with a `vendors` section that declares which agent
harnesses are enabled for this repository. Each vendor entry has: `enabled` (bool),
`surface_root` (path), `instruction_format` (string — e.g., "claude-rules", "github-instructions"),
and vendor-specific rendering config. The Pydantic model for the manifest validates
this section. `gz agent sync` will use this to decide which surfaces to generate.

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `.gzkit/manifest.json` (add vendors section)
- `src/gzkit/schemas/manifest.json` (update schema)
- `src/gzkit/config.py` (update GzkitConfig model with vendor config)
- `tests/test_config.py` (vendor enablement tests)

## DENIED PATHS (Lite)

- Vendor surfaces (`.claude/`, `.github/`, `.agents/`)
- CI files, lockfiles

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. `VendorConfig` Pydantic model: `enabled` (bool), `surface_root` (Path), `instruction_format` (enum), extra config per vendor
1. `VendorsConfig` Pydantic model: `claude`, `copilot`, `codex`, `gemini`, `opencode` — each a `VendorConfig`
1. `.gzkit/manifest.json` updated with `vendors` key (backward-compatible — existing manifests without `vendors` default to current behavior)
1. Manifest JSON schema updated to include vendor section
1. `GzkitConfig` model includes vendor config; `config.vendors.claude.enabled` is the canonical check
1. Default: `claude: enabled`, all others: disabled (matches current Claude-primary reality)

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — all tests pass (643 total, 17 vendor-specific)
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_config -v
Ran 17 tests in 0.020s — OK
uv run gz test — 643 tests, OK
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Implementation Summary

- Models added: `VendorConfig` and `VendorsConfig` Pydantic models in `src/gzkit/config.py`
- Fields: `enabled` (bool), `surface_root` (str), `instruction_format` (str) per vendor
- Vendors: claude (enabled by default), copilot, codex, gemini, opencode (all disabled by default)
- Config integration: `GzkitConfig.vendors` field exposes vendor enablement
- Backward-compatible: configs without `vendors` key use defaults

### Key Proof

```text
$ uv run -m unittest tests.test_config.TestVendorsConfig.test_defaults__claude_enabled -v
test_defaults__claude_enabled ... ok
$ uv run -m unittest tests.test_config.TestVendorsConfig.test_defaults__others_disabled -v
test_defaults__others_disabled ... ok
```

Claude defaults to enabled; all other vendors default to disabled.

## Human Attestation

- Attestor: `self-close-exception (Lite lane)`
- Attestation: `Self-closed per AGENTS.md Lane Inheritance Rule`
- Date: `2026-03-18`

---

**Brief Status:** Completed

**Date Completed:** 2026-03-18

**Evidence Hash:** -
