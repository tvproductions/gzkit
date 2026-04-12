"""Git-sync command implementation."""

import json
import os
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    GzCliError,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.git_sync import (
    _compute_git_sync_state,
    _git_status_lines,
    _head_is_merge_commit,
    _skip_disables_xenon,
    _skip_tokens,
)
from gzkit.quality import run_behave, run_lint, run_tests
from gzkit.utils import git_cmd

GIT_SYNC_SKILL_PATH = ".gzkit/skills/git-sync/SKILL.md"


def _plan_git_sync(
    project_root: Path,
    current_branch: str,
    target_branch: str,
    remote: str,
    apply: bool,
    auto_add: bool,
    allow_push: bool,
) -> dict[str, Any]:
    """Build sync plan and compute branch state/blockers."""
    actions: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if current_branch != target_branch:
        blockers.append(f"Not on branch {target_branch} (current: {current_branch})")

    if _head_is_merge_commit(project_root):
        blockers.append("Merge commit at HEAD. Linearize history before git-sync.")

    status_lines, status_error = _git_status_lines(project_root)
    if status_error:
        blockers.append(status_error)
    dirty = bool(status_lines)

    if dirty and auto_add:
        actions.append("git add -A")

    actions.append(f"git fetch --prune {remote}")

    if apply and not blockers:
        rc_fetch, _out_fetch, err_fetch = git_cmd(project_root, "fetch", "--prune", remote)
        if rc_fetch != 0:
            blockers.append(err_fetch or f"Fetch failed for remote {remote}.")

    sync_state = _compute_git_sync_state(project_root, target_branch, remote)
    warnings.extend(sync_state["warnings"])
    ahead = sync_state["ahead"]
    behind = sync_state["behind"]
    diverged = sync_state["diverged"]

    if diverged:
        actions.append(f"git pull --rebase {remote} {target_branch}")
    elif behind > 0:
        actions.append(f"git pull --ff-only {remote} {target_branch}")

    if allow_push and (ahead > 0 or diverged):
        actions.append(f"git push {remote} {target_branch}")

    if not apply and dirty and not auto_add:
        blockers.append("Working tree is dirty. Use --auto-add or clean it before applying sync.")

    return {
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "actions": actions,
        "blockers": blockers,
        "warnings": warnings,
    }


def _enforce_git_sync_skip_policy() -> None:
    """Block git-sync when SKIP can bypass xenon complexity enforcement."""
    skip_raw = os.environ.get("SKIP", "")
    tokens = _skip_tokens(skip_raw)
    if not _skip_disables_xenon(tokens):
        return
    msg = (
        "Refusing git-sync with SKIP that can bypass xenon complexity checks. Unset SKIP and rerun."
    )
    raise GzCliError(msg)  # noqa: TRY003


def _run_sync_prechecks(
    project_root: Path,
    run_lint_gate: bool,
    run_test_gate: bool,
    blockers: list[str],
    executed: list[str],
) -> None:
    """Run lint/test guardrails before git mutation steps."""
    if run_lint_gate and not blockers:
        lint_result = run_lint(project_root)
        if lint_result.success:
            executed.append("gz lint (pre-sync)")
        else:
            blockers.append("Lint failed before sync.")

    if run_test_gate and not blockers:
        test_result = run_tests(project_root)
        if test_result.success:
            executed.append("gz test (pre-sync)")
        else:
            blockers.append("Tests failed before sync.")

    if run_test_gate and not blockers:
        behave_result = run_behave(project_root)
        if behave_result.success:
            executed.append("gz behave (pre-sync)")
        else:
            blockers.append("Behave scenarios failed before sync.")


def _build_sync_commit_message(staged_files: list[str]) -> str:
    """Build a descriptive commit message from staged file paths."""
    if not staged_files:
        return "chore: sync staged changes (gz git-sync)"

    # Classify changes by top-level area
    areas: dict[str, list[str]] = {}
    for path in staged_files:
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "src":
            area = "/".join(parts[:3])  # src/gzkit/commands etc.
        elif len(parts) >= 2 and parts[0] == "docs":
            area = "/".join(parts[:3])  # docs/design/adr etc.
        elif len(parts) >= 2 and parts[0] == "tests":
            area = "tests"
        elif len(parts) >= 2 and parts[0] == ".claude":
            area = ".claude"
        elif len(parts) >= 2 and parts[0] == ".gzkit":
            area = ".gzkit"
        elif len(parts) >= 2 and parts[0] == "config":
            area = "config"
        else:
            area = parts[0] if parts else "root"
        areas.setdefault(area, []).append(path)

    # Build summary from areas
    area_summaries = []
    for area in sorted(areas):
        count = len(areas[area])
        label = area.replace("src/gzkit/", "")
        if count == 1:
            area_summaries.append(label)
        else:
            area_summaries.append(f"{label} ({count} files)")

    summary = ", ".join(area_summaries[:4])
    if len(area_summaries) > 4:
        summary += f" +{len(area_summaries) - 4} more"

    return f"chore: update {summary} (gz git-sync)"


def _commit_staged_changes(project_root: Path, blockers: list[str], executed: list[str]) -> None:
    """Create sync auto-commit when staged changes are present."""
    if blockers:
        return

    rc_staged, staged_out, _err_staged = git_cmd(project_root, "diff", "--cached", "--name-only")
    if rc_staged != 0 or not staged_out.strip():
        return

    staged_files = [f for f in staged_out.strip().splitlines() if f.strip()]
    message = _build_sync_commit_message(staged_files)

    rc_commit, _out_commit, err_commit = git_cmd(
        project_root,
        "commit",
        "-m",
        message,
    )
    if rc_commit == 0:
        executed.append("git commit")
    else:
        blockers.append(err_commit or "Auto-commit failed.")


def _pull_if_needed(
    project_root: Path,
    remote: str,
    target_branch: str,
    diverged: bool,
    behind: int,
    blockers: list[str],
    executed: list[str],
) -> None:
    """Pull branch updates if local branch is behind/diverged."""
    if blockers or not (diverged or behind > 0):
        return

    if diverged:
        rc_pull, _out_pull, err_pull = git_cmd(
            project_root, "pull", "--rebase", remote, target_branch
        )
        pull_cmd = f"git pull --rebase {remote} {target_branch}"
    else:
        rc_pull, _out_pull, err_pull = git_cmd(
            project_root, "pull", "--ff-only", remote, target_branch
        )
        pull_cmd = f"git pull --ff-only {remote} {target_branch}"

    if rc_pull == 0:
        executed.append(pull_cmd)
    else:
        blockers.append(err_pull or "Pull failed.")


def _push_if_ahead(
    project_root: Path,
    remote: str,
    target_branch: str,
    allow_push: bool,
    blockers: list[str],
    executed: list[str],
) -> None:
    """Push only when branch is ahead after sync actions."""
    if blockers or not allow_push:
        return

    post_state = _compute_git_sync_state(project_root, target_branch, remote)
    if post_state["ahead"] <= 0:
        return

    rc_push, _out_push, err_push = git_cmd(project_root, "push", remote, target_branch)
    if rc_push == 0:
        executed.append(f"git push {remote} {target_branch}")
    else:
        blockers.append(err_push or "Push failed.")


def _run_post_sync_lint(
    project_root: Path,
    run_lint_gate: bool,
    blockers: list[str],
    executed: list[str],
    warnings: list[str],
) -> None:
    """Run lint once more to confirm repository is clean after sync."""
    if blockers or not run_lint_gate:
        return

    lint_post = run_lint(project_root)
    if lint_post.success:
        executed.append("gz lint (post-sync)")
    else:
        warnings.append("Post-sync lint failed.")


def _execute_git_sync(
    project_root: Path,
    dirty: bool,
    auto_add: bool,
    run_lint_gate: bool,
    run_test_gate: bool,
    allow_push: bool,
    diverged: bool,
    behind: int,
    remote: str,
    target_branch: str,
    blockers: list[str],
    warnings: list[str],
) -> list[str]:
    """Execute apply-mode sync steps and return executed command list."""
    executed: list[str] = []
    if blockers:
        return executed

    if dirty and auto_add:
        rc_add, _out_add, err_add = git_cmd(project_root, "add", "-A")
        if rc_add == 0:
            executed.append("git add -A")
        else:
            blockers.append(err_add or "git add -A failed.")

    _run_sync_prechecks(project_root, run_lint_gate, run_test_gate, blockers, executed)
    _commit_staged_changes(project_root, blockers, executed)
    _pull_if_needed(project_root, remote, target_branch, diverged, behind, blockers, executed)
    _push_if_ahead(project_root, remote, target_branch, allow_push, blockers, executed)
    _run_post_sync_lint(project_root, run_lint_gate, blockers, executed, warnings)

    return executed


def git_sync(
    branch: str | None,
    remote: str,
    apply: bool,
    run_lint_gate: bool,
    run_test_gate: bool,
    auto_add: bool,
    allow_push: bool,
    as_json: bool,
    show_skill: bool = False,
) -> None:
    """Sync local branch with remote using a guarded git ritual."""
    if show_skill:
        print(GIT_SYNC_SKILL_PATH)  # noqa: T201
        return

    _enforce_git_sync_skip_policy()
    _config = ensure_initialized()
    project_root = get_project_root()

    rc_repo, inside, err_repo = git_cmd(project_root, "rev-parse", "--is-inside-work-tree")
    if rc_repo != 0 or inside != "true":
        raise GzCliError(err_repo or "Not a git repository.")

    rc_branch, current_branch, err_branch = git_cmd(
        project_root, "rev-parse", "--abbrev-ref", "HEAD"
    )
    if rc_branch != 0:
        raise GzCliError(err_branch or "Could not determine current branch.")

    target_branch = branch or current_branch
    plan = _plan_git_sync(
        project_root=project_root,
        current_branch=current_branch,
        target_branch=target_branch,
        remote=remote,
        apply=apply,
        auto_add=auto_add,
        allow_push=allow_push,
    )
    dirty = cast(bool, plan["dirty"])
    ahead = cast(int, plan["ahead"])
    behind = cast(int, plan["behind"])
    diverged = cast(bool, plan["diverged"])
    actions = cast(list[str], plan["actions"])
    blockers = cast(list[str], plan["blockers"])
    warnings = cast(list[str], plan["warnings"])

    executed: list[str] = []
    if apply:
        executed = _execute_git_sync(
            project_root=project_root,
            dirty=dirty,
            auto_add=auto_add,
            run_lint_gate=run_lint_gate,
            run_test_gate=run_test_gate,
            allow_push=allow_push,
            diverged=diverged,
            behind=behind,
            remote=remote,
            target_branch=target_branch,
            blockers=blockers,
            warnings=warnings,
        )

    result: dict[str, Any] = {
        "branch": target_branch,
        "remote": remote,
        "apply": apply,
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
        "diverged": diverged,
        "actions": actions,
        "executed": executed,
        "blockers": blockers,
        "warnings": warnings,
    }

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
        if blockers:
            raise SystemExit(1)
        return

    if not apply:
        console.print("[bold]Git sync plan (dry-run)[/bold]")
    else:
        console.print("[bold]Git sync execution[/bold]")
    console.print(f"  Branch: {target_branch}")
    console.print(f"  Remote: {remote}")
    console.print(f"  ahead={ahead} behind={behind} diverged={diverged} dirty={dirty}")

    console.print("  Actions:")
    for action in actions:
        console.print(f"    - {action}")

    if executed:
        console.print("  Executed:")
        for item in executed:
            console.print(f"    - {item}")

    if warnings:
        console.print("  Warnings:")
        for warning in warnings:
            console.print(f"    - {warning}")

    if blockers:
        console.print("  Blockers:")
        for blocker in blockers:
            console.print(f"    - {blocker}")
        raise SystemExit(1)

    if apply:
        console.print("[green]Git sync completed.[/green]")
    else:
        console.print("  Use --apply to execute.")
