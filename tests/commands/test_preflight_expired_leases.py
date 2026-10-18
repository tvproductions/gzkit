"""gz preflight reports an expired work lock as a booked lease, never a cleanup.

Operator ruling 2026-10-18: expiry is booked and announced, never evicted, for the
token block as for the hangar. ``--apply`` no longer removes an expired work lock, so
preflight must not count one as an issue it offers to clean; only the orphan
``mx-session`` lock, whose hangar is closed, is still cleaned.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.preflight import preflight_cmd
from gzkit.lock_manager import LockData, read_lock, write_lock
from gzkit.mx.marker import SESSION_LOCK_KEY


def _root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir()
    (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")
    return root


def _expired(root: Path, obpi_id: str) -> None:
    claimed = (datetime.now(UTC) - timedelta(days=3)).isoformat()
    write_lock(
        root,
        LockData(
            obpi_id=obpi_id,
            agent="agent-a",
            pid=1,
            session_id="s",
            claimed_at=claimed,
            branch="main",
            ttl_minutes=60,
        ),
    )


def _run(root: Path, **kwargs) -> tuple[str, int]:
    config = MagicMock()
    config.paths.ledger = ".gzkit/ledger.jsonl"
    out = io.StringIO()
    code = 0
    with (
        patch("gzkit.commands.preflight.ensure_initialized", return_value=config),
        patch("gzkit.commands.preflight.get_project_root", return_value=root),
        patch("gzkit.commands.preflight.console", Console(file=out, width=200)),
        redirect_stdout(out),
    ):
        try:
            preflight_cmd(**kwargs)
        except SystemExit as exc:
            code = int(exc.code or 0)
    return out.getvalue(), code


class TestAnExpiredWorkLockIsAnnouncedNotCleaned(unittest.TestCase):
    def test_an_expired_work_lock_alone_is_not_an_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root, "OBPI-0.1.0-01")
            text, code = _run(root)
        self.assertEqual(code, 0)
        self.assertIn("never evicted", text)
        self.assertNotIn("--apply to clean up", text)

    def test_apply_leaves_the_expired_work_lock_held(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root, "OBPI-0.1.0-01")
            _run(root, apply=True)
            self.assertIsNotNone(read_lock(root, "OBPI-0.1.0-01"))

    def test_the_orphan_session_lock_is_still_an_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root, SESSION_LOCK_KEY)
            text, code = _run(root)
        self.assertEqual(code, 1)
        self.assertIn("--apply to clean up", text)

    def test_json_marks_which_expired_locks_stay_held(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root, "OBPI-0.1.0-01")
            _expired(root, SESSION_LOCK_KEY)
            text, _ = _run(root, as_json=True)
        held = {row["obpi_id"]: row["held"] for row in json.loads(text)["expired_locks"]}
        self.assertEqual(held, {"OBPI-0.1.0-01": True, SESSION_LOCK_KEY: False})


if __name__ == "__main__":
    unittest.main()
