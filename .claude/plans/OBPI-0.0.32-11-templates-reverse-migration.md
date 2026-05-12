# Plan: OBPI-0.0.32-11 Templates Reverse-Migration

## OBPI Reference

OBPI-0.0.32-11-templates-reverse-migration

## Context

Templates currently live only at `src/gzkit/templates/<name>.md` (11 `.md` files
plus `__init__.py` plus a `skills/` subdir). `.gzkit/templates/` does NOT exist.
This is a direction-reversal from skills/rules/personas: templates already live at
the package surface, so the migration moves them FROM `src/gzkit/templates/` TO
`.gzkit/templates/` (new authored canonical), then re-establishes `src/gzkit/templates/`
copies for wheel-shipping.

The `__init__.py` uses `importlib.resources.files("gzkit.templates")` throughout — no
`Path(__file__).parent` patterns. Dual-surface works because the `cp`-back step
re-establishes the `.md` files at the package surface before any `importlib.resources`
resolution runs.

The `src/gzkit/templates/skills/` subdir contains a `git-sync` item; it is retained
at the package surface only (not subject to dual-surface invariant in this OBPI).

**Prerequisite checks (STOP-on-BLOCKER confirmation):**
- `.gzkit/templates/` does NOT exist: confirmed ✓
- `src/gzkit/templates/__init__.py` exists: confirmed ✓
- `render_template()` uses `importlib.resources`: confirmed ✓
- Working tree: clean at plan time ✓

## Files

### New files
- `.gzkit/templates/` (new directory — destination for git mv)
- `tests/test_templates.py::TestTemplatesLayoutDualSurface` (new test class added to existing file)

### Modified files
- `.gzkit/templates/<name>.md` × 11 (created via `git mv` from `src/gzkit/templates/`)
- `src/gzkit/templates/<name>.md` × 11 (re-established via `cp` from `.gzkit/templates/`)
- `src/gzkit/templates/__init__.py` — UNCHANGED (byte-identical, no logic changes)

### Untouched (out of scope)
- `pyproject.toml` — no wheel-include extension (OBPI-06)
- `src/gzkit/commands/init_cmd.py` — no integration changes (OBPI-12)
- `src/gzkit/templates/skills/` subdir — retained at package surface as-is
- `gz agent sync control-surfaces` — sync extension is OBPI-08

## Steps

### Task 1: Create .gzkit/templates/ directory and git mv all .md files

Create the `.gzkit/templates/` directory, then use `git mv` (not `cp + rm`) for every
`.md` file under `src/gzkit/templates/`:

```bash
mkdir -p .gzkit/templates
git mv src/gzkit/templates/adr_pool.md .gzkit/templates/adr_pool.md
git mv src/gzkit/templates/adr.md .gzkit/templates/adr.md
git mv src/gzkit/templates/agents.md .gzkit/templates/agents.md
git mv src/gzkit/templates/audit_plan.md .gzkit/templates/audit_plan.md
git mv src/gzkit/templates/audit.md .gzkit/templates/audit.md
git mv src/gzkit/templates/claude.md .gzkit/templates/claude.md
git mv src/gzkit/templates/closeout.md .gzkit/templates/closeout.md
git mv src/gzkit/templates/constitution.md .gzkit/templates/constitution.md
git mv src/gzkit/templates/copilot.md .gzkit/templates/copilot.md
git mv src/gzkit/templates/obpi.md .gzkit/templates/obpi.md
git mv src/gzkit/templates/prd.md .gzkit/templates/prd.md
```

After this step: `.gzkit/templates/` has all 11 `.md` files; `src/gzkit/templates/*.md`
files are absent (moved away). The `__init__.py` and `skills/` subdir remain at
`src/gzkit/templates/`.

### Task 2: Re-establish byte-equivalent copies at src/gzkit/templates/

```bash
cp .gzkit/templates/adr_pool.md src/gzkit/templates/adr_pool.md
cp .gzkit/templates/adr.md src/gzkit/templates/adr.md
cp .gzkit/templates/agents.md src/gzkit/templates/agents.md
cp .gzkit/templates/audit_plan.md src/gzkit/templates/audit_plan.md
cp .gzkit/templates/audit.md src/gzkit/templates/audit.md
cp .gzkit/templates/claude.md src/gzkit/templates/claude.md
cp .gzkit/templates/closeout.md src/gzkit/templates/closeout.md
cp .gzkit/templates/constitution.md src/gzkit/templates/constitution.md
cp .gzkit/templates/copilot.md src/gzkit/templates/copilot.md
cp .gzkit/templates/obpi.md src/gzkit/templates/obpi.md
cp .gzkit/templates/prd.md src/gzkit/templates/prd.md
```

This MUST happen before any test that exercises `render_template()` or
`importlib.resources.files("gzkit.templates")`. The dual-surface layout is now
established: `.gzkit/templates/` (authored canonical) ↔ `src/gzkit/templates/` (package copy).

### Task 3: Add TestTemplatesLayoutDualSurface byte-parity test to tests/test_templates.py

Add a new test class `TestTemplatesLayoutDualSurface` to the existing
`tests/test_templates.py`. The class mirrors
`TestSkillsLayoutDualSurface.test_dual_surface_byte_parity` from `tests/test_skills.py`:

- `test_dual_surface_byte_parity`: iterate `.gzkit/templates/*.md`; for each, assert
  the byte-identical copy exists at `src/gzkit/templates/<name>.md`; assert
  `authored.read_bytes() == pkg_copy.read_bytes()`.
- `@covers("REQ-0.0.32-11-07")` decorator on the parity test.
- `@covers("REQ-0.0.32-11-01")` decorator covering the git-mv requirement (absence of
  `.gzkit/templates/` before migration is a precondition, not a test; the parity test
  is the failure-closed mechanism for ongoing drift).

The test does NOT add any CORE_TEMPLATES, scaffold_core_templates, or
_iter_canonical_template_slugs — those belong to OBPI-12.

### Task 4: Run RED-GREEN-REFACTOR for the byte-parity test

**RED phase:** Before step 1-2 complete, the byte-parity test fails because
`.gzkit/templates/` doesn't exist. This is the natural RED state after adding
the test but before the migration.

In practice, since Tasks 1-2 and 3 must produce a working state for `gz check`
to pass, the implementation ordering is: write test (RED), do migration Tasks 1-2
(GREEN), verify.

**GREEN phase:** After Tasks 1 and 2, `test_dual_surface_byte_parity` passes
because `.gzkit/templates/` has the authored canonical files and `src/gzkit/templates/`
has the byte-equivalent copies.

### Task 5: Verify all existing render_template tests still pass

Run:
```bash
uv run -m unittest tests.test_templates -v
```

Expected: all existing tests in `TestLoadTemplate`, `TestRenderTemplate`,
`TestAgentsTemplateSemantic`, `TestAdapterTemplatesReferenceCanon`,
`TestRootSurfaceSlimming`, `TestListTemplates`, `TestObpiDiscoveryChecklistOrder`,
`TestObpiTemplateDemoSection` continue to pass. These confirm REQ-0.0.32-11-05
(render_template() resolves post-migration).

### Task 6: Run full quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

All must exit 0. This satisfies REQ-0.0.32-11-10 (`gz check` exits 0).

## Verification

```bash
# Structural verification
test -d .gzkit/templates && echo "OK: .gzkit/templates exists"
test -d src/gzkit/templates && echo "OK: src/gzkit/templates exists"
test -f src/gzkit/templates/__init__.py && echo "OK: __init__.py retained"
ls .gzkit/templates/*.md | wc -l    # expect 11
ls src/gzkit/templates/*.md | wc -l  # expect 11
diff -r .gzkit/templates/ src/gzkit/templates/ --exclude=__init__.py --exclude="__pycache__" --exclude=skills
# expect: no diff

# render_template regression
python -c "from gzkit.templates import render_template; print(render_template('adr.md', {'id':'TEST','title':'Test'})[:80])"
# expect: substantive template content

# No CORE_TEMPLATES or scope-creep in __init__.py
grep -n "CORE_TEMPLATES\|scaffold_core_templates\|_iter_canonical_template_slugs" src/gzkit/templates/__init__.py
# expect: no matches
```

## Notes

**Destination-in-mind disclosure (gz-plan-audit Step 6a):**

Approach concluded before writing this plan: `git mv` all `.md` files to `.gzkit/templates/`,
then `cp` back to re-establish package surface. No `__init__.py` logic changes needed.
The `importlib.resources` resolution continues to work because the package surface
(`src/gzkit/templates/*.md`) is fully repopulated before any test runs.

**Rejected alternatives:**
1. `cp + rm` instead of `git mv` — rejected: REQ-0.0.32-11-01 explicitly prohibits bulk
   cp+rm; git history preservation is the requirement
2. Doing the `git mv` and `cp`-back in a single pass without ordering discipline —
   rejected: the step ordering matters because `importlib.resources` will fail if the
   `.md` files are absent from `src/gzkit/templates/` when tests run; the `cp`-back
   must complete before any test exercising `render_template()`
3. Modifying `__init__.py` to resolve from `.gzkit/templates/` directly — rejected:
   this is scope creep (beyond allowed paths), and the dual-surface model is exactly
   designed to avoid this; the package surface stays populated

**Template count:** The OBPI brief says "13+" files but the current count is 11. The
brief's FAIL-CLOSED REQ says "every `.md` file currently under `src/gzkit/templates/`"
which is the correct specification. All 11 existing files are migrated.
