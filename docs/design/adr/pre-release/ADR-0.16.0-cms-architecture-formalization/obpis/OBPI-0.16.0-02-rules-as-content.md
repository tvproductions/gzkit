---
id: OBPI-0.16.0-02-rules-as-content
parent: ADR-0.16.0-cms-architecture-formalization
item: 2
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.16.0-02 — rules-as-content

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.16.0-cms-architecture-formalization/ADR-0.16.0-cms-architecture-formalization.md`
- OBPI Entry: `OBPI-0.16.0-02 — "Implement .gzkit/rules/ as canonical content; define vendor-neutral rule format"`

## OBJECTIVE (Lite)

Create `.gzkit/rules/` as the canonical source for constraint rules. Define a
vendor-neutral rule format (Markdown with YAML frontmatter: `id`, `paths`, `description`).
Migrate existing `.github/instructions/*.md` content into `.gzkit/rules/` as canonical
source. The vendor-specific rendering (Claude `paths:` frontmatter, Copilot `applyTo:`
frontmatter) is handled in OBPI-04 (template engine).

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `.gzkit/rules/` (new canonical directory)
- `src/gzkit/rules.py` (new module for rule loading/validation)
- `tests/test_rules.py` (new)

## DENIED PATHS (Lite)

- Vendor surfaces (`.claude/rules/`, `.github/instructions/`) — touched in OBPI-04
- CI files, lockfiles

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. `.gzkit/rules/` directory created with canonical rule files
1. Rule frontmatter schema defined: `id` (string), `paths` (list of glob patterns), `description` (string)
1. Pydantic model `RuleFrontmatter` validates rule files
1. Rule registered in content type registry (from OBPI-01)
1. Existing `.github/instructions/` content preserved as migration source (not deleted — vendor rendering comes in OBPI-04)
1. `load_rules()` function reads and validates all rules from `.gzkit/rules/`

## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — 633 tests pass
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_rules tests.test_registry -v
Ran 59 tests in 0.100s — OK
Full suite: 633 tests in 31s — OK
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Implementation Summary

- Files added: `.gzkit/rules/` (11 canonical rule files), `RuleFrontmatter`/`CanonicalRule`/`load_rules()` in `src/gzkit/rules.py`
- Tests added: 20 new tests across 5 test classes in `tests/test_rules.py`, 1 updated in `tests/test_registry.py`
- Registry updated: Rule type now has `frontmatter_model=RuleFrontmatter`, `schema_name="rule"`
- Date completed: 2026-03-18
- Defects noted: None

### Key Proof

```bash
uv run -m unittest tests.test_rules.TestLoadRules.test_load_actual_canonical_rules -v
# test_load_actual_canonical_rules ... ok — loads all 11 rules from .gzkit/rules/, validates frontmatter
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
