"""Orphaned-implementation trust audit (GHI #438).

Fail-closed when a non-completed OBPI brief has ledger evidence of a
lock-claim, allowed-path artifact edits, and a force-release without an
intervening ``obpi_completion_*`` event. This catches the silent broken
state reproduced in the ADR-0.0.31 closeout: a session claims the lock,
edits the canon inside the brief's allowed-paths, then force-releases
the lock without running ``gz obpi complete``. Frontmatter still says
``Draft``, the audit row already exists, and downstream reconciliation
does not surface the mismatch.

Recovery: either complete the ceremony with
``uv run gz obpi pipeline <OBPI-ID> --from=verify``, or — when the
implementation landing is intentional without ceremony (a GHI explains
why) — opt out by placing the line
``<!-- gz-validate-skip: orphaned-implementation GHI-<num> -->``
anywhere in the brief body. The marker follows the shape established by
the GHI #432 speculative-skip convention in
``src/gzkit/hooks/obpi.py``.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from gzkit.core.validation_rules import parse_frontmatter
from gzkit.governance.brief_path_validity import (
    extract_allowed_paths,
    glob_root,
    has_glob_chars,
)
from gzkit.validate import ValidationError

_COMPLETED_STATUSES = frozenset({"completed", "attested_completed", "validated", "withdrawn"})
_LOCK_CLAIMED = "obpi_lock_claimed"
_LOCK_RELEASED = "obpi_lock_released"
_COMPLETION_PREFIX = "obpi_completion_"
_ARTIFACT_EDITED = "artifact_edited"
_SKIP_MARKER_RE = re.compile(
    r"<!--\s*gz-validate-skip:\s*orphaned-implementation\b",
)


def _parse_ts(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").removeprefix("./")


def _path_covered_by_allowed(event_path: str, allowed: list[str]) -> bool:
    """Return True when event_path falls under any allowed-path entry."""
    normalized = _normalize_path(event_path)
    for entry in allowed:
        if entry.startswith("-"):
            continue
        ent = _normalize_path(entry).rstrip("/")
        if not ent:
            continue
        if has_glob_chars(ent):
            root = glob_root(ent)
            if not root:
                return True
            if normalized == root or normalized.startswith(root + "/"):
                return True
        elif normalized == ent or normalized.startswith(ent + "/"):
            return True
    return False


def _load_ledger_events(ledger: Path) -> list[dict]:
    events: list[dict] = []
    for raw in ledger.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        try:
            events.append(json.loads(stripped))
        except json.JSONDecodeError:
            continue
    return events


def _has_skip_marker(brief_path: Path) -> bool:
    return bool(_SKIP_MARKER_RE.search(brief_path.read_text(encoding="utf-8")))


def _brief_id_and_status(brief_path: Path) -> tuple[str | None, str | None]:
    fm, _ = parse_frontmatter(brief_path.read_text(encoding="utf-8"))
    raw_id = fm.get("id")
    raw_status = fm.get("status")
    obpi_id = raw_id if isinstance(raw_id, str) else None
    status = raw_status.lower() if isinstance(raw_status, str) else None
    return obpi_id, status


def _partition_events(
    events: list[dict],
) -> tuple[dict[str, list[dict]], list[tuple[datetime, str]]]:
    """Group lifecycle events by OBPI id; collect (ts, path) for artifact_edited."""
    obpi_lifecycle: dict[str, list[dict]] = defaultdict(list)
    artifact_events: list[tuple[datetime, str]] = []
    for ev in events:
        kind = ev.get("event")
        if not isinstance(kind, str):
            continue
        if kind == _ARTIFACT_EDITED:
            ts = _parse_ts(ev.get("ts"))
            path = ev.get("path") or ev.get("id")
            if ts is not None and isinstance(path, str):
                artifact_events.append((ts, path))
            continue
        if kind in {_LOCK_CLAIMED, _LOCK_RELEASED} or kind.startswith(_COMPLETION_PREFIX):
            oid = ev.get("id")
            if isinstance(oid, str):
                obpi_lifecycle[oid].append(ev)
    return obpi_lifecycle, artifact_events


def _latest_claim_ts(history: list[dict]) -> datetime | None:
    latest: datetime | None = None
    for ev in history:
        if ev.get("event") != _LOCK_CLAIMED:
            continue
        ts = _parse_ts(ev.get("ts"))
        if ts is not None and (latest is None or ts > latest):
            latest = ts
    return latest


def _completion_after(history: list[dict], anchor: datetime) -> bool:
    for ev in history:
        kind = ev.get("event")
        if not isinstance(kind, str) or not kind.startswith(_COMPLETION_PREFIX):
            continue
        ts = _parse_ts(ev.get("ts"))
        if ts is not None and ts >= anchor:
            return True
    return False


def _latest_force_release_ts(history: list[dict], after: datetime) -> datetime | None:
    latest: datetime | None = None
    for ev in history:
        if ev.get("event") != _LOCK_RELEASED or not ev.get("force"):
            continue
        ts = _parse_ts(ev.get("ts"))
        if ts is None or ts < after:
            continue
        if latest is None or ts > latest:
            latest = ts
    return latest


def _edited_paths_in_window(
    artifact_events: list[tuple[datetime, str]],
    allowed: list[str],
    start: datetime,
    end: datetime,
) -> list[str]:
    return sorted(
        {
            path
            for ts, path in artifact_events
            if start <= ts <= end and _path_covered_by_allowed(path, allowed)
        }
    )


def _build_error(
    project_root: Path,
    brief_path: Path,
    obpi_id: str,
    claim_ts: datetime,
    release_ts: datetime,
    edited_paths: list[str],
) -> ValidationError:
    rel = brief_path.relative_to(project_root).as_posix()
    preview = ", ".join(edited_paths[:5])
    more = "" if len(edited_paths) <= 5 else f" (+{len(edited_paths) - 5} more)"
    message = (
        f"{obpi_id}: lock force-released at {release_ts.isoformat()} after edits to "
        f"allowed-path artifacts ({preview}{more}) without an obpi_completion_* event "
        f"since lock claim at {claim_ts.isoformat()}. Implementation may have landed "
        f"without ceremony — run `uv run gz obpi pipeline {obpi_id} --from=verify` to "
        "investigate, or declare intent with "
        "`<!-- gz-validate-skip: orphaned-implementation GHI-<num> -->` in the brief body."
    )
    return ValidationError(type="orphaned_implementation", artifact=rel, message=message)


def audit_orphaned_implementation(project_root: Path) -> list[ValidationError]:
    """Detect lock-claim + force-release + allowed-path edits without completion (GHI #438)."""
    adr_root = project_root / "docs" / "design" / "adr"
    ledger = project_root / ".gzkit" / "ledger.jsonl"
    if not adr_root.is_dir() or not ledger.is_file():
        return []

    obpi_lifecycle, artifact_events = _partition_events(_load_ledger_events(ledger))

    errors: list[ValidationError] = []
    for brief_path in sorted(adr_root.rglob("obpis/*.md")):
        obpi_id, status = _brief_id_and_status(brief_path)
        if obpi_id is None or status in _COMPLETED_STATUSES:
            continue
        if _has_skip_marker(brief_path):
            continue
        allowed = extract_allowed_paths(brief_path) or []
        if not allowed:
            continue

        history = obpi_lifecycle.get(obpi_id, [])
        claim_ts = _latest_claim_ts(history)
        if claim_ts is None:
            continue
        if _completion_after(history, claim_ts):
            continue
        release_ts = _latest_force_release_ts(history, claim_ts)
        if release_ts is None:
            continue

        edited = _edited_paths_in_window(artifact_events, allowed, claim_ts, release_ts)
        if not edited:
            continue

        errors.append(_build_error(project_root, brief_path, obpi_id, claim_ts, release_ts, edited))
    return errors
