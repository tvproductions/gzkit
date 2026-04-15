"""Tests for gzkit.arb.step_reporter.

@covers REQ-0.25.0-33-03
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator


def _load_schema() -> dict:
    schema_path = (
        Path(__file__).resolve().parents[2] / "data" / "schemas" / "arb_step_receipt.schema.json"
    )
    return json.loads(schema_path.read_text(encoding="utf-8"))


class TestRunStepViaArb(unittest.TestCase):
    """run_step_via_arb wraps arbitrary commands and emits step receipts."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._receipts_dir = Path(self._tempdir.name) / "receipts"
        self._prior_env = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
        os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(self._receipts_dir)
        self._validator = Draft202012Validator(_load_schema())
        self._git_patcher = patch(
            "gzkit.arb.step_reporter._git_context",
            return_value={"commit": "abcdef1", "branch": "main", "dirty": False},
        )
        self._git_patcher.start()

    def tearDown(self) -> None:
        self._git_patcher.stop()
        if self._prior_env is None:
            os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
        else:
            os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = self._prior_env
        self._tempdir.cleanup()

    def _run_with_fake_result(self, result: subprocess.CompletedProcess):
        from gzkit.arb.step_reporter import run_step_via_arb

        with patch("gzkit.arb.step_reporter.subprocess.run", return_value=result):
            return run_step_via_arb(
                name="unittest",
                cmd=["uv", "run", "-m", "unittest"],
                quiet=True,
            )

    def test_passing_step_writes_receipt(self) -> None:
        fake = subprocess.CompletedProcess(["uv", "run", "-m", "unittest"], 0, "OK\n", "")
        exit_status, path = self._run_with_fake_result(fake)
        self.assertEqual(exit_status, 0)
        self.assertIsNotNone(path)

        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = list(self._validator.iter_errors(payload))
        self.assertEqual(errors, [], msg=f"Invalid receipt: {errors}")
        self.assertEqual(payload["schema"], "gzkit.arb.step_receipt.v1")
        self.assertEqual(payload["step"]["name"], "unittest")
        self.assertEqual(payload["exit_status"], 0)
        self.assertEqual(payload["stdout_tail"], "OK\n")

    def test_failing_step_writes_receipt(self) -> None:
        fake = subprocess.CompletedProcess(
            ["uv", "run", "-m", "unittest"], 1, "", "AssertionError: boom\n"
        )
        exit_status, path = self._run_with_fake_result(fake)
        self.assertEqual(exit_status, 1)
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = list(self._validator.iter_errors(payload))
        self.assertEqual(errors, [], msg=f"Invalid receipt: {errors}")
        self.assertEqual(payload["exit_status"], 1)
        self.assertIn("AssertionError", payload["stderr_tail"])

    def test_tail_truncation(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        long_stdout = "x" * 5000
        fake = subprocess.CompletedProcess(["echo"], 0, long_stdout, "")
        with patch("gzkit.arb.step_reporter.subprocess.run", return_value=fake):
            exit_status, path = run_step_via_arb(
                name="echo-big",
                cmd=["echo", "big"],
                max_output_chars=200,
                quiet=True,
            )
        self.assertEqual(exit_status, 0)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["stdout_tail"]), 200)
        self.assertTrue(payload["stdout_truncated"])

    def test_empty_name_rejected(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        with self.assertRaises(ValueError):
            run_step_via_arb(name="", cmd=["echo", "hi"])

    def test_empty_cmd_rejected(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        with self.assertRaises(ValueError):
            run_step_via_arb(name="echo", cmd=[])
