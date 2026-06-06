"""Reconcile-receipt freshness helper (OBPI-0.0.37-07).

Pure function: no gzkit imports, no ledger reads, no side effects.
Used by ``check_reconcile_receipt_gate`` in ``pipeline_runtime.py``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def is_receipt_fresh(
    receipt_ts: datetime,
    allowed_paths: list[str],
    project_root: Path,
) -> bool:
    """Return True when receipt_ts > max(mtime(p)) for all allowed_paths.

    Each entry in ``allowed_paths`` is a project-relative path string.
    Glob patterns are expanded via ``Path.glob``; a missing (non-glob)
    path that does not exist on disk returns False to force re-reconcile.
    An empty ``allowed_paths`` list returns False.

    Args:
        receipt_ts: Timestamp of the most recent ``brief_reconciled`` event.
        allowed_paths: Project-relative path strings from the brief's Allowed
            Paths section.
        project_root: Absolute path to the project root directory.

    Returns:
        True iff receipt_ts is strictly newer than every file in the
        allowed-paths domain.  False if any path is missing or if
        allowed_paths is empty.
    """
    mtimes: list[float] = []
    for pattern in allowed_paths:
        direct = project_root / pattern
        if direct.exists():
            mtimes.append(direct.stat().st_mtime)
        else:
            matches = list(project_root.glob(pattern))
            if not matches:
                return False
            for match in matches:
                mtimes.append(match.stat().st_mtime)
    if not mtimes:
        return False
    max_mtime = datetime.fromtimestamp(max(mtimes), tz=UTC)
    return receipt_ts > max_mtime
