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
    creates_paths: set[str] | None = None,
) -> bool:
    """Return True when receipt_ts > max(mtime(p)) for all allowed_paths.

    Each entry in ``allowed_paths`` is a project-relative path string.
    Glob patterns are expanded via ``Path.glob``; a missing (non-glob)
    path that does not exist on disk returns False to force re-reconcile.
    An empty ``allowed_paths`` list returns False.

    Paths the brief declares it will create (``creates_paths``) are exempt
    from the missing-path → False rule: a net-new file does not exist at
    Stage-2 entry, so its absence must not force re-reconcile. Freshness is
    then decided by the existing files in the allowlist domain. This mirrors
    the brief-creates exemption ``brief_path_validity`` already honors
    (GHI #419) and is what unblocks net-new-file OBPIs at the Stage-2
    reconcile gate.

    Args:
        receipt_ts: Timestamp of the most recent ``brief_reconciled`` event.
        allowed_paths: Project-relative path strings from the brief's Allowed
            Paths section.
        project_root: Absolute path to the project root directory.
        creates_paths: Project-relative paths the brief declares it creates;
            absent-on-disk entries in this set are exempt rather than fatal.

    Returns:
        True iff receipt_ts is strictly newer than every existing file in the
        allowed-paths domain.  False if any non-create path is missing or if
        no existing files remain in the domain.
    """
    creates = creates_paths or set()
    mtimes: list[float] = []
    for pattern in allowed_paths:
        direct = project_root / pattern
        if direct.exists():
            mtimes.append(direct.stat().st_mtime)
        elif pattern.removeprefix("./").rstrip("/") in creates:
            continue
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
