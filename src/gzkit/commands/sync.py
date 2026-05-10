"""Git-sync command implementation."""

import json
import os
import re
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
from gzkit.quality import run_lint, run_tests
from gzkit.utils import git_cmd

GIT_SYNC_SKILL_PATH = ".gzkit/skills/git-sync/SKILL.md"

# Cap on ledger entries embedded in a single auto-commit body. Twelve is
# enough to convey the shape of a ceremony batch without bloating the log
# beyond a comfortable terminal page; overflow is surfaced as a count line.
_MAX_LEDGER_EVENTS_IN_COMMIT = 12

# Anchor extraction patterns. The builder groups output by family
# (ADR semver, ADR pool, OBPI, GHI) in this order.
_ANCHOR_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ADR-semver", re.compile(r"\bADR-\d+\.\d+\.\d+(?:-[a-z0-9][a-z0-9-]*)?\b")),
    ("ADR-pool", re.compile(r"\bADR-pool\.[a-z0-9][a-z0-9.-]*\b")),
    ("OBPI", re.compile(r"\bOBPI-\d+\.\d+\.\d+-\d+(?:-[a-z0-9][a-z0-9-]*)?\b")),
    ("GHI", re.compile(r"\bGHI #\d+\b")),
)


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

    # Fetch unconditionally so ahead/behind reflects current remote state, not
    # stale local refs (GHI #343). In apply-mode a fetch failure is a blocker;
    # in dry-run it degrades to a warning so the planner still works offline
    # while making the staleness window visible to the operator.
    if not blockers:
        rc_fetch, _out_fetch, err_fetch = git_cmd(project_root, "fetch", "--prune", remote)
        if rc_fetch != 0:
            msg = err_fetch or f"Fetch failed for remote {remote}."
            if apply:
                blockers.append(msg)
            else:
                warnings.append(f"{msg} ahead/behind may be stale.")

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
        # Behave no longer runs as a sync pre-gate — pre-commit enforces
        # unittest/lint/type checks, and behave is Heavy-lane / closeout-scope.
        # For explicit pre-sync BDD coverage, run `gz test --bdd` beforehand.


_SYNC_CEREMONY_TRAILER = "Ceremony: gz-git-sync"


def _extract_governance_anchors(diff_text: str) -> list[str]:
    """Return sorted, deduped governance anchor IDs found in staged diff text.

    Surfaces OBPI / ADR (semver + pool) / GHI identifiers so the auto-commit
    body cites the artifacts the sync touched (GHI #439). Grouped by family
    in a stable order (ADR semver → ADR pool → OBPI → GHI); within a family
    the IDs are sorted alphabetically. Lexicographic ordering is acceptable
    here because the consumer is a human reading ``git log`` — not a
    semver-comparison surface.
    """
    grouped: dict[str, set[str]] = {family: set() for family, _ in _ANCHOR_PATTERNS}
    for family, pattern in _ANCHOR_PATTERNS:
        for match in pattern.finditer(diff_text):
            grouped[family].add(match.group(0))

    ordered: list[str] = []
    for family, _ in _ANCHOR_PATTERNS:
        ordered.extend(sorted(grouped[family]))
    return ordered


def _recent_unsynced_ledger_events(
    project_root: Path, since_iso: str | None
) -> list[dict[str, Any]]:
    """Return ledger entries with ``ts`` strictly greater than ``since_iso``.

    Reads ``.gzkit/ledger.jsonl`` and filters by ISO-8601 timestamp string
    comparison (the ledger writes a single canonical zoned format, so string
    comparison is monotonic). Malformed JSONL lines are skipped silently —
    the auto-commit message is best-effort enrichment, not a validator.
    When ``since_iso`` is ``None`` every event is returned (used for fresh
    branches with no prior commit on this ref).
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    try:
        raw = ledger_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    events: list[dict[str, Any]] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            entry = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if since_iso is not None:
            ts = entry.get("ts")
            if not isinstance(ts, str) or ts <= since_iso:
                continue
        events.append(entry)
    return events


def _format_anchors_section(anchors: list[str]) -> str:
    lines = ["Governance anchors touched:"]
    lines.extend(f"- {anchor}" for anchor in anchors)
    return "\n".join(lines)


def _format_ledger_events_section(events: list[dict[str, Any]]) -> str:
    total = len(events)
    capped = events[:_MAX_LEDGER_EVENTS_IN_COMMIT]
    lines = ["Ledger events since last commit:"]
    for entry in capped:
        event = entry.get("event", "?")
        ts = entry.get("ts", "")
        ident = entry.get("id")
        if ident:
            lines.append(f"- {event} {ident} ({ts})")
        else:
            lines.append(f"- {event} ({ts})")
    if total > _MAX_LEDGER_EVENTS_IN_COMMIT:
        lines.append(f"... ({total} total since last commit)")
    return "\n".join(lines)


def _classify_staged_areas(staged_files: list[str]) -> str:
    areas: dict[str, list[str]] = {}
    for path in staged_files:
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "src" or len(parts) >= 2 and parts[0] == "docs":
            area = "/".join(parts[:3])
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
    return summary


def _build_sync_commit_message(
    staged_files: list[str],
    *,
    anchors: list[str] | None = None,
    ledger_events: list[dict[str, Any]] | None = None,
) -> str:
    """Build a descriptive commit message from staged files + governance context.

    Every sync commit carries a ``Ceremony: gz-git-sync`` trailer so
    ``gz validate --commit-trailers`` accepts the commit as
    governance-intent-bound (GHI #201). Sync commits bundle work already
    authored under other governance anchors (OBPIs, ADRs, defect fixes);
    the ceremony trailer names this class explicitly rather than forcing
    a synthetic Task id.

    When ``anchors`` or ``ledger_events`` are supplied (GHI #439), the body
    additionally surfaces the OBPI/ADR/GHI IDs touched in the staged diff
    and the ledger events accumulated since the last commit on this branch.
    Both sections are omitted when empty so genuinely path-shape-only syncs
    retain their compact pre-enrichment shape.
    """
    subject = (
        "chore: sync staged changes (gz git-sync)"
        if not staged_files
        else f"chore: update {_classify_staged_areas(staged_files)} (gz git-sync)"
    )

    sections: list[str] = [subject]
    if anchors:
        sections.append(_format_anchors_section(anchors))
    if ledger_events:
        sections.append(_format_ledger_events_section(ledger_events))
    sections.append(_SYNC_CEREMONY_TRAILER)
    return "\n\n".join(sections)


_CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(fix|feat|refactor|test|docs|chore|perf|style|ci|build|revert)(\([^)]+\))?!?:\s"
)


def _detect_stranded_commit_message(project_root: Path) -> str | None:
    """Return the subject of a stranded prior commit attempt, or None.

    A "stranded" message is a conventional-commit-shaped subject sitting in
    ``.git/COMMIT_EDITMSG`` (preserved by git after a failed commit attempt)
    whose subject does not match HEAD's subject — meaning the prior
    ``git commit -m "..."`` invocation never landed (pre-commit hooks rejected
    it, the operator aborted, etc.). If such a message exists, the sync
    auto-commit path MUST refuse to silently rewrite the operator's intent;
    see GHI #437 for the failure case (``Closes #434`` trailer + ARB receipt
    IDs erased by the template ``chore: update`` rewrite).
    """
    editmsg_path = project_root / ".git" / "COMMIT_EDITMSG"
    try:
        raw = editmsg_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    subject: str | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        subject = stripped
        break
    if subject is None or not _CONVENTIONAL_COMMIT_RE.match(subject):
        return None

    rc_head, head_subject, _err = git_cmd(project_root, "log", "-1", "--format=%s")
    if rc_head == 0 and head_subject.strip() == subject:
        return None
    return subject


def _commit_staged_changes(project_root: Path, blockers: list[str], executed: list[str]) -> None:
    """Create sync auto-commit when staged changes are present."""
    if blockers:
        return

    rc_staged, staged_out, _err_staged = git_cmd(project_root, "diff", "--cached", "--name-only")
    if rc_staged != 0 or not staged_out.strip():
        return

    stranded = _detect_stranded_commit_message(project_root)
    if stranded is not None:
        blockers.append(
            "Refusing to auto-commit: .git/COMMIT_EDITMSG holds a stranded prior "
            f"commit attempt with subject {stranded!r} that has not landed. Re-run "
            "the original `git commit` to land the authored message (or clear "
            ".git/COMMIT_EDITMSG to release the guard), then re-run gz git-sync."
        )
        return

    staged_files = [f for f in staged_out.strip().splitlines() if f.strip()]

    # GHI #439: enrich the commit body with governance anchors from the staged
    # diff and ledger events accumulated since HEAD. Both are best-effort —
    # failures degrade silently to the pre-enrichment shape so commit-authoring
    # never blocks on enrichment IO.
    rc_diff, diff_text, _err_diff = git_cmd(project_root, "diff", "--cached")
    anchors = _extract_governance_anchors(diff_text) if rc_diff == 0 else []

    rc_head_ts, head_iso, _err_head_ts = git_cmd(project_root, "log", "-1", "--format=%cI")
    since_iso = head_iso.strip() if rc_head_ts == 0 and head_iso.strip() else None
    ledger_events = _recent_unsynced_ledger_events(project_root, since_iso)

    message = _build_sync_commit_message(staged_files, anchors=anchors, ledger_events=ledger_events)

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
