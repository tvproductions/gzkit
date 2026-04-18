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
    # Allow pytest mentions in the guards test module (tests must exercise the detected patterns)
    "/tests/test_hooks_guards.py",
)


def iter_files(root: Path) -> Iterable[Path]:
    """Iterate over files to scan, excluding common generated/virtual paths."""
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        # Prune any descendant of an excluded directory (rglob does not prune).
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts[:-1]):
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


def forbid_pytest(root: Path) -> int:
    """Scan repository for pytest usage and return exit code.

    Args:
        root: Project root directory to scan.

    Returns:
        0 if no pytest usage found
        1 if pytest usage detected

    """
    findings: list[tuple[Path, list[str]]] = []
    for f in iter_files(root):
        v = scan_file(f)
        if v:
            findings.append((f, v))

    if findings:
        print("pytest usage detected; this repository enforces unittest-only.")  # noqa: T201
        for path, msgs in findings:
            _safe_print(f"- {path}")
            for m in msgs:
                _safe_print(f"    {m}")
        print("\nPlease remove pytest references or dependencies.")  # noqa: T201
        return 1
    return 0


def _safe_print(s: str) -> None:
    """Print a string with ASCII-escape fallback for narrow-encoding terminals.

    The pre-commit hook invocation path (``uv run -m gzkit.hooks.guards``)
    bypasses the CLI entrypoint's ``sys.stdout.reconfigure(encoding='utf-8')``
    guard, so finding output that contains non-ASCII bytes can raise
    ``UnicodeEncodeError`` on Windows cp1252 terminals. Fall back to a
    backslash-escaped ASCII form rather than crashing the hook.
    """
    try:
        print(s)  # noqa: T201
    except UnicodeEncodeError:
        print(s.encode("ascii", "backslashreplace").decode("ascii"))  # noqa: T201


def _run_git(args: list[str], cwd: Path) -> str:
    """Return stdout of ``git <args>`` from ``cwd``; empty string on failure."""
    import subprocess  # noqa: PLC0415

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, OSError):
        return ""
    return result.stdout or ""


def forbid_manual_ledger_edits(root: Path) -> int:
    """Reject staged ledger edits that are not strict appends (GHI #207).

    Every write to ``.gzkit/ledger.jsonl`` must go through ``gz`` commands,
    which append-only. A staged diff that modifies or deletes existing lines
    is a manual-edit signal and fails closed. New trailing append-only lines
    are allowed — the agent may have legitimately emitted an event via
    ``gz`` before staging.
    """
    staged = _run_git(["diff", "--cached", ".gzkit/ledger.jsonl"], root)
    if not staged:
        return 0
    # Hunks: look for ``-`` lines that aren't ``---`` or ``+++``, and ``+``
    # lines that aren't ``+++``. A strict append only contains ``+`` bodies
    # after the final hunk header; no ``-`` bodies anywhere.
    for raw in staged.splitlines():
        if raw.startswith("---") or raw.startswith("+++"):
            continue
        if raw.startswith("-") and not raw.startswith("--"):
            _safe_print(
                "Manual edit to .gzkit/ledger.jsonl detected — ledger is "
                "append-only via gz commands (CLAUDE.md governance rule 16)."
            )
            _safe_print(f"  offending line: {raw}")
            return 1
    return 0


def forbid_skill_sync_drift(root: Path) -> int:
    """Reject canonical skill/rule edits without their vendor mirrors (GHI #210).

    Every change to ``.gzkit/skills/**/SKILL.md`` must carry its
    ``.claude/skills/<same-path>`` mirror in the same commit. Same for
    ``.gzkit/rules/**`` and ``.claude/rules/**`` / ``.github/instructions/**``.
    The mirror is generated by ``gz agent sync control-surfaces`` — if it's
    missing from the staged diff, sync was skipped.
    """
    staged = _run_git(["diff", "--cached", "--name-only"], root)
    if not staged:
        return 0
    staged_paths = {line.strip() for line in staged.splitlines() if line.strip()}

    errors: list[str] = []
    for path in sorted(staged_paths):
        if path.startswith(".gzkit/skills/") and path.endswith("SKILL.md"):
            rel = path[len(".gzkit/skills/") :]
            mirror_claude = f".claude/skills/{rel}"
            mirror_github = f".github/skills/{rel}"
            if mirror_claude not in staged_paths and mirror_github not in staged_paths:
                errors.append(
                    f"{path} edited without `{mirror_claude}` / `{mirror_github}` "
                    "mirror. Run `uv run gz agent sync control-surfaces`."
                )
        if path.startswith(".gzkit/rules/") and path.endswith(".md"):
            rel = path[len(".gzkit/rules/") :]
            mirror_claude = f".claude/rules/{rel}"
            mirror_github = f".github/instructions/{rel}"
            if mirror_claude not in staged_paths and mirror_github not in staged_paths:
                errors.append(
                    f"{path} edited without `{mirror_claude}` / `{mirror_github}` "
                    "mirror. Run `uv run gz agent sync control-surfaces`."
                )
    if errors:
        _safe_print("Skill/rule sync drift detected:")
        for err in errors:
            _safe_print(f"  - {err}")
        return 1
    return 0


def main() -> int:
    """Entry point for command-line usage."""
    root = Path.cwd()
    rc = forbid_pytest(root)
    if rc:
        return rc
    rc = forbid_manual_ledger_edits(root)
    if rc:
        return rc
    rc = forbid_skill_sync_drift(root)
    if rc:
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
