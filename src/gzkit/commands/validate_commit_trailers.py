"""Commit-trailer validators (Task: and Eval-feedback-source:).

Extracted from ``validate_cmd.py`` (A3 module split). Both validators read the
commits the next push publishes through ``_pushable_commits`` and look up GHI
labels through ``_issue_labels`` — the seams ``tests/governance/`` patch. The
eval-feedback-loop behave steps patch this module's ``subprocess.run``.
"""

import json
import re
import subprocess
from pathlib import Path

from gzkit.tasks import (
    has_task_trailer,
    parse_eval_feedback_source_trailers,
)
from gzkit.validate import ValidationError

_CODE_PATH_PREFIXES = ("src/", "tests/")


def _git_out(project_root: Path, args: list[str]) -> str | None:
    """Return stdout of ``git <args>``, or None when git fails or is missing."""
    try:
        return subprocess.run(
            ["git", *args],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
            encoding="utf-8",
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _pushable_commits(project_root: Path) -> list[tuple[str, str, list[str]]]:
    """Return (short sha, message, changed paths) for each commit the next push publishes.

    That is ``@{upstream}..HEAD``, oldest first. Reading HEAD alone let a
    trailer-less code commit through whenever a non-code commit sat on top of it
    at pre-push, which ``gz git-sync``'s ``.gzkit`` chore commit does in most
    sessions (GHI #1017). Without an upstream (an untracked branch, CI's
    detached checkout) the range is unknowable, so HEAD alone is read. Commits
    already on the upstream are published history and are not re-flagged.
    Paths use forward slashes, relative to the repo root.
    """
    revs = _git_out(project_root, ["rev-list", "--reverse", "@{upstream}..HEAD"])
    commits: list[tuple[str, str, list[str]]] = []
    for rev in revs.split() if revs is not None else ["HEAD"]:
        header = _git_out(project_root, ["log", "-1", "--abbrev=7", "--format=%h%x00%B", rev])
        files = _git_out(project_root, ["show", "--name-only", "--pretty=", rev])
        if header is None or files is None:
            continue
        short_sha, _, message = header.partition("\x00")
        paths = [line.strip() for line in files.splitlines() if line.strip()]
        commits.append((short_sha.strip(), message, paths))
    return commits


def _validate_commit_trailers(project_root: Path) -> list[ValidationError]:
    """Flag pushable commits touching src/ or tests/ without a Task: trailer.

    GHI #552 strict-mode (post-2026-05-27): src/tests commits MUST carry a
    `Task:` trailer; `Ceremony:` and `Eval-feedback-source:` no longer
    substitute for src/tests scope. The pre-GHI-#552 OR-permissive rule was
    the doctrinal escape valve that silently abandoned TASK discipline
    (3 Task: vs. 305+ Ceremony: trailers in 30-day audit window).

    Task: trailer accepts BOTH the formal four-tier ID `TASK-X.Y.Z-NN-MM-PP`
    (under an OBPI/REQ) AND the slug-form `TASK-<slug>-#<ghi>` (direct-fix
    work outside OBPI scope, per GHI #160 Phase 7 convention).

    Scans every commit ``_pushable_commits`` returns — preventing new trailer
    omissions before they publish, not retroactively flagging historical
    commits. Non-code commits (docs/, .gzkit/, etc.) are skipped.
    """
    errors: list[ValidationError] = []
    for short_sha, message, files in _pushable_commits(project_root):
        if not any(f.startswith(_CODE_PATH_PREFIXES) for f in files):
            continue
        if has_task_trailer(message):
            continue
        errors.append(
            ValidationError(
                type="commit_trailers",
                artifact=short_sha or "HEAD",
                message=(
                    "Commit touches src/ or tests/ but has no `Task:` trailer — "
                    "TASK chain is broken (GHI #552 strict-mode). Expected "
                    "'Task: TASK-X.Y.Z-NN-MM-PP' for OBPI-scoped work or "
                    "'Task: TASK-<slug>-#<ghi>' for direct-fix work. "
                    "`Ceremony:` and `Eval-feedback-source:` no longer substitute "
                    "for `Task:` on src/tests scope (per AGENTS.md § Workflow: "
                    "PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation). "
                    "If it is not yet pushed, add the trailer: `git commit --amend` "
                    "at HEAD, or reword it with a rebase if later commits sit on top."
                ),
            )
        )
    return errors


_RULE_PATH_PREFIXES = (".gzkit/rules/", "AGENTS.md")
_CLOSES_RE = re.compile(r"(?:closes|fixes)\s+#(\d+)", re.IGNORECASE)
_EVAL_FEEDBACK_LABEL = "eval-feedback"


def _issue_labels(project_root: Path, number: str) -> list[str]:
    """Return GHI ``number``'s label names, or [] when gh cannot answer."""
    result = subprocess.run(
        ["gh", "issue", "view", number, "--json", "labels"],
        capture_output=True,
        text=True,
        errors="replace",
        encoding="utf-8",
        check=False,
        cwd=project_root,
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        return [lbl.get("name", "") for lbl in data.get("labels", [])]
    except (json.JSONDecodeError, AttributeError):
        return []


def _validate_eval_feedback_trailer(project_root: Path) -> list[ValidationError]:
    """Flag pushable rule-edit commits closing an eval-feedback GHI without the trailer."""
    errors: list[ValidationError] = []
    labels_cache: dict[str, list[str]] = {}
    for short_sha, message, files in _pushable_commits(project_root):
        if not any(f.startswith(_RULE_PATH_PREFIXES) for f in files):
            continue
        closes_eval_feedback = False
        for num in _CLOSES_RE.findall(message):
            if num not in labels_cache:
                labels_cache[num] = _issue_labels(project_root, num)
            if _EVAL_FEEDBACK_LABEL in labels_cache[num]:
                closes_eval_feedback = True
                break
        if not closes_eval_feedback or parse_eval_feedback_source_trailers(message):
            continue
        errors.append(
            ValidationError(
                type="commit_trailers",
                artifact=short_sha or "HEAD",
                message=(
                    "Commit touches rule files and closes an eval-feedback GHI "
                    "but has no Eval-feedback-source: trailer. Add "
                    "'Eval-feedback-source: <event-id-or-artifact-path>' to the commit trailer."
                ),
            )
        )
    return errors
