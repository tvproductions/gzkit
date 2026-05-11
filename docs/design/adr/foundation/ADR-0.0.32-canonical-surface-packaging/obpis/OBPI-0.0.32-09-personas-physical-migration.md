---
id: OBPI-0.0.32-09-personas-physical-migration
parent: ADR-0.0.32-canonical-surface-packaging
item: 9
lane: Heavy
status: Draft
---

# OBPI-0.0.32-09-personas-physical-migration: Personas Physical Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`
- **Checklist Item:** #9 — "Personas physical migration — establish dual-surface for all 6 canonical personas: retain `.gzkit/personas/<slug>.md` as authored source-of-truth AND add byte-equivalent copy at `src/gzkit/personas/<slug>.md` for wheel-shipping; create `src/gzkit/personas/__init__.py` if needed for package discovery; byte-parity test fails closed on drift. Vendor mirrors at `.claude/personas/`, `.github/personas/`, `.agents/personas/` remain a transformed shape — that transformation is intentional and OUT of the byte-parity invariant for vendor mirrors. Scaffolder + init wiring deferred to OBPI-10; sync mechanism deferred to OBPI-08."

**Status:** Draft

## Objective

Establish the dual-surface layout for personas per ADR-0.0.32's canonical-routing model: keep the 6 hand-authored canonical persona files in place at `.gzkit/personas/<slug>.md` (the authored source-of-truth) AND add a byte-identical copy at `src/gzkit/personas/<slug>.md` (the surface that ships in the wheel). Create `src/gzkit/personas/__init__.py` as a thin package marker (no public-symbol API surface today; personas are data, not library API) so the package can be enumerated via `importlib.resources.files("gzkit.personas")` after OBPI-06's wheel-include extension lands. The authored `.gzkit/personas/` surface is **never deleted** — agents and operators continue to edit there, and the byte-parity test enforces equality between the two surfaces.

Vendor mirrors at `.claude/personas/<slug>.md`, `.github/personas/<slug>.md`, and `.agents/personas/<slug>.md` already exist and are a **transformed render** of `.gzkit/personas/<slug>.md` — they expose a vendor-specific trimmed shape rather than a byte-equivalent copy. That transformation is intentional and OUT of this OBPI's byte-parity scope. OBPI-08's `gz agent sync control-surfaces` continues to regenerate vendor-mirror renders from `.gzkit/personas/` as canonical source; the byte-parity test in this OBPI binds only `.gzkit/personas/` ↔ `src/gzkit/personas/`, not the vendor-render leg.

**No scaffolder authoring, no init_cmd integration, no automated sync mechanism in this OBPI** — `CORE_PERSONAS` registry + `scaffold_core_personas` + init wiring belong to OBPI-10; the `gz agent sync control-surfaces` mechanism that propagates `.gzkit/personas/` to `src/gzkit/personas/` AND vendor renders belongs to OBPI-08.

## Lane

**Heavy** — restructures Python package layout (adds new `src/gzkit/personas/` package) and establishes the dual-surface invariant for the personas surface. Per § Lane & Kind Attestation Matrix, foundation-kind + heavy lane requires brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/personas/__init__.py` — new thin package marker (empty module docstring + nothing else; personas are data-only)
- `src/gzkit/personas/<slug>.md` — destination byte-equivalent copy of `.gzkit/personas/<slug>.md` (6 files); created via `cp`, NOT `git mv`
- `.gzkit/personas/<slug>.md` — authored canonical source-of-truth (retained; never deleted by this OBPI)
- `tests/test_personas.py` (new) — byte-parity test mirroring `tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity`; one slug-set test confirming `.gzkit/personas/` ↔ `src/gzkit/personas/` byte-equivalence

## Denied Paths

- `pyproject.toml` — wheel includes belong to OBPI-06; this OBPI adds the dual-surface copy but does NOT extend the wheel manifest
- `src/gzkit/personas/__init__.py` (logic) — no `CORE_PERSONAS` registry, no `scaffold_core_personas` function, no `_iter_canonical_persona_slugs` enumerator added in this OBPI; OBPI-10 owns those
- `src/gzkit/commands/init_cmd.py` — no `scaffold_core_personas` invocation, no integration changes in this OBPI; OBPI-10 owns the wiring
- `src/gzkit/skills/**`, `src/gzkit/rules/**`, `src/gzkit/templates/**`, `src/gzkit/chores/**` — out of scope
- `features/**` — no behave coverage in this OBPI
- `src/gzkit/governance/trust_audits.py` — `gz validate --distribution` belongs to OBPI-07
- `.claude/personas/`, `.github/personas/`, `.agents/personas/` — vendor renders belong to OBPI-08 (and remain transformed, not byte-equivalent)
- `gz agent sync control-surfaces` extension to cover `.gzkit/personas/ → src/gzkit/personas/` — belongs to OBPI-08
- `docs/governance/trust-doctrine.md` — T0 doctrine belongs to ADR-0.0.31

## Requirements (FAIL-CLOSED)

1. `.gzkit/personas/<slug>.md` MUST remain in place as the authored canonical source-of-truth for every persona (6 files: implementer, main-session, narrator, pipeline-orchestrator, quality-reviewer, spec-reviewer). A byte-identical copy MUST be added at `src/gzkit/personas/<slug>.md`. The authored surface is never deleted; the package surface is added alongside.
2. `src/gzkit/personas/<slug>.md` MUST be byte-identical to `.gzkit/personas/<slug>.md`. No content edits in either surface. A byte-parity test (`tests/test_personas.py::TestPersonasLayoutDualSurface::test_dual_surface_byte_parity`) MUST fail closed on drift.
3. `src/gzkit/personas/__init__.py` MUST be created as a thin package marker. Empty module docstring is acceptable; NO public-symbol API surface is permitted (personas are data, not library).
4. NO `CORE_PERSONAS` registry, `scaffold_core_personas` function, or `_iter_canonical_persona_slugs` enumerator is permitted in this OBPI's `__init__.py`. Adding any of them is scope creep into OBPI-10.
5. NO wheel-include extension is permitted. `pyproject.toml` continues to ship the existing surfaces (skills package data per OBPI-01) after this OBPI; personas wheel-include extension belongs to OBPI-06.
6. NO `gz agent sync control-surfaces` modification is permitted. The byte-parity test in this OBPI is detection-only; the convenience sync that propagates `.gzkit/personas/` to `src/gzkit/personas/` belongs to OBPI-08.
7. Vendor mirrors at `.claude/personas/`, `.github/personas/`, `.agents/personas/` MUST NOT be modified by this OBPI — they remain whatever transformed shape `gz agent sync control-surfaces` currently produces. Their relationship to `.gzkit/personas/` is a transformed render, not a byte-equivalent copy, and is OUT of this OBPI's byte-parity invariant.
8. `uv run gz check` MUST exit 0 after the migration.

> STOP-on-BLOCKERS:
> - If `src/gzkit/personas/` already exists as a directory, STOP and inspect — verify whether prior partial work needs to be reconciled before proceeding.
> - If `.gzkit/personas/` contains files OTHER than the 6 expected `.md` files (e.g., an auxiliary directory), STOP and decide per-file whether to copy alongside.
> - If a `from gzkit.personas import X` site appears anywhere in `src/` or `tests/` (none should exist today, but check), STOP — personas were not previously a package; if any code attempts to import from a future `gzkit.personas` package, the symbol must be defined and `_iter_canonical_persona_slugs` is the proper home, but that belongs to OBPI-10.
> - If the briefly-intended `git mv` semantics are about to remove files from `.gzkit/personas/`, STOP — the canonical-routing model requires retention at `.gzkit/` (see OBPI-01's 2026-05-11 course-correction insights record).

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Decision — § Canonical-routing scope table (personas row)
- [ ] Parent ADR § Decision — § Named exceptions (vendor-mirror render shape is intentional for personas)
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Lane & Kind Attestation Matrix
- [ ] `AGENTS.md` § Persona (the persona table cited there names the 6 slugs this OBPI must preserve)
- [ ] `.claude/rules/cross-platform.md` — `pathlib.Path`, UTF-8 encoding for file-system operations

**Context — sibling OBPIs + skills precedent:**

- [ ] OBPI-0.0.32-01 (attested) — the dual-surface shape this OBPI mirrors for personas
- [ ] `tests/test_skills.py::TestSkillsLayoutDualSurface::test_dual_surface_byte_parity` — the byte-parity test pattern this OBPI replicates
- [ ] OBPI-0.0.32-10 (sibling) — confirms what is OUT OF SCOPE here

**Prerequisites (check existence, STOP if missing):**

- [ ] 6 `.md` files under `.gzkit/personas/` (sanity check)
- [ ] `src/gzkit/personas/` does NOT yet exist
- [ ] Git working tree clean before starting

**Existing Code:**

- [ ] Verify no `from gzkit.personas import X` references exist anywhere in `src/`, `tests/`, or `features/`
- [ ] Inspect `.claude/personas/<slug>.md` and `.gzkit/personas/<slug>.md` for the SAME slug to confirm vendor mirrors are a transformed render (not byte-equivalent) — this fact is what justifies the carve-out

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR checklist item #9 quoted verbatim above

### Gate 2: TDD (Red-Green-Refactor)

- [ ] RED: byte-parity regression test fails before the package surface is populated
- [ ] GREEN: test passes after the 6 file copies and the `__init__.py` marker land
- [ ] Coverage above 40% floor

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] No operator-facing surface change → no manpage update required; if any doc references `src/gzkit/personas/` as a non-existent path, update accordingly
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy)

- [ ] No new behave scenarios; existing scenarios that exercise persona discovery (if any) MUST continue to pass

### Gate 5: Human (Heavy + Foundation — brief-level)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test -d .gzkit/personas
test -d src/gzkit/personas
test -f src/gzkit/personas/__init__.py
ls .gzkit/personas/*.md | wc -l       # expect 6 (authored canonical, retained)
ls src/gzkit/personas/*.md | wc -l    # expect 6 (byte-equivalent package copy)
diff -r .gzkit/personas/ src/gzkit/personas/ --exclude=__init__.py --exclude=__pycache__
# expect: no diff
```

## Acceptance Criteria

- [ ] REQ-0.0.32-09-01: Dual-surface layout established for personas — `.gzkit/personas/<slug>.md` retained as authored canonical source-of-truth (6 files); byte-identical copy added at `src/gzkit/personas/<slug>.md`. Byte-parity test fails closed on drift
- [ ] REQ-0.0.32-09-02: `src/gzkit/personas/__init__.py` exists as a thin package marker (empty module docstring acceptable; NO public-symbol API)
- [ ] REQ-0.0.32-09-03: No `CORE_PERSONAS`, `scaffold_core_personas`, or `_iter_canonical_persona_slugs` is added to `src/gzkit/personas/__init__.py` in this OBPI
- [ ] REQ-0.0.32-09-04: `src/gzkit/commands/init_cmd.py` is byte-identical to the pre-OBPI version (no integration changes here)
- [ ] REQ-0.0.32-09-05: `pyproject.toml` is byte-identical to the pre-OBPI version (no wheel-include extension in this OBPI)
- [ ] REQ-0.0.32-09-06: `gz agent sync control-surfaces` is byte-identical to the pre-OBPI version (sync mechanism is OBPI-08's scope)
- [ ] REQ-0.0.32-09-07: Vendor mirrors at `.claude/personas/`, `.github/personas/`, `.agents/personas/` remain unmodified (their transformed-render shape is intentional per § Named exceptions)
- [ ] REQ-0.0.32-09-08: `uv run gz check` exits 0 after the migration

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent + Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** Byte-parity regression test recorded
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs --strict passes
- [ ] **Gate 4 (BDD):** Existing scenarios still pass
- [ ] **Gate 5 (Human):** Foundation-kind heavy-lane brief-level attestation recorded

## Evidence

### Gate 1 (ADR) — Implementation Summary placeholder

- [ ] Decision item quote pinned per GHI #321

### Gate 2 (TDD)

```text
# Paste byte-parity test output
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

Before this OBPI: 6 canonical persona files lived only at `.gzkit/personas/<slug>.md` (authored canonical), with no presence in the Python package — the wheel could not ship them and the canonical content was unreachable from `importlib.resources`. After this OBPI: those 6 files remain at `.gzkit/personas/<slug>.md` as the authored canonical source-of-truth AND a byte-identical copy lives at `src/gzkit/personas/<slug>.md` as the package surface (precondition for OBPI-06 wheel includes and OBPI-10 scaffolder authoring). Vendor mirrors at `.claude/personas/`, `.github/personas/`, `.agents/personas/` continue to carry their existing transformed-render shape — that transformation is intentional per ADR-0.0.32 § Named exceptions and is OUT of this OBPI's byte-parity scope.

### Key Proof

```bash
ls .gzkit/personas/*.md | wc -l       # Expected: 6 (authored canonical, retained)
ls src/gzkit/personas/*.md | wc -l    # Expected: 6 (byte-equivalent package copy)
diff -r .gzkit/personas/ src/gzkit/personas/ --exclude=__init__.py --exclude=__pycache__
# Expected: no diff
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- (none at authoring time)

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
