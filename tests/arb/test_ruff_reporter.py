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

from gzkit.arb.ruff_reporter import run_ruff_via_arb


def _fake_run_factory(ruff_returncode: int, ruff_stdout: str = "", ruff_stderr: str = ""):
    """Route ruff check calls to fake output; leave version + git calls stubbed."""

    def fake_run(cmd, **kwargs):
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
        # A root with no data/ruff_baseline.json, so every finding counts, as plain Ruff.
        self._root = Path(self._tempdir.name)
        self._prior_env = os.environ.get("GZKIT_ARB_RECEIPTS_ROOT")
        os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = str(self._receipts_dir)

    def tearDown(self) -> None:
        if self._prior_env is None:
            os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
        else:
            os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = self._prior_env
        self._tempdir.cleanup()

    def _assert_valid_receipt(self, path: Path, expected_exit: int) -> dict:
        """Validate the receipt through the ARB validator that reads receipts in production."""
        from gzkit.arb.validator import validate_receipts

        result = validate_receipts(root=path.parent, limit=-1)
        self.assertEqual(result.errors, [], msg=f"Receipt invalid: {result.errors}")
        self.assertEqual((result.scanned, result.valid), (1, 1))
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "gzkit.arb.lint_receipt.v1")
        self.assertEqual(payload["exit_status"], expected_exit)
        return payload

    def test_green_run_writes_receipt_with_empty_findings(self) -> None:
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="[]", ruff_stderr="")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)

        self.assertEqual(exit_status, 0)
        self.assertIsNotNone(path)
        payload = self._assert_valid_receipt(path, expected_exit=0)
        self.assertEqual(payload["findings"], [])
        self.assertEqual(payload["findings_total"], 0)

    def test_ruff_receipt_file_ends_with_newline(self) -> None:
        """Receipts must end with `\\n` so the ``end-of-file-fixer``
        pre-commit hook does not rewrite them on every commit.
        """
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="[]", ruff_stderr="")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            _, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)
        self.assertIsNotNone(path)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(
            text.endswith("\n"),
            msg=f"Receipt must end with newline; last 20 chars: {text[-20:]!r}",
        )

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
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)

        self.assertEqual(exit_status, 1)
        payload = self._assert_valid_receipt(path, expected_exit=1)
        self.assertEqual(payload["findings_total"], 1)
        finding = payload["findings"][0]
        self.assertEqual(finding["rule"], "E501")
        self.assertEqual(finding["path"], "src/example.py")
        self.assertEqual(finding["line"], 10)

    def test_a_finding_the_baseline_holds_is_not_recorded_and_the_run_passes(self) -> None:
        """Ruff selects ALL under data/ruff_baseline.json (RO-9 tranche 4)."""
        (self._root / "data").mkdir()
        rows = [{"file": "src/example.py", "rule": "E501", "count": 1}]
        (self._root / "data" / "ruff_baseline.json").write_text(
            json.dumps({"rows": rows}), encoding="utf-8"
        )
        item = {
            "code": "E501",
            "filename": str(self._root / "src" / "example.py"),
            "location": {"row": 10, "column": 81},
            "message": "line too long",
        }
        fake = _fake_run_factory(ruff_returncode=1, ruff_stdout=json.dumps([item]))
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            held_status, held_path = run_ruff_via_arb(
                paths=["src"], quiet=True, project_root=self._root
            )
        self.assertEqual(held_status, 0)
        self.assertEqual(self._assert_valid_receipt(held_path, expected_exit=0)["findings"], [])

        # Control: one more of the same finding than the row holds fails, naming it.
        fake = _fake_run_factory(ruff_returncode=1, ruff_stdout=json.dumps([item, item]))
        held_path.unlink()
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)
        self.assertEqual(status, 1)
        payload = self._assert_valid_receipt(path, expected_exit=1)
        self.assertEqual([f["path"] for f in payload["findings"]], ["src/example.py"] * 2)

    def test_a_row_its_findings_no_longer_fill_is_recorded_naming_the_ratchet(self) -> None:
        (self._root / "data").mkdir()
        rows = [{"file": "src/example.py", "rule": "E501", "count": 2}]
        (self._root / "data" / "ruff_baseline.json").write_text(
            json.dumps({"rows": rows}), encoding="utf-8"
        )
        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="[]")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)
        self.assertEqual(status, 1)
        [finding] = self._assert_valid_receipt(path, expected_exit=1)["findings"]
        self.assertEqual((finding["rule"], finding["path"]), ("E501", "src/example.py"))
        self.assertIn("gz lint --ratchet", finding["message"])

    def test_a_partial_run_leaves_the_rows_of_files_it_did_not_read(self) -> None:
        (self._root / "data").mkdir()
        rows = [{"file": "scripts/other.py", "rule": "E501", "count": 1}]
        (self._root / "data" / "ruff_baseline.json").write_text(
            json.dumps({"rows": rows}), encoding="utf-8"
        )
        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="[]")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            status, _ = run_ruff_via_arb(paths=["src/"], quiet=True, project_root=self._root)
        self.assertEqual(status, 0)

    def test_a_malformed_baseline_is_an_arb_error_not_a_verdict(self) -> None:
        (self._root / "data").mkdir()
        (self._root / "data" / "ruff_baseline.json").write_text("{}", encoding="utf-8")
        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="[]")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)
        self.assertEqual(status, 2)
        [finding] = json.loads(path.read_text(encoding="utf-8"))["findings"]
        self.assertEqual(finding["rule"], "ARB000")
        self.assertIn("malformed", finding["message"])

    def test_ruff_that_could_not_start_is_not_read_as_a_clean_run(self) -> None:
        fake = _fake_run_factory(ruff_returncode=127, ruff_stdout="", ruff_stderr="no uv")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)
        self.assertEqual(status, 127)
        self.assertEqual(
            json.loads(path.read_text(encoding="utf-8"))["findings"][0]["rule"], "ARB000"
        )

    def test_broken_ruff_falls_back_to_arb000(self) -> None:
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(
            ruff_returncode=2,
            ruff_stdout="not-json",
            ruff_stderr="ruff crashed",
        )
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)

        self.assertEqual(exit_status, 2)
        payload = self._assert_valid_receipt(path, expected_exit=2)
        self.assertEqual(payload["findings_total"], 1)
        self.assertEqual(payload["findings"][0]["rule"], "ARB000")

    def test_receipt_always_written_even_for_clean_runs(self) -> None:
        """Rule: exit code 0 means 'Command succeeded; receipt created'."""
        from gzkit.arb.ruff_reporter import run_ruff_via_arb

        fake = _fake_run_factory(ruff_returncode=0, ruff_stdout="", ruff_stderr="")
        with patch("gzkit.arb.ruff_reporter._run_command", side_effect=fake):
            exit_status, path = run_ruff_via_arb(paths=["src"], quiet=True, project_root=self._root)

        self.assertEqual(exit_status, 0)
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())
