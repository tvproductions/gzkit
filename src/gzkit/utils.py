"""Low-level utilities for gzkit.

Contains shared logic for shell execution, git, and string parsing.
"""

import re
import subprocess
from pathlib import Path


def run_exec(cmd: list[str], cwd: Path, timeout: int | None = None) -> tuple[int, str, str]:
    """Run a subprocess command and return (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
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


def resolve_git_head_commit(project_root: Path) -> str | None:
    """Return the current HEAD short SHA, or None when unavailable."""
    rc, head_sha, _err = git_cmd(project_root, "rev-parse", "--short=7", "HEAD")
    if rc == 0 and head_sha:
        return head_sha.strip()
    return None


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
) -> tuple[dict[str, str] | None, list[str]]:
    """Capture git anchor data and report degradations as warnings."""
    anchor: dict[str, str] = {}
    warnings: list[str] = []

    head_commit = resolve_git_head_commit(project_root)
    if head_commit:
        anchor["commit"] = head_commit
    else:
        warnings.append("Could not resolve HEAD commit for receipt anchor.")

    rc_tag, tag, err_tag = git_cmd(project_root, "tag", "--points-at", "HEAD")
    if rc_tag == 0 and tag:
        anchor["tag"] = tag.splitlines()[0].strip()
    elif rc_tag != 0 and err_tag:
        warnings.append(err_tag)

    if adr_id:
        semver_match = re.search(r"\d+\.\d+\.\d+", adr_id)
        if semver_match:
            anchor["semver"] = semver_match.group(0)
        else:
            warnings.append(f"Could not derive semver anchor from ADR ID: {adr_id}")
    else:
        warnings.append("Could not derive semver anchor: parent ADR ID missing.")

    if "commit" not in anchor or "semver" not in anchor:
        return None, warnings
    return anchor, warnings


def capture_validation_anchor(project_root: Path, adr_id: str | None = None) -> dict[str, str]:
    """Capture git commit and tag info for temporal anchoring."""
    anchor, warnings = capture_validation_anchor_with_warnings(project_root, adr_id)
    if anchor is not None:
        return anchor

    _ = warnings
    return {"commit": "0000000", "semver": "0.0.0"}
