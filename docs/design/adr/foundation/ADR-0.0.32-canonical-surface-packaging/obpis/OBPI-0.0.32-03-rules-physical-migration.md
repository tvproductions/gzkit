---
id: OBPI-0.0.32-03-rules-physical-migration
parent: ADR-0.0.32-canonical-surface-packaging
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.32-03-rules-physical-migration: Rules Physical Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #3 — "Rules physical migration — `git mv .gzkit/rules/<slug>.md src/gzkit/rules/<slug>.md` for all 14 canonical rules; convert `src/gzkit/rules.py` → `src/gzkit/rules/__init__.py` preserving every public symbol re-export. Registry + scaffolder + init wiring explicitly deferred to OBPI-04."

**Status:** Draft

## Objective

Move 14 canonical rule files from `.gzkit/rules/<slug>.md` into `src/gzkit/rules/<slug>.md` (file-not-dir layout, distinct from skills/chores per-slug-subdir layout) via `git mv` (preserving per-file history). Convert the existing `src/gzkit/rules.py` module (563 lines) into `src/gzkit/rules/__init__.py` so every `from gzkit.rules import X` import site continues to resolve. **No registry authoring, no scaffolder authoring, no init_cmd integration in this OBPI** — those land in OBPI-04. This is the chores precedent's OBPI-0.0.21-01 shape applied to rules: physical migration as its own atomic unit.

## Lane

**Heavy** — restructures Python package layout (module → package conversion). Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/rules.py` — convert to package; delete the file after content moves
- `src/gzkit/rules/__init__.py` — receives byte-equivalent contents of the former `src/gzkit/rules.py` (no logic changes)
- `src/gzkit/rules/<slug>.md` — destination of `git mv` from `.gzkit/rules/<slug>.md` (14 files)
- `.gzkit/rules/<slug>.md` — source of `git mv`
- `tests/test_rules.py`, `tests/test_instruction_audit.py`, `tests/test_registry.py` — minimal additions (regression tests for public-symbol re-exports through the new package)

## Denied Paths

- `pyproject.toml` — wheel includes belong to OBPI-06; this OBPI moves files but does NOT extend the wheel manifest
- `src/gzkit/rules/__init__.py` — no `CORE_RULES` registry, no `scaffold_core_rules` function, no `_iter_canonical_rule_slugs` enumerator added in this OBPI; OBPI-04 owns those
- `src/gzkit/commands/init_cmd.py` — no `scaffold_core_rules` invocation, no integration changes in this OBPI; OBPI-04 owns the wiring
- `src/gzkit/skills.py`, `src/gzkit/skills/**` — skills belong to OBPI-01 / -02
- `src/gzkit/hooks/**`, `src/gzkit/personas/**`, `src/gzkit/templates/**` — out of scope
- `features/**` — no behave coverage in this OBPI
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/rules/`, `.github/instructions/` — mirror regen belongs to OBPI-08
- `docs/governance/trust-doctrine.md` — T0 doctrine belongs to ADR-0.0.31

## Requirements (FAIL-CLOSED)

1. `git mv .gzkit/rules/<slug>.md src/gzkit/rules/<slug>.md` MUST be used for every one of the 14 canonical rules so per-file git history is preserved.
2. After the moves, `src/gzkit/rules/<slug>.md` MUST be byte-identical to the pre-move `.gzkit/rules/<slug>.md`. No content edits.
3. `src/gzkit/rules.py` MUST NOT exist after this OBPI. Its contents MUST move to `src/gzkit/rules/__init__.py` such that every `from gzkit.rules import X` import site in `src/` and `tests/` continues to resolve without modification.
4. `src/gzkit/rules/__init__.py` MUST be byte-equivalent to the prior `src/gzkit/rules.py` contents — no new functions, no removed functions, no signature changes.
5. NO `CORE_RULES`, `scaffold_core_rules`, or `_iter_canonical_rule_slugs` is permitted in this OBPI's `__init__.py`. Adding any of them is scope creep into OBPI-04.
6. NO `scaffold_core_rules` invocation in `src/gzkit/commands/init_cmd.py` is permitted in this OBPI. Adding it is scope creep into OBPI-04.
7. NO wheel-include extension is permitted. `pyproject.toml` continues to ship chores-only after this OBPI.
8. Regression tests MUST cover every previously-public symbol in `src/gzkit/rules.py` (e.g. `RuleFrontmatter`, `ClassifiedRule`, `load_rules`, `render_rules_to_dir`, `sync_claude_rules`, `sync_nested_agents_md`, `validate_rule_placement`, `_parse_instruction_frontmatter`, `_extract_body_after_frontmatter`, `_extract_subtree_prefix`).
9. `uv run gz check` MUST exit 0 after the migration.

> STOP-on-BLOCKERS:
> - If `src/gzkit/rules/` already exists as a directory, STOP.
> - If `.gzkit/rules/` contains files OTHER than `.md` (e.g. JSON, YAML), STOP and decide per-file whether to move with — and document the decision (auxiliary content's package-data shipping is OBPI-06's responsibility).
> - If any `from gzkit.rules import X` site fails to resolve after the package conversion, STOP and add the missing re-export.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — package-layout block, file-not-dir layout for rules
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding for any file-system operations

**Context — chores precedent + sibling OBPIs:**

- [ ] OBPI-0.0.21-01 — chores physical migration precedent
- [ ] OBPI-0.0.32-01 (sibling) — same shape applied to skills
- [ ] OBPI-04 (sibling) — confirms what is OUT OF SCOPE here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/rules.py` exists at 563 lines
- [ ] 14 files under `.gzkit/rules/` (`ls .gzkit/rules/*.md | wc -l` returns 14)
- [ ] `src/gzkit/rules/` does NOT yet exist
- [ ] Git working tree clean before starting

**Existing Code:**

- [ ] Enumerate every public symbol in `src/gzkit/rules.py` before starting
- [ ] Enumerate every `from gzkit.rules import X` site in `src/` and `tests/`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #3 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: regression tests for public-symbol re-exports
- [ ] GREEN: tests pass after package conversion
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] No operator-facing surface change → no manpage update; if any doc references `src/gzkit/rules.py` as a path, update to the new package location
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios; existing scenarios that exercise rule-loading MUST continue to pass

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test ! -f src/gzkit/rules.py
test -f src/gzkit/rules/__init__.py
ls src/gzkit/rules/*.md | wc -l                                              # expect 14
python -c "from gzkit.rules import RuleFrontmatter, ClassifiedRule, load_rules, render_rules_to_dir, sync_claude_rules, sync_nested_agents_md, validate_rule_placement; print('imports OK')"
```

## Acceptance Criteria

- [ ] REQ-0.0.32-03-01: All 14 rule files moved via `git mv` from `.gzkit/rules/<slug>.md` to `src/gzkit/rules/<slug>.md`; per-file git history preserved
- [ ] REQ-0.0.32-03-02: `src/gzkit/rules.py` does not exist post-OBPI; `src/gzkit/rules/__init__.py` exists byte-equivalent (modulo docstring)
- [ ] REQ-0.0.32-03-03: Every previously-public symbol in `gzkit.rules` remains importable
- [ ] REQ-0.0.32-03-04: NO `CORE_RULES`, `scaffold_core_rules`, or `_iter_canonical_rule_slugs` exists in `src/gzkit/rules/__init__.py` after this OBPI (those are OBPI-04's scope)
- [ ] REQ-0.0.32-03-05: `src/gzkit/commands/init_cmd.py` is byte-identical to the pre-OBPI version (no integration changes here)
- [ ] REQ-0.0.32-03-06: `pyproject.toml` is byte-identical to the pre-OBPI version
- [ ] REQ-0.0.32-03-07: `uv run gz check` exits 0 after the migration

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Regression tests recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Path-reference doc updates landed; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing rule-loading scenarios still pass
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste regression-test output
```

### Code Quality

```text
# Paste lint, format, ty output
```

### Gate 3 (Docs)

```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)

```text
# Paste existing scenario regression output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: 14 canonical rule files lived only at `.gzkit/rules/`. After this OBPI: those files live at `src/gzkit/rules/<slug>.md` as Python package data, with `from gzkit.rules import X` continuing to resolve through the new `src/gzkit/rules/__init__.py`. The wheel does not yet ship them (OBPI-06) and no scaffolder yet exists (OBPI-04) — this OBPI delivers the layout, not the closure. Mirrors the chores precedent's atomic-migration discipline.

### Key Proof

```bash
ls src/gzkit/rules/*.md | wc -l
# Expected: 14
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure class A addressed by this OBPI's layout work; class A closure depends on OBPI-04 + OBPI-06 also landing

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
