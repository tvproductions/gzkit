"""Reconcile-freshness trust audit (GHI #213 / Architectural Boundary 4)."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from gzkit.validate import ValidationError

_RECONCILE_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "frontmatter_reconciled",
        "reconcile_run",
        "reconcile_completed",
        "state_reconciled",
        "obpi_reconciled",
    }
)

_RECONCILE_GRACE_SECONDS = 86400  # 24-hour pre-commit window


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _latest_reconcile_ts(ledger: Path) -> datetime | None:
    """Return the most recent reconcile-event timestamp, or ``None`` if absent."""
    latest: datetime | None = None
    for raw in ledger.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("event") not in _RECONCILE_EVENT_TYPES:
            continue
        parsed = _parse_ts(event.get("ts"))
        if parsed is not None and (latest is None or parsed > latest):
            latest = parsed
    return latest


def _head_commit_ts(project_root: Path) -> datetime | None:
    """Return HEAD's committer timestamp, or ``None`` on git unavailability."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
            encoding="utf-8",
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return _parse_ts(out)


def audit_reconcile_freshness(project_root: Path) -> list[ValidationError]:
    """Flag when reconciliation has not run since HEAD or within a recency window.

    Reconciliation is a core architectural operation, not a maintenance
    chore (CLAUDE.md architectural-boundary 4). If the latest
    ``frontmatter_reconciled`` / ``reconcile_*`` ledger event is older than
    HEAD's commit timestamp by more than 24 hours, derived state is
    potentially stale.
    """
    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return []

    latest = _latest_reconcile_ts(ledger)
    head_ts = _head_commit_ts(project_root)
    if latest is None or head_ts is None:
        # Ledger has no reconcile events yet, or git is unavailable — fail open
        # per Architectural Boundary 4 (zero-event history is bootstrap, not drift).
        return []

    delta = (head_ts - latest).total_seconds()
    if delta <= _RECONCILE_GRACE_SECONDS:
        return []

    now = datetime.now(UTC).isoformat()
    return [
        ValidationError(
            type="reconcile_freshness",
            artifact=f".gzkit/ledger.jsonl::latest={latest.isoformat()}",
            message=(
                f"Latest reconcile event is older than HEAD by {int(delta)}s "
                f"(HEAD={head_ts.isoformat()}, now={now}). Run "
                "`uv run gz frontmatter reconcile` before the next release."
            ),
        )
    ]
