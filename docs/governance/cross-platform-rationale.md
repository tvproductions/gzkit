# Cross-Platform Development — Rationale

*Lifted from `.gzkit/rules/cross-platform.md` under GHI #327 diet pass.
The binding rule remains canonical in `.gzkit/rules/cross-platform.md`;
this page holds code examples, helper patterns, and scope-boundary details.*

## Code Examples

### File Paths (Always pathlib.Path)

```python
from pathlib import Path
config_path = Path("config") / "settings.json"
config_path.read_text(encoding="utf-8")
```

### Relative path rendering

```python
# Correct — POSIX separators on every platform
rel = path.relative_to(project_root).as_posix()
console.print(f"  Brief: {brief.relative_to(project_root).as_posix()}")

# Wrong — emits backslash on Windows
rel = str(path.relative_to(project_root))
console.print(f"  Brief: {brief.relative_to(project_root)}")
```

### Temporary Files (Context Managers)

```python
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir) / "data.json"
    # Cleanup automatic (Windows-safe)
```

### Subprocess (List Form)

```python
subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8")
subprocess.run(["uv", "run", "-m", "unittest"], check=True)
```

## Scope boundary of the runtime UTF-8 guard

The runtime guard covers **only** `uv run gz ...` and `uv run -m gzkit ...`.
It does **not** cover:

- `python -c "<script>"` one-liners (fresh interpreter, no reconfigure)
- `python tools/<helper>.py` / `uv run python <script>` (fresh interpreter)
- `jq` / `awk` / `sed` / other non-Python tools in the pipeline

Each is a fresh process defaulting to `cp1252` on Windows.

### Windows-safe helper patterns

| Invocation shape | Windows-safe form |
|---|---|
| `python -c "..."` processing gz output | Prefer a gz-native path first; if not, use `uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); ..."` |
| Ad-hoc helper script `tools/<name>.py` | `sys.stdout.reconfigure` / `sys.stdin.reconfigure` at top |
| `jq` / `awk` on Windows | Pipe to file (`--output path.json`) and parse the file |

**Preference order:** gz-native extraction > reconfigured `uv run python` > raw `python -c`.

## Mechanical check

```bash
uv run gz validate --utf8-prefix
```

Scope (GHI #275): `PYTHONUTF8=1` prefix on `uv run gz` invocations, gz-to-python
pipe patterns without reconfigure, `tools/**/*.py` entry-points without
reconfigure. Waivers in `_UTF8_PIPE_WAIVERS`. Exits 3 on unwaived violations.

## Origin

GHI #327 — instructions-files-diet pass (2026-05-07).
