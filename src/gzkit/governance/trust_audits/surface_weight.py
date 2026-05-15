"""Surface-weight validator — ADR-0.0.33 Invariant 2.

Computes the per-turn surface corpus line count (AGENTS.md, CLAUDE.md,
.claude/rules/**), reads the direction-binding floor from
data/surface_weight_floor.json, and enforces band-based exit codes.
Returns a list[ValidationError]; empty list means clean.
"""

from __future__ import annotations

import contextlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

# Band constants — pinned by ADR-0.0.33 Decision. ALWAYS read from this block.
_GREEN_CEILING = 1800
_YELLOW_CEILING = 2200

_FLOOR_PATH = Path("data") / "surface_weight_floor.json"
_WAIVERS_PATH = Path("data") / "surface_weight_waivers.json"
_LEDGER_PATH = Path(".gzkit") / "ledger.jsonl"
_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")
_RULES_GLOB = ".claude/rules/**/*.md"
_DRIFT_THRESHOLD_HOURS = 24
_RECALIBRATION_EVENT_TYPE = "surface_weight_recalibrated"


def validate_surface_weight(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for surface weight violations."""
    floor_path = project_root / _FLOOR_PATH
    if not floor_path.exists():
        return []  # Bootstrap: no floor yet

    floor = _load_floor(floor_path)
    if floor is None:
        return []

    # Check floor drift first (REQ-05)
    drift_errors = _check_floor_drift(floor, project_root)
    if drift_errors:
        return drift_errors

    current = _count_surface_lines(project_root)
    floor_lines = floor.get("lines", 0)

    # REQ-01: at or below floor → clean
    if current <= floor_lines:
        return []

    delta = current - floor_lines

    # REQ-03: red band → fail closed, no waiver dispensation
    if current > _YELLOW_CEILING:
        msg = (
            f"Surface weight in red band: {current} lines (delta +{delta} from floor "
            f"{floor_lines}). Red band (>{_YELLOW_CEILING}) is fail-closed; "
            f"no waiver dispensation applies."
        )
        return [_make_error(msg)]

    # REQ-02: yellow band
    if current > _GREEN_CEILING:
        waivers = _load_waivers(project_root / _WAIVERS_PATH)
        if _has_active_waiver(waivers, delta):
            return []  # Waiver dispensation: exit 0 with implicit warning

        msg = (
            f"Surface weight in yellow band: {current} lines (delta +{delta} from floor "
            f"{floor_lines}). Yellow band ({_GREEN_CEILING + 1}–{_YELLOW_CEILING}) requires "
            f"an active waiver. Add an entry to data/surface_weight_waivers.json or reduce "
            f"the surface corpus."
        )
        return [_make_error(msg)]

    # Above floor but still in green band (floor < current ≤ 1800)
    return []


def _count_surface_lines(project_root: Path) -> int:
    """Count total lines in the per-turn surface corpus."""
    total = 0
    for name in _SURFACE_FILES:
        path = project_root / name
        if path.exists():
            with contextlib.suppress(OSError):
                total += len(path.read_text(encoding="utf-8").splitlines())
    rules_root = project_root / ".claude" / "rules"
    if rules_root.exists():
        for rule_path in sorted(rules_root.rglob("*.md")):
            with contextlib.suppress(OSError):
                total += len(rule_path.read_text(encoding="utf-8").splitlines())
    return total


def _load_floor(floor_path: Path) -> dict | None:
    """Load and return the floor snapshot dict, or None on parse error."""
    try:
        return json.loads(floor_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _load_waivers(waivers_path: Path) -> list[dict]:
    """Load waivers list from JSON file."""
    if not waivers_path.exists():
        return []
    try:
        data = json.loads(waivers_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _has_active_waiver(waivers: list[dict], delta: int) -> bool:
    """Return True if any non-expired waiver covers the given delta."""
    today = datetime.now(tz=UTC).date()
    for waiver in waivers:
        try:
            expires_str = waiver.get("expires", "")
            expires = datetime.strptime(expires_str, "%Y-%m-%d").date()
            delta_covered = int(waiver.get("delta_lines", 0))
        except (ValueError, TypeError):
            continue
        if expires >= today and delta_covered >= delta:
            return True
    return False


def _check_floor_drift(floor: dict, project_root: Path) -> list[ValidationError]:
    """Check if the floor timestamp predates the most recent recalibration event by >24h."""
    ledger_path = project_root / _LEDGER_PATH
    if not ledger_path.exists():
        return []

    last_recalibration_ts: datetime | None = None
    try:
        for line in ledger_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event") == _RECALIBRATION_EVENT_TYPE:
                ts_str = event.get("ts", "")
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=UTC)
                    if last_recalibration_ts is None or ts > last_recalibration_ts:
                        last_recalibration_ts = ts
                except (ValueError, TypeError):
                    pass
    except (OSError, json.JSONDecodeError):
        return []

    if last_recalibration_ts is None:
        return []  # Bootstrap: no recalibration events

    floor_ts_str = floor.get("timestamp", "")
    if not floor_ts_str:
        return []
    try:
        floor_ts = datetime.fromisoformat(floor_ts_str)
        if floor_ts.tzinfo is None:
            floor_ts = floor_ts.replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return []

    if last_recalibration_ts > floor_ts + timedelta(hours=_DRIFT_THRESHOLD_HOURS):
        msg = (
            f"Floor drift detected: floor snapshot timestamped {floor_ts.isoformat()} "
            f"predates most recent recalibration event at "
            f"{last_recalibration_ts.isoformat()} by more than {_DRIFT_THRESHOLD_HOURS}h. "
            f"Recalibrate via: uv run gz adr emit-receipt with event "
            f"surface_weight_recalibrated, then update data/surface_weight_floor.json."
        )
        return [_make_error(msg)]

    return []


def _make_error(message: str) -> ValidationError:
    """Build a surface_weight ValidationError."""
    return ValidationError(
        type="surface_weight",
        artifact=_FLOOR_PATH.as_posix(),
        message=message,
    )
