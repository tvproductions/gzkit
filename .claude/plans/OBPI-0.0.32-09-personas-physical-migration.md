# Plan: OBPI-0.0.32-09-personas-physical-migration

## OBPI

OBPI-0.0.32-09-personas-physical-migration
Parent ADR: ADR-0.0.32-canonical-surface-packaging (foundation, heavy lane)

## Context

This OBPI establishes the dual-surface layout for the personas canonical surface,
mirroring OBPI-01 (skills) and OBPI-03 (rules) for personas.

**Critical finding from prerequisites check:** `src/gzkit/personas.py` ALREADY EXISTS
as a 538-line Python module with a full public API (`scaffold_default_personas`,
`compose_persona_frame`, `evaluate_persona_drift`, `render_persona_for_vendor`,
`DEFAULT_PERSONAS`, `VENDOR_ADAPTERS`, `TRAIT_PROXY_REGISTRY`). Multiple import
sites exist in `src/` and `tests/`. This is the SAME situation as OBPI-01 (skills):
a **module-to-package conversion** (`personas.py` → `personas/__init__.py`), NOT a
fresh creation of an empty `__init__.py`.

The brief's STOP-on-BLOCKERS note ("none should exist today, but check") anticipated
that no imports would exist. In reality, `personas.py` already supplies the API —
the conversion preserves every existing symbol. REQ-03/04/05/06/07 apply as
negative constraints: don't ADD new symbols (CORE_PERSONAS, scaffold_core_personas,
_iter_canonical_persona_slugs) in this OBPI — those belong to OBPI-10.

**Vendor mirrors confirmed transformed:** `.claude/personas/` holds trimmed
single-sentence renders, NOT byte-equivalent copies of `.gzkit/personas/`. The
carve-out is verified; byte-parity scope is `.gzkit/personas/ ↔ src/gzkit/personas/`
only.

## Files

### Created
- `tests/test_personas.py` — byte-parity test mirroring `TestSkillsLayoutDualSurface`
- `src/gzkit/personas/__init__.py` — converted from `src/gzkit/personas.py` (preserves all API)
- `src/gzkit/personas/implementer.md` — byte-identical copy of `.gzkit/personas/implementer.md`
- `src/gzkit/personas/main-session.md` — byte-identical copy
- `src/gzkit/personas/narrator.md` — byte-identical copy
- `src/gzkit/personas/pipeline-orchestrator.md` — byte-identical copy
- `src/gzkit/personas/quality-reviewer.md` — byte-identical copy
- `src/gzkit/personas/spec-reviewer.md` — byte-identical copy

### Removed
- `src/gzkit/personas.py` — superseded by `src/gzkit/personas/__init__.py` (same content)

### Unchanged
- `.gzkit/personas/*.md` — 6 canonical authored files retained in place (never deleted)
- `pyproject.toml` — wheel-include extension deferred to OBPI-06
- `src/gzkit/commands/init_cmd.py` — no integration changes (OBPI-10 scope)
- `src/gzkit/sync_surfaces.py` — no changes (OBPI-08 scope)
- `.claude/personas/`, `.github/personas/`, `.agents/personas/` — vendor renders untouched

## Steps

### Step 1: Write failing byte-parity test (RED phase)

Create `tests/test_personas.py` with class `TestPersonasLayoutDualSurface`:

```python
@covers("REQ-0.0.32-09-01")
def test_persona_files_retained_at_authored_source(self): ...
    # asserts .gzkit/personas/*.md present (6 files)

@covers("REQ-0.0.32-09-01")
@covers("REQ-0.0.32-09-02")
def test_dual_surface_byte_parity(self): ...
    # asserts .gzkit/personas/<slug>.md == src/gzkit/personas/<slug>.md bytes

@covers("REQ-0.0.32-09-02")
def test_package_init_exists_as_thin_marker(self): ...
    # asserts src/gzkit/personas/__init__.py exists and has NO CORE_PERSONAS symbol
```

Also `TestPersonasScopeNegative`:
```python
@covers("REQ-0.0.32-09-03")
def test_no_core_personas_in_init(self): ...
    # asserts CORE_PERSONAS, scaffold_core_personas, _iter_canonical_persona_slugs
    # are NOT exported from gzkit.personas.__init__ in this OBPI

@covers("REQ-0.0.32-09-04")
def test_init_cmd_unchanged(self): ...
    # asserts init_cmd.py has no scaffold_core_personas call (only scaffold_default_personas)

@covers("REQ-0.0.32-09-05")
def test_pyproject_unchanged(self): ...
    # asserts pyproject.toml does not include src/gzkit/personas pattern (OBPI-06 scope)
```

Run to confirm RED: `uv run -m unittest tests.test_personas -v`
Expected: `test_dual_surface_byte_parity` FAILS (src/gzkit/personas/ package doesn't exist yet)

### Step 2: Module-to-package conversion

Convert `src/gzkit/personas.py` to `src/gzkit/personas/__init__.py`:

```bash
mkdir src/gzkit/personas
mv src/gzkit/personas.py src/gzkit/personas/__init__.py
```

The file content is UNCHANGED — every existing public symbol preserved.
No new symbols added (CORE_PERSONAS etc. deferred to OBPI-10).

### Step 3: Copy 6 canonical persona files

```bash
cp .gzkit/personas/implementer.md src/gzkit/personas/implementer.md
cp .gzkit/personas/main-session.md src/gzkit/personas/main-session.md
cp .gzkit/personas/narrator.md src/gzkit/personas/narrator.md
cp .gzkit/personas/pipeline-orchestrator.md src/gzkit/personas/pipeline-orchestrator.md
cp .gzkit/personas/quality-reviewer.md src/gzkit/personas/quality-reviewer.md
cp .gzkit/personas/spec-reviewer.md src/gzkit/personas/spec-reviewer.md
```

Verify retention: `.gzkit/personas/` still has all 6 files.
Verify byte-parity: `diff -r .gzkit/personas/ src/gzkit/personas/ --exclude=__init__.py --exclude=__pycache__` shows no diff.

### Step 4: Run tests — confirm GREEN

```bash
uv run -m unittest tests.test_personas -v
```

Expected: all tests PASS (byte-parity established).

Also run the full test suite to confirm no regressions from the module-to-package conversion:
```bash
uv run -m unittest -q
```

### Step 5: Quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

Run verification commands from the brief:
```bash
test -d .gzkit/personas
test -d src/gzkit/personas
test -f src/gzkit/personas/__init__.py
ls .gzkit/personas/*.md | wc -l       # expect 6
ls src/gzkit/personas/*.md | wc -l    # expect 6
diff -r .gzkit/personas/ src/gzkit/personas/ --exclude=__init__.py --exclude=__pycache__
# expect: no diff
```

### Step 6: Present OBPI Acceptance Ceremony

Stage 4 evidence template with full REQ coverage table.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
test -d src/gzkit/personas
test -f src/gzkit/personas/__init__.py
diff -r .gzkit/personas/ src/gzkit/personas/ --exclude=__init__.py --exclude=__pycache__
```

## Rejected Alternatives

**Create empty `__init__.py` and discard existing personas.py content:** Rejected.
`personas.py` has 538 lines of production API consumed by 8 import sites in src/ and
tests/. Creating an empty `__init__.py` would break all consumers. Module-to-package
conversion (same as OBPI-01 for skills) is the only correct path.

**Leave personas.py in place and create personas/ alongside:** Rejected. Python does
not permit both `src/gzkit/personas.py` and `src/gzkit/personas/` to coexist — the
package directory takes precedence, making the `.py` file unreachable and causing
import errors. The file must be moved into the new package as `__init__.py`.

## Notes

- ADR checklist item quote: "Personas physical migration — establish dual-surface for
  all 6 canonical personas: retain `.gzkit/personas/<slug>.md` as authored
  source-of-truth AND add byte-equivalent copy at `src/gzkit/personas/<slug>.md` for
  wheel-shipping; create `src/gzkit/personas/__init__.py` if needed for package
  discovery (no public-symbol exports beyond the data surface); byte-parity test fails
  closed on drift."
- "no public-symbol exports beyond the data surface" means: don't ADD new symbols
  (CORE_PERSONAS, scaffold_core_personas, _iter_canonical_persona_slugs) — NOT:
  strip existing API from personas.py during conversion.
- Existing vendor mirrors (.claude/personas/, .github/personas/, .agents/personas/)
  confirmed transformed-render shape (not byte-equivalent) — OUT of byte-parity scope.
