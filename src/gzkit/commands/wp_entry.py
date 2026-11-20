"""``gz wp entry`` commands over the maintenance record (RP-12 O4 task 1).

The group the operator ruled on 2026-11-20 (RP-12 ruling 168). `book` is the
stamped call of the dispatch that did the work (rulings 167 and 175, ruling 133's
form): `gz`'s entry keeps the stamped dispatch id before it consumes the stamp,
and the writer, `gzkit.mx.entries.record_entry_book`, refuses a call not stamped
with the dispatch named. The open MX session, read from the marker here and passed
as a parameter, is recorded with the entry (ruling 8); the writer reads neither the
stamp nor the marker (ruling 174), and every refusal it raises exits 3 and books
nothing.
"""

from typing import TYPE_CHECKING

from gzkit.cli.formatters import OutputFormatter
from gzkit.commands.common import ensure_initialized, get_project_root
from gzkit.commands.wp_tag import MARKER_RECOVERY
from gzkit.core.exceptions import PolicyBreachError
from gzkit.ledger import Ledger
from gzkit.mx import marker
from gzkit.mx.entries import EntryBook, EntryError, record_entry_book

if TYPE_CHECKING:
    from pathlib import Path


def _open_session_id(root: Path, ledger_path: Path) -> str | None:
    """Read the open MX session's id, or None when no marker is present.

    A marker present but not on, unreadable, unbound to an open session or
    exiting, records no entry either, and its recovery is not `gz mx enter`, which
    a present marker refuses; so it is refused here with the recovery its cause names.

    Returns:
        The marker's session id while the condition is on, or None when it is absent.

    Raises:
        PolicyBreachError: A marker is present and the condition is not on.

    """
    held = marker.condition(root, ledger_path)
    if held.on and held.marker is not None:
        return held.marker.session_id
    if held.cause in MARKER_RECOVERY:
        msg = (
            f"The MX marker is present but {held.cause}, so no session is open to record "
            "the entry under. An entry records the MX session its work was done under "
            f"(RP-12 ruling 8). {MARKER_RECOVERY[held.cause]}, then book the entry again."
        )
        raise PolicyBreachError(msg)
    return None


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
            commenced or blocked, a ledger row that does not parse); nothing is booked.

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
