"""Unit tests for gz mx repair (GHI #1273).

Operator ruling 2026-10-31 ("b"): the recovery the condition's announcement names is
a verb under ``gz mx``. A marker is rewritten from the session its ledger keeps open,
removed when no session backs it, and left alone when it is healthy.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.commands.mx_cmd import mx_enter_cmd, mx_repair_cmd
from gzkit.mx import marker
from gzkit.mx.marker import Marker
from tests.commands.common import SilencedConsoleTestCase
from tests.mx.held import bind_session


def _events(root: Path, event_type: str) -> list[dict]:
    ledger = root / ".gzkit" / "ledger.jsonl"
    if not ledger.is_file():
        return []
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line]
    return [row for row in rows if row.get("event") == event_type]


class TestMxRepair(SilencedConsoleTestCase):
    def setUp(self) -> None:
        super().setUp()
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir()

    def _open(self) -> Marker:
        mx_enter_cmd(
            reason="drydock",
            attestor="g0",
            inspection_scope=["ADR-0.0.74"],
            project_root=self.root,
        )
        held = marker.read(self.root)
        assert held is not None
        return held

    def _repair(self) -> dict:
        mx_repair_cmd(attestor="g0", project_root=self.root)
        return _events(self.root, "mx_marker_repaired")[-1]

    def test_an_unreadable_marker_is_rewritten_from_its_open_session(self) -> None:
        held = self._open()
        marker.marker_path(self.root).write_text("{not json", encoding="utf-8")

        booked = self._repair()

        rebuilt = marker.read(self.root)
        assert rebuilt is not None
        self.assertEqual(
            rebuilt.model_dump(exclude={"opened_at"}), held.model_dump(exclude={"opened_at"})
        )
        self.assertTrue(marker.condition(self.root).on)
        self.assertEqual(booked["cause"], "unreadable")
        self.assertEqual(booked["action"], "rewritten")
        self.assertEqual(booked["session_id"], held.session_id)
        self.assertEqual(booked["attestor"], "g0")

    def test_a_missing_marker_is_rewritten_while_its_session_is_open(self) -> None:
        held = self._open()
        marker.marker_path(self.root).unlink()

        booked = self._repair()

        self.assertTrue(marker.condition(self.root).on)
        self.assertEqual((booked["cause"], booked["action"]), ("absent", "rewritten"))
        self.assertEqual(booked["session_id"], held.session_id)

    def test_a_marker_naming_the_wrong_session_is_rewritten_from_the_open_one(self) -> None:
        held = self._open()
        marker.write(Marker(session_id="other"), self.root)

        self._repair()

        rebuilt = marker.read(self.root)
        assert rebuilt is not None
        self.assertEqual(rebuilt.session_id, held.session_id)

    def test_the_rewrite_keeps_the_mode_and_contract_the_session_opened_with(self) -> None:
        (self.root / "contract.md").write_text("# c\n", encoding="utf-8")
        ledger = self.root / ".gzkit" / "ledger.jsonl"
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "mx_session_opened",
            "id": "s",
            "ts": "2026-10-20T00:00:00+00:00",
            "session_id": "s",
            "reason": "drydock",
            "attestor": "g0",
            "inspection_scope": [],
            "mode": "safe",
            "contract": "contract.md",
        }
        ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")

        self._repair()

        rebuilt = marker.read(self.root)
        assert rebuilt is not None
        self.assertEqual((rebuilt.level, rebuilt.contract), ("drydock", "contract.md"))
        self.assertEqual(rebuilt.opened_at, "2026-10-20T00:00:00+00:00")

    def test_a_marker_no_session_backs_is_removed(self) -> None:
        marker.write(Marker(session_id="hand-made"), self.root)

        booked = self._repair()

        self.assertFalse(marker.is_active(self.root))
        self.assertEqual((booked["cause"], booked["action"]), ("unbound", "removed"))

    def test_a_marker_left_exiting_by_a_killed_exit_is_rewritten(self) -> None:
        held = self._open()
        marker.write(held.model_copy(update={"exiting": True}), self.root)

        booked = self._repair()

        self.assertTrue(marker.condition(self.root).on)
        self.assertEqual((booked["cause"], booked["action"]), ("exiting", "rewritten"))

    def test_a_healthy_marker_or_none_changes_nothing(self) -> None:
        mx_repair_cmd(attestor="g0", project_root=self.root)
        self.assertEqual(_events(self.root, "mx_marker_repaired"), [])

        held = self._open()
        mx_repair_cmd(attestor="g0", project_root=self.root)
        self.assertEqual(marker.read(self.root), held)
        self.assertEqual(_events(self.root, "mx_marker_repaired"), [])

    def test_two_open_sessions_refuse_rather_than_guess(self) -> None:
        bind_session(self.root, "a")
        bind_session(self.root, "b")
        marker.marker_path(self.root).write_text("{not json", encoding="utf-8")

        with self.assertRaises(SystemExit) as refused:
            mx_repair_cmd(attestor="g0", project_root=self.root)

        self.assertEqual(refused.exception.code, 1)
        self.assertEqual(_events(self.root, "mx_marker_repaired"), [])

    def test_an_empty_attestor_refuses(self) -> None:
        marker.write(Marker(session_id="hand-made"), self.root)

        with self.assertRaises(SystemExit) as refused:
            mx_repair_cmd(attestor="  ", project_root=self.root)

        self.assertEqual(refused.exception.code, 1)
        self.assertTrue(marker.is_active(self.root))


if __name__ == "__main__":
    unittest.main()
