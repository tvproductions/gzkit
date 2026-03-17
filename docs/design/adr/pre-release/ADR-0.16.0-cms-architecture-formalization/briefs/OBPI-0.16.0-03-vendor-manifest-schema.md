---
id: OBPI-0.16.0-03-vendor-manifest-schema
parent: ADR-0.16.0-cms-architecture-formalization
item: 3
lane: Lite
status: Draft
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

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` — all tests pass
- [ ] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
