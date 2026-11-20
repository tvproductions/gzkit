"""The open MX session, read from the marker for a `gz wp` act that records it (RP-12).

A tag is held by the open MX session (rulings 3 and 114), and an entry records the
session its work was done under (ruling 8). The writers take the session's id as a
parameter and read no marker (rulings 119 and 174); the commands read it here, one
reader for every group, each naming its own act in the refusal.
"""

from typing import TYPE_CHECKING

from gzkit.core.exceptions import PolicyBreachError
from gzkit.mx import marker

if TYPE_CHECKING:
    from pathlib import Path

#: The recovery for a marker present but not on, by its cause (`.gzkit/rules/mx-mode.md`).
MARKER_RECOVERY = {
    "unreadable": "Have the operator repair it through the gz-mx skill (`uv run gz mx repair`)",
    "unbound": "Have the operator repair it through the gz-mx skill (`uv run gz mx repair`)",
    "exiting": "Let the exit finish, then have the operator open a session through the gz-mx skill",
}


def open_session_id(root: Path, ledger_path: Path, *, why: str, again: str) -> str | None:
    """Read the open MX session's id, or None when no marker is present.

    A marker present but not on, unreadable, unbound to an open session or exiting,
    serves no act either, and its recovery is not `gz mx enter`, which a present
    marker refuses; so it is refused here with the recovery its cause names. ``why``
    completes "no session is open ..." with the act's need for one, and ``again`` names
    the step that repeats the act once the marker is repaired.

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
            f"The MX marker is present but {held.cause}, so no session is open {why}. "
            f"{MARKER_RECOVERY[held.cause]}, then {again}."
        )
        raise PolicyBreachError(msg)
    return None
