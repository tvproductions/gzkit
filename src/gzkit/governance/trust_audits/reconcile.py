"""Reconcile-freshness trust audit (GHI #213 / Architectural Boundary 4)."""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.validate import ValidationError


def audit_reconcile_freshness(project_root: Path) -> list[ValidationError]:
    """Flag when reconciliation has not run since HEAD or within a recency window.

    Reconciliation is a core architectural operation, not a maintenance
    chore (CLAUDE.md architectural-boundary 4). If the latest
    ``frontmatter_reconciled`` / ``reconcile_*`` ledger event is older than
    HEAD's commit timestamp, derived state is potentially stale.
    """
    import subprocess  # noqa: PLC0415
    from datetime import UTC, datetime  # noqa: PLC0415

    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return []

    latest: datetime | None = None
    reconcile_events = {
        "frontmatter_reconciled",
        "reconcile_run",
        "reconcile_completed",
        "state_reconciled",
        "obpi_reconciled",
    }
    for raw in ledger.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("event") not in reconcile_events:
            continue
        ts = event.get("ts")
        if not isinstance(ts, str):
            continue
        try:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if latest is None or parsed > latest:
            latest = parsed

    try:
        head_ts_text = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    try:
        head_ts = datetime.fromisoformat(head_ts_text.replace("Z", "+00:00"))
    except ValueError:
        return []

    if latest is None:
        # Ledger has no reconcile events yet — the reconciliation pathway is
        # still being mechanized. Skip rather than fail until the event types
        # above are emitted by ``gz frontmatter reconcile`` / ``gz state``.
        return []
    # Allow a 24-hour grace window so in-flight commits don't fail pre-commit
    # on a strictly monotonic comparison.
    delta = (head_ts - latest).total_seconds()
    if delta > 86400:
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
    return []
