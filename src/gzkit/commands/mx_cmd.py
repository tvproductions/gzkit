"""gz mx command group — Maintenance Hangar (MX) mode operations.

ADR-0.0.74 Decision item #4: gz mx enter. The operator opens the door
(reason + attestor); the tool sets the marker, writes mx_session_opened,
and captures the inspection scope. The agent never opens the hangar on its own.
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit import lock_manager
from gzkit.commands.common import console, get_project_root
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.lock_manager import LockData
from gzkit.mx import marker
from gzkit.mx.marker import Marker

# Lock identity on the token rail — singleton key for the MX session.
_MX_LOCK_KEY = "mx-session"

# Default TTL matches OBPI lock TTL (not MX-specific — the marker is the real
# session truth, not the lock; the lock serializes concurrent entry only).
_DEFAULT_TTL_MINUTES = 120

# Ledger path relative to project root (parallel to marker.py's _LEDGER_RELPATH).
_LEDGER_RELPATH = (".gzkit", "ledger.jsonl")


def _mx_session_opened_event(
    session_id: str,
    reason: str,
    attestor: str,
    inspection_scope: list[str],
) -> LedgerEvent:
    """Build the mx_session_opened ledger event."""
    return LedgerEvent(
        event="mx_session_opened",
        id=session_id,
        extra={
            "session_id": session_id,
            "reason": reason,
            "attestor": attestor,
            "inspection_scope": list(inspection_scope),
        },
    )


def mx_enter_cmd(
    reason: str,
    attestor: str,
    inspection_scope: list[str],
    project_root: Path | None = None,
) -> None:
    """Open the MX maintenance hangar.

    Sets the marker file, writes one ``mx_session_opened`` ledger event, and
    captures the inspection scope.  The operator (``attestor``) is required;
    an agent cannot open the hangar autonomously.  Empty or whitespace-only
    ``reason`` or ``attestor`` fails closed with exit 1.
    """
    if not reason.strip():
        console.print("[red]ERROR:[/red] --reason cannot be empty.")
        sys.exit(1)
    if not attestor.strip():
        console.print(
            "[red]ERROR:[/red] --attestor cannot be empty. "
            "MX cannot be opened autonomously — an operator attestor is required."
        )
        sys.exit(1)

    root = project_root if project_root is not None else get_project_root()

    if marker.is_active(root):
        console.print("[red]ERROR:[/red] MX mode is already active.")
        sys.exit(1)

    # Acquire the session on the lock_manager token rail to serialize concurrent entry.
    session_id = lock_manager.resolve_session_id()
    lock = LockData(
        obpi_id=_MX_LOCK_KEY,
        agent=lock_manager.resolve_agent(),
        pid=os.getpid(),
        session_id=session_id,
        claimed_at=datetime.now(UTC).isoformat(),
        branch=lock_manager.current_branch(),
        ttl_minutes=_DEFAULT_TTL_MINUTES,
    )
    try:
        lock_manager.write_lock(root, lock)
    except FileExistsError:
        console.print(
            "[red]ERROR:[/red] Concurrent MX entry detected — another session is opening."
        )
        sys.exit(1)

    # Write the marker (sets MX==TRUE).
    now = datetime.now(UTC).isoformat()
    m = Marker(
        session_id=session_id,
        opened_at=now,
        reason=reason.strip(),
        attestor=attestor.strip(),
        inspection_scope=list(inspection_scope),
    )
    marker.write(m, root)

    # Write the mx_session_opened ledger event (binds the marker anti-contrivance).
    ledger = Ledger(root.joinpath(*_LEDGER_RELPATH))
    ledger.append(
        _mx_session_opened_event(session_id, reason.strip(), attestor.strip(), inspection_scope)
    )

    console.print(
        f"[green]MX session opened.[/green] session_id={session_id}, attestor={attestor.strip()}"
    )
