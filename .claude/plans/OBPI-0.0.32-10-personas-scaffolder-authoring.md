# Plan: OBPI-0.0.32-10-personas-scaffolder-authoring

## Context

OBPI-0.0.32-10 implements ADR-0.0.32 checklist item #10:

> "Personas scaffolder authoring — build `CORE_PERSONAS` registry symmetric to `CORE_SKILLS`/`CORE_RULES`/`CORE_CHORES`; author `scaffold_core_personas` that copies canonical persona content from `importlib.resources.files("gzkit.personas")` (the wheel's package surface) into the adopter's `.gzkit/personas/<slug>.md`; integrate with `init_cmd._scaffold_project_skeleton` (fresh init) and `_repair_missing_artifacts` (re-run repair). Depends on OBPI-09 landing first."

Prerequisites confirmed:
- OBPI-09 status: `Completed`
- 6 canonical persona `.md` files at `src/gzkit/personas/` (implementer, main-session, narrator, pipeline-orchestrator, quality-reviewer, spec-reviewer)
- `src/gzkit/personas/__init__.py` exists as package marker

Brief path error noted: brief says `docs/user/manpages/gz-init.md` but actual path is `docs/user/manpages/init.md`. Plan uses the correct path.

## Files

- `src/gzkit/personas/__init__.py` — add `CORE_PERSONAS`, `_iter_canonical_persona_slugs`, `scaffold_core_personas`
- `src/gzkit/commands/init_cmd.py` — update import, wire `scaffold_core_personas` into fresh init + repair
- `tests/test_personas.py` — remove 4 OBPI-09 negative boundary guards for OBPI-10 symbols; add OBPI-10 positive tests
- `tests/commands/test_init.py` — add persona scaffolding integration tests; update existing persona test to use canonical slug
- `docs/user/manpages/init.md` — add persona scaffolding section
- `docs/user/runbook.md` — update personas scaffolding section

## Steps

### Step 1: Write failing tests (RED)

**In `tests/test_personas.py`:**

1a. Remove the 4 negative tests that guard OBPI-10 symbols from `TestPersonasScopeNegative`:
   - `test_no_core_personas_registry` (lines ~88-96)
   - `test_no_scaffold_core_personas` (lines ~98-106)
   - `test_no_iter_canonical_persona_slugs` (lines ~108-116)
   - `test_init_cmd_has_no_scaffold_core_personas_call` (lines ~118-127)

   These were OBPI-09 scope guards. When OBPI-10 lands, those symbols MUST exist.

1b. Add `TestPersonasScaffolderObpi10` class with:
   - `test_core_personas_enumerates_all_6_slugs()` @covers REQ-0.0.32-10-01
   - `test_iter_canonical_persona_slugs_returns_6_entries()` @covers REQ-0.0.32-10-02
   - `test_scaffold_core_personas_writes_byte_identical_content()` @covers REQ-0.0.32-10-03
   - `test_scaffold_core_personas_skip_existing_preserves_operator_edits()` @covers REQ-0.0.32-10-06

**In `tests/commands/test_init.py`:**

1c. Update `test_init_does_not_overwrite_existing_personas` to use canonical slug `main-session.md`
    instead of `default-agent.md` (since `scaffold_core_personas` replaces `scaffold_default_personas`
    in the fresh-init path).

1d. Add `TestInitPersonasScaffoldingObpi10` class with:
   - `test_fresh_init_produces_6_canonical_persona_files()` @covers REQ-0.0.32-10-04, REQ-0.0.32-10-07
   - `test_repair_adds_missing_canonical_personas()` @covers REQ-0.0.32-10-05

Run tests → observe RED for all OBPI-10 tests.

### Step 2: Implement scaffold_core_personas in src/gzkit/personas/__init__.py

2a. Add at top of file (after existing imports):
   ```python
   import importlib.resources
   from collections.abc import Iterator
   from importlib.resources.abc import Traversable
   ```

2b. Add `_iter_canonical_persona_slugs()`:
   ```python
   def _iter_canonical_persona_slugs() -> Iterator[Traversable]:
       root = importlib.resources.files("gzkit.personas")
       for entry in root.iterdir():
           if not entry.is_file():
               continue
           if not entry.name.endswith(".md"):
               continue
           yield entry
   ```

2c. Add `CORE_PERSONAS: list[str]`:
   ```python
   CORE_PERSONAS: list[str] = sorted(
       entry.name[:-3]
       for entry in _iter_canonical_persona_slugs()
   )
   ```

2d. Add `scaffold_core_personas(project_root, config=None, *, skip_existing=False)`:
   - Uses hardcoded `.gzkit/personas/` path (consistent with existing `scaffold_default_personas`;
     `config.py` is outside allowed paths, no `canonical_personas` config field needed).
   - Returns `list[Path]` of newly created paths.
   - Pattern mirrors `scaffold_core_rules` / `_scaffolder.py` exactly.

Run tests → observe GREEN for Step 2 unit tests.

### Step 3: Wire scaffold_core_personas into init_cmd.py

3a. Update import line:
   `from gzkit.personas import scaffold_default_personas`
   → `from gzkit.personas import scaffold_core_personas, scaffold_default_personas`
   (keep `scaffold_default_personas` import for now; it is still tested in OBPI-09 tests)

3b. In `_scaffold_project_skeleton` (~line 594-597): replace
   ```python
   personas = scaffold_default_personas(project_root)
   console.print(f"  Scaffolded {len(personas)} default personas")
   ```
   with
   ```python
   personas = scaffold_core_personas(project_root, config)
   console.print(f"  Scaffolded {len(personas)} core personas")
   ```

3c. Add `_repair_personas(project_root, config, *, dry_run=False) -> list[str]` helper
   (mirrors `_repair_rules`):
   ```python
   def _repair_personas(project_root, config, *, dry_run=False):
       if dry_run:
           personas_dir = project_root / ".gzkit" / "personas"
           return [
               f"Would scaffold persona: {entry.name[:-3]}"
               for entry in _iter_canonical_persona_slugs()
               if not (personas_dir / entry.name).exists()
           ]
       new_personas = scaffold_core_personas(project_root, config, skip_existing=True)
       return [f"Scaffolded new persona: {path.name}" for path in new_personas]
   ```

3d. In `_repair_missing_artifacts` (~line 394): after `_repair_rules(...)` call, add:
   ```python
   # Repair personas — scaffold any core personas added in newer gzkit versions
   repaired.extend(_repair_personas(project_root, config, dry_run=dry_run))
   ```

3e. Add import of `_iter_canonical_persona_slugs` to `_repair_personas` (lazy import mirrors
    the `_repair_rules` pattern).

Run tests → observe GREEN for all OBPI-10 tests.

### Step 4: Quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

### Step 5: Documentation updates

5a. In `docs/user/manpages/init.md`: add "Persona Scaffolding" subsection after the
    existing Rules Scaffolding section, describing that `gz init` now scaffolds 6
    canonical persona files into `.gzkit/personas/` from `importlib.resources.files("gzkit.personas")`.

5b. In `docs/user/runbook.md` (~line 934): update the existing personas section to
    mention that `gz init` scaffolds the 6 canonical personas and that `.gzkit/personas/`
    is the project canonical source-of-truth per ADR-0.0.32.

5c. Run: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`

### Step 6: Covers gate

```bash
uv run gz covers OBPI-0.0.32-10-personas-scaffolder-authoring --json
```
Confirm `uncovered_reqs == 0` before proceeding to Stage 4.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
python -c "from gzkit.personas import CORE_PERSONAS, scaffold_core_personas, _iter_canonical_persona_slugs; print('imports OK', len(CORE_PERSONAS), sum(1 for _ in _iter_canonical_persona_slugs()))"
```

Expected output: `imports OK 6 6`

## Key Design Decisions

1. **CORE_PERSONAS shape**: `list[str]` of sorted slug names — same shape as `CORE_RULES`.
   Not a dict; consistent with all sibling registries.

2. **Config path**: hardcoded `.gzkit/personas/` (no `canonical_personas` config field).
   `src/gzkit/config.py` is outside allowed paths. Consistent with `scaffold_default_personas`
   which already uses `project_root / ".gzkit" / "personas"` directly.

3. **init_cmd fresh init**: REPLACE `scaffold_default_personas` with `scaffold_core_personas`.
   The 6 canonical gzkit personas supersede the 2 generic project-agnostic defaults for
   gzkit adopters. REQ-0.0.32-10-07 requires `gz init` to produce 6 canonical persona files.

4. **tests/test_personas.py negative guards**: Remove the 4 OBPI-09 scope guards that asserted
   OBPI-10 symbols must NOT exist. Those were intentional scope guards meant to fail when
   OBPI-10 landed.

## Destination-in-mind (plan-before-exploration disclosure per gz-plan-audit § 6a)

Before exploration, the intended approach was: mirror `scaffold_core_rules` / `_scaffolder.py`
exactly, using `importlib.resources.files("gzkit.personas")` as the source.

Rejected alternatives considered:
- **Separate `_scaffolder.py` module**: rules uses this because `rules/__init__.py` is ~620 lines.
  `personas/__init__.py` is smaller. Chose direct `__init__.py` addition to avoid module sprawl.
- **Adding `canonical_personas` to config.py**: Rejected — `config.py` is outside allowed paths
  and `.gzkit/personas/` is already hardcoded in `scaffold_default_personas`.
- **Keeping both `scaffold_default_personas` AND `scaffold_core_personas` in fresh init**: Rejected
  — REQ-0.0.32-10-07 requires exactly 6 canonical persona files; mixing would produce 8 total.
