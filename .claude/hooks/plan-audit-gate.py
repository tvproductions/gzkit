#!/usr/bin/env python3
"""Plan Audit Gate Hook.

PreToolUse hook on ExitPlanMode that enforces the gz-plan-audit pre-flight
alignment check. If the most recent plan in .claude/plans/ references an OBPI,
the agent cannot exit plan mode until /gz-plan-audit has been run.

How it works:
  1. Finds the most recently modified plan file in .claude/plans/
  2. Checks if the plan references an OBPI ID (pattern: OBPI-X.Y.Z-NN)
  3. If yes, looks for an audit receipt at .claude/plans/.plan-audit-receipt.json
  4. Receipt must reference the same OBPI and be newer than the plan file
  5. No valid receipt -> exit 2 (blocked)

Receipt format (.claude/plans/.plan-audit-receipt.json):
  {
    "obpi_id": "OBPI-0.12.0-02",
    "timestamp": "2026-03-12T12:00:00Z",
    "verdict": "PASS"
  }

Exit codes:
  0 - Allow operation (no OBPI plan, or audit receipt valid)
  2 - Block operation (OBPI plan exists but no valid audit receipt)
"""

import json
import os
import re
import sys
from pathlib import Path

RECEIPT_FILE = ".plan-audit-receipt.json"
OBPI_PATTERN = re.compile(r"OBPI-[\d.]+-\d+")
NEW_FILE_PATTERNS = re.compile(
    r"\(new\)|\bcreate\s+`?(?:src|tests)/|new\s+file|new\s+module",
    re.IGNORECASE,
)
PRIOR_ART_PATTERNS = re.compile(
    r"existing\s+pattern|prior\s+art|/prior-art|registry|grep|"
    r"already\s+exist|codebase\s+inventory|search.*before|pattern\s+discovery",
    re.IGNORECASE,
)


def find_plans_dir(cwd: str) -> Path | None:
    """Return the project-local plans dir (used for receipt lookup)."""
    plans_dir = Path(cwd) / ".claude" / "plans"
    return plans_dir if plans_dir.is_dir() else None


def _claude_home() -> Path:
    """Return Claude home, honoring GZKIT_CLAUDE_HOME for test isolation."""
    override = os.environ.get("GZKIT_CLAUDE_HOME")
    return Path(override) if override else Path.home()


def plan_search_dirs(cwd: str) -> list[Path]:
    """Return both project-local and global plans dirs (#128).

    Claude Code's plan mode writes new plans to ``~/.claude/plans/`` by
    default. The historic project-local-only search produced a silent FAIL
    receipt that aborted the OBPI pipeline.
    """
    project_local = Path(cwd) / ".claude" / "plans"
    global_local = _claude_home() / ".claude" / "plans"
    seen: set[Path] = set()
    dirs: list[Path] = []
    for candidate in (project_local, global_local):
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved in seen or not candidate.is_dir():
            continue
        seen.add(resolved)
        dirs.append(candidate)
    return dirs


def find_most_recent_plan(plans_dir: Path) -> Path | None:
    """Find the most recent plan across both project-local and global dirs (#128)."""
    cwd_root = plans_dir.parent.parent
    md_files: list[Path] = []
    for search_dir in plan_search_dirs(str(cwd_root)):
        for path in search_dir.iterdir():
            if path.suffix == ".md" and not path.name.startswith("."):
                md_files.append(path)
    if not md_files:
        return None
    return max(md_files, key=lambda path: path.stat().st_mtime)


def extract_obpi_ids(plan_path: Path) -> list[str]:
    """Extract all referenced OBPI ids from a plan file."""
    try:
        content = plan_path.read_text(encoding="utf-8")
    except OSError:
        return []
    return list(set(OBPI_PATTERN.findall(content)))


def check_audit_receipt(
    plans_dir: Path, obpi_ids: list[str], plan_mtime: float
) -> tuple[bool, str]:
    """Check whether a valid audit receipt exists."""
    receipt_path = plans_dir / RECEIPT_FILE
    if not receipt_path.exists():
        return False, "No audit receipt found"

    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, "Audit receipt is corrupted"

    receipt_obpi = receipt.get("obpi_id", "")
    receipt_verdict = receipt.get("verdict", "")

    if receipt_obpi not in obpi_ids:
        return (
            False,
            f"Audit receipt is for {receipt_obpi}, but plan references {', '.join(obpi_ids)}",
        )

    receipt_mtime = receipt_path.stat().st_mtime
    if receipt_mtime < plan_mtime:
        return (
            False,
            "Audit receipt is older than plan file (plan was modified after audit)",
        )

    if receipt_verdict not in ("PASS", "FAIL"):
        return False, f"Audit receipt has invalid verdict: {receipt_verdict!r}"

    return True, f"Valid receipt: {receipt_obpi} -> {receipt_verdict}"


def check_prior_art_awareness(plan_path: Path) -> str | None:
    """Warn when new-file plans omit evidence of prior-art discovery."""
    try:
        content = plan_path.read_text(encoding="utf-8")
    except OSError:
        return None

    has_new_files = bool(NEW_FILE_PATTERNS.search(content))
    has_prior_art = bool(PRIOR_ART_PATTERNS.search(content))

    if has_new_files and not has_prior_art:
        return (
            "PRIOR ART REMINDER: Plan proposes new files but does not "
            "reference existing codebase patterns. Consider running "
            "/prior-art before implementing to avoid duplicating "
            "existing capabilities."
        )
    return None


def main() -> None:
    """Gate ExitPlanMode on gz-plan-audit completion."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())

    plans_dir = find_plans_dir(cwd)
    if not plans_dir:
        sys.exit(0)

    plan_file = find_most_recent_plan(plans_dir)
    if not plan_file:
        sys.exit(0)

    prior_art_warning = check_prior_art_awareness(plan_file)
    if prior_art_warning:
        print(prior_art_warning, file=sys.stderr)

    obpi_ids = extract_obpi_ids(plan_file)
    if not obpi_ids:
        sys.exit(0)

    is_valid, reason = check_audit_receipt(plans_dir, obpi_ids, plan_file.stat().st_mtime)
    if is_valid:
        sys.exit(0)

    print(
        f"BLOCKED: Cannot exit plan mode - plan audit required.\n"
        f"\n"
        f"Plan '{plan_file.name}' references: {', '.join(obpi_ids)}\n"
        f"Reason: {reason}\n"
        f"\n"
        f"REQUIRED: Run the pre-flight alignment audit first:\n"
        f"  /gz-plan-audit {obpi_ids[0]}\n"
        f"\n"
        f"This verifies ADR <-> OBPI <-> Plan alignment before "
        f"implementation begins.\n",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
