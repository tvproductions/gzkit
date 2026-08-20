# Plan: OBPI-0.0.32-15-t0-maintenance-surfaces

**OBPI:** OBPI-0.0.32-15-t0-maintenance-surfaces
**Parent ADR:** ADR-0.0.32-canonical-surface-packaging
**Lane:** Heavy
**Date:** 2026-05-14

## Context

ADR-0.0.32 shipped OBPIs 01-14. OBPI-07 delivered `gz validate --distribution`
which detects drift in two categories:

- `ON_DISK_NOT_INCLUDED` — file under canonical surface tree but not covered by
  a wheel include glob (currently: `_scaffolder.py`, `complexity-thresholds.json`)
- `ON_DISK_NOT_BASELINE` — file on disk and wheel-included but not in baseline
  manifest (currently: 19 new skill SKILL.md files added after baseline freeze)

There is no canonical CLI recovery path for either category. OBPI-15 ships it:

**S1** — `gz validate --distribution --regenerate` rewrites
`data/distribution_baseline_manifest.json` from on-disk truth, fixing
`ON_DISK_NOT_BASELINE` errors. Emits a `distribution_baseline_regenerated`
ledger event.

**S2** — Per-surface `_classify_*_file` helpers (rules, skills, personas,
templates) classify files as `canonical`, `package_only`, or `runtime_state`.
The validator consults classifiers to exempt `package_only` from
`ON_DISK_NOT_INCLUDED`. The sync mechanism and doctrine follow.

Root-cause accounting for current 21 errors:
- `src/gzkit/rules/_scaffolder.py` → `package_only` (no `.gzkit/rules/` counterpart)
- `src/gzkit/rules/complexity-thresholds.json` → `canonical` (`.gzkit/rules/complexity-thresholds.json` exists) → add `src/gzkit/rules/**/*.json` glob to wheel include
- 19 skill SKILL.md files → `ON_DISK_NOT_BASELINE` → fixed by regenerator

## Allowed Paths (from brief)

```
src/gzkit/governance/trust_audits/distribution.py
src/gzkit/commands/validate_cmd.py
data/distribution_baseline_manifest.json
docs/user/manpages/validate.md
features/validate_distribution.feature
tests/governance/test_distribution_audit.py
src/gzkit/rules/__init__.py
src/gzkit/skills/__init__.py
src/gzkit/personas/__init__.py
src/gzkit/templates/__init__.py
.gzkit/rules/skill-surface-sync.md
pyproject.toml  [tool.hatch.build.targets.wheel] include: block only
src/gzkit/sync_surfaces.py
tests/test_rules.py
tests/test_skills.py
tests/test_personas.py
tests/test_templates.py
docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/ADR-0.0.32-canonical-surface-packaging.md
docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis/OBPI-0.0.32-15-t0-maintenance-surfaces.md
```

## Files

- `src/gzkit/governance/trust_audits/distribution.py` — add `regenerate_distribution_baseline()`, consult classifiers
- `src/gzkit/commands/validate_cmd.py` — wire `--regenerate` flag
- `src/gzkit/rules/__init__.py` — add `_classify_rule_file`
- `src/gzkit/skills/__init__.py` — add `_classify_skill_file`
- `src/gzkit/personas/__init__.py` — add `_classify_persona_file`
- `src/gzkit/templates/__init__.py` — add `_classify_template_file`
- `tests/governance/test_distribution_audit.py` — add regenerator + classifier-exemption tests
- `tests/test_rules.py` — add `TestClassifyRuleFile`
- `tests/test_skills.py` — add `TestClassifySkillFile`
- `tests/test_personas.py` — add `TestClassifyPersonaFile`
- `tests/test_templates.py` — add `TestClassifyTemplateFile`
- `pyproject.toml` — add `src/gzkit/rules/**/*.json` glob
- `.gzkit/rules/skill-surface-sync.md` — extend class-classifier section
- `src/gzkit/sync_surfaces.py` — extend classifier consultation to all surfaces
- `docs/user/manpages/validate.md` — document `--regenerate` flag
- `features/validate_distribution.feature` — add REQ-0.0.32-15 scenarios
- `data/distribution_baseline_manifest.json` — regenerated output

## Steps

### Step 1: TDD — Author classifier tests (RED)

Write tests before implementation. These will fail until Step 2.

**1a. `tests/test_rules.py`** — Add `TestClassifyRuleFile`:
- `test_package_only_scaffolder_py` — `_scaffolder.py` → `"package_only"` (no .gzkit counterpart)
- `test_canonical_complexity_thresholds_json` — `complexity-thresholds.json` with .gzkit counterpart → `"canonical"`
- `test_package_only_json_without_counterpart` — json file with no .gzkit counterpart → `"package_only"`
- `test_package_only_init_py` — `__init__.py` → `"package_only"`
- `test_canonical_md` — `*.md` file → `"canonical"`

**1b. `tests/test_skills.py`** — Add `TestClassifySkillFile`:
- `test_canonical_skill_md` — `SKILL.md` → `"canonical"`
- `test_package_only_init_py` — `__init__.py` → `"package_only"`

**1c. `tests/test_personas.py`** — Add `TestClassifyPersonaFile`:
- `test_canonical_persona_md` — `*.md` → `"canonical"`
- `test_package_only_init_py` — `__init__.py` → `"package_only"`

**1d. `tests/test_templates.py`** — Add `TestClassifyTemplateFile`:
- `test_canonical_template_md` — `*.md` → `"canonical"`
- `test_package_only_init_py` — `__init__.py` → `"package_only"`

**1e. `tests/governance/test_distribution_audit.py`** — Add:
- `TestRegenerateDistributionBaseline`:
  - `test_regenerator_is_callable` — `regenerate_distribution_baseline` importable
  - `test_regenerate_writes_manifest` — round-trip: run regenerator, manifest written
  - `test_regenerator_emits_ledger_event` — ledger has `distribution_baseline_regenerated` event
  - `test_regenerate_then_audit_exits_zero` — after regenerate, `audit_distribution()` returns []
  - `test_regenerate_is_idempotent` — second run produces no diff
- `TestPackageOnlyExemption`:
  - `test_package_only_file_not_flagged_as_on_disk_not_included` — classifier exempts `__init__.py`-type files

All these tests should fail initially (RED phase).

### Step 2: Implement per-surface classifiers (GREEN phase for Step 1 tests)

**2a. `src/gzkit/rules/__init__.py`** — Add:
```python
def _classify_rule_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state"]:
    """Classify a rules file. Signature-compatible with _classify_chore_file."""
    path = Path(path)
    name = path.name
    path_posix = path.as_posix()

    # package_only: __init__.py and __pycache__
    if name == "__init__.py" or "__pycache__" in path.parts:
        return "package_only"

    # .py files: canonical only when present at .gzkit/ surface
    if name.endswith(".py"):
        if ".gzkit/rules/" in path_posix:
            return "canonical"
        if project_root is not None:
            try:
                rel = path.relative_to(project_root / "src" / "gzkit" / "rules")
                counterpart = project_root / ".gzkit" / "rules" / rel
                return "canonical" if counterpart.exists() else "package_only"
            except ValueError:
                pass
        return "package_only"

    # non-md non-py: json/yaml — canonical if .gzkit/ counterpart exists
    if not name.endswith(".md"):
        if ".gzkit/rules/" in path_posix:
            return "canonical"
        if project_root is not None:
            try:
                rel = path.relative_to(project_root / "src" / "gzkit" / "rules")
                counterpart = project_root / ".gzkit" / "rules" / rel
                return "canonical" if counterpart.exists() else "package_only"
            except ValueError:
                pass
        return "package_only"

    # Default: canonical (*.md)
    return "canonical"
```

**2b. `src/gzkit/skills/__init__.py`** — Add `_classify_skill_file` (simpler — skills surface contains only SKILL.md and `__init__.py`):
```python
def _classify_skill_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state"]:
    path = Path(path)
    name = path.name
    if name == "__init__.py" or "__pycache__" in path.parts:
        return "package_only"
    return "canonical"
```

**2c. `src/gzkit/personas/__init__.py`** — Add `_classify_persona_file` (similar to skills):
```python
def _classify_persona_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state"]:
    path = Path(path)
    name = path.name
    if name == "__init__.py" or "__pycache__" in path.parts:
        return "package_only"
    return "canonical"
```

**2d. `src/gzkit/templates/__init__.py`** — Add `_classify_template_file`:
```python
def _classify_template_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state"]:
    path = Path(path)
    name = path.name
    if name == "__init__.py" or "__pycache__" in path.parts:
        return "package_only"
    return "canonical"
```

After Step 2: run `uv run -m unittest tests/test_rules.py tests/test_skills.py tests/test_personas.py tests/test_templates.py` → should pass.

### Step 3: Update distribution.py — regenerator + classifier exemption

**3a.** Add `regenerate_distribution_baseline(project_root: Path) -> dict` function:
- Walks on-disk canonical surface trees (same `surface_roots` from `_load_inputs`)
- Consults per-surface classifier: only include files classified `canonical`
- Builds new manifest dict: `{"surfaces": {"skills": [...], "rules": [...], ...}}`
- Writes to `data/distribution_baseline_manifest.json` atomically
- Computes before/after hash and emits `distribution_baseline_regenerated` ledger event
- Returns metadata dict for callers

**3b.** Update `_collect_errors` (or add classifier dispatch to `_walk_surface_files`):
- Import per-surface classifiers
- In the `ON_DISK_NOT_INCLUDED` check: skip files classified as `package_only` or `runtime_state`
- This exempts `src/gzkit/rules/_scaffolder.py` from the error

After Step 3: run `uv run -m unittest tests/governance/test_distribution_audit.py` → regenerator tests should pass.

### Step 4: Wire --regenerate flag in validate_cmd.py

- Add `check_distribution_regenerate: bool = False` parameter to `collect_validation_errors()`
- Add `--regenerate` flag to the argparse parser for the `--distribution` scope
- When `--distribution --regenerate` is requested: call `regenerate_distribution_baseline(project_root)` and exit 0 (not an audit — a write operation)
- Guard: `--regenerate` without `--distribution` is a no-op with a warning

### Step 5: Update pyproject.toml wheel includes

- `complexity-thresholds.json` classifies as `canonical` (`.gzkit/rules/complexity-thresholds.json` exists)
- Add glob: `"src/gzkit/rules/**/*.json"` to `[tool.hatch.build.targets.wheel] include:`

After Step 5: `src/gzkit/rules/complexity-thresholds.json` is no longer `ON_DISK_NOT_INCLUDED`.

### Step 6: Extend sync_surfaces.py classifier consultation

- Import `_classify_rule_file`, `_classify_skill_file`, `_classify_persona_file`, `_classify_template_file`
- In each surface's sync block (rules, skills, personas, templates): apply classifier before propagating files
  - Skip `package_only` files (never copy to `.gzkit/` canonical side)
  - Skip `runtime_state` files (never modify in either direction)
- Pattern mirrors the existing chores classifier integration at line 641

### Step 7: Extend skill-surface-sync.md doctrine

- Rename/extend the `## Chores class-classifier` section to `## Canonical surface class-classifier`
- Add a unified table covering all five canonical surfaces (chores, rules, skills, personas, templates)
- Bump rule version in frontmatter

### Step 8: Update manpage validate.md

- Document `--distribution --regenerate` flag behavior
- Add example invocation: before/after flow

### Step 9: Add BDD scenarios to features/validate_distribution.feature

Add scenarios tagged with `@REQ-0.0.32-15-01` through `@REQ-0.0.32-15-03`:
- `Scenario: regenerator rewrites manifest from on-disk truth`
- `Scenario: regenerator emits distribution_baseline_regenerated ledger event`
- `Scenario: validate --distribution exits 0 after regeneration`
- `Scenario: regenerator is idempotent on second run`

### Step 10: Run regenerator and verify final state

```bash
uv run gz validate --distribution --regenerate
uv run gz validate --distribution  # expected: exit 0
```

## Verification

```bash
# Construction housekeeping
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

# OBPI-specific
uv run gz validate --distribution --regenerate
uv run gz validate --distribution  # exit 0
python -c "from gzkit.rules import _classify_rule_file; from gzkit.skills import _classify_skill_file; from gzkit.personas import _classify_persona_file; from gzkit.templates import _classify_template_file; print('OK')"
python -c "from pathlib import Path; from gzkit.rules import _classify_rule_file; print(_classify_rule_file(Path('src/gzkit/rules/_scaffolder.py')))"  # package_only
rg '"event": "distribution_baseline_regenerated"' .gzkit/ledger.jsonl | tail -1
```

## Notes

- The regenerator only writes `canonical`-class files to the manifest — `package_only` files are never in the baseline
- `_scaffolder.py` → `package_only` (no `.gzkit/rules/_scaffolder.py` counterpart)
- `complexity-thresholds.json` → `canonical` (`.gzkit/rules/complexity-thresholds.json` exists) → needs wheel include glob addition
- The 19 `ON_DISK_NOT_BASELINE` skill files are all `canonical` SKILL.md — regenerator adds them to baseline
- Regression gate: all OBPIs 01-14 byte-parity and behavioral tests must still pass
- Ledger event emitted via `gzkit.ledger.append_event()` using same pattern as other governance commands
