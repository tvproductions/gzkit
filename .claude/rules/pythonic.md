---
paths:
  - "**/*.py"
---

# Pythonic Standards (Idiomatic Code Contract)

## Core Principles

1. **Clarity over cleverness** — explicit, readable, consistent code
2. **Separation of concerns** — isolate IO, transforms, QC, persistence
3. **Typed interfaces** — enforce with `uvx ty check .`
4. **EAFP for IO, LBYL for contracts** — clear error boundaries
5. **Context managers** — for files, DBs, sessions, progress phases
6. **No mutable defaults** — use `None` + factory
7. **Pydantic BaseModel for data** — TypedDict for shapes; see models policy
8. **Explicit exceptions** — typed errors; **no bare `except:` / `except Exception:`**
9. **Small units** — ≤50 lines/function, ≤600 lines/module, ≤300 lines/class
10. **No implicit globals** — explicit configuration and state

## Size Limits & Refactoring

**Limits:** Functions ≤50 lines | Modules ≤600 lines | Classes ≤300 lines

**When to refactor:** Module >600 (split by concern) | Function >50 (extract helpers) | Class >300 (SRP, mixins) | Deeply nested >3 levels (early returns, guards)

**Process:** Stop, explain violation, propose plan, estimate effort, wait for approval.

**Exceptions:** Generated code, vendored libs, data tables, CLI parsers (with justification)

## Architecture & Typing

**Structure:** Packages by concern (`commands/`, `hooks/`, `models/`, `schemas/`). Public API via `__all__`.

**Typing:** Use `ty` for static checking. Public APIs annotated. `TypedDict` for shapes, Pydantic `BaseModel` for records. `# type: ignore` needs justification. No untyped new code.

**Stack:** `ty` (static+runtime) + `ruff` + `xenon` + `vulture` + `unittest`. Typing is **governed and attested**—no alternatives without ADR.

## Imports (PEP 8)

- **Top-level imports only.** Standard library, third-party, then local. One import per line.
- **No lazy imports** (imports inside functions/blocks) unless required for optional dependencies or to avoid import-time side effects/cycles.
- **Required waiver:** inline rationale + `# noqa: PLC0415` on the lazy import line.
- **Do not use lazy imports** for micro-optimizations or convenience; prefer top-level imports and dependency injection.

## Error Handling

**Types:** Use `core.errors` (`TransientError`, `ConfigError`, `DataError`, `SystemError`, `LogicError`). Always raise meaningful exceptions. Retries via `core.retry`.

**Blind-except (non-negotiable):** Forbidden: `except Exception:` / bare `except:`. Catch specific exceptions, translate to `core.errors`. CLI may catch once, wrap, render error, exit non-zero.

### Exception Handling Guidelines

**Never use `except Exception:` — always catch specific exception types.**

1. **Identify what can actually fail** in the code block:
    - File I/O: `OSError`, `FileNotFoundError`, `PermissionError`
    - Parsing: `ValueError`, `json.JSONDecodeError`, `KeyError`
    - Network: `TimeoutError`, `ConnectionError`, `OSError`, `playwright.sync_api.Error`, `playwright.sync_api.TimeoutError`
    - Database: `sqlite3.Error`, `sqlite3.IntegrityError`
    - Type issues: `TypeError`, `AttributeError`
    - Import issues: `ImportError`, `ModuleNotFoundError`

2. **Use specific exception unions**:

    ```python
    # ✅ GOOD - specific exceptions
    try:
        data = json.loads(Path(config_path).read_text())
    except (OSError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Config load failed: {e}")
    ```

3. **Avoid broad catches**:

    ```python
    # ❌ BAD - too broad
    try:
        do_something()
    except Exception as e:
        pass
    ```

4. **Boundary exceptions only** - Use `Exception` only at CLI entry points or top-level boundaries, with `# noqa: BLE001` and justification:

    ```python
    # ✅ ACCEPTABLE - boundary catch-all with justification
    try:
        main()
    except Exception as e:  # noqa: BLE001 - CLI boundary catch-all
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)
    ```

5. **Fail fast** - When unsure, be too specific and let unexpected errors bubble up rather than silencing them. It's better to crash with a clear traceback than hide bugs.

## Verbosity & Progress

Governed by `ProgressManager`. Screen-only Rich output. Flags: `--quiet` (summary) | default (table/bars) | `-v` (diagnostics) | `-vv` (substeps) | `--no-color`. Long ops use `ProgressManager` phases.

## Testing

Mock external boundaries (network, filesystem, DB). Verify evidence/reports, exit codes {0,2,3}. Fast suite <5s. Cover error and success paths.

**Style guards:** Test for `except Exception`/bare `except` outside approved files. Verify exception translation.

## Toolchain (Astral)

| Tool         | Role                  | Command                 |
| ------------ | --------------------- | ----------------------- |
| **uv**       | Environment/execution | `uv run` / `uvx`        |
| **ruff**     | Linting/formatting    | `uv run ruff check .`   |
| **ty**       | Static typing         | `uvx ty check .`        |
| **unittest** | Testing               | `uv run -m unittest -q` |

**Local workflow:**

```bash
uv run ruff check . --fix && uv run ruff format .
uvx ty check .
uv run -m unittest -q
```

**CI gates:** All above commands must pass. CI blocks failing PRs.

## Review Checklist

- [ ] Small, cohesive units (≤50/≤600/≤300 line limits)
- [ ] Public surfaces typed; ty passes
- [ ] PEP 8 clean (ruff E/W); imports at top-level
- [ ] No lazy imports without explicit waiver (`# noqa: PLC0415` + rationale)
- [ ] Structured exceptions; no bare `except`/`except Exception:`
- [ ] ProgressManager used; verbosity respected
- [ ] Tests for error and success paths
- [ ] Ruff + ty + unittest green

## Performance

Use iterators/generators for large data. Batch DB operations with context-managed transactions. Avoid full in-memory archive loads.

## Enforcement

PRs and CI enforce this file. Deviations require documented ADR.

**Ruff config (recommended):** Enable `BLE001` (flake8-blind-except). Scope ignores to specific files if needed:

```toml
[lint]
select = ["E", "F", "I", "BLE"]
[lint.per-file-ignores]
"src/gzkit/cli.py" = ["BLE001"]
```
