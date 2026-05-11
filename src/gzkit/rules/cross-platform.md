---
id: cross-platform
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
description: Cross-platform development policy (Windows primary, macOS, Linux)
---

<!-- rule-version: 0.3.0 -->

# Cross-Platform Development Policy (Binding)

> **Rule version:** `0.3.0` — diet pass under GHI #327; lifted helper patterns and scope-boundary details to `docs/governance/cross-platform-rationale.md`.

**Platforms:** Windows (primary), macOS, Linux | **Doctrine:** ADR-0.0.1

## Quick Reference

| Category     | Use                             | Avoid                         |
| ------------ | ------------------------------- | ----------------------------- |
| Paths        | `Path("dir") / "file"`          | `"dir/file"` or `"dir\\file"` |
| Rel. paths   | `.relative_to(root).as_posix()` | `str(.relative_to(root))`     |
| Encoding     | `encoding="utf-8"`              | Default encoding              |
| Temp files   | Context managers                | Raw `shutil.rmtree()`         |
| Subprocess   | List form, `uv run`             | `shell=True`, bare `python`   |
| Line endings | `newline=""` for CSV            | Hard-coded `\r\n`             |
| Console out  | Runtime UTF-8 config in entrypoint | Bare Unicode via Rich       |

## Render relative paths via `.as_posix()` (binding)

`str(Path.relative_to(root))` emits backslash on Windows. Always use `.as_posix()` when the result is compared against forward-slash literals, embedded in JSON/YAML/ledger, or stored on identifier fields. Enforced by `tests/governance/test_path_separator_portability.py` (GHI #383).

## Console / UTF-8 (binding)

The CLI entrypoint handles UTF-8 at startup. Do NOT prefix `uv run gz` with `PYTHONUTF8=1`. The runtime guard covers only `uv run gz ...` — fresh `python -c` or helper scripts need explicit `sys.stdout.reconfigure(encoding='utf-8')`. Enforced by `gz validate --utf8-prefix` (GHI #275).

## Code Review Checklist

- [ ] All file operations use `pathlib.Path`
- [ ] All file I/O specifies `encoding="utf-8"`
- [ ] Temp files use context managers
- [ ] No `shell=True` in subprocess
- [ ] No hard-coded path separators
- [ ] Relative paths rendered via `.as_posix()`

> See [`docs/governance/cross-platform-rationale.md`](../../docs/governance/cross-platform-rationale.md) for scope-boundary details, Windows-safe helper patterns, code examples, and mechanical check details.
