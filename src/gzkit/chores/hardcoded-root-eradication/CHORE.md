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
CHORES_DIR = ".gzkit/chores"
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
grep -rn '".gzkit/chores"' src/
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
| exitCodeEquals | `uv run gz lint` | 0 (includes parents-pattern lint) |
| exitCodeEquals | `uv run gz check-config-paths` | 0 (includes source path literal scan) |
| exitCodeEquals | `uv run -m unittest -q` | 0 |

> **Do not re-add any `grep` for `Path(__file__).*parents` (GHI #782).** All three
> are gone — the repo-wide one and the two per-directory ones over
> `src/gzkit/eval/` and `src/gzkit/hooks/`.
>
> `gz lint` — the first criterion above — asserts the property, and asserts it
> better: `gzkit.quality._find_parents_access_lines` walks the AST over
> `src/gzkit/**/*.py`, a scope that strictly contains every directory the greps
> covered, so it matches the *expression* and never the text. Its docstring states
> the difference: *"String literals and comments containing the pattern text are
> not flagged."*
>
> The repo-wide grep was a strictly weaker duplicate and went first. It needed
> `--exclude=quality.py` because the detector necessarily contains the pattern it
> detects, and it failed on a comment in `check_module_size.py` documenting
> *compliance* with this very chore — so complying with the rule and explaining the
> compliance broke its checker. Tightening the regex to skip `#` lines would only
> have moved the blind spot into docstrings; a second `--exclude` would have bought
> one file an exemption and left the next author to buy their own (the shape
> GHI #779 argued against).
>
> **The two per-directory greps were NOT redundant when the first was deleted, and
> that distinction is the point.** The detector matched only `ast.Subscript`, so
> `Path(__file__).parents[2]` was caught while `for p in Path(__file__).parents:`
> was not — and the greps caught both. Deleting them on the redundancy argument
> alone would have silently dropped real coverage. The detector was widened to flag
> `.parents` attribute access whether or not it is subscripted
> (`test_non_subscript_parents_access_detected`) FIRST; only then did the greps
> become safe to remove. `Path(__file__).parent` (singular) is a different
> attribute, is not a positional walk, and is still allowed.

## Evidence Commands

```bash
grep -rn "Path(__file__).*parents" src/ > .gzkit/chores/hardcoded-root-eradication/proofs/root-derivations.txt
grep -rn '"docs/design"\|"data/eval"\|"config/"\|".gzkit/chores"\|"artifacts/"' src/ > .gzkit/chores/hardcoded-root-eradication/proofs/path-literals.txt
uv run -m unittest -q 2>&1 > .gzkit/chores/hardcoded-root-eradication/proofs/tests.txt
```

---

**End of CHORE: Config-First Enforcement (Anti-Vibe-Code)**
