---
id: cross-platform
paths:
  - "src/**/*.py"
  - "src/gzkit/**/*.md"
  - "tests/**/*.py"
description: Cross-platform development policy (Windows, macOS, Linux — co-equal)
---

<!-- rule-version: 0.8.0 -->

# Cross-Platform Development Policy (Binding)

> **Rule version:** `0.8.0` — adds § Executable resolution: the package spawns a tool resolved off absolute `PATH` entries, never the current directory (RO-9 tranche 4, Ruff S607); version narrative in [Rule Version History](../../docs/governance/rule-version-history.md#cross-platformmd).

**Platforms:** Windows, macOS, Linux — co-equal. Max cross-platform; no platform is favored over another.

## Quick Reference

| Category     | Use                             | Avoid                         |
| ------------ | ------------------------------- | ----------------------------- |
| Paths        | `Path("dir") / "file"`          | `"dir/file"` or `"dir\\file"` |
| Rel. paths   | `.relative_to(root).as_posix()` | `str(.relative_to(root))`     |
| Encoding     | `encoding="utf-8"`              | Default encoding              |
| Temp files   | Context managers                | Raw `shutil.rmtree()`         |
| Subprocess   | List form, `uv run`, `resolve_argv` | `shell=True`, bare `python`   |
| Line endings | `newline=""` for CSV            | Hard-coded `\r\n`             |
| Console out  | Runtime UTF-8 config in entrypoint | Bare Unicode via Rich       |

## Render relative paths via `.as_posix()` (binding)

`str(Path.relative_to(root))` emits backslash on Windows. Always use `.as_posix()` when the result is compared against forward-slash literals, embedded in JSON/YAML/ledger, or stored on identifier fields. Enforced by `tests/governance/test_path_separator_portability.py` (GHI #383).

## Console / UTF-8 (binding)

The CLI entrypoint handles UTF-8 at startup. Do NOT prefix `uv run gz` with `PYTHONUTF8=1`. The runtime guard covers only `uv run gz ...` — fresh `python -c` or helper scripts need explicit `sys.stdout.reconfigure(encoding='utf-8')`. Enforced by `gz validate --utf8-prefix` (GHI #275).

## Delivered path literals (binding)

**Wheel-delivered instruction text names no path only its authoring environment can resolve.**

Content gzkit **delivers to another party** — every `.md` the uv_build wheel
ships (the `[tool.uv.build-backend]` module tree minus its excludes) — MUST NOT
name a path that only the authoring environment can resolve. This widens the section above from
platform portability to *environment* portability: a literal rooted at
`/Users/<name>/` fails on a second Mac, not only on Linux.

Fails closed: a named user's home (`/Users/<name>/`, `/home/<name>/`), a
Windows drive root (`<Drive>:\` or `<Drive>:/`), and machine-provisioning roots
(`/opt/`, `/srv/`, `/mnt/`).

Portable forms — use these: an explicit override the reader supplies (an env
var carrying **no default**), a repo-relative path, or `~/` / `$HOME/`, which
expand per reader. Deliberately NOT flagged: `~/`, `$HOME/`, and `/tmp`,
`/usr`, `/var`, `/private`, which resolve on every POSIX machine. A
machine-specific path under one of those roots is a limit of this clause,
stated rather than implied.

**Remove the prose with the path.** If a required step becomes unsatisfiable
once the machine-local default is gone, say plainly that the step is skipped
and the resulting disposition is provisional. A missing review surface is a
recorded limitation of the run, never a silent pass — converting a
maintainer-only step into a silent skip is a worse defect than the literal.

Enforced by `gz validate --wheel-path-literals` (default `gz check` scope),
implemented in `src/gzkit/governance/trust_audits/wheel_path_literals.py` and
tested at `tests/governance/test_wheel_path_literals.py`. The audit reads the
same wheel prediction `--distribution` reads, so witness scope cannot drift from
delivery scope. This section is the canonical rule home; the validator is its
enforcement artifact, not the rule itself. Placeholder forms like
`/Users/<name>/` are inert by construction, which is how this rule names the
shape it forbids without tripping its own witness.

## Executable resolution (binding)

The shipped package never hands a bare tool name to the operating system: on Windows `CreateProcess`, and `shutil.which` with it, try the current directory before `PATH`, so a `git.exe` committed to a repository gzkit runs inside would be the one spawned. Spawn through `gzkit.executables` — `resolve_executable("git")` in a literal argv, `resolve_argv(argv)` for a variable one, `find_executable` for a presence probe — which reads absolute `PATH` entries only. Resolve inside the call, so a recorded argv keeps the bare, portable name. Enforced over `src/gzkit` by Ruff S607 under `gz lint`, with `tests/test_executables.py` holding the search order; tests, features and scripts spawn into their own temporary repositories and carry S607 in their curated exception list (operator ruling 2026-10-24, *"Package fixed, tests curated (Rec.)"*).

## Subprocess reads (binding)

Every text-mode subprocess capture that decodes sub-process stdout/stderr MUST pass `errors="replace"`. `encoding="utf-8"` alone is insufficient: tool/git output on non-UTF-8 locales (cp1252/latin-1) raises `UnicodeDecodeError` — a `ValueError`, so `except (OSError, subprocess.SubprocessError)` does not catch it and the command aborts mid-run. Text mode means `text=True`, `encoding=`, or `universal_newlines=True` combined with a capture (`check_output`, `capture_output=True`, `stdout=PIPE`). Mirror the good pattern at `src/gzkit/quality.py::run_command`. Do NOT add `errors=` to a bytes-mode call — it silently enables text mode and flips the return type. Enforced by `tests/governance/test_subprocess_errors_replace.py` via `audit_subprocess_errors` (GHI #582).

## Code Review Checklist

- [ ] All file operations use `pathlib.Path`
- [ ] All file I/O specifies `encoding="utf-8"`
- [ ] Text-mode subprocess captures pass `errors="replace"`
- [ ] Temp files use context managers
- [ ] No `shell=True` in subprocess
- [ ] Package spawns resolve their executable through `gzkit.executables`
- [ ] No hard-coded path separators
- [ ] Relative paths rendered via `.as_posix()`

> See [`docs/governance/cross-platform-rationale.md`](../../docs/governance/cross-platform-rationale.md) for scope-boundary details, Windows-safe helper patterns, code examples, and mechanical check details.
