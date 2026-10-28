"""Safe mode holds the alarms off; any other marker state lets them run (ruling 2026-10-25)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from gzkit.commands.quality import _STEP_GUARD_META
from gzkit.commands.validate_cmd import VALIDATOR_REGISTRY
from gzkit.mx import alarms, levels


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

    def test_a_missing_separator_or_command_is_a_usage_error(self):
        for argv in (["hook"], ["hook", "--"], ["hook", "x", "cmd"]):
            with self.subTest(argv=argv), mock.patch("sys.stderr"):
                self.assertEqual(alarms.main(argv), 2)

    def test_an_alarm_on_reports_its_command_status(self):
        with mock.patch.object(alarms, "alarms_off", return_value=False):
            self.assertEqual(alarms.main(["hook", *self._FAIL]), 3)


class TestFastStaticStaysArmed(unittest.TestCase):
    """Lint and the fast static checks stay armed in safe mode (operator, 2026-10-27)."""

    _HOOKS = ("ruff-check", "complexity-ceiling", "surface-fidelity-cheap", "lint-pre-push")
    _SCOPES = ("complexity_ceiling", "bullet_retention", "surface_weight", "pointer_anchors")
    _STEPS = ("Lint", "Complexity ceiling")

    def test_no_fast_static_hook_routes_through_the_alarm_switch(self):
        config = yaml.safe_load(
            (Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml").read_text(
                encoding="utf-8"
            )
        )
        entries = {h["id"]: h.get("entry", "") for repo in config["repos"] for h in repo["hooks"]}
        for hook in self._HOOKS:
            with self.subTest(hook=hook):
                self.assertIn(hook, entries)
                self.assertNotIn("gzkit.mx.alarms", entries[hook])

    def test_the_pytest_ban_hook_never_routes_through_the_alarm_switch(self):
        """Operator, 2026-10-25: "never, ever, ever turn this off: "the pytest ban""."""
        config = yaml.safe_load(
            (Path(__file__).resolve().parents[2] / ".pre-commit-config.yaml").read_text(
                encoding="utf-8"
            )
        )
        entries = {h["id"]: h.get("entry", "") for repo in config["repos"] for h in repo["hooks"]}
        self.assertIn("forbid-pytest", entries)
        self.assertNotIn("gzkit.mx.alarms", entries["forbid-pytest"])

    def test_fast_static_scopes_are_pinned_critical(self):
        levels_by_scope = {e.stem: e.level for e in VALIDATOR_REGISTRY}
        for scope in self._SCOPES:
            with self.subTest(scope=scope):
                self.assertEqual(levels_by_scope[scope], levels.CRITICAL)

    def test_fast_static_check_steps_are_pinned_critical(self):
        for step in self._STEPS:
            with self.subTest(step=step):
                self.assertEqual(_STEP_GUARD_META[step][1], levels.CRITICAL)
