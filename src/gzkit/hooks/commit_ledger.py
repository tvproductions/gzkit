"""Record governance-artifact edits at the COMMIT locus (GHI #847).

The PostToolUse principal this backs up — ``.claude/hooks/ledger-writer.py`` —
binds ``Edit|Write`` and keys on ``tool_input.file_path``, a field a Bash
payload does not carry. So a governance artifact written by ``sed``, a heredoc,
inline ``python``, ``git apply``, or an editor outside the session emits
nothing at all. Measured 2026-08-21 across the three sessions that implemented
OBPI-0.35.0-09: 3h38m between ``pipeline_launched`` and ``brief_reconciled``
with zero ``artifact_edited`` rows, and exactly one such row in the whole day.

That blindness is not merely a partial Layer-2 record. ``gz validate
--orphaned-implementation`` reads ``(ts, path)`` pairs from this event type to
detect implementation outside an OBPI's allowed paths; for the Bash channel it
has been silently inert, and absence of events is indistinguishable from
absence of work.

Reading the commit answers the question the hook was asked but could not hear:
did a governance artifact change, and did anything record it? This is the
remedy shape ``1700f99b`` and ``dc572677`` established for the sibling arms,
applied to a recorder rather than a gate.

**Backstop, not a second emitter.** A path already carrying an
``artifact_edited`` row since the previous commit is skipped, so this fires
exactly when the tool locus was bypassed and stays silent when it was not.
That is the operator's 2026-08-22 ruling, taken against a measurement rather
than a worry: unconditional commit-locus emission would have added 1165 rows
over 60 days (229 commits, median 1 per commit, max 197), roughly doubling the
type, while the tool locus already emits 2.71x per (path, day) because every
``Edit`` call fires.

**Declared coverage limits.** A write that is never committed stays invisible —
the commit is the state this observes, and an uncommitted edit has no state to
observe. Merge commits produce no ``diff-tree`` output without ``-m`` and are
not walked; gzkit commits directly to main (operator directive 2026-06-16), so
authored content does not arrive that way. A rebase replays commits and can
re-record a path whose original row fell outside the replayed window.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.core import is_governance_artifact
from gzkit.ledger import Ledger, artifact_edited_event

_ARTIFACT_EDITED = "artifact_edited"


def _git(args: list[str], root: Path) -> str:
    """Return stdout of ``git <args>`` run from ``root``; empty on any failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (FileNotFoundError, OSError):
        return ""
    return result.stdout or ""


def _parse_ts(value: str) -> datetime | None:
    """Parse an ISO-8601 timestamp as aware-UTC, tolerating a trailing ``Z``."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def governance_paths_in_commit(root: Path, rev: str = "HEAD") -> list[str]:
    """Governance artifacts added, modified, or renamed into place by ``rev``.

    Deletions are excluded on purpose: the ``Edit|Write`` principal cannot
    observe one, and a backstop that recorded more than the locus it backs up
    would be asserting a different claim.
    """
    out = _git(
        ["diff-tree", "--no-commit-id", "-r", "--root", "--diff-filter=AMR", "--name-only", rev],
        root,
    )
    candidates = (line.strip() for line in out.splitlines())
    return sorted({path for path in candidates if path and is_governance_artifact(path)})


def _window_start(root: Path, rev: str = "HEAD") -> datetime | None:
    """Commit time of ``rev``'s first parent, or ``None`` for a root commit.

    The parent bounds the dedup window. Suppressing on any row anywhere in
    history would blind the recorder to every edit after a file's first.
    """
    return _parse_ts(_git(["log", "-1", "--format=%cI", f"{rev}^"], root).strip())


def paths_recorded_since(ledger_path: Path, since: datetime | None) -> set[str]:
    """Paths already carrying an ``artifact_edited`` row at or after ``since``.

    ``since`` is ``None`` for a root commit, where the window is all of
    history — which for a first commit is an empty ledger anyway.
    """
    recorded: set[str] = set()
    try:
        text = ledger_path.read_text(encoding="utf-8")
    except OSError:
        return recorded
    for line in text.splitlines():
        stripped = line.strip()
        # Cheap prefilter: the ledger is ~15k lines and most are other types.
        if not stripped or _ARTIFACT_EDITED not in stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict) or row.get("event") != _ARTIFACT_EDITED:
            continue
        path = row.get("path") or row.get("id")
        if not isinstance(path, str):
            continue
        ts = _parse_ts(str(row.get("ts") or ""))
        if since is None or (ts is not None and ts >= since):
            recorded.add(path)
    return recorded


def record_committed_artifact_edits(root: Path, rev: str = "HEAD") -> list[str]:
    """Emit one backstop ``artifact_edited`` row per bypassed governance write.

    Returns the paths recorded, sorted. Empty when the commit touched no
    governance artifact, when every one was already recorded, or when the
    project has no ledger — none of which is an error condition here.
    """
    changed = governance_paths_in_commit(root, rev)
    if not changed:
        return []
    ledger_path = root / GzkitConfig.load(root / ".gzkit.json").paths.ledger
    if not ledger_path.exists():
        return []
    already = paths_recorded_since(ledger_path, _window_start(root, rev))
    pending = [path for path in changed if path not in already]
    if not pending:
        return []
    commit = _git(["rev-parse", rev], root).strip() or None
    session = os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("COPILOT_SESSION_ID")
    ledger = Ledger(ledger_path)
    for path in pending:
        ledger.append(artifact_edited_event(path, session, commit=commit))
    return pending


def main() -> int:
    """post-commit entry point. Always exits 0 — a recorder gates nothing.

    Git ignores a post-commit hook's exit status, so a non-zero return would
    be theatre. Failure is reported on stderr and the commit stands.
    """
    try:
        recorded = record_committed_artifact_edits(Path.cwd())
    except Exception as exc:  # noqa: BLE001 - never let a recorder break a commit
        print(f"[ledger] commit-locus recorder skipped: {exc}", file=sys.stderr)  # noqa: T201
        return 0
    if recorded:
        noun = "edit" if len(recorded) == 1 else "edits"
        print(  # noqa: T201
            f"[ledger] recorded {len(recorded)} governance {noun} the tool locus did not see"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
