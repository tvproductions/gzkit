"""Shared git-sync readiness helpers."""

import os
from pathlib import Path
from typing import Any

from gzkit.utils import git_cmd

_readiness_cache: dict[str, dict[str, Any]] = {}


def invalidate_git_cache() -> None:
    """Clear the cached git readiness state.

    Call this after any operation that mutates git state (add, commit, push).
    """
    _readiness_cache.clear()


def _skip_tokens(skip_value: str) -> set[str]:
    """Parse pre-commit SKIP env format into normalized token set."""
    tokens: set[str] = set()
    for chunk in skip_value.split(","):
        for token in chunk.split():
            normalized = token.strip().lower()
            if normalized:
                tokens.add(normalized)
    return tokens


def _skip_disables_xenon(skip_tokens: set[str]) -> bool:
    """Return True when SKIP tokens can disable xenon complexity hooks."""
    if not skip_tokens:
        return False
    if "all" in skip_tokens or "xenon-complexity" in skip_tokens:
        return True
    return any(token.startswith("xenon") for token in skip_tokens)


def _compute_git_sync_state(project_root: Path, branch: str, remote: str) -> dict[str, Any]:
    """Compute ahead/behind/divergence against a remote branch."""
    warnings: list[str] = []
    ahead = 0
    behind = 0
    diverged = False

    rc_head, head, err_head = git_cmd(project_root, "rev-parse", branch)
    if rc_head != 0:
        warnings.append(err_head or f"Could not resolve local branch: {branch}")
        return {
            "head": None,
            "remote_head": None,
            "ahead": ahead,
            "behind": behind,
            "diverged": diverged,
            "warnings": warnings,
        }

    rc_remote, remote_head, err_remote = git_cmd(project_root, "rev-parse", f"{remote}/{branch}")
    if rc_remote != 0:
        warnings.append(err_remote or f"Could not resolve remote branch: {remote}/{branch}")
        return {
            "head": head,
            "remote_head": None,
            "ahead": ahead,
            "behind": behind,
            "diverged": diverged,
            "warnings": warnings,
        }

    rc_ahead, ahead_s, _ = git_cmd(
        project_root, "rev-list", "--count", f"{remote}/{branch}..{branch}"
    )
    rc_behind, behind_s, _ = git_cmd(
        project_root, "rev-list", "--count", f"{branch}..{remote}/{branch}"
    )
    if rc_ahead == 0 and ahead_s.isdigit():
        ahead = int(ahead_s)
    if rc_behind == 0 and behind_s.isdigit():
        behind = int(behind_s)
    diverged = ahead > 0 and behind > 0

    return {
        "head": head,
        "remote_head": remote_head,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "warnings": warnings,
    }


def _head_is_merge_commit(project_root: Path) -> bool:
    """Return True when HEAD itself is a merge commit."""
    rc_merge, merge_head, _ = git_cmd(project_root, "rev-list", "--max-count=1", "--merges", "HEAD")
    rc_head, head_sha, _ = git_cmd(project_root, "rev-parse", "HEAD")
    return rc_merge == 0 and rc_head == 0 and bool(merge_head) and merge_head == head_sha


def _git_status_lines(project_root: Path) -> tuple[list[str], str | None]:
    """Return porcelain status lines, or an error if status can't be read."""
    rc_status, status_out, err_status = git_cmd(project_root, "status", "--porcelain")
    if rc_status != 0:
        return [], err_status or "Could not read git status."
    lines = [line for line in status_out.splitlines() if line.strip()]
    return lines, None


def assess_git_sync_readiness(
    project_root: Path, remote: str = "origin", *, use_cache: bool = True
) -> dict[str, Any]:
    """Return sync-readiness state for OBPI completion validation.

    Results are cached within the process to avoid redundant subprocess calls.
    Pass ``use_cache=False`` to force a fresh capture (e.g., after git mutations).
    """
    cache_key = str(project_root.resolve())
    if use_cache and cache_key in _readiness_cache:
        return _readiness_cache[cache_key]

    blockers: list[str] = []
    warnings: list[str] = []

    skip_tokens = _skip_tokens(os.environ.get("SKIP", ""))
    if _skip_disables_xenon(skip_tokens):
        blockers.append(
            "Refusing completion validation with SKIP that can bypass xenon complexity checks."
        )

    rc_repo, inside, err_repo = git_cmd(project_root, "rev-parse", "--is-inside-work-tree")
    if rc_repo != 0 or inside != "true":
        blockers.append("Not a git repository.")
        return {
            "branch": None,
            "remote": remote,
            "dirty": False,
            "ahead": 0,
            "behind": 0,
            "diverged": False,
            "actions": [],
            "warnings": warnings,
            "blockers": blockers,
        }

    rc_branch, current_branch, err_branch = git_cmd(
        project_root, "rev-parse", "--abbrev-ref", "HEAD"
    )
    if rc_branch != 0:
        blockers.append(err_branch or "Could not determine current branch.")
        return {
            "branch": None,
            "remote": remote,
            "dirty": False,
            "ahead": 0,
            "behind": 0,
            "diverged": False,
            "actions": [],
            "warnings": warnings,
            "blockers": blockers,
        }

    if _head_is_merge_commit(project_root):
        blockers.append("Merge commit at HEAD. Linearize history before completion.")

    status_lines, status_error = _git_status_lines(project_root)
    if status_error:
        blockers.append(status_error)
    dirty = bool(status_lines)

    sync_state = _compute_git_sync_state(project_root, current_branch, remote)
    warnings.extend(sync_state["warnings"])
    ahead = sync_state["ahead"]
    behind = sync_state["behind"]
    diverged = sync_state["diverged"]

    actions: list[str] = []
    if dirty:
        actions.append("git add -A")
    actions.append(f"git fetch --prune {remote}")
    if diverged:
        actions.append(f"git pull --rebase {remote} {current_branch}")
    elif behind > 0:
        actions.append(f"git pull --ff-only {remote} {current_branch}")
    if ahead > 0 or diverged:
        actions.append(f"git push {remote} {current_branch}")

    result = {
        "branch": current_branch,
        "remote": remote,
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "actions": actions,
        "warnings": warnings,
        "blockers": blockers,
    }
    _readiness_cache[cache_key] = result
    return result
