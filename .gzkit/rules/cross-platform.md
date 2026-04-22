---
id: cross-platform
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
description: Cross-platform development policy (Windows/macOS/Linux)
---

# Cross-Platform Development Policy (Binding)

**Platforms:** Windows (primary), macOS, Linux
**Doctrine:** ADR-0.0.1

---

## Quick Reference

| Category     | Use                             | Avoid                         |
| ------------ | ------------------------------- | ----------------------------- |
| Paths        | `Path("dir") / "file"`          | `"dir/file"` or `"dir\\file"` |
| Encoding     | `encoding="utf-8"`              | Default encoding              |
| Temp files   | Context managers                | Raw `shutil.rmtree()`         |
| Subprocess   | List form, `uv run`             | `shell=True`, bare `python`   |
| Cleanup      | Context managers, `gc.collect()` | `ignore_errors=True`          |
| Line endings | `newline=""` for CSV            | Hard-coded `\r\n`             |
| Console out  | Runtime UTF-8 config in entrypoint | Bare Unicode glyphs via Rich  |

---

## File Paths (Always pathlib.Path)

```python
from pathlib import Path
config_path = Path("config") / "settings.json"
config_path.read_text(encoding="utf-8")
```

---

## Encoding (Always UTF-8)

```python
Path("data.json").read_text(encoding="utf-8")
```

---

## Temporary Files (Context Managers)

```python
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir) / "data.json"
    # Cleanup automatic (Windows-safe)
```

---

## Subprocess (List Form)

```python
subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8")
subprocess.run(["uv", "run", "-m", "unittest"], check=True)
```

---

## Console Output (Rich / Unicode)

Rich uses Unicode glyphs (checkmarks, arrows, warning signs) that fail on Windows legacy console (cp1252).

**Runtime guard:** The CLI entrypoint handles UTF-8 configuration at startup (`sys.stdout.reconfigure(encoding="utf-8")`). No env-var prefix is needed.

**Agent guard:** Do NOT prefix shell commands with `PYTHONUTF8=1`. The runtime handles encoding.

```bash
uv run gz gates --adr ADR-0.1.0
```

### Scope boundary of the runtime guard (binding)

The runtime guard covers **only** `uv run gz ...` and `uv run -m gzkit ...`. Those invocations enter through the gzkit CLI entrypoint, which reconfigures `sys.stdout`/`sys.stderr` before emitting.

The runtime guard does **not** cover:

- `python -c "<script>"` one-liners (fresh interpreter, no reconfigure)
- `python tools/<helper>.py` / `uv run python <script>` (fresh interpreter)
- `jq` / `awk` / `sed` / other non-Python tools in the pipeline

Each of those is a fresh process. On Windows they default to `cp1252` and crash on any UTF-8 codepoint (em-dash, right-arrow, checkmark, etc.) in piped data — even when the gz output feeding them is perfectly UTF-8.

Observed failure class: agent pipes `uv run gz ... --json` through `python -c` to extract fields, a GHI title contains `→`, and the helper interpreter raises `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'`. The gz output is fine; the helper is the fault (GHI #234).

### Windows-safe helper patterns

| Invocation shape | Windows-safe form |
|---|---|
| `python -c "..."` processing gz output | **Prefer a gz-native path first** — check whether `uv run gz ...` already exposes the field. If not, use `uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); sys.stdin.reconfigure(encoding='utf-8'); <script>"` |
| Ad-hoc helper script `tools/<name>.py` | Same `sys.stdout.reconfigure` / `sys.stdin.reconfigure` block at the top of the script, before any `print` |
| `jq` / `awk` / other non-Python tool on Windows | Pipe the raw gz output to a file (`--output path.json`) and parse the file, or accept the UTF-8-unsafe shell is not supported |

**Preference order:** gz-native extraction > reconfigured `uv run python` > raw `python -c`. The first closes the class; the second hardens it; the third is the observed failure mode.

### Mechanical check

```bash
uv run gz validate --utf8-prefix
```

Scope (GHI #275):

- `PYTHONUTF8=1 uv run gz ...` env-prefix anti-pattern in `docs/**`, `.gzkit/skills/**`, `.claude/skills/**`, `features/**` (GHI #206 original).
- `gz ... | python[-c] ...` pipelines that omit `sys.stdout.reconfigure(encoding='utf-8')` inside the helper.
- `gz ... | jq|awk|sed` pipelines (non-Python tools — rule prescribes `--output path.json` file handoff).
- `tools/**/*.py` entry-point scripts (have `if __name__ == "__main__":` and call `print`) that omit `sys.stdout.reconfigure(encoding='utf-8')` at module load.

Waivers are explicit in `_UTF8_PIPE_WAIVERS` (`src/gzkit/governance/trust_audits.py`) per trust-doctrine T2 — closed-OBPI evidence files are waived rather than rewritten. Exits 3 on unwaived violations.

---

## Code Review Checklist

- [ ] All file operations use `pathlib.Path`
- [ ] All file I/O specifies `encoding="utf-8"`
- [ ] Temp files use context managers
- [ ] No `shell=True` in subprocess
- [ ] No hard-coded path separators
- [ ] Console output uses ASCII fallbacks or runtime UTF-8 config
- [ ] Ad-hoc `python -c` / helper scripts processing gz output configure UTF-8 stdin/stdout explicitly (runtime guard covers only `uv run gz ...`)
