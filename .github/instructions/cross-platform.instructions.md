---
applyTo: "src/**/*.py,tests/**/*.py"
---

# Cross-Platform Development Policy (Binding)

**Platforms:** Windows (primary), macOS, Linux
**Doctrine:** ADR-0.0.1

---

## Quick Reference

| Category     | ✅ Use                          | ❌ Avoid                      |
| ------------ | ------------------------------- | ----------------------------- |
| Paths        | `Path("dir") / "file"`          | `"dir/file"` or `"dir\\file"` |
| Encoding     | `encoding="utf-8"`              | Default encoding              |
| Temp files   | Context managers                | Raw `shutil.rmtree()`         |
| Subprocess   | List form, `uv run`             | `shell=True`, bare `python`   |
| Cleanup      | Context managers, `gc.collect()` | `ignore_errors=True`          |
| Line endings | `newline=""` for CSV            | Hard-coded `\r\n`             |

---

## File Paths (Always pathlib.Path)

```python
# ✅ RIGHT
from pathlib import Path
config_path = Path("config") / "settings.json"
config_path.read_text(encoding="utf-8")

# ❌ WRONG
config = "config/settings.json"  # Breaks on Windows
```

---

## Encoding (Always UTF-8)

```python
# ✅ RIGHT
Path("data.json").read_text(encoding="utf-8")
with open(path, "w", encoding="utf-8", newline="") as f:  # CSV

# ❌ WRONG
Path("data.json").read_text()  # Defaults to cp1252 on Windows
```

### stdout UTF-8 (Scripts with Unicode Output)

For scripts that print Unicode (box-drawing, emoji, non-ASCII):

```python
import sys

# ✅ PREFERRED - reconfigure stdout (Python 3.7+)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass  # Fall back to default encoding

# ✅ ALSO OK - TextIOWrapper (older pattern)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
```

Place this early in the script, before any print statements.

---

## Temporary Files

### Pattern 1: Context Manager (Preferred)

```python
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir) / "data.json"
    # Cleanup automatic (Windows-safe)
```

### Pattern 2: Manual Cleanup

```python
def tearDown(self):
    shutil.rmtree(self.temp_dir)
```

---

## Windows File Locking

**Problem:** Windows cannot delete files with open handles. Tests pass on Mac but fail with `PermissionError: WinError 32` on Windows.

**Solution:**

- Use context managers for file operations
- Call `gc.collect()` before cleanup if needed

---

## Subprocess

```python
# ✅ RIGHT - list form
subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8")
subprocess.run(["uv", "run", "-m", "unittest"], check=True)

# ❌ WRONG
subprocess.run("git status", shell=True)  # Shell injection risk
subprocess.run(["python", "-m", "unittest"])  # Which python?
```

---

## Rich Console (Preferred for User Output)

For scripts conveying rich information to users (tables, progress, styled text):

```python
# ✅ RIGHT - use Rich Console with encoding handling
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
table = Table(title="Status", box=box.ROUNDED)
table.add_column("Name")
table.add_column("Status")
table.add_row("item", "[green]OK[/green]")
console.print(table)
```

---

## Platform Checks (Rare)

Only use `sys.platform` for unavoidable platform-specific APIs:

```python
# ✅ OK - UTF-8 stdout workaround (when not using Rich)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ❌ WRONG - basic file operations
if sys.platform == "win32":
    path = Path("config\\file")  # Just use Path("/")
```

---

## Code Review Checklist

- [ ] All file operations use `pathlib.Path`
- [ ] All file I/O specifies `encoding="utf-8"`
- [ ] Temp files use context managers
- [ ] No raw `shutil.rmtree()` in tearDown
- [ ] No `shell=True` in subprocess
- [ ] No hard-coded path separators
- [ ] Rich output uses `Console()` with proper encoding

---

## References

- Test cleanup: `.github/instructions/tests.instructions.md`
- ADR: ADR-0.0.1
