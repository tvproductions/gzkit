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

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AliasChoices, BaseModel, BeforeValidator, ConfigDict, Field

# The single MX truth-source location (ADR-0.0.74 Boundary Invariant #1). Every
# surface — code guards and agents — reads MX state from here and nowhere else.
MARKER_RELPATH = (".gzkit", "mx.json")
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")

# Ledger event types the binding check matches (raw "event" field, per the
# ledger line shape {"schema":…, "event":…, …}).
_OPENED_EVENT = "mx_session_opened"
_CLOSED_EVENT = "mx_session_closed"

# The standby level commanded at entry, and what a marker or ledger ``mode`` names
# (operator rulings 2026-10-27 and 2026-10-31, "A" and "a"; GHI #1273).
Level = Literal["hangar", "drydock"]
LEVEL_OF_MODE: dict[str, Level] = {"mx": "hangar", "safe": "drydock"}

# Why the condition reads as it does: ``on``, or the reason it is off.
ConditionCause = Literal["on", "absent", "unreadable", "unbound", "exiting"]

# The hangar's lease on the token rail: the singleton lock key `gz mx enter` claims.
# Named here, beside the marker it leases, so the lock reaper and the MX commands
# read one definition (GHI #1257).
SESSION_LOCK_KEY = "mx-session"


class Marker(BaseModel):
    """The marker payload. ``session_id`` is the binding key to the ledger.

    ``opened_at`` / ``reason`` / ``attestor`` / ``inspection_scope`` are the
    fields ``gz mx enter`` (OBPI-04) populates and ``gz mx exit`` (OBPI-05)
    re-runs against; OBPI-01 ships the schema and the load-bearing
    ``session_id`` binding.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str = Field(..., description="Binding key to the mx_session_opened ledger event")
    opened_at: str = Field(
        "", description="ISO-8601 open timestamp (written by gz mx enter, OBPI-04)"
    )
    reason: str = Field("", description="Operator reason for entering MX mode")
    attestor: str = Field("", description="Operator who opened the hangar")
    inspection_scope: list[str] = Field(
        default_factory=list, description="ADRs/OBPIs under inspection"
    )
    level: Annotated[Level, BeforeValidator(lambda value: LEVEL_OF_MODE.get(value, value))] = Field(
        "hangar",
        validation_alias=AliasChoices("level", "mode"),
        description=(
            "hangar: guards demote and the slow alarms stay on; drydock, safe mode: guards "
            "demote, the slow alarms are off and ceremony is suspended under a contract. A "
            "marker written before GHI #1273 carries ``mode``, read here as its alias"
        ),
    )
    contract: str = Field(
        "", description="Project-relative path of the safe-mode contract; empty under mx"
    )
    exiting: bool = Field(
        False,
        description=(
            "True while gz mx exit re-runs the guards: the marker is held through the "
            "checks, as gz obpi complete holds its lock, and demotes nothing (GHI #1257)"
        ),
    )


class Condition(BaseModel):
    """One reading of the non-operational condition, for whatever would lower a control."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    cause: ConditionCause = Field(..., description="Why the condition reads as it does")
    marker: Marker | None = Field(None, description="The marker payload, when it parsed")

    @property
    def on(self) -> bool:
        """Whether the marker lowers anything."""
        return self.cause == "on"


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
    """Return the single MX truth-source path (``<root>/.gzkit/mx.json``)."""
    root = project_root if project_root is not None else _find_project_root()
    return root.joinpath(*MARKER_RELPATH)


def is_active(project_root: Path | None = None) -> bool:
    """Return ``True`` when the marker file is present on disk → ``MX==TRUE``.

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


def _ledger_path(project_root: Path | None = None, ledger_path: Path | None = None) -> Path:
    if ledger_path is not None:
        return ledger_path
    root = project_root if project_root is not None else _find_project_root()
    return root.joinpath(*_LEDGER_RELPATH)


def _open_session_ids(ledger: Path) -> set[str]:
    """``session_id``s with an ``mx_session_opened`` and no later close.

    Read raw with stdlib ``json`` (tolerant of malformed lines, no
    ``gzkit.ledger`` dependency) so the binding check works when gz is the
    patient. Memoized on the ledger's size and modification time: every guard
    asks, and the ledger is tens of megabytes (GHI #1273).
    """
    try:
        stat = ledger.stat()
    except OSError:
        return set()
    return set(_scan_open_session_ids(ledger, stat.st_size, stat.st_mtime_ns))


@lru_cache(maxsize=8)
def _scan_open_session_ids(ledger: Path, _size: int, _mtime_ns: int) -> frozenset[str]:
    """Scan *ledger*; ``_size`` and ``_mtime_ns`` exist only to key the memo.

    Returns:
        The ids with an ``mx_session_opened`` and no ``mx_session_closed``.

    """
    opened: set[str] = set()
    closed: set[str] = set()
    try:
        text = ledger.read_text(encoding="utf-8")
    except OSError:
        return frozenset()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except ValueError, TypeError:
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
    return frozenset(opened - closed)


def is_valid(project_root: Path | None = None, ledger_path: Path | None = None) -> bool:
    """Return ``True`` only when the marker is present AND ledger-bound.

    Bound means a real, still-open ``mx_session_opened`` ledger event backs the
    marker (anti-contrivance). A hand-created marker with no matching event is
    void → ``False``; a marker whose session was closed (``mx_session_closed``)
    is also void.
    """
    marker = read(project_root)
    if marker is None or not marker.session_id:
        return False
    ledger = _ledger_path(project_root, ledger_path)
    return marker.session_id in _open_session_ids(ledger)


def condition(project_root: Path | None = None, ledger_path: Path | None = None) -> Condition:
    """Return the one reading of *on*: present, readable, ledger-bound and not exiting.

    Anything else is normal operation at full strength, so a hand-made or corrupted
    marker lowers nothing (operator ruling 2026-10-27, "A"; GHI #1273). A reader that
    raises protection on the file itself keeps :func:`is_active` (ruling 2026-10-31).

    Returns:
        The reading, with its cause and the marker when it parsed.

    """
    if not is_active(project_root):
        return Condition(cause="absent")
    held = read(project_root)
    if held is None:
        return Condition(cause="unreadable")
    if held.session_id not in _open_session_ids(_ledger_path(project_root, ledger_path)):
        return Condition(cause="unbound", marker=held)
    return Condition(cause="exiting" if held.exiting else "on", marker=held)
