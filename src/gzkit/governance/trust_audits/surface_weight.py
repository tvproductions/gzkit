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

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core.validation_rules import ValidationError

# Band constants — pinned by ADR-0.0.33 Decision. ALWAYS read from this block.
# Recalibrated 2026-08-11 by operator ruling (GovZero canon owner), witnessed by a
# `surface_weight_recalibrated` ledger event — the FIRST such event ever emitted, because
# until GHI #791 no verb could produce one and the prescribed `gz adr emit-receipt`
# carried a closed `--event` enum. Operational evidence: the corpus stood at exactly
# 2600/2600, so the next rule edit adding a line would have failed `gz check` closed with
# no waiver able to cover it (largest live waiver 340 against a delta of 742, and the
# shrink-only ratchet at baseline_count 6 forbids adding a seventh entry). Measured growth
# 1859 -> 2600 over 88 days (~8.4 lines/day), so +400 buys ~47 days. The 400-line
# yellow-band width is preserved from both prior generations (1800/2200, 2600/3000).
# The operator explicitly overrode ADR-0.0.33's 6-month recalibration cadence, 42 days
# after the 2026-06-30 change; that override is recorded rather than silent, which is the
# whole point of the event. The 15k corpus-split shrink (GHI #533 / ADR-0.0.37) remains
# the durable reduction path; revisit these bands at that closeout.
#
# Prior generation: green 2600 / yellow 3000, set 2026-06-30 by operator directive as an
# unwitnessed config tweak — the ADR anti-pattern 3 breach GHI #791 diagnosed and closed.
_GREEN_CEILING = 3000
_YELLOW_CEILING = 3400

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

    # Witness-integrity arms first: while the Layer-2 record disagrees with the
    # Layer-1 surfaces it witnesses, a band verdict computed from those surfaces
    # is a number nobody should act on. Floor drift (REQ-05), then band drift
    # (GHI #792) — the same early-return shape, one per witnessed surface.
    drift_errors = _check_floor_drift(floor, project_root)
    if drift_errors:
        return drift_errors

    band_errors = _check_band_coherence(project_root)
    if band_errors:
        return band_errors

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

    # Above floor but still in green band (floor < current <= _GREEN_CEILING)
    return []


class RecalibrationOutcome(BaseModel):
    """What a completed recalibration changed. Returned by :func:`recalibrate_surface_weight`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    floor_lines: int = Field(..., description="The newly snapshotted corpus line count")
    previous_floor_lines: int = Field(..., description="The floor this recalibration superseded")
    green_ceiling: int = Field(..., description="Green band ceiling in force at recalibration")
    yellow_ceiling: int = Field(..., description="Yellow band ceiling in force at recalibration")


def recalibrate_surface_weight(
    project_root: Path, *, attestor: str, reason: str
) -> RecalibrationOutcome:
    """Re-snapshot the surface-weight floor and witness it on the ledger (GHI #791).

    This is the producer ADR-0.0.33 § Anti-patterns item 3 requires and that no
    registered verb supplied: *"Band changes are ledger events, not config
    tweaks."* OBPI-0.0.33-02 REQ 4 named ``gz adr emit-receipt`` as the emitter,
    whose ``--event`` is a closed enum that cannot accept
    ``surface_weight_recalibrated`` — so the ledger held zero such events and the
    bands had already moved once unwitnessed.

    **The write order is load-bearing, not incidental.** The floor is committed
    BEFORE the event is appended. :func:`_check_floor_drift` fails closed once a
    recalibration event postdates the floor snapshot by more than
    ``_DRIFT_THRESHOLD_HOURS``, so the two surfaces validate each other and the
    failure modes are asymmetric: a written floor with a failed append leaves a
    green gate and a re-runnable command, while an appended event with a failed
    floor write strands a RED gate that no operator action short of hand-editing
    the ledger could clear — and hand-editing is forbidden (``AGENTS.md``
    Never #2). Fail-safe therefore means floor-first.

    Attestation is fail-closed on both fields, mirroring ``gz obpi repudiate``:
    an unattested band change is the silent recalibration the anti-pattern names,
    and a blank reason makes the ledger record unreadable as evidence later.

    Raises:
        ValueError: if ``attestor`` or ``reason`` is empty or whitespace-only.
            Neither surface is mutated.

    """
    from gzkit.ledger import Ledger  # noqa: PLC0415 — avoids an import cycle
    from gzkit.ledger_events import surface_weight_recalibrated_event  # noqa: PLC0415

    if not attestor.strip():
        msg = (
            "Recalibration requires --attestor. ADR-0.0.33 § Anti-patterns item 3 forbids "
            "an unattested band change ('Band changes are ledger events, not config tweaks'); "
            "an anonymous event cannot discharge it. Re-run with --attestor '<name>'."
        )
        raise ValueError(msg)
    if not reason.strip():
        msg = (
            "Recalibration requires --reason. The ledger event is the only durable record of "
            "WHY the bands moved; without it the witness is indistinguishable from the silent "
            "tweak it exists to replace. Re-run with --reason '<operational evidence>'."
        )
        raise ValueError(msg)

    current = _count_surface_lines(project_root)
    floor_path = project_root / _FLOOR_PATH
    existing = _load_floor(floor_path) or {}
    previous_lines = int(existing.get("lines", 0))

    # Floor first — see the write-order note above.
    floor_path.parent.mkdir(parents=True, exist_ok=True)
    floor_path.write_text(
        json.dumps(
            {
                "lines": current,
                "timestamp": datetime.now(tz=UTC).isoformat(),
                "note": (
                    f"Recalibrated by {attestor}: {reason} "
                    f"(superseded floor {previous_lines}; bands "
                    f"green <= {_GREEN_CEILING}, yellow <= {_YELLOW_CEILING}). "
                    "Re-snapshot via: uv run gz validate --surface-weight --recalibrate."
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    Ledger(project_root / _LEDGER_PATH).append(
        surface_weight_recalibrated_event(
            attestor=attestor,
            reason=reason,
            floor_lines=current,
            previous_floor_lines=previous_lines,
            green_ceiling=_GREEN_CEILING,
            yellow_ceiling=_YELLOW_CEILING,
        )
    )

    return RecalibrationOutcome(
        floor_lines=current,
        previous_floor_lines=previous_lines,
        green_ceiling=_GREEN_CEILING,
        yellow_ceiling=_YELLOW_CEILING,
    )


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


def _newest_recalibration(project_root: Path) -> tuple[datetime, dict] | None:
    """Return the most recent recalibration event and its parsed timestamp, or None.

    One ledger scan serving both consumers — :func:`_check_floor_drift` (which
    reads the timestamp) and :func:`_check_band_coherence` (which reads the band
    ceilings). They were never going to agree about "most recent" if each walked
    the ledger with its own copy of the comparison.

    ``None`` means bootstrap: no recalibration has ever been witnessed, so there
    is no baseline for either consumer to measure against.
    """
    ledger_path = project_root / _LEDGER_PATH
    if not ledger_path.exists():
        return None

    newest: tuple[datetime, dict] | None = None
    try:
        for line in ledger_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("event") != _RECALIBRATION_EVENT_TYPE:
                continue
            try:
                ts = datetime.fromisoformat(event.get("ts", ""))
            except (ValueError, TypeError):
                continue
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            if newest is None or ts > newest[0]:
                newest = (ts, event)
    except (OSError, json.JSONDecodeError):
        return None
    return newest


def _check_band_coherence(project_root: Path) -> list[ValidationError]:
    """Fail closed when the live band constants disagree with their newest witness.

    The mechanical arm of ADR-0.0.33 § Anti-Patterns item 3 — *"Adjusting the
    surface-weight green/yellow/red thresholds without an attested recalibration
    event ... Band changes are ledger events, not config tweaks"* (GHI #792).
    GHI #791 gave that ceremony a producer; nothing made SKIPPING it detectable,
    so the 2026-06-30 change (green 1800->2600) went 42 days undetected across
    every ``gz check`` run in the window and was found only because a human went
    looking at the ceremony.

    **Compares state, never detects an edit.** A checker watching for a diff on
    the constants would need git awareness, would fire only at commit time, and
    would be defeated by any path not routed through that hook. Disagreement
    between the constants and the newest witness is a standing property: true or
    false at any moment, on a fresh clone, in CI, or mid-session. The recovery is
    the verb that already exists, and it is self-healing — recalibrating emits an
    event carrying the current constants, which restores agreement.

    Only the NEWEST witness binds. A superseded band generation is history, not
    drift; reading "any event" would redden every repo that has recalibrated
    twice.
    """
    newest = _newest_recalibration(project_root)
    if newest is None:
        return []  # Bootstrap: no witnessed baseline, so the constants ARE the baseline.

    _, event = newest
    witnessed_green = event.get("green_ceiling")
    witnessed_yellow = event.get("yellow_ceiling")

    # A witness that carries NO band claim is silent about bands, not evidence of
    # drift. Reporting drift here would fail for a reason the finding does not
    # name — the FACADE shape `_qc_negative_controls` exists to catch — and the
    # honest diagnosis of a bandless event is "this says nothing", not "these
    # disagree". It is not a bypass: `schemas/ledger.json` marks both ceilings
    # REQUIRED on this event type, so `gz validate --ledger` fail-closes on a
    # bandless one and no governed path can emit it.
    if witnessed_green is None and witnessed_yellow is None:
        return []

    if witnessed_green == _GREEN_CEILING and witnessed_yellow == _YELLOW_CEILING:
        return []

    msg = (
        f"Band drift detected: the code carries green <= {_GREEN_CEILING} / "
        f"yellow <= {_YELLOW_CEILING}, but the most recent "
        f"{_RECALIBRATION_EVENT_TYPE} event witnesses green <= {witnessed_green} / "
        f"yellow <= {witnessed_yellow}. ADR-0.0.33 Anti-Pattern 3 forbids a silent "
        f"band change ('Band changes are ledger events, not config tweaks'); the "
        f"constants in src/gzkit/governance/trust_audits/surface_weight.py moved "
        f"without an attested event. Re-witness via: uv run gz validate "
        f'--surface-weight --recalibrate --attestor "<name>" --reason '
        f'"<operational evidence>" — or revert the constants to the witnessed values.'
    )
    return [_make_error(msg)]


def _check_floor_drift(floor: dict, project_root: Path) -> list[ValidationError]:
    """Check if the floor timestamp predates the most recent recalibration event by >24h."""
    newest = _newest_recalibration(project_root)
    if newest is None:
        return []  # Bootstrap: no recalibration events
    last_recalibration_ts = newest[0]

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
            f"Recalibrate via: uv run gz validate --surface-weight --recalibrate "
            f'--attestor "<name>" --reason "<operational evidence>" — it re-snapshots '
            f"data/surface_weight_floor.json and appends the witnessing event together."
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
