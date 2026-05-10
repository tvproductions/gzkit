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

    def test_step_receipt_file_ends_with_newline(self) -> None:
        """Receipts must end with `\\n` so the ``end-of-file-fixer``
        pre-commit hook does not rewrite them on every commit (the fix
        loop was burning operator tokens during ``gz git-sync``).
        """
        fake = subprocess.CompletedProcess(["uv", "run", "-m", "unittest"], 0, "OK\n", "")
        _, path = self._run_with_fake_result(fake)
        self.assertIsNotNone(path)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(
            text.endswith("\n"),
            msg=f"Receipt must end with newline; last 20 chars: {text[-20:]!r}",
        )

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
                name="echobig",
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


class TestStepNameCanonicalRegex(unittest.TestCase):
    """Writer rejects step names the receipt-binding regex cannot match.

    The canonical run_id pattern in
    ``src/gzkit/governance/trust_audits/attestation_receipts.py:31``
    is ``arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}``. Any step name
    outside ``[a-z][a-z0-9]*`` (hyphens, underscores, uppercase, leading
    digit) produces a receipt the heavy/foundation receipt-binding gate
    rejects as ``malformed_id``. Fail-fast at write time so the
    inconsistency cannot reach attestation. (GHI #441.)
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._receipts_dir = Path(self._tempdir.name) / "receipts"
        self._prior_env = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
        os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(self._receipts_dir)
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

    def test_hyphenated_name_rejected(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        with self.assertRaises(ValueError) as ctx:
            run_step_via_arb(name="advisory-scorecard", cmd=["echo", "x"])
        self.assertIn("[a-z][a-z0-9]*", str(ctx.exception))

    def test_underscore_name_rejected(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        with self.assertRaises(ValueError):
            run_step_via_arb(name="advisory_scorecard", cmd=["echo", "x"])

    def test_uppercase_name_rejected(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        with self.assertRaises(ValueError):
            run_step_via_arb(name="AdvisoryScorecard", cmd=["echo", "x"])

    def test_leading_digit_name_rejected(self) -> None:
        from gzkit.arb.step_reporter import run_step_via_arb

        with self.assertRaises(ValueError):
            run_step_via_arb(name="1leading", cmd=["echo", "x"])

    def test_canonical_name_accepted(self) -> None:
        """Canonical hyphenless lowercase names continue to work."""
        from gzkit.arb.step_reporter import run_step_via_arb

        fake = subprocess.CompletedProcess(["echo", "x"], 0, "ok\n", "")
        with patch("gzkit.arb.step_reporter.subprocess.run", return_value=fake):
            exit_status, path = run_step_via_arb(
                name="advisoryscorecard",
                cmd=["echo", "x"],
                quiet=True,
            )
        self.assertEqual(exit_status, 0)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["step"]["name"], "advisoryscorecard")
        self.assertTrue(payload["run_id"].startswith("arb-step-advisoryscorecard-"))
