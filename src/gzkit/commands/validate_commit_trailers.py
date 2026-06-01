"""Commit-trailer validators (Task: and Eval-feedback-source:).

Extracted from ``validate_cmd.py`` (A3 module split). These validators inspect
the HEAD commit only and share ``_head_commit_message_and_files`` — patched by
``tests/governance/test_eval_feedback_trailer.py`` and the eval-feedback-loop
behave steps, which target this module's namespace.
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


def _head_commit_message_and_files(project_root: Path) -> tuple[str, list[str]] | None:
    """Return (commit_message, changed_paths) for HEAD, or None if no git/HEAD.

    Paths are reported with forward slashes, relative to the repo root.
    """
    try:
        msg = subprocess.run(
            ["git", "log", "-1", "--pretty=%B", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        files = subprocess.run(
            ["git", "show", "--name-only", "--pretty=", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return msg, [line.strip() for line in files.splitlines() if line.strip()]


def _validate_commit_trailers(project_root: Path) -> list[ValidationError]:
    """Flag HEAD commits touching src/ or tests/ without a Task: trailer.

    GHI #552 strict-mode (post-2026-05-27): src/tests commits MUST carry a
    `Task:` trailer; `Ceremony:` and `Eval-feedback-source:` no longer
    substitute for src/tests scope. The pre-GHI-#552 OR-permissive rule was
    the doctrinal escape valve that silently abandoned TASK discipline
    (3 Task: vs. 305+ Ceremony: trailers in 30-day audit window).

    Task: trailer accepts BOTH the formal four-tier ID `TASK-X.Y.Z-NN-MM-PP`
    (under an OBPI/REQ) AND the slug-form `TASK-<slug>-#<ghi>` (direct-fix
    work outside OBPI scope, per GHI #160 Phase 7 convention).

    Scans HEAD only — preventing new trailer omissions, not retroactively
    flagging historical commits. Non-code commits (docs/, .gzkit/, etc.) are
    skipped.
    """
    head = _head_commit_message_and_files(project_root)
    if head is None:
        return []
    message, files = head
    code_files = [f for f in files if f.startswith(_CODE_PATH_PREFIXES)]
    if not code_files:
        return []
    if has_task_trailer(message):
        return []
    short_sha = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    return [
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
                "PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation)."
            ),
        )
    ]


_RULE_PATH_PREFIXES = (".gzkit/rules/", "AGENTS.md")
_CLOSES_RE = re.compile(r"(?:closes|fixes)\s+#(\d+)", re.IGNORECASE)
_EVAL_FEEDBACK_LABEL = "eval-feedback"


def _validate_eval_feedback_trailer(project_root: Path) -> list[ValidationError]:
    """Flag rule-edit commits closing an eval-feedback GHI without Eval-feedback-source: trailer."""
    head = _head_commit_message_and_files(project_root)
    if head is None:
        return []
    message, files = head
    rule_files = [f for f in files if any(f.startswith(p) for p in _RULE_PATH_PREFIXES)]
    if not rule_files:
        return []
    issue_numbers = _CLOSES_RE.findall(message)
    if not issue_numbers:
        return []
    has_eval_feedback_close = False
    for num in issue_numbers:
        result = subprocess.run(
            ["gh", "issue", "view", num, "--json", "labels"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            cwd=project_root,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                labels = [lbl.get("name", "") for lbl in data.get("labels", [])]
                if _EVAL_FEEDBACK_LABEL in labels:
                    has_eval_feedback_close = True
                    break
            except (json.JSONDecodeError, AttributeError):
                pass
    if not has_eval_feedback_close:
        return []
    if parse_eval_feedback_source_trailers(message):
        return []
    short_sha = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    return [
        ValidationError(
            type="commit_trailers",
            artifact=short_sha or "HEAD",
            message=(
                "Commit touches rule files and closes an eval-feedback GHI "
                "but has no Eval-feedback-source: trailer. Add "
                "'Eval-feedback-source: <event-id-or-artifact-path>' to the commit trailer."
            ),
        )
    ]
