---
id: cross-platform
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
description: Cross-platform development policy (Windows, macOS, Linux — co-equal)
---

<!-- rule-version: 0.5.0 -->

# Cross-Platform Development Policy (Binding)

> **Rule version:** `0.5.0` — added § Subprocess reads (GHI #582): text-mode subprocess captures MUST pass `errors="replace"`, since `encoding="utf-8"` alone still raises `UnicodeDecodeError` (a `ValueError` that `except OSError` misses) on non-UTF-8 tool/git output. Prior `0.4.0` — corrected the platform framing: removed the inaccurate "Windows (primary)" label and the miscited `Doctrine: ADR-0.0.1` reference (ADR-0.0.1 is canonical-govzero-parity; no cross-platform ADR exists). gzkit targets all platforms co-equally (operator directive 2026-06-28). Prior `0.3.0` — diet pass under GHI #327; lifted helper patterns and scope-boundary details to `docs/governance/cross-platform-rationale.md`.

**Platforms:** Windows, macOS, Linux — co-equal. Max cross-platform; no platform is favored over another.

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

## Subprocess reads (binding)

Every text-mode subprocess capture that decodes sub-process stdout/stderr MUST pass `errors="replace"`. `encoding="utf-8"` alone is insufficient: tool/git output on non-UTF-8 locales (cp1252/latin-1) raises `UnicodeDecodeError` — a `ValueError`, so `except (OSError, subprocess.SubprocessError)` does not catch it and the command aborts mid-run. Text mode means `text=True`, `encoding=`, or `universal_newlines=True` combined with a capture (`check_output`, `capture_output=True`, `stdout=PIPE`). Mirror the good pattern at `src/gzkit/quality.py::run_command`. Do NOT add `errors=` to a bytes-mode call — it silently enables text mode and flips the return type. Enforced by `tests/governance/test_subprocess_errors_replace.py` via `audit_subprocess_errors` (GHI #582).

## Code Review Checklist

- [ ] All file operations use `pathlib.Path`
- [ ] All file I/O specifies `encoding="utf-8"`
- [ ] Text-mode subprocess captures pass `errors="replace"`
- [ ] Temp files use context managers
- [ ] No `shell=True` in subprocess
- [ ] No hard-coded path separators
- [ ] Relative paths rendered via `.as_posix()`

> See [`docs/governance/cross-platform-rationale.md`](../../docs/governance/cross-platform-rationale.md) for scope-boundary details, Windows-safe helper patterns, code examples, and mechanical check details.
