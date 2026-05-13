# Plan: OBPI-0.0.32-06-t0-smoke-test

**OBPI:** OBPI-0.0.32-06-t0-smoke-test
**ADR:** ADR-0.0.32-canonical-surface-packaging (checklist item #6)
**Lane:** Heavy
**Authored:** 2026-05-13

## Context

OBPI-0.0.32-01 (skills dual-surface) and OBPI-0.0.32-02 (skills scaffolder
refactor) are both Completed. The wheel currently ships only
`src/gzkit/chores/**/*.md`. This OBPI extends the wheel include list to cover
all canonical surfaces (skills 70 SKILL.md, rules 19 .md, personas 6 .md,
templates 12 .md), authors a frozen baseline manifest, and builds an
end-to-end smoke scenario (`uv build → install → gz init → assert
byte-equivalence`) that fails CI on any T0 drift.

Current counts in `src/gzkit/`:
- skills: 70 SKILL.md files
- rules: 19 .md files
- personas: 6 .md files
- templates: 12 .md files
- hooks/scripts: no scripts yet (glob added for forward-compatibility)

gzkit version: 0.26.2

## Files

**To modify:**
- `pyproject.toml` — extend `[tool.hatch.build.targets.wheel] include:`

**To create:**
- `data/distribution_baseline_manifest.json` — frozen manifest JSON
- `tests/distribution/__init__.py` — package init
- `tests/distribution/test_baseline_manifest.py` — unit tests for manifest
- `features/distribution_invariant.feature` — smoke scenario
- `features/steps/distribution_invariant_steps.py` — step definitions
- `docs/governance/distribution_baseline.md` — governance doc

## Steps

### Step 1: Extend pyproject.toml wheel includes

Read `pyproject.toml` `[tool.hatch.build.targets.wheel]` block (lines 56–70).
Extend the `include:` list to add:

```toml
"src/gzkit/skills/**/*.md",
"src/gzkit/rules/**/*.md",
"src/gzkit/personas/**/*.md",
"src/gzkit/templates/**/*.md",
"src/gzkit/hooks/scripts/**",
```

Also extend `exclude:` to explicitly exclude `src/gzkit/chores/*/proofs/**`
(already present) — verify the new include globs are NOT accidentally caught
by any exclude rule.

Verify with:
```bash
uv build && unzip -l dist/py_gzkit-*.whl | grep "gzkit/skills.*SKILL.md" | wc -l
# expect 70
```

REQ covered: REQ-0.0.32-06-02, REQ-0.0.32-06-08, REQ-0.0.32-06-09

### Step 2: Author data/distribution_baseline_manifest.json (TDD GREEN side)

Enumerate the following from the `src/gzkit/` package tree and produce
surface-relative path lists (paths relative to each surface root):

- `skills`: all paths matching `src/gzkit/skills/*/SKILL.md`
  → relative form: `"<slug>/SKILL.md"` (e.g. `"gz-prd/SKILL.md"`)
- `rules`: all `src/gzkit/rules/*.md` (excluding __pycache__ and __init__.py)
  → relative form: filename (e.g. `"cli.md"`)
- `personas`: all `src/gzkit/personas/*.md`
  → relative form: filename
- `templates`: all `src/gzkit/templates/*.md`
  → relative form: filename

Schema:
```json
{
  "schema_version": "1.0",
  "gzkit_version": "0.26.2",
  "surfaces": {
    "skills": ["<slug>/SKILL.md", ...],
    "rules": ["cli.md", ...],
    "personas": ["main-session.md", ...],
    "templates": ["adr.md", ...]
  }
}
```

Write to `data/distribution_baseline_manifest.json`.
Hooks surface is omitted from the manifest (no scripts exist yet).

REQ covered: REQ-0.0.32-06-03

### Step 3: Author unit tests — tests/distribution/

Create `tests/distribution/__init__.py` (empty).

Create `tests/distribution/test_baseline_manifest.py` with three test classes:

**TestManifestSchemaValidation:**
- `test_schema_version_present`: loads manifest, asserts `schema_version == "1.0"`
- `test_gzkit_version_present`: asserts version string non-empty
- `test_surfaces_key_present`: asserts `surfaces` is a dict
- `test_required_surfaces_present`: asserts skills, rules, personas, templates keys exist

**TestManifestFileResolution:**
- `test_skills_resolve_to_real_files`: for each entry in surfaces.skills, assert
  `src/gzkit/skills/<entry>` exists as a real file
- `test_rules_resolve_to_real_files`: for each entry in surfaces.rules, assert
  `src/gzkit/rules/<entry>` exists
- `test_personas_resolve_to_real_files`: for each entry in surfaces.personas, assert
  `src/gzkit/personas/<entry>` exists
- `test_templates_resolve_to_real_files`: for each entry in surfaces.templates, assert
  `src/gzkit/templates/<entry>` exists
- `test_skills_count_floor`: assert len(surfaces.skills) >= 60 (REQ-09 floor)
- `test_rules_count_floor`: assert len(surfaces.rules) >= 14 (REQ-09 floor)

**TestManifestDuplicateDetection:**
- `test_no_duplicate_skills`: assert len(set) == len(list) for surfaces.skills
- `test_no_duplicate_rules`: same for rules
- `test_no_duplicate_personas`: same for personas
- `test_no_duplicate_templates`: same for templates

Decorator on each test class method: `@covers("REQ-0.0.32-06-05")`
or inline `@covers REQ-0.0.32-06-05` in docstring per `.gzkit/rules/tests.md`.

REQ covered: REQ-0.0.32-06-05

### Step 4: Author features/distribution_invariant.feature

Feature: Distribution invariant T0 smoke test
(Heavy-lane Gate 4 proof for ADR-0.0.32 OBPI-06)

Write scenario tagged `@REQ-0.0.32-06-01` `@REQ-0.0.32-06-04` `@slow`:

```gherkin
@REQ-0.0.32-06-01
@REQ-0.0.32-06-04
@REQ-0.0.32-06-07
@slow
Scenario: Build-install-init smoke test passes against frozen baseline manifest
  Given the gzkit source tree is clean and buildable
  When I build the wheel with "uv build"
  And I install the wheel into a fresh temporary venv
  And I run "gz init" in a fresh project directory using the installed binary
  Then every baseline manifest entry is present in the installed project's .gzkit tree
  And no installed .gzkit artifact is absent from the baseline manifest
  And the smoke test completes within the documented runtime budget
```

Write additional scenario tagged `@REQ-0.0.32-06-06` for manifest schema:

```gherkin
@REQ-0.0.32-06-03
@REQ-0.0.32-06-06
Scenario: Baseline manifest validates against frozen schema
  Given the baseline manifest exists at "data/distribution_baseline_manifest.json"
  Then the manifest has schema_version "1.0"
  And the manifest surfaces include skills, rules, personas, and templates
  And each skill entry resolves to a real file under src/gzkit/skills/
  And each rule entry resolves to a real file under src/gzkit/rules/
```

REQ covered: REQ-0.0.32-06-01, REQ-0.0.32-06-03, REQ-0.0.32-06-04, REQ-0.0.32-06-07

### Step 5: Author features/steps/distribution_invariant_steps.py

Implement step definitions for the smoke scenario:

**`_uv_build(project_root)`:** Runs `subprocess.run(["uv", "build"], cwd=project_root)`.
Returns path of newest `.whl` in `dist/`.

**`_create_temp_venv(venv_path)`:** Runs `subprocess.run(["uv", "venv", str(venv_path)])`.
Returns path to the `gz` binary inside the venv.

**`_install_wheel(venv_path, wheel_path)`:** Runs
`subprocess.run(["uv", "pip", "install", str(wheel_path), "--python", str(venv_path / "bin" / "python")])`.

**`_gz_init_in_tempdir(gz_binary, project_dir)`:** Runs gz init as subprocess with
the venv's gz binary in the tempdir.

**`_enumerate_gzkit_artifacts(project_dir)`:** Walks `project_dir / ".gzkit"`,
returns surface-relative path dict keyed by surface name (skills, rules, personas, templates).

**Cleanup:** Use `context.add_cleanup()` or register via `after_scenario` in
`environment.py` to delete temp venv and temp project dir on exit (both SUCCESS and FAILURE).
Wheel in `dist/` is NOT cleaned (it's part of the build artifact; cleared by `uv build`
on next run). Document this in a comment.

**Runtime measurement:** Record `time.monotonic()` before/after the full build-install-init
cycle, store in `context.smoke_runtime_s`. Log it at end.

**@slow tag handling:** The scenario is tagged `@slow`. Document in
`docs/governance/distribution_baseline.md` that it is excluded from `gz test`
but included in `uv run -m behave features/distribution_invariant.feature`.

Covers all REQs: REQ-0.0.32-06-01, -02, -04, -06, -07, -08, -09.

Module-level docstring must include:
```
@covers REQ-0.0.32-06-01
@covers REQ-0.0.32-06-04
@covers REQ-0.0.32-06-07
```

### Step 6: Author docs/governance/distribution_baseline.md

Short doc (≤200 lines) covering:
1. Role of the baseline manifest in enforcing T0 distribution invariant
2. How to read the manifest schema
3. Refresh discipline: when to update the manifest (new surface promotion,
   new canonical artifact addition)
4. Step-by-step: how to regenerate the manifest after a new canonical surface lands
5. How to run the smoke test: `uv run -m behave features/distribution_invariant.feature`
6. @slow tag explanation: excluded from `gz test` smoke run by default

Must pass `mkdocs build --strict`.

REQ covered: REQ-0.0.32-06-06

### Step 7: Verify all gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

# Docs
uv run mkdocs build --strict

# Wheel includes
uv build
unzip -l dist/py_gzkit-*.whl | grep "gzkit/skills.*SKILL.md" | wc -l    # expect 70
unzip -l dist/py_gzkit-*.whl | grep "gzkit/rules.*\.md" | wc -l         # expect 19
unzip -l dist/py_gzkit-*.whl | grep "gzkit/personas.*\.md" | wc -l      # expect 6
unzip -l dist/py_gzkit-*.whl | grep "gzkit/templates.*\.md" | wc -l     # expect 12

# Smoke scenario
uv run -m behave features/distribution_invariant.feature

# REQ covers parity
uv run gz covers OBPI-0.0.32-06-t0-smoke-test --json
```

## Notes

- The behave smoke test uses the REAL `uv build` (not editable install). This is
  different from `chores_distribution.feature` which uses `sys.executable -m gzkit`.
  Runtime is expected to be 30–90s depending on build cache state; document in doc.
- If `uv build` fails during scenario execution for reasons unrelated to this OBPI
  (e.g., existing pyproject.toml issue), escalate as separate GHI per STOP-on-BLOCKERS.
- Personas are already in `src/gzkit/personas/` (6 files) even though OBPI-09 hasn't
  formally established the dual-surface. Including them in wheel includes is safe and
  forward-compatible with OBPI-09's landing.
- The baseline manifest captures state AT OBPI-06 landing time. Future surface
  promotions (OBPI-03 rules, OBPI-09 personas, OBPI-11 templates) will each refresh
  the manifest as their own last step.
- `tests/distribution/test_baseline_manifest.py` uses the REPO state (reads from
  `src/gzkit/` directly) to verify the manifest, not a built wheel. The behave scenario
  does the wheel-install verification.
