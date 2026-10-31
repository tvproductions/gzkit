"""Open MX conditions for tests: a marker only counts when the ledger backs it (GHI #1273)."""

import json
from typing import TYPE_CHECKING

from gzkit.mx import marker
from gzkit.mx.marker import Marker

if TYPE_CHECKING:
    from pathlib import Path


def bind_session(root: Path, session_id: str) -> None:
    """Append the ``mx_session_opened`` row that binds a marker to *session_id*."""
    ledger = root / ".gzkit" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    row = {"event": "mx_session_opened", "session_id": session_id}
    with ledger.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")


def open_marker(root: Path, held: Marker | None = None) -> Marker:
    """Write *held*, or a default marker, and bind it, so the condition reads on.

    Returns:
        The marker written.

    """
    held = held if held is not None else Marker(session_id="test-session")
    marker.write(held, root)
    bind_session(root, held.session_id)
    return held
