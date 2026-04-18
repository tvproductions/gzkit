---
id: OBPI-0.16.0-01-content-type-registry
parent: ADR-0.16.0-cms-architecture-formalization
item: 1
lane: Lite
status: attested_completed
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

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.16.0-01-01: `ContentType` Pydantic model: `name`, `schema_name`, `frontmatter_model`, `lifecycle_states`, `canonical_path_pattern`, `vendor_rendering_rules`
- [x] REQ-0.16.0-01-02: `ContentTypeRegistry` class with `register()`, `get()`, `list_all()`, `validate_artifact()` methods
- [x] REQ-0.16.0-01-03: All current types registered: ADR, OBPI, PRD, Constitution, Rule, Skill, Attestation, LedgerEvent
- [x] REQ-0.16.0-01-04: Registry is a singleton loaded at import time — no lazy initialization surprises
- [x] REQ-0.16.0-01-05: `validate_artifact()` uses the registered Pydantic model for frontmatter validation


## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — 612 tests pass
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_registry -v
Ran 24 tests in 0.001s — OK
Full suite: 612 tests in 31s — OK
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Implementation Summary

- Files added: `src/gzkit/registry.py` (ContentType model, ContentTypeRegistry, singleton REGISTRY with 8 types)
- Tests added: `tests/test_registry.py` (24 tests across 4 test classes)
- Date completed: 2026-03-18
- Defects noted: None

### Key Proof

```bash
uv run -m unittest tests.test_registry.TestGlobalRegistry.test_all_eight_types_registered -v
# test_all_eight_types_registered ... ok — ADR, OBPI, PRD, Constitution, Rule, Skill, Attestation, LedgerEvent
```

## Human Attestation

- Attestor: human:Jeff
- Attestation: Completed
- Date: 2026-03-18

## Tracked Defects

_No defects tracked._

---

**Brief Status:** Completed

**Date Completed:** 2026-03-18

**Evidence Hash:** -
