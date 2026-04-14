"""Low-level utilities for gzkit.

Contains shared logic for shell execution, git, and string parsing.
"""

import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gzkit.events import EventAnchor


def run_exec(cmd: list[str], cwd: Path, timeout: int | None = None) -> tuple[int, str, str]:
    """Run a subprocess command and return (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"


def git_cmd(project_root: Path, *args: str) -> tuple[int, str, str]:
    """Run git command in project root."""
    return run_exec(["git", *args], cwd=project_root)


_git_cache: dict[str, str | None] = {}


def resolve_git_head_commit(project_root: Path) -> str | None:
    """Return the current HEAD short SHA, or None when unavailable.

    Cached within the process to avoid redundant subprocess calls.
    """
    key = f"head:{project_root}"
    if key in _git_cache:
        return _git_cache[key]
    rc, head_sha, _err = git_cmd(project_root, "rev-parse", "--short=7", "HEAD")
    result = head_sha.strip() if rc == 0 and head_sha else None
    _git_cache[key] = result
    return result


def list_changed_files_between(
    project_root: Path,
    base_ref: str,
    target_ref: str = "HEAD",
) -> list[str] | None:
    """Return changed files between two refs, or None when git cannot resolve them."""
    rc, stdout, _err = git_cmd(project_root, "diff", "--name-only", f"{base_ref}..{target_ref}")
    if rc != 0:
        return None
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def capture_validation_anchor_with_warnings(
    project_root: Path,
    adr_id: str | None = None,
) -> "tuple[EventAnchor | None, list[str]]":
    """Capture git anchor data and report degradations as warnings.

    Returns a typed ``EventAnchor`` when both commit and semver can be
    resolved; returns ``None`` with accumulated warnings when the anchor
    is degraded (missing required fields). The typed return shape replaces
    the legacy ``dict[str, str] | None`` per GHI #143.
    """
    from gzkit.events import EventAnchor

    warnings: list[str] = []

    head_commit = resolve_git_head_commit(project_root)
    if not head_commit:
        warnings.append("Could not resolve HEAD commit for receipt anchor.")

    tag_value: str | None = None
    rc_tag, tag, err_tag = git_cmd(project_root, "tag", "--points-at", "HEAD")
    if rc_tag == 0 and tag:
        tag_value = tag.splitlines()[0].strip()
    elif rc_tag != 0 and err_tag:
        warnings.append(err_tag)

    semver_value: str | None = None
    if adr_id:
        semver_match = re.search(r"\d+\.\d+\.\d+", adr_id)
        if semver_match:
            semver_value = semver_match.group(0)
        else:
            warnings.append(f"Could not derive semver anchor from ADR ID: {adr_id}")
    else:
        warnings.append("Could not derive semver anchor: parent ADR ID missing.")

    if head_commit is None or semver_value is None:
        return None, warnings
    return EventAnchor(commit=head_commit, tag=tag_value, semver=semver_value), warnings


def capture_validation_anchor(project_root: Path, adr_id: str | None = None) -> "EventAnchor":
    """Capture git commit and tag info for temporal anchoring.

    Degraded fallback returns a sentinel ``EventAnchor`` with zeroed commit
    and semver so downstream consumers always receive a typed value.
    """
    from gzkit.events import EventAnchor

    anchor, warnings = capture_validation_anchor_with_warnings(project_root, adr_id)
    if anchor is not None:
        return anchor

    _ = warnings
    return EventAnchor(commit="0000000", semver="0.0.0")
