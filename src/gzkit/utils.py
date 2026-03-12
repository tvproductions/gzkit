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


def capture_validation_anchor_with_warnings(
    project_root: Path,
    adr_id: str | None = None,
) -> tuple[dict[str, str] | None, list[str]]:
    """Capture git anchor data and report degradations as warnings."""
    anchor: dict[str, str] = {}
    warnings: list[str] = []

    rc_head, head_sha, err_head = git_cmd(project_root, "rev-parse", "HEAD")
    if rc_head == 0 and head_sha:
        anchor["commit"] = head_sha[:7]
    else:
        warnings.append(err_head or "Could not resolve HEAD commit for receipt anchor.")

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
