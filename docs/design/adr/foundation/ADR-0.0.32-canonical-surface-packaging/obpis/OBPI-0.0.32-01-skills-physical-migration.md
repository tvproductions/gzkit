---
id: OBPI-0.0.32-01-skills-physical-migration
parent: ADR-0.0.32-canonical-surface-packaging
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.32-01-skills-physical-migration: Skills Physical Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #1 — "Skills physical migration — `git mv .gzkit/skills/<slug>/SKILL.md src/gzkit/skills/<slug>/SKILL.md` for all 61 canonical skills; convert `src/gzkit/skills.py` → `src/gzkit/skills/__init__.py` preserving every public symbol re-export. Scaffolder refactor explicitly deferred to OBPI-02."

**Status:** Draft

## Objective

Establish the dual-surface layout for skills: keep the 70 hand-authored canonical SKILL.md files in place at `.gzkit/skills/<slug>/SKILL.md` (the authored source of truth) and add a byte-identical copy at `src/gzkit/skills/<slug>/SKILL.md` (the surface that ships in the wheel). Convert the existing `src/gzkit/skills.py` module (479 lines) into `src/gzkit/skills/__init__.py` so every `from gzkit.skills import X` import site continues to resolve. **No scaffolder refactor in this OBPI** — `scaffold_core_skills` continues to render through `templates/skill.md` after this OBPI lands; OBPI-02 is the brief that refactors it to copy from package canonical content. **No sync-mechanism enforcement in this OBPI** — dev-time sync `.gzkit/ → src/gzkit/` is tracked as GHI #449.

<!-- gz-validate-skip: command-shape -->
**No adopter-side refresh in this OBPI** — `gz upgrade` is tracked as GHI #450.

**Course correction (2026-05-11):** Brief originally specified `git mv` and "moved" semantics, but the correct model under ADR-0.0.32 is dual-surface (authored at `.gzkit/`, copied to `src/gzkit/` for wheel shipping). Operator clarified mid-implementation: "the truest canonical source, for everything, is `.gzkit/`." REQ-01 wording amended accordingly. Insights record at `.gzkit/insights/agent-insights.jsonl` (2026-05-11T08:55:00Z).

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

1. `.gzkit/skills/<slug>/SKILL.md` MUST remain in place as the authored canonical source of truth for every skill (~70 files at OBPI execution time). A byte-identical copy MUST be added at `src/gzkit/skills/<slug>/SKILL.md`. The authored surface is never deleted; the package surface is added alongside.
2. `src/gzkit/skills/<slug>/SKILL.md` MUST be byte-identical to `.gzkit/skills/<slug>/SKILL.md`. No content edits in either surface. A byte-parity test (`tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity`) MUST fail closed on drift.
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

- [ ] REQ-0.0.32-01-01: Dual-surface layout established — `.gzkit/skills/<slug>/SKILL.md` retained as authored canonical source (~70 files); byte-identical copy added at `src/gzkit/skills/<slug>/SKILL.md`. Byte-parity test `tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity` fails closed on drift
- [ ] REQ-0.0.32-01-02: `src/gzkit/skills.py` does not exist post-OBPI; `src/gzkit/skills/__init__.py` exists with byte-equivalent (modulo docstring) contents; package surface SKILL.md files are byte-identical to authored source
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

Before this OBPI: 70 hand-authored canonical SKILL.md files lived only at `.gzkit/skills/<slug>/SKILL.md`, with no presence in the Python package — the wheel could not ship them, and the canonical content was unreachable from `importlib.resources`. After this OBPI: those 70 files remain at `.gzkit/skills/<slug>/SKILL.md` as the **authored canonical source of truth** AND a byte-identical copy lives at `src/gzkit/skills/<slug>/SKILL.md` as the **package surface** (precondition for OBPI-06 wheel includes). `src/gzkit/skills.py` is converted to `src/gzkit/skills/__init__.py` so every `from gzkit.skills import X` import site continues to resolve. The byte-parity test (`test_dual_surface_byte_parity`) fails closed if the two surfaces drift.

Sync invariants now in place (mechanical or upcoming):

- `.gzkit/skills/ ↔ src/gzkit/skills/` — byte-parity test fails closed on drift (this OBPI). Convenience sync mechanism deferred to GHI #449.
- `.gzkit/skills/ → .[vendor]/skills/` — existing `gz agent sync control-surfaces` (unchanged).
<!-- gz-validate-skip: command-shape -->
- `src/gzkit/skills/ → adopter's .gzkit/skills/` — deferred to GHI #450 (`gz upgrade` adopter subcommand).

The wheel does not yet ship the package surface (OBPI-06), the scaffolder does not yet copy from `importlib.resources` (OBPI-02), and the mirrors are not yet regenerated from the new surface (OBPI-08). This OBPI delivers the dual-surface layout, not the T0 closure. Each subsequent OBPI in this ADR depends on the layout being right.

### Key Proof


Dual-surface layout established and byte-parity guard in place:

```bash
$ find .gzkit/skills/ -name SKILL.md | wc -l       # 70 authored
$ find src/gzkit/skills/ -name SKILL.md | wc -l    # 70 package copy
$ uv run -m unittest tests.test_skills -v          # 26/26 pass
```

Full quality gates green (ARB receipts):
- arb-ruff-abda11a07b154a2c9e07d55c72c6d930 (lint clean)
- arb-step-typecheck-db038e775abd4331821873d815741764 (typecheck clean)
- arb-step-unittest-ffde8346d9964d06bb99dd75e41248e7 (4790/4790 pass)
- arb-step-mkdocs-0f77fc27fab6418cb2d80e9f33110ed1 (docs build clean)

REQ coverage: 8/8 covered (verified by `uv run gz covers OBPI-0.0.32-01-skills-physical-migration --json`).

Byte-parity gate: `tests.test_skills.TestSkillsLayoutDualSurface.test_dual_surface_byte_parity` fails closed on any drift between `.gzkit/skills/<slug>/SKILL.md` and `src/gzkit/skills/<slug>/SKILL.md` (read_bytes comparison across all 70 slugs).

Imports continuous post-conversion:

```bash
$ uv run python -c "from gzkit.skills import CORE_SKILLS, scaffold_core_skills, audit_skills, SkillAuditIssue, _parse_frontmatter, DEFAULT_MAX_REVIEW_AGE_DAYS, list_skills, scaffold_skill, Skill, get_skill, SkillAuditReport; print('imports OK')"
imports OK
```

### Implementation Summary


- Dual-surface layout established: .gzkit/skills/<slug>/SKILL.md (70 files, authored canonical source, retained) plus src/gzkit/skills/<slug>/SKILL.md (70 byte-identical copies for wheel shipping). src/gzkit/skills.py converted to src/gzkit/skills/__init__.py via git mv; every `from gzkit.skills import X` site continues to resolve.
- Course correction (2026-05-11): Brief originally specified git mv semantics that removed SKILL.md from .gzkit/. Operator clarified "the truest canonical source, for everything, is .gzkit/". Reversed via git mv back + cp; REQ-1/-2 wording amended; insights record appended at .gzkit/insights/agent-insights.jsonl (2026-05-11T08:55:00Z).
- Scope expansion (REQ-8 compliance, AGENTS.md PRIME DIRECTIVE 4): 2 files outside the original allowed-paths list updated for the layout change — tests/policy/test_naming_conventions.py (added src/gzkit/skills carve-out) and tests/test_skill_naming.py (added src/gzkit/skills root + __pycache__ filter). 9 files were temporarily patched during initial implementation; 7 were reverted after the operator's course correction restored .gzkit/skills/ as authoritative.
- Out-of-scope deferrals filed: GHI #449 (.gzkit/ -> src/gzkit/ dev-time sync mechanism — parity test is detection-only; convenience sync step is missing) and GHI #450 (gz upgrade adopter subcommand — depends on OBPI-0.0.32-06 wheel includes + OBPI-0.0.32-02 scaffolder refactor).
- 26 REQ-derived regression tests added at tests/test_skills.py covering all 8 REQs via @covers decorators including dual-surface byte-parity gate (TestSkillsLayoutDualSurface.test_dual_surface_byte_parity).
- Behave coverage waiver added (data/behave_coverage_waivers.json): adr-0.0.32-bdd-deferred-to-obpi-06 — BDD coverage routed to OBPI-0.0.32-06 (T0 smoke test); OBPI-01 is layout-only verified via Python unit tests.
- Files created: 72 (src/gzkit/skills/__init__.py + 70 src/gzkit/skills/<slug>/SKILL.md + tests/test_skills.py).
- Files modified: 5 (test_naming_conventions, test_skill_naming, brief, insights, behave_coverage_waivers).
- Files deleted: 1 (src/gzkit/skills.py — converted to __init__.py).
- Date completed: 2026-05-11.
- Attestation status: attest completed — operator attested with explicit phrase after Stage 4 evidence presented.
- Defects noted: none beyond the course-correction (documented in insights record) and the two filed follow-up GHIs.

## Tracked Defects

- GHI #318 — failure class B addressed by this OBPI's layout work; class B closure depends on OBPI-02 + OBPI-06 also landing

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — dual-surface layout established for 70 canonical SKILL.md files: .gzkit/skills/<slug>/SKILL.md retained as authored source of truth, byte-identical copy added at src/gzkit/skills/<slug>/SKILL.md as wheel-shipping surface, src/gzkit/skills.py converted to src/gzkit/skills/__init__.py via git mv preserving all 10 __all__ symbols. 4790/4790 tests pass (26 new regression tests covering all 8 REQs at tests/test_skills.py); ARB receipts: arb-ruff-abda11a07b154a2c9e07d55c72c6d930, arb-step-typecheck-db038e775abd4331821873d815741764, arb-step-unittest-ffde8346d9964d06bb99dd75e41248e7, arb-step-mkdocs-0f77fc27fab6418cb2d80e9f33110ed1. Course correction (operator: "the truest canonical source, for everything, is .gzkit/") reversed initial git mv removal and added cp-based dual surface; insights record at .gzkit/insights/agent-insights.jsonl (2026-05-11T08:55:00Z). Out-of-scope deferrals filed as GHI #449 (.gzkit -> src/gzkit dev-time sync mechanism) and GHI #450 (gz upgrade adopter subcommand). Byte-parity test test_dual_surface_byte_parity gates drift fail-closed.
- Date: 2026-05-11

---

**Brief Status:** Completed

**Date Completed:** 2026-05-11

**Evidence Hash:** -
