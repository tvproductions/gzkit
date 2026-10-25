"""Safe mode holds the alarms off; any other marker state lets them run (ruling 2026-10-25)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.mx import alarms


class TestAlarmsOff(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def _marker(self, mode: str, *, exiting: bool = False) -> None:
        body = {"session_id": "s", "opened_at": "2026-10-25T00:00:00+00:00", "mode": mode}
        body["exiting"] = exiting
        if mode == "safe":
            body["contract"] = "docs/c.md"
        (self.root / ".gzkit" / "mx.json").write_text(json.dumps(body), encoding="utf-8")

    def test_safe_mode_holds_the_alarms_off(self):
        self._marker("safe")
        self.assertTrue(alarms.alarms_off(self.root))

    def test_the_exit_rerun_turns_them_back_on(self):
        self._marker("safe", exiting=True)
        self.assertFalse(alarms.alarms_off(self.root))

    def test_the_hangar_and_no_marker_leave_them_on(self):
        self.assertFalse(alarms.alarms_off(self.root))
        self._marker("mx")
        self.assertFalse(alarms.alarms_off(self.root))


class TestMain(unittest.TestCase):
    _FAIL = ("--", sys.executable, "-c", "raise SystemExit(3)")

    def test_an_alarm_off_does_not_run(self):
        with mock.patch.object(alarms, "alarms_off", return_value=True):
            self.assertEqual(alarms.main(["hook", *self._FAIL]), 0)

    def test_an_alarm_on_reports_its_command_status(self):
        with mock.patch.object(alarms, "alarms_off", return_value=False):
            self.assertEqual(alarms.main(["hook", *self._FAIL]), 3)
