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


def capture_validation_anchor(project_root: Path, adr_id: str | None = None) -> dict[str, str]:
    """Capture git commit and tag info for temporal anchoring."""
    anchor = {}

    # 1. Capture Commit SHA
    rc_head, head_sha, _ = git_cmd(project_root, "rev-parse", "HEAD")
    if rc_head == 0 and head_sha:
        anchor["commit"] = head_sha[:7]

    # 2. Capture Tag (if any)
    rc_tag, tag, _ = git_cmd(project_root, "tag", "--points-at", "HEAD")
    if rc_tag == 0 and tag:
        anchor["tag"] = tag.splitlines()[0].strip()

    # 3. Resolve SemVer
    if adr_id:
        semver_match = re.search(r"\d+\.\d+\.\d+", adr_id)
        if semver_match:
            anchor["semver"] = semver_match.group(0)

    # Ensure required fields exist even if git fails
    if "commit" not in anchor:
        anchor["commit"] = "0000000"
    if "semver" not in anchor:
        anchor["semver"] = "0.0.0"

    return anchor
