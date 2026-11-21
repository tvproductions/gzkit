"""Open MX conditions for tests: a marker only counts when the ledger backs it (GHI #1273).

`git_project` makes a fixture project a git repository with a commit, which a green
`gz mx exit` needs since a git it cannot read refuses the exit (RP-12 ruling 193).
"""

import json
import subprocess
from typing import TYPE_CHECKING

from gzkit.mx import marker
from gzkit.mx.marker import Marker
from tests.commands.common import _isolated_git_env

if TYPE_CHECKING:
    from pathlib import Path


def bind_session(root: Path, session_id: str) -> None:
    """Append the ``mx_session_opened`` row that binds a marker to *session_id*."""
    ledger = root / ".gzkit" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_opened",
        "id": session_id,
        "ts": "2026-10-31T00:00:00+00:00",
        "session_id": session_id,
    }
    with ledger.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")


def git_project(root: Path) -> None:
    """Make *root* a git repository with one commit, so the exit can read its commits.

    `gz mx exit` refuses a git it cannot read (RP-12 ruling 193), and a repository with
    no commit is one it cannot read, so a fixture that exits green needs a commit.
    """
    env = _isolated_git_env()
    for args in (
        ["init", "-q"],
        ["config", "user.email", "t@e.st"],
        ["config", "user.name", "tester"],
        ["-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", "chore: seed"],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, env=env)  # noqa: S603 — a temp repo


def open_marker(root: Path, held: Marker | None = None) -> Marker:
    """Write *held*, or a default marker, and bind it, so the condition reads on.

    Returns:
        The marker written.

    """
    held = held if held is not None else Marker(session_id="test-session")
    marker.write(held, root)
    bind_session(root, held.session_id)
    return held
