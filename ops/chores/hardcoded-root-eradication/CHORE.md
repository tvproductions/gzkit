# CHORE: Config-First Enforcement (Anti-Vibe-Code)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `hardcoded-root-eradication`

---

## Overview

Enforce 12-factor config-first discipline across the codebase. Every resource
path, directory name, schema location, threshold value, default setting, and
structural assumption must flow from config (`manifest.json`, `.gzkit.json`,
`config/` files, or CLI arguments) — never hardcoded in source modules.

Agents trained on open-source codebases reflexively vibe-code constants,
magic strings, and `Path(__file__).parents[N]` derivations. This chore
exists as a recurring quality gate to catch and remediate that drift.

## Why (12-Factor Principle #3)

> "An app's config is everything that is likely to vary between deploys.
> Config should be strictly separated from code."

In gzkit terms: if a value depends on project structure, deployment context,
or user preference, it belongs in config — not in a module-level constant.

## Anti-Patterns (What to Find)

### 1. Hardcoded project root derivation

```python
# BAD
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DATA_DIR = _PROJECT_ROOT / "data" / "eval"
```

### 2. Hardcoded resource paths / filenames

```python
# BAD
SCHEMA_PATH = project_root / "data" / "schemas" / "eval_dataset.schema.json"
CHORES_DIR = "ops/chores"
```

### 3. Hardcoded thresholds / magic numbers

```python
# BAD
if coverage < 40.0:  # should come from config
    fail()
```

### 4. Hardcoded structural assumptions

```python
# BAD
adr_dir = project_root / "docs" / "design" / "adr"
# GOOD
adr_dir = project_root / config.structure.design_root / "adr"
```

## Correct Pattern

```python
# GOOD: resolve from manifest/config, accept as parameter
def load_datasets(*, data_dir: Path | None = None) -> list[Dataset]:
    search_dir = data_dir or _resolve_from_config("eval_data_dir")
    ...
```

Resolution order: explicit parameter > config file > manifest > sensible default.

## Scan Commands

```bash
# Module-level root derivations
grep -rn "Path(__file__).*parents" src/

# Hardcoded path segments that should come from manifest.structure
grep -rn '"docs/design"' src/
grep -rn '"data/eval"' src/
grep -rn '"config/"' src/
grep -rn '"ops/chores"' src/
grep -rn '"artifacts/"' src/

# Magic numbers that should come from config
grep -rn "40\.0\|0\.5" src/gzkit/ --include="*.py" | grep -v test | grep -v "#"
```

## Workflow

### 1. Scan

Run all scan commands above. Categorize findings as:
- **Root derivation** — `Path(__file__).parents[N]`
- **Path literal** — hardcoded directory or filename strings
- **Magic value** — thresholds, limits, defaults embedded in logic
- **Structural assumption** — directory layouts assumed without config

### 2. Plan

For each finding:
1. Identify the config source (manifest, `.gzkit.json`, `config/*.json`)
2. Determine if the config key already exists or must be added
3. Plan parameter threading from entry point to usage

### 3. Implement

- Remove module-level constants
- Add function parameters with `None` defaults
- Resolve from config at the call site (CLI handler / command function)
- Update tests to pass explicit values

### 4. Validate

```bash
grep -rn "Path(__file__).*parents" src/
uv run ruff check .
uv run -m unittest -q
uv run gz check-config-paths
```

## Checklist

- [ ] Zero `Path(__file__).parents[N]` in `src/gzkit/` (excluding `__init__.py`)
- [ ] Path literals replaced with manifest/config lookups
- [ ] Threshold values pulled from config files
- [ ] All path-dependent functions accept explicit path parameters
- [ ] Tests pass with temp-dir paths (no implicit project root leakage)

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| outputNotContains | `grep -rn "Path(__file__).*parents" src/gzkit/eval/` | `parents` |
| outputNotContains | `grep -rn "Path(__file__).*parents" src/gzkit/hooks/` | `parents` |
| outputNotContains | `grep -rn "Path(__file__).*parents\[" src/gzkit/` | `parents[` |
| exitCodeEquals | `uv run gz lint` | 0 (includes parents-pattern lint) |
| exitCodeEquals | `uv run gz check-config-paths` | 0 (includes source path literal scan) |
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
grep -rn "Path(__file__).*parents" src/ > ops/chores/hardcoded-root-eradication/proofs/root-derivations.txt
grep -rn '"docs/design"\|"data/eval"\|"config/"\|"ops/chores"\|"artifacts/"' src/ > ops/chores/hardcoded-root-eradication/proofs/path-literals.txt
uv run -m unittest -q 2>&1 > ops/chores/hardcoded-root-eradication/proofs/tests.txt
```

---

**End of CHORE: Config-First Enforcement (Anti-Vibe-Code)**
