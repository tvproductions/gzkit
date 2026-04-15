"""Tests for gzkit.arb.ruff_reporter.

@covers REQ-0.25.0-33-03
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


def _fake_run_factory(ruff_returncode: int, ruff_stdout: str = "", ruff_stderr: str = ""):
    """Route ruff check calls to fake output; leave version + git calls stubbed."""

    def fake_run(cmd, **kwargs):  # noqa: ARG001
        if "ruff" in cmd and "check" in cmd:
            return subprocess.CompletedProcess(cmd, ruff_returncode, ruff_stdout, ruff_stderr)
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


class TestRunRuffViaArb(unittest.TestCase):
    """run_ruff_via_arb wraps ruff and emits schema-compliant lint receipts."""

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

    def _assert_valid_receipt(self, path: Path, expected_exit: int) -> dict:
        from jsonschema import Draft202012Validator

        schema_path = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "schemas"
            / "arb_lint_receipt.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = list(validator.iter_errors(payload))
        self.assertEqual(errors, [], msg=f"Receipt invalid: {errors}")
        self.assertEqual(payload["schema"], "gzkit.arb.lint_receipt.v1")
        self.assertEqual(payload["exit_status"], expected_exit)
        return payload

    def test_green_run_writes_receipt_with_empty_findings(self) -> None:
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="[]", ruff_stderr="")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True)

        self.assertEqual(exit_status, 0)
        self.assertIsNotNone(path)
        payload = self._assert_valid_receipt(path, expected_exit=0)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["findings_total"], 0)

    def test_failing_run_captures_parsed_findings(self) -> None:
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        ruff_json = json.dumps(
            [
                {
                    "code": "E501",
                    "filename": "src/example.py",
                    "location": {"row": 10, "column": 81},
                    "message": "line too long",
                }
            ]
        )
        fake = _fake_run_factory(ruff_returncode=1, ruff_stdout=ruff_json, ruff_stderr="")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True)

        self.assertEqual(exit_status, 1)
        payload = self._assert_valid_receipt(path, expected_exit=1)
        self.assertEqual(payload["findings_total"], 1)
        finding = payload["findings"][0]
        self.assertEqual(finding["rule"], "E501")
        self.assertEqual(finding["path"], "src/example.py")
        self.assertEqual(finding["line"], 10)

    def test_broken_ruff_falls_back_to_arb000(self) -> None:
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(
            ruff_returncode=2,
            ruff_stdout="not-json",
            ruff_stderr="ruff crashed",
        )
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True)

        self.assertEqual(exit_status, 2)
        payload = self._assert_valid_receipt(path, expected_exit=2)
        self.assertEqual(payload["findings_total"], 1)
        self.assertEqual(payload["findings"][0]["rule"], "ARB000")

    def test_receipt_always_written_even_for_clean_runs(self) -> None:
        """Rule: exit code 0 means 'Command succeeded; receipt created'."""
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="", ruff_stderr="")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True)

        self.assertEqual(exit_status, 0)
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())
