"""Tests for gzkit.commands.arb dispatchers.

@covers REQ-0.25.0-33-03
@covers REQ-0.25.0-33-05
"""

import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


class TestArbCommands(unittest.TestCase):
    """CLI dispatcher functions honor exit codes and emit receipts."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._receipts_dir = Path(self._tempdir.name) / "receipts"
        self._prior_env = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
        os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(self._receipts_dir)

    def tearDown(self) -> None:
        if self._prior_env is None:
            os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
        else:
            os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = self._prior_env
        self._tempdir.cleanup()

    def _fake_ruff_runner(self, returncode: int, stdout: str = "[]"):
        def fake_run(cmd, **kwargs):  # noqa: ARG001
            if "ruff" in cmd and "check" in cmd:
                return subprocess.CompletedProcess(cmd, returncode, stdout, "")
            if "ruff" in cmd and "--version" in cmd:
                return subprocess.CompletedProcess(cmd, 0, "ruff 0.5.0\n", "")
            if cmd[:2] == ["git", "rev-parse"] and cmd[-1] == "HEAD":
                return subprocess.CompletedProcess(cmd, 0, "abcdef1234567\n", "")
            if cmd[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(cmd, 0, "main\n", "")
            if cmd[:2] == ["git", "status"]:
                return subprocess.CompletedProcess(cmd, 0, "", "")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        return fake_run

    def test_arb_ruff_cmd_returns_exit_status_0_on_success(self) -> None:
        from gzkit.commands.arb import arb_ruff_cmd

        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=self._fake_ruff_runner(0)):
            exit_code = arb_ruff_cmd(paths=["src"], quiet=True)

        self.assertEqual(exit_code, 0)

    def test_arb_ruff_cmd_returns_exit_status_1_on_findings(self) -> None:
        from gzkit.commands.arb import arb_ruff_cmd

        findings = json.dumps(
            [{"code": "E501", "filename": "x.py", "location": {"row": 1}, "message": "m"}]
        )
        fake = self._fake_ruff_runner(1, stdout=findings)
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_code = arb_ruff_cmd(paths=["src"], quiet=True)

        self.assertEqual(exit_code, 1)

    def test_arb_step_cmd_runs_and_writes_receipt(self) -> None:
        from gzkit.commands.arb import arb_step_cmd

        fake = subprocess.CompletedProcess(["echo", "hi"], 0, "hi\n", "")
        with (
            patch("gzkit.arb.step_reporter.subprocess.run", return_value=fake),
            patch(
                "gzkit.arb.step_reporter._git_context",
                return_value={"commit": "abcdef1"},
            ),
        ):
            exit_code = arb_step_cmd(name="echo", argv=["echo", "hi"], quiet=True)

        self.assertEqual(exit_code, 0)
        receipts = list(self._receipts_dir.glob("*.json"))
        self.assertEqual(len(receipts), 1)

    def test_arb_step_cmd_rejects_empty_name(self) -> None:
        from gzkit.commands.arb import arb_step_cmd

        exit_code = arb_step_cmd(name="", argv=["echo"], quiet=True)
        self.assertEqual(exit_code, 2)

    def test_arb_validate_cmd_empty_dir_returns_0(self) -> None:
        from gzkit.commands.arb import arb_validate_cmd

        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = arb_validate_cmd()
        self.assertEqual(exit_code, 0)
        self.assertIn("ARB Receipt Validation", buf.getvalue())

    def test_arb_validate_cmd_json_output(self) -> None:
        from gzkit.commands.arb import arb_validate_cmd

        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = arb_validate_cmd(as_json=True)
        self.assertEqual(exit_code, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["scanned"], 0)

    def test_arb_advise_cmd_empty_dir_returns_0(self) -> None:
        from gzkit.commands.arb import arb_advise_cmd

        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = arb_advise_cmd()
        self.assertEqual(exit_code, 0)
        self.assertIn("ARB Advice", buf.getvalue())

    def test_arb_patterns_cmd_empty_dir_returns_0(self) -> None:
        from gzkit.commands.arb import arb_patterns_cmd

        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = arb_patterns_cmd()
        self.assertEqual(exit_code, 0)
        self.assertIn("Pattern Extraction Report", buf.getvalue())

    def test_arb_patterns_cmd_compact_mode(self) -> None:
        from gzkit.commands.arb import arb_patterns_cmd

        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = arb_patterns_cmd(compact=True)
        self.assertEqual(exit_code, 0)
        self.assertIn("arb patterns:", buf.getvalue())
