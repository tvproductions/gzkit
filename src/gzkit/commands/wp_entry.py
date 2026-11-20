"""``gz wp entry`` commands over the maintenance record (RP-12 O4 task 1, acts 2 and 3).

The group the operator ruled on 2026-11-20 (RP-12 ruling 168). `book` is the
stamped call of the dispatch that did the work (rulings 167 and 175, ruling 133's
form): `gz`'s entry keeps the stamped dispatch id before it consumes the stamp,
and the writer, `gzkit.mx.entries.record_entry_book`, refuses a call not stamped
with the dispatch named. The open MX session, read from the marker here and passed
as a parameter, is recorded with the entry (ruling 8); the writer reads neither the
stamp nor the marker (ruling 174), and every refusal it raises exits 3 and books
nothing. `show` renders the record from the ledger, read-only (rulings 8 and 168):
each entry with its order's Gate 5, the signature, joined by `record_view`.
"""

from typing import TYPE_CHECKING

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.commands.open_session import open_session_id
from gzkit.core.exceptions import PolicyBreachError
from gzkit.ledger import Ledger
from gzkit.mx.entries import EntryBook, EntryError, record_entry_book, record_view

if TYPE_CHECKING:
    from pathlib import Path

    from gzkit.mx.entries import RecordedEntry


def _open_session_id(root: Path, ledger_path: Path) -> str | None:
    """Read the open MX session the entry records its work was done under.

    Returns:
        The session's id, or None when no marker is present (`open_session_id`).

    """
    return open_session_id(
        root,
        ledger_path,
        why=(
            "to record the entry under. An entry records the MX session its work was "
            "done under (RP-12 ruling 8)"
        ),
        again="book the entry again",
    )


def wp_entry_book_cmd(
    *, request: dict[str, str], stamped_dispatch_id: str | None, as_json: bool
) -> None:
    """Book the performer's maintenance-record entry for one act (RP-12 rulings 8, 167-175).

    ``request`` carries the verb's fields: the slug, the dispatch named, what was
    done, the measurement before and after, and the witness that measured them.
    The entry is the stamped call of the dispatch ``--dispatch`` names:
    ``stamped_dispatch_id`` is the id the call was stamped with, None for an
    unstamped call, and the writer refuses unless it is the one named. The open
    MX session, read from the marker here, is recorded with the entry; the order
    and package are read from the dispatch record. Prints ``Booked <ENT-id> on
    <ORD-id> by <D-id>.``, or with ``--json`` the `entry_booked` event booked.

    Raises:
        PolicyBreachError: The marker is present but not on, or the writer refuses
            the entry (no MX session open, the call not stamped with the dispatch
            named, a malformed slug or a blank field, the dispatch not a live
            Implementer, SingleDriver or Restoration on an order, the order not
            commenced or blocked); nothing is booked.

    """
    config = ensure_initialized()
    root = get_project_root()
    ledger_path = root / config.paths.ledger
    try:
        event = record_entry_book(
            Ledger(ledger_path),
            EntryBook.model_validate(request),
            stamped_id=stamped_dispatch_id,
            mx_session_id=_open_session_id(root, ledger_path),
        )
    except EntryError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    fmt.emit(
        event if as_json else f"Booked {event.entry_id} on {event.order} by {event.dispatch_id}."
    )


def _gate5_line(view: RecordedEntry) -> str:
    """Write the entry's signature: its order's Gate 5 attestor, decision and date (ruling 8).

    Returns:
        ``<attestor>, <decision>, <ts>`` once the order is closed, else ``not signed``.

    """
    closed = view.gate5
    if closed is None:
        return "not signed"
    return f"{closed.attestor}, {closed.decision}, {closed.ts}"


def _entry_block(view: RecordedEntry) -> str:
    """Write one entry as a block of labelled lines, each element legible (ruling 126's form).

    Returns:
        The entry's id, order and package, then each element of 14 CFR 43.9(a) on its own line.

    """
    entry = view.entry
    fields = (
        ("Booked", entry.ts),
        ("Performer", entry.dispatch_id),
        ("Description", entry.description),
        ("Before", entry.before),
        ("After", entry.after),
        ("Witness", entry.witness),
        ("MX session", entry.mx_session_id),
        ("Gate 5", _gate5_line(view)),
    )
    return "\n".join(
        (
            f"{entry.entry_id} on {entry.order} ({entry.work_package})",
            *(f"  {label + ':':<13}{value}" for label, value in fields),
        )
    )


def wp_entry_show_cmd(*, as_json: bool) -> None:
    """Show the maintenance record: every entry, oldest first (RP-12 rulings 8 and 168).

    The record is a Layer 3 view rendered from the ledger's `entry_booked` events
    through `gzkit.mx.entries.record_view`, each entry with its order's Gate 5, the
    signature 14 CFR 43.9(a) asks of the approver, once the order closes. The human
    form is a block of labelled lines per entry, ruling 126's form for the tag-out
    log, and a plain line when there is none; ``--json`` prints the list, each entry
    its event's fields with ``gate5``, the closing `order_transitioned` or None.

    The verb writes nothing, needs no MX session and is not refused from a
    subagent's call: a read is no one's act.

    Raises:
        PolicyBreachError: An `entry_booked` row, or an order's closing row, does not parse; the
            refusal names the row and the void that recovers it.

    """
    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    try:
        views = record_view(ledger)
    except EntryError as exc:
        raise PolicyBreachError(str(exc)) from exc
    fmt = OutputFormatter(OutputFormatter.mode_from_flags(json_flag=as_json))
    if as_json:
        fmt.emit(
            [
                {
                    **view.entry.model_dump(mode="json"),
                    "gate5": view.gate5.model_dump(mode="json") if view.gate5 else None,
                }
                for view in views
            ]
        )
    elif not views:
        fmt.emit("No entry has been booked.")
    else:
        fmt.emit("\n\n".join(_entry_block(view) for view in views))
