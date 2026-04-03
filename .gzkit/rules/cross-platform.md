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

---

## Code Review Checklist

- [ ] All file operations use `pathlib.Path`
- [ ] All file I/O specifies `encoding="utf-8"`
- [ ] Temp files use context managers
- [ ] No `shell=True` in subprocess
- [ ] No hard-coded path separators
- [ ] Console output uses ASCII fallbacks or runtime UTF-8 config
