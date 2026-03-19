# CHORE: Pythonic Refactoring

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `pythonic-refactoring`

---

## Overview

Enforce Pythonic idioms and type safety across the codebase using ruff (idioms/style) + ty (type correctness).

| Tool | Focus | What It Catches |
|------|-------|-----------------|
| **ruff** | Idioms & Style | Comprehensions, pathlib, early returns, simplification |
| **ty** | Type Correctness | Type mismatches, None-safety, protocol violations |

## Policy and Guardrails

- **Lane:** Lite — internal style, no external contract changes
- **Tools:** ruff + ty (both must pass)
- **No behavioral changes** — tests must pass after any refactoring

## Pythonic Rules Enforced

### ruff Rules (Style + Idioms)

| Code | Name | What It Enforces |
|------|------|------------------|
| `UP` | pyupgrade | Modern syntax (f-strings, type unions, match) |
| `SIM` | flake8-simplify | Cleaner patterns, ternaries, early returns |
| `C4` | flake8-comprehensions | List/dict/set comprehensions over loops |
| `PIE` | flake8-pie | Misc Pythonic patterns |
| `PTH` | flake8-use-pathlib | `pathlib` over `os.path` |
| `FURB` | refurb | Modern Python 3.10+ idioms |
| `RET` | flake8-return | Guard clauses, early returns |
| `TC` | flake8-type-checking | TYPE_CHECKING imports for perf |

### ty Rules (Type Safety)

All ~120 ty rules at default severity, including:

- `possibly-missing-attribute` — None-safety
- `invalid-assignment` — Type mismatches
- `unused-ignore-comment` — Stale `# type: ignore` comments
- `call-non-callable` — Runtime errors from bad calls

## Workflow

### 1. Baseline

```bash
uvx ruff check . > ops/chores/pythonic-refactoring/proofs/ruff-baseline.txt
uvx ty check . --exclude 'features/**' > ops/chores/pythonic-refactoring/proofs/ty-baseline.txt
```

### 2. Plan

Prioritize fixes by:

1. **Auto-fixable** — `ruff check --fix` handles most issues automatically
2. **High-value** — `PTH` (pathlib), `RET` (early returns) improve readability
3. **Type safety** — ty's `possibly-missing-attribute` prevents runtime errors

### 3. Implement

Apply Pythonic idioms. Most common patterns:

```python
# SIM105: Use contextlib.suppress() instead of try/except/pass
with contextlib.suppress(SomeError):
    do_something()

# PTH123: Use Path.open() instead of open()
data = path.read_text()

# RET505: Remove unnecessary else after return
if condition:
    return x
return y
```

### 4. Validate

```bash
uvx ruff check .
uvx ty check . --exclude 'features/**'
uv run -m unittest -q
```

## Quick Fix Commands

```bash
uvx ruff check . --fix
```

> Do NOT use `--unsafe-fixes` — TC003 moves imports into TYPE_CHECKING blocks, breaking Pydantic models.

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uvx ruff check .` | 0 |
| exitCodeEquals | `uvx ty check . --exclude 'features/**'` | 0 |
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uvx ruff check . > ops/chores/pythonic-refactoring/proofs/ruff-report.txt
uvx ty check . --exclude 'features/**' > ops/chores/pythonic-refactoring/proofs/ty-report.txt
```

## Run Log

| Run Date | ruff Before | ruff After | ty Before | ty After | Notes |
|----------|-------------|------------|-----------|----------|-------|
| _YYYY-MM-DD_ | _X_ | _Y_ | _A_ | _B_ | _modules improved_ |

---

**End of CHORE: Pythonic Refactoring**
