---
id: OBPI-0.0.32-01-skills-physical-migration
parent: ADR-0.0.32-canonical-surface-packaging
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.32-01-skills-physical-migration: Skills Physical Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #1 — "Skills physical migration — `git mv .gzkit/skills/<slug>/SKILL.md src/gzkit/skills/<slug>/SKILL.md` for all 61 canonical skills; convert `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` preserving every public symbol re-export. Scaffolder refactor explicitly deferred to OBPI-02."

**Status:** Draft

## Objective

Move 61 hand-authored canonical SKILL.md files from `.gzkit/skills/<slug>/` into `src/gzkit/skills/<slug>/SKILL.md` via `git mv` (preserving per-file history). Convert the existing `src/gzkit/skills.py` module (438 lines) into `src/gzkit/skills/__init__.py` so every `from gzkit.skills import X` import site continues to resolve. **No scaffolder refactor in this OBPI** — `scaffold_core_skills` continues to render through `templates/skill.md` after this OBPI lands; OBPI-02 is the brief that refactors it to copy from package canonical content. This OBPI is the chores precedent's OBPI-0.0.21-01 shape: physical migration as its own atomic unit, separate from the resolver/scaffolder semantics that depend on it.

## Lane

**Heavy** — restructures Python package layout (module → package conversion). Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/skills.py` — convert to package; delete the file after content moves
- `src/gzkit/skills/__init__.py` — receives the contents of the former `src/gzkit/skills.py` byte-equivalent (no logic changes; only re-export preservation)
- `src/gzkit/skills/<slug>/SKILL.md` — destination of `git mv` from `.gzkit/skills/<slug>/SKILL.md` (61 files)
- `.gzkit/skills/<slug>/SKILL.md` — source of `git mv`
- `tests/test_skills.py`, `tests/commands/test_init.py` — minimal additions (one regression test per public-symbol re-export to confirm imports still resolve post-package-conversion)

## Denied Paths

- `pyproject.toml` — wheel includes belong to OBPI-06; this OBPI moves files but does NOT extend the wheel manifest
- `src/gzkit/templates/skill.md` — deletion belongs to OBPI-02 (after the scaffolder no longer references it)
- `src/gzkit/rules.py`, `src/gzkit/rules/**` — rules belong to OBPI-03 / -04
- `src/gzkit/commands/init_cmd.py` — no init wiring changes in this OBPI
- `src/gzkit/hooks/**`, `src/gzkit/personas/**`, `src/gzkit/templates/*.md` (other than `skill.md`) — out of scope
- `features/**` — no behave coverage in this OBPI; smoke test belongs to OBPI-06
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/skills/`, `.github/skills/` — mirror regen belongs to OBPI-08
- Any change to `scaffold_core_skills` body, `_SKILL_TEMPLATE`, or scaffolder templating logic — that is OBPI-02's surface
- `docs/governance/trust-doctrine.md` — T0 doctrine belongs to ADR-0.0.31

## Requirements (FAIL-CLOSED)

1. `git mv .gzkit/skills/<slug>/SKILL.md src/gzkit/skills/<slug>/SKILL.md` MUST be used for every one of the 61 canonical skills so per-file git history is preserved. A bulk `cp` + `rm` is NEVER acceptable.
2. After the moves, `src/gzkit/skills/<slug>/SKILL.md` MUST be byte-identical to the pre-move `.gzkit/skills/<slug>/SKILL.md`. No content edits.
3. `src/gzkit/skills.py` MUST NOT exist after this OBPI. Its contents MUST move to `src/gzkit/skills/__init__.py` such that every `from gzkit.skills import X` import site in `src/` and `tests/` continues to resolve without modification.
4. `src/gzkit/skills/__init__.py` MUST be byte-equivalent to the prior `src/gzkit/skills.py` contents — no new functions, no removed functions, no signature changes. The single permitted edit is module-docstring text-only updates that reflect the new package location (if any).
5. `from gzkit.skills_audit import …` import sites MUST continue to work; the audit module is a sibling under `src/gzkit/`, not a child of the new package.
6. `uv run gz check` MUST exit 0 after the migration lands — same lint, type, test, and format state as before, just with a different on-disk layout.
7. NO scaffolder logic change is permitted. `scaffold_core_skills` continues to call `render_template("skill.md", ...)` exactly as today; the stub-template path remains in place until OBPI-02 refactors it.
8. NO wheel-include extension is permitted. `pyproject.toml [tool.hatch.build.targets.wheel] include:` continues to ship chores-only after this OBPI; the wheel does not yet contain skills package data. OBPI-06 owns that extension. Until OBPI-06 lands, the migration achieves the layout but not the T0 closure — that is the expected intermediate state.
9. Regression tests MUST cover: `from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills, SkillAuditIssue, _parse_frontmatter, DEFAULT_MAX_REVIEW_AGE_DAYS, list_skills, scaffold_skill` (every previously-public symbol enumerated by `grep -n "^def \|^class \|^[A-Z_]* = " src/gzkit/skills.py` BEFORE this OBPI starts).

> STOP-on-BLOCKERS:
> - If `git mv` reports a name collision (a `src/gzkit/skills/<slug>/` already exists), STOP.
> - If any `.gzkit/skills/<slug>/` contains files OTHER than `SKILL.md` (e.g. `assets/`, `examples/`), STOP and decide per-slug whether the auxiliary content moves with — and document the decision in this OBPI's evidence (auxiliary content's package-data shipping is OBPI-06's responsibility, not this OBPI's).
> - If any `from gzkit.skills import X` site fails to resolve after the package conversion, STOP and add the missing re-export in `__init__.py` before continuing.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — package-layout block, two-surface layout
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding for any file-system operations

**Context — chores precedent:**

- [ ] `src/gzkit/chores/__init__.py` — confirms the package-with-__init__.py + per-slug-subdirs layout
- [ ] OBPI-0.0.21-01-physical-migration — the canonical "physical migration is its own OBPI" precedent
- [ ] Sibling OBPI-02 (skills scaffolder refactor) — confirms what is OUT OF SCOPE here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/skills.py` exists at 438 lines (sanity check)
- [ ] 61 directories under `.gzkit/skills/` each containing `SKILL.md`
- [ ] `src/gzkit/skills/` does NOT yet exist
- [ ] Git working tree clean before starting

**Existing Code:**

- [ ] Enumerate every public symbol in `src/gzkit/skills.py` before starting (so the regression test list is complete)
- [ ] Enumerate every `from gzkit.skills import X` site in `src/` and `tests/`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #1 quoted verbatim above

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: regression tests for public-symbol imports written first against the package conversion (will pass trivially as long as conversion preserves the symbols)
- [ ] GREEN: tests pass after package conversion
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] No operator-facing surface change → no manpage update needed; if any doc references `src/gzkit/skills.py` as a path, update to the new package location
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios in this OBPI; existing scenarios that exercise `gz init` MUST continue to pass with the post-migration layout (regression-only signal)

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test ! -f src/gzkit/skills.py
test -f src/gzkit/skills/__init__.py
ls src/gzkit/skills/ | grep -v __init__.py | grep -v __pycache__ | wc -l    # expect 61
find src/gzkit/skills/ -name SKILL.md | wc -l                               # expect 61
python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills, SkillAuditIssue, _parse_frontmatter, DEFAULT_MAX_REVIEW_AGE_DAYS, list_skills, scaffold_skill; print('imports OK')"
```

## Acceptance Criteria

- [ ] REQ-0.0.32-01-01: All 61 SKILL.md files moved via `git mv` from `.gzkit/skills/<slug>/SKILL.md` to `src/gzkit/skills/<slug>/SKILL.md`; per-file git history preserved
- [ ] REQ-0.0.32-01-02: `src/gzkit/skills.py` does not exist post-OBPI; `src/gzkit/skills/__init__.py` exists with byte-equivalent (modulo docstring) contents
- [ ] REQ-0.0.32-01-03: Every public symbol previously importable from `gzkit.skills` remains importable; regression test enumerates the full set
- [ ] REQ-0.0.32-01-04: `from gzkit.skills_audit import ...` import sites continue to resolve
- [ ] REQ-0.0.32-01-05: `scaffold_core_skills` body is byte-identical to the pre-OBPI version (no scaffolder logic change in this OBPI)
- [ ] REQ-0.0.32-01-06: `pyproject.toml` is byte-identical to the pre-OBPI version (no wheel-include extension in this OBPI)
- [ ] REQ-0.0.32-01-07: `src/gzkit/templates/skill.md` continues to exist (its deletion is OBPI-02's responsibility)
- [ ] REQ-0.0.32-01-08: `uv run gz check` exits 0 after the migration

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Regression tests for public-symbol re-exports recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Path-reference doc updates landed; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing init-related scenarios still pass (regression signal)
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste regression-test output (import-resolution checks)
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

Before this OBPI: 61 hand-authored canonical SKILL.md files lived only at `.gzkit/skills/<slug>/`. After this OBPI: those files live at `src/gzkit/skills/<slug>/SKILL.md` as a Python package, with `from gzkit.skills import X` continuing to resolve through the new `src/gzkit/skills/__init__.py`. The wheel does not yet ship them (that is OBPI-06) and the scaffolder does not yet copy them (that is OBPI-02) — this OBPI delivers the layout, not the closure. Each subsequent OBPI in this ADR depends on the layout being right, which is why the chores precedent kept physical migration as its own atomic unit.

### Key Proof

```bash
ls src/gzkit/skills/ | grep -v __init__.py | grep -v __pycache__ | wc -l
# Expected: 61
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #318 — failure class B addressed by this OBPI's layout work; class B closure depends on OBPI-02 + OBPI-06 also landing

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
