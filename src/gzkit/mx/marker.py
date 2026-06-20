"""MX marker — the single filesystem truth-source for Maintenance Hangar mode.

ADR-0.0.74 Decision item #1: a dumb filesystem truth-file whose *presence* means
``MX==TRUE``, read without importing any gzkit-internal subsystem (pydantic +
stdlib only) so it opens even when gz's own subsystems are the patient, and
*valid only* when bound to a real ``mx_session_opened`` ledger event the tool
wrote — a hand-created marker with no matching event is void (anti-contrivance).

**No gzkit-internal imports** (binding): this module must import cleanly when
unrelated ``gz`` subsystems are broken or mid-repair — the literal MX premise
(repairing gz while gz is the patient). Pydantic + stdlib only; pydantic is a
pinned core dependency, as present as the interpreter wherever gzkit runs, so it
is not "the patient". ``tests/mx/test_marker.py`` AST-asserts the absence of any
``gzkit.*`` import. The ledger binding is read raw (line-by-line stdlib
``json``), never via ``gzkit.ledger`` — coupling the marker to a breakable gz
subsystem (whose ``LedgerEvent`` validation would also reject the malformed
lines we want to tolerate) is exactly what MX mode exists to survive.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

# The single MX truth-source location (ADR-0.0.74 Boundary Invariant #1). Every
# surface — code guards and agents — reads MX state from here and nowhere else.
MARKER_RELPATH = (".gzkit", "mx.json")
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")

# Ledger event types the binding check matches (raw "event" field, per the
# ledger line shape {"schema":…, "event":…, …}).
_OPENED_EVENT = "mx_session_opened"
_CLOSED_EVENT = "mx_session_closed"


class Marker(BaseModel):
    """The marker payload. ``session_id`` is the binding key to the ledger.

    ``opened_at`` / ``reason`` / ``attestor`` / ``inspection_scope`` are the
    fields ``gz mx enter`` (OBPI-04) populates and ``gz mx exit`` (OBPI-05)
    re-runs against; OBPI-01 ships the schema and the load-bearing
    ``session_id`` binding.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str = Field(
        ..., description="Binding key to the mx_session_opened ledger event"
    )
    opened_at: str = Field(
        "", description="ISO-8601 open timestamp (written by gz mx enter, OBPI-04)"
    )
    reason: str = Field("", description="Operator reason for entering MX mode")
    attestor: str = Field("", description="Operator who opened the hangar")
    inspection_scope: list[str] = Field(
        default_factory=list, description="ADRs/OBPIs under inspection"
    )


def _find_project_root(start: Path | None = None) -> Path:
    """Walk up from *start* (cwd by default) to the nearest dir holding ``.gzkit``.

    Self-contained stdlib walk — deliberately does NOT import ``gzkit.hooks`` so
    the marker read keeps working when gz itself is broken. Falls back to the
    starting dir when no ``.gzkit`` is found, so callers get a deterministic path
    rather than an exception.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".gzkit").is_dir():
            return candidate
    return current


def marker_path(project_root: Path | None = None) -> Path:
    """The single MX truth-source path (``<root>/.gzkit/mx.json``)."""
    root = project_root if project_root is not None else _find_project_root()
    return root.joinpath(*MARKER_RELPATH)


def is_active(project_root: Path | None = None) -> bool:
    """``True`` when the marker file is present on disk → ``MX==TRUE``.

    Presence only — the cheap truth-file read code guards use. Validity (the
    ledger binding) is the separate anti-contrivance gate, :func:`is_valid`.
    """
    return marker_path(project_root).is_file()


def read(project_root: Path | None = None) -> Marker | None:
    """Parse and validate the marker payload (pydantic over stdlib-read bytes).

    Returns ``None`` when the marker is absent, malformed, or fails schema
    validation — never raises into a guard. (``ValidationError`` subclasses
    ``ValueError``, so the single except covers bad JSON and bad schema.)
    """
    path = marker_path(project_root)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        return Marker.model_validate_json(raw)
    except ValueError:
        return None


def write(marker: Marker, project_root: Path | None = None) -> Path:
    """Persist *marker* as JSON and return its path.

    Low-level write only — the coupled ``mx_session_opened`` ledger event is
    written by ``gz mx enter`` (OBPI-04), not here.
    """
    path = marker_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(marker.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def _ledger_path(
    project_root: Path | None = None, ledger_path: Path | None = None
) -> Path:
    if ledger_path is not None:
        return ledger_path
    root = project_root if project_root is not None else _find_project_root()
    return root.joinpath(*_LEDGER_RELPATH)


def _open_session_ids(ledger: Path) -> set[str]:
    """``session_id``s with an ``mx_session_opened`` and no later close.

    Read raw with stdlib ``json`` (tolerant of malformed lines, no
    ``gzkit.ledger`` dependency) so the binding check works when gz is the
    patient.
    """
    opened: set[str] = set()
    closed: set[str] = set()
    try:
        text = ledger.read_text(encoding="utf-8")
    except OSError:
        return set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except (ValueError, TypeError):
            continue
        if not isinstance(event, dict):
            continue
        sid = event.get("session_id")
        if not isinstance(sid, str) or not sid:
            continue
        kind = event.get("event")
        if kind == _OPENED_EVENT:
            opened.add(sid)
        elif kind == _CLOSED_EVENT:
            closed.add(sid)
    return opened - closed


def is_valid(
    project_root: Path | None = None, ledger_path: Path | None = None
) -> bool:
    """``True`` only when the marker is present AND bound to a real, still-open
    ``mx_session_opened`` ledger event (anti-contrivance).

    A hand-created marker with no matching event is void → ``False``; a marker
    whose session was closed (``mx_session_closed``) is also void.
    """
    marker = read(project_root)
    if marker is None or not marker.session_id:
        return False
    ledger = _ledger_path(project_root, ledger_path)
    return marker.session_id in _open_session_ids(ledger)
