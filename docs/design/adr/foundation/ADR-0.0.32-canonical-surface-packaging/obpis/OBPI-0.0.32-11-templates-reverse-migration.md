---
id: OBPI-0.0.32-11-templates-reverse-migration
parent: ADR-0.0.32-canonical-surface-packaging
item: 11
lane: Heavy
status: Completed
---

# OBPI-0.0.32-11-templates-reverse-migration: Templates Reverse-Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #11 — "Templates reverse-migration — establish dual-surface for all 13+ canonical templates by REVERSE-migrating from the current single-surface location: `git mv src/gzkit/templates/*.md .gzkit/templates/*.md` to establish `.gzkit/templates/` as the new authored canonical source-of-truth; add byte-equivalent copy back at `src/gzkit/templates/*.md` for wheel-shipping; preserve `src/gzkit/templates/__init__.py` (Python package) and any non-`.md` adjuncts; existing `render_template()` consumers continue resolving through `gzkit.templates` package; byte-parity test fails closed on drift. This is a direction reversal from skills/rules/personas migrations because templates already live at the package surface today. Scaffolder + init wiring deferred to OBPI-12; sync mechanism deferred to OBPI-08."

**Status:** Draft

## Objective

Establish the dual-surface layout for templates per ADR-0.0.32's canonical-routing model. This is a **direction reversal** from the skills/rules/personas migrations: templates currently live ONLY at `src/gzkit/templates/<name>.md` (13+ markdown files plus `__init__.py` plus a `skills/` subdir); `.gzkit/templates/` does NOT exist today. The migration steps:

1. `git mv src/gzkit/templates/<name>.md .gzkit/templates/<name>.md` for every `.md` file under `src/gzkit/templates/` so per-file git history is preserved across the relocation. `.gzkit/templates/` becomes the new authored canonical source-of-truth.
2. `cp .gzkit/templates/<name>.md src/gzkit/templates/<name>.md` to re-establish `src/gzkit/templates/<name>.md` as the byte-equivalent wheel-shipping copy.
3. Preserve `src/gzkit/templates/__init__.py` (Python package) and any non-`.md` adjuncts (e.g., the `skills/` subdir) — they stay at the package surface only; templates' canonical-content scope is the `.md` files.
4. Existing `render_template()` and `gzkit.templates` consumers continue resolving through the package's `__init__.py` (which exposes the package's data files via `importlib.resources` regardless of where the `.md` lives on disk).

The byte-parity test enforces equality between `.gzkit/templates/<name>.md` and `src/gzkit/templates/<name>.md`. Templates have no vendor-mirror leg (templates are consumed by scaffolders at init time, not exposed to agent runtime) — `.[vendor]/templates/` does NOT exist and is not in scope.

**No scaffolder authoring, no init_cmd integration, no automated sync mechanism in this OBPI** — `CORE_TEMPLATES` registry + `scaffold_core_templates` + init wiring belong to OBPI-12; the `gz agent sync control-surfaces` mechanism that propagates `.gzkit/templates/` to `src/gzkit/templates/` belongs to OBPI-08.

## Lane

**Heavy** — relocates Python package data (13+ files) from the package surface to a new authored canonical surface; establishes the dual-surface invariant for the templates surface. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/templates/<name>.md` — destination of `git mv` from `src/gzkit/templates/<name>.md` (13+ files); becomes authored canonical source-of-truth
- `src/gzkit/templates/<name>.md` — byte-equivalent copy re-established via `cp` after the `git mv`; the wheel-shipping shadow
- `src/gzkit/templates/__init__.py` — retained as-is; no logic changes
- `tests/test_templates.py` (new) — byte-parity test mirroring `tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity`; one slug-set test confirming `.gzkit/templates/` ↔ `src/gzkit/templates/` byte-equivalence
- `tests/test_render_template.py` (or equivalent, if a render-template test surface exists) — regression coverage to confirm `render_template()` and any `gzkit.templates` consumers continue resolving after the on-disk relocation

## Denied Paths

- `pyproject.toml` — wheel includes belong to OBPI-06; this OBPI moves files but does NOT extend the wheel manifest
- `src/gzkit/templates/__init__.py` (logic) — no `CORE_TEMPLATES` registry, no `scaffold_core_templates` function, no `_iter_canonical_template_slugs` enumerator added in this OBPI; OBPI-12 owns those
- `src/gzkit/commands/init_cmd.py` — no `scaffold_core_templates` invocation, no integration changes in this OBPI; OBPI-12 owns the wiring
- `src/gzkit/templates/skills/` (subdir) — if templates contains a `skills/` adjunct directory at OBPI start, it stays at the package surface only (not subject to dual-surface invariant in this OBPI; surface the question if the subdir contains canonical content that operator-edit-worthy)
- `src/gzkit/skills/**`, `src/gzkit/rules/**`, `src/gzkit/personas/**`, `src/gzkit/chores/**` — other surfaces' migrations belong to their own OBPIs
- `features/**` — no behave coverage in this OBPI
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `gz agent sync control-surfaces` extension to cover `.gzkit/templates/ → src/gzkit/templates/` — belongs to OBPI-08

## Requirements (FAIL-CLOSED)

1. `git mv src/gzkit/templates/<name>.md .gzkit/templates/<name>.md` MUST be used for every `.md` file currently under `src/gzkit/templates/` so per-file git history is preserved through the relocation. A bulk `cp + rm` is NEVER acceptable for the `git mv` step.
2. After the `git mv`, `.gzkit/templates/<name>.md` MUST contain every previously-existing template `.md` file with byte-identical content. The authored canonical surface comes into existence by this step.
3. After the `git mv`, `cp .gzkit/templates/<name>.md src/gzkit/templates/<name>.md` MUST re-establish the byte-equivalent package-surface copy. `src/gzkit/templates/<name>.md` exists again post-OBPI with byte-identical content to the `.gzkit/templates/<name>.md` source.
4. `src/gzkit/templates/__init__.py` MUST exist post-OBPI with byte-identical contents to the pre-OBPI version (no logic changes; the Python package is retained as-is so `render_template()` resolution path is unchanged).
5. `src/gzkit/templates/skills/` (subdir, if present at OBPI start) MUST be retained at the package surface as-is. If it contains operator-edit-worthy canonical content, that question is OUT of this OBPI's scope and MUST be surfaced as a follow-up GHI rather than addressed in-flight.
6. Any non-`.md` adjuncts under `src/gzkit/templates/` (e.g., `__pycache__/`) MUST NOT be relocated to `.gzkit/templates/`; they stay at the package surface.
7. A byte-parity test (`tests/test_templates.py::TestTemplatesLayoutDualSurface::test_dual_surface_byte_parity`) MUST fail closed on drift between `.gzkit/templates/<name>.md` and `src/gzkit/templates/<name>.md`.
8. NO `CORE_TEMPLATES` registry, `scaffold_core_templates` function, or `_iter_canonical_template_slugs` enumerator is permitted in this OBPI's `src/gzkit/templates/__init__.py`. Adding any of them is scope creep into OBPI-12.
9. NO wheel-include extension is permitted in this OBPI. `pyproject.toml` continues to ship existing surfaces; templates wheel-include extension belongs to OBPI-06.
10. NO `gz agent sync control-surfaces` modification is permitted. The byte-parity test is detection-only; the convenience sync that propagates `.gzkit/templates/` to `src/gzkit/templates/` belongs to OBPI-08.
11. Every `render_template()` call site (and every site that imports anything from `gzkit.templates`) MUST continue resolving after the migration. Regression tests MUST cover at least one render of a relocated template.
12. `uv run gz check` MUST exit 0 after the migration.

> STOP-on-BLOCKERS:
> - If `.gzkit/templates/` already exists as a directory, STOP and inspect — verify whether prior partial work needs to be reconciled before proceeding.
> - If `src/gzkit/templates/` contains files other than `.md`, `__init__.py`, the `skills/` subdir, and `__pycache__/`, STOP and decide per-file how to handle the additional content.
> - If `src/gzkit/templates/skills/` contains canonical operator-edit-worthy content (not stub templates / generation inputs), STOP and surface as a follow-up GHI before continuing; do not in-flight-expand scope.
> - If `render_template()` or `gzkit.templates` resolution paths use any mechanism other than `importlib.resources` (e.g., direct `Path(__file__).parent / "skill.md"`), STOP — those paths must be updated to use `importlib.resources` before the migration relocates `.md` files away from `src/gzkit/templates/`, OR the package surface must remain populated (which the dual-surface model satisfies — make sure the step ordering puts the `cp` back BEFORE any test that exercises template rendering).

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — § Canonical-routing scope (templates row)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `.claude/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding for any file-system operations

**Context — sibling OBPIs + skills/rules precedent:**

- [ ] OBPI-0.0.32-01 (attested) — the dual-surface shape; note that templates is reverse-direction (`src/gzkit/` → `.gzkit/` first)
- [ ] OBPI-0.0.32-09 (sibling) — personas physical migration; similar shape but forward direction
- [ ] `tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity` — byte-parity test pattern to replicate

**Prerequisites (check existence, STOP if missing):**

- [ ] 13+ `.md` files under `src/gzkit/templates/` (sanity check)
- [ ] `src/gzkit/templates/__init__.py` exists
- [ ] `.gzkit/templates/` does NOT yet exist
- [ ] Git working tree clean before starting

**Existing Code:**

- [ ] Enumerate every `render_template()` call site and every `from gzkit.templates import` site in `src/` and `tests/`
- [ ] Inspect `src/gzkit/templates/skills/` subdir contents to determine its disposition
- [ ] Inspect `gzkit.templates` resolution path — confirm it uses `importlib.resources` (not direct `Path(__file__).parent`)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #11 quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: byte-parity regression test + `render_template()` regression test fail before migration (or fail after partial migration if the `cp`-back step is incomplete)
- [ ] GREEN: tests pass after the `git mv` + `cp`-back step ordering completes
- [ ] Coverage above 40% floor

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] No operator-facing surface change → no manpage update required; if any doc references `src/gzkit/templates/<name>.md` as a path the operator should edit, update to `.gzkit/templates/<name>.md`
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios; existing scenarios that exercise template rendering MUST continue to pass

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test -d .gzkit/templates
test -d src/gzkit/templates
test -f src/gzkit/templates/__init__.py
ls .gzkit/templates/*.md | wc -l       # expect 13+ (authored canonical, the new home)
ls src/gzkit/templates/*.md | wc -l    # expect 13+ (byte-equivalent package copy)
diff -r .gzkit/templates/ src/gzkit/templates/ --exclude=__init__.py --exclude=__pycache__ --exclude=skills
# expect: no diff (modulo subdir + python package)
python -c "from gzkit.templates import render_template; print(render_template('adr.md', {'id':'TEST','title':'Test'})[:100])"
# expect: substantive multi-section content (NOT a one-line stub or import error)
```

## Acceptance Criteria

- [ ] REQ-0.0.32-11-01: All 13+ template `.md` files moved via `git mv` from `src/gzkit/templates/<name>.md` to `.gzkit/templates/<name>.md`; per-file git history preserved
- [ ] REQ-0.0.32-11-02: Byte-equivalent copies re-established at `src/gzkit/templates/<name>.md` post-migration; byte-parity test fails closed on drift
- [ ] REQ-0.0.32-11-03: `src/gzkit/templates/__init__.py` is byte-identical to the pre-OBPI version (Python package retained as-is)
- [ ] REQ-0.0.32-11-04: `src/gzkit/templates/skills/` subdir (if present) is retained at the package surface; its disposition is in scope only as STOP-on-BLOCKER inspection
- [ ] REQ-0.0.32-11-05: `render_template()` and `gzkit.templates` import sites continue resolving post-migration; at least one regression test exercises a real template render
- [ ] REQ-0.0.32-11-06: NO `CORE_TEMPLATES`, `scaffold_core_templates`, or `_iter_canonical_template_slugs` exists in `src/gzkit/templates/__init__.py` post-OBPI
- [ ] REQ-0.0.32-11-07: `src/gzkit/commands/init_cmd.py` is byte-identical to the pre-OBPI version (no integration changes here)
- [ ] REQ-0.0.32-11-08: `pyproject.toml` is byte-identical to the pre-OBPI version (no wheel-include extension)
- [ ] REQ-0.0.32-11-09: `gz agent sync control-surfaces` is byte-identical to the pre-OBPI version (sync mechanism is OBPI-08's scope)
- [ ] REQ-0.0.32-11-10: `uv run gz check` exits 0 after the migration

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Byte-parity + render-template regression tests recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Path-reference doc updates landed; mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing render-template scenarios still pass
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste byte-parity + render-template regression test output
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
# Paste regression scenario output
```

### Gate 5 (Human)

```text
# Record attestation text + ATTEST confirmation
```

### Value Narrative

Before this OBPI: 13+ canonical template files lived only at `src/gzkit/templates/<name>.md` (the package surface). Operators could not edit templates at the natural authoring location (`.gzkit/templates/`) because that directory didn't exist; any template edit required reaching into `src/gzkit/templates/` (a package-internal surface). After this OBPI: those template files live at `.gzkit/templates/<name>.md` as the authored canonical source-of-truth (where operators naturally edit) AND a byte-identical copy lives at `src/gzkit/templates/<name>.md` as the package surface (precondition for OBPI-06 wheel includes and OBPI-12 scaffolder authoring). `render_template()` and every `gzkit.templates` consumer continues resolving through the package's `__init__.py`. The byte-parity test fails closed if the two surfaces drift.

This is a direction-reversal from skills/rules/personas migrations — those started with `.gzkit/<surface>/` populated and added `src/gzkit/<surface>/` as the byte-equivalent copy; templates start with `src/gzkit/templates/` populated and ADD `.gzkit/templates/` as the new authored canonical. The endpoint is the same dual-surface invariant.

### Key Proof


```bash
$ ls .gzkit/templates/*.md | wc -l && ls src/gzkit/templates/*.md | wc -l
11
11

$ diff -r .gzkit/templates/ src/gzkit/templates/ --exclude=__init__.py --exclude=__pycache__ --exclude=skills
# (zero output — byte-parity holds across all 11 .md files)

$ uv run gz covers OBPI-0.0.32-11-templates-reverse-migration --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['summary'])"
# {'identifier': 'OBPI-0.0.32-11-templates-reverse-migration', 'total_reqs': 10, 'covered_reqs': 10, 'uncovered_reqs': 0, 'coverage_percent': 100.0}

$ uv run python -c "from gzkit.templates import render_template; print(render_template('adr', id='TEST', title='Test')[:80])"
---
id: TEST
status: Draft
kind: {kind}
semver: {semver}
lane: lite
parent: {parent}
date: 2026-05-12
---

# TEST: Test

$ uv run gz arb ruff
arb ruff exit_status=0 receipt=/Users/jeff/Documents/Code/gzkit/artifacts/receipts/arb-ruff-9649c7ef0074409c9fd5ed0fa1ed3e56.json

$ uv run gz arb typecheck
arb step name=typecheck exit_status=0 receipt=/Users/jeff/Documents/Code/gzkit/artifacts/receipts/arb-step-typecheck-55fcfa0b0a384625abfda8a65248577b.json

$ uv run gz arb step --name unittest -- uv run -m unittest -q
Ran 4833 tests in 41.893s
OK (skipped=1)
arb step name=unittest exit_status=0 receipt=/Users/jeff/Documents/Code/gzkit/artifacts/receipts/arb-step-unittest-fa86d3be431546e28b428fe50fad789a.json

$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
INFO    -  Documentation built in 2.43 seconds
arb step name=mkdocs exit_status=0 receipt=/Users/jeff/Documents/Code/gzkit/artifacts/receipts/arb-step-mkdocs-fefc00669d14493a8db202d8761db1ac.json
```

### Implementation Summary


- **ADR § Decision item implemented:** ADR-0.0.32 checklist #11 — "Templates reverse-migration — establish dual-surface for all 13+ canonical templates by REVERSE-migrating from the current single-surface location: `git mv src/gzkit/templates/*.md .gzkit/templates/*.md` to establish `.gzkit/templates/` as the new authored canonical source-of-truth; add byte-equivalent copy back at `src/gzkit/templates/*.md` for wheel-shipping; preserve `src/gzkit/templates/__init__.py` (Python package) and any non-`.md` adjuncts; existing `render_template()` consumers continue resolving through `gzkit.templates` package; byte-parity test fails closed on drift. This is a direction reversal from skills/rules/personas migrations because templates already live at the package surface today. Scaffolder + init wiring deferred to OBPI-12; sync mechanism deferred to OBPI-08."
- **Files migrated:** 11 `.md` template files moved via `git mv` from `src/gzkit/templates/` to `.gzkit/templates/` (per-file git history preserved): `adr_pool.md`, `adr.md`, `agents.md`, `audit_plan.md`, `audit.md`, `claude.md`, `closeout.md`, `constitution.md`, `copilot.md`, `obpi.md`, `prd.md`. Brief said "13+"; actual count is 11.
- **Files re-established:** Same 11 `.md` files at `src/gzkit/templates/<name>.md` via `cp` (byte-equivalent package-surface copies for wheel-shipping).
- **Files untouched (by design):** `src/gzkit/templates/__init__.py` byte-identical to pre-OBPI; `src/gzkit/templates/skills/` retained at package surface; `pyproject.toml`, `src/gzkit/sync_surfaces.py`, `src/gzkit/commands/init_cmd.py` unchanged.
- **Tests added:** `TestTemplatesLayoutDualSurface` class in `tests/test_templates.py` with 8 tests covering all 10 REQs via `@covers` decorators (1 byte-parity, 1 authored-surface-populated, 1 init.py API preserved, 1 skills/ subdir retained, 1 no-scope-creep (subTests on 3 forbidden names), 1 pyproject no extension, 1 sync_surfaces no extension, 1 all-templates-loadable smoke); `@covers("REQ-0.0.32-11-05")` added to existing `TestRenderTemplate.test_render_substitutes_values`. Total: 9 REQ-decorated tests in test_templates.py post-OBPI.
- **Waiver:** `data/behave_coverage_waivers.json` entry under shared rationale `adr-0.0.32-bdd-deferred-to-obpi-06` (BDD coverage routed to OBPI-0.0.32-06 T0 smoke test, same precedent as OBPI-01/02/03/09).
- **Date completed:** 2026-05-12
- **Attestation status:** Operator attested "attest completed" at Stage 4 ceremony; relayed via `--attestor-present` per Stage 5 primary path (pipeline marker satisfies co-presence proxy).
- **Defects noted:** Course-correction `improvement` record appended to `.gzkit/insights/agent-insights.jsonl` (bare `python` invocation in a `uv` project, immediately corrected). The malformed schema (used `timestamp` instead of `ts`, string `evidence` instead of list) was caught by `tests/governance/test_promoted_advisory_audits.py::test_insights_shape_ghi_358` during Stage 3 — fixed in place; insights record now schema-valid.

## Tracked Defects

- (none at authoring time)

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Operator (g0) attested at Stage 4 ceremony after reviewing the full evidence pack: dual-surface layout established (11 `.md` files at `.gzkit/templates/` authored canonical + byte-identical copies at `src/gzkit/templates/` for wheel-shipping; `diff -r` exits zero modulo `__init__.py`/`__pycache__`/`skills/`), REQ coverage 10/10 via `gz covers` (TestTemplatesLayoutDualSurface 8 tests + TestRenderTemplate.test_render_substitutes_values), ARB receipts arb-ruff-9649c7ef0074409c9fd5ed0fa1ed3e56 (lint clean), arb-step-typecheck-55fcfa0b0a384625abfda8a65248577b (ty clean), arb-step-unittest-fa86d3be431546e28b428fe50fad789a (4833/4833 pass, 1 skipped), arb-step-mkdocs-fefc00669d14493a8db202d8761db1ac (docs strict clean). Foundation-kind + heavy-lane brief-level Gate 5 satisfied per § Lane & Kind Attestation Matrix.
- Date: 2026-05-12

---

**Brief Status:** Completed

**Date Completed:** 2026-05-12

**Evidence Hash:** -
