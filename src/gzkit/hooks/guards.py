"""Policy enforcement guards.

Unittest-only policy enforcement: scan for pytest usage and reject it.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "site",
    "build",
    "dist",
    "htmlcov",
}

SCAN_EXTS = {".py", ".toml", ".ini", ".cfg", ".yaml", ".yml", ".txt"}

PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*import\s+pytest\b"),
    re.compile(r"^\s*from\s+pytest\s+import\b"),
    re.compile(r"\bpytest\."),
    re.compile(r"@\s*pytest\."),
    re.compile(r"\bpy\.test\b"),
]

EXCLUDE_PATH_SNIPPETS = (
    "/.venv/",
    "/venv/",
    "/env/",
    "/site/",
    "/build/",
    "/dist/",
    "/htmlcov/",
    "/site-packages/",
    # Allow pytest mentions in guard enforcement files themselves
    "/gzkit/hooks/guards.py",
)


def iter_files(root: Path) -> Iterable[Path]:
    """Iterate over files to scan, excluding common generated/virtual paths."""
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in EXCLUDE_DIRS:
                continue
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        posix = p.as_posix()
        if "/docs/" in posix or posix.startswith("docs/"):
            continue
        if any(snippet in posix for snippet in EXCLUDE_PATH_SNIPPETS) or posix.startswith("site/"):
            continue
        yield p


def scan_file(path: Path) -> list[str]:
    """Scan a single file for pytest usage violations.

    Returns list of violation messages (empty if clean).
    """
    violations: list[str] = []
    if path.name == "conftest.py":
        violations.append("contains pytest-specific conftest.py")
        return violations
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return [f"unreadable file: {e}"]

    if path.name in {"pyproject.toml", "requirements.txt", "requirements-dev.txt"}:
        if re.search(r"(?i)\bpytest\b", text):
            violations.append("declares pytest dependency")
        return violations

    for i, line in enumerate(text.splitlines(), start=1):
        for pat in PATTERNS:
            if pat.search(line):
                violations.append(f"L{i}: {line.strip()}")
                break
    return violations


def forbid_pytest() -> int:
    """Scan repository for pytest usage and return exit code.

    Returns:
        0 if no pytest usage found
        1 if pytest usage detected
    """
    root = Path(__file__).resolve().parents[3]
    findings: list[tuple[Path, list[str]]] = []
    for f in iter_files(root):
        v = scan_file(f)
        if v:
            findings.append((f, v))

    if findings:
        print("pytest usage detected; this repository enforces unittest-only.")
        for path, msgs in findings:
            print(f"- {path}")
            for m in msgs:
                print(f"    {m}")
        print("\nPlease remove pytest references or dependencies.")
        return 1
    return 0


def main() -> int:
    """Entry point for command-line usage."""
    return forbid_pytest()


if __name__ == "__main__":
    raise SystemExit(main())
