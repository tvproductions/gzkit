---
id: OBPI-0.16.0-01-content-type-registry
parent: ADR-0.16.0-cms-architecture-formalization
item: 1
lane: Lite
status: Draft
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.16.0-01 — content-type-registry

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-0.16.0-cms-architecture-formalization.md`
- OBPI Entry: `OBPI-0.16.0-01 — "Formal registry of all governance content types with Pydantic models, schemas, lifecycle rules"`

## OBJECTIVE (Lite)

Create a content type registry (`src/gzkit/registry.py`) that catalogs every governance
artifact type. Each registered type declares: its Pydantic frontmatter model, its JSON
schema name, its allowed lifecycle states, its canonical path pattern, and its vendor
rendering rules. The registry is the single lookup for "what content types exist and
how are they shaped."

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `src/gzkit/registry.py` (new)
- `tests/test_registry.py` (new)

## DENIED PATHS (Lite)

- Vendor surfaces (`.claude/`, `.github/`, `.agents/`)
- CI files, lockfiles

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. `ContentType` Pydantic model: `name`, `schema_name`, `frontmatter_model`, `lifecycle_states`, `canonical_path_pattern`, `vendor_rendering_rules`
1. `ContentTypeRegistry` class with `register()`, `get()`, `list_all()`, `validate_artifact()` methods
1. All current types registered: ADR, OBPI, PRD, Constitution, Rule, Skill, Attestation, LedgerEvent
1. Registry is a singleton loaded at import time — no lazy initialization surprises
1. `validate_artifact()` uses the registered Pydantic model for frontmatter validation

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
