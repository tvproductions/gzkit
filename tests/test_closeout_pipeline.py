"""Tests for the end-to-end closeout pipeline (OBPI-0.19.0-01).

Verifies that ``gz closeout ADR-X.Y.Z`` runs quality gates inline,
prompts for human attestation, bumps version, and marks the ADR Completed.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.quality import QualityResult
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _make_qr(success: bool = True, command: str = "test", returncode: int = 0) -> QualityResult:
    """Build a synthetic QualityResult for mocking."""
    return QualityResult(
        success=success,
        command=command,
        stdout="OK" if success else "",
        stderr="" if success else "FAIL",
        returncode=returncode,
    )


class TestCloseoutPipelineGates(unittest.TestCase):
    """Closeout executes verification steps inline via run_command (REQ-01)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_gates_run_inline_and_pass(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(mock_run.called, "run_command must be called for gate execution")
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("gate_checked", ledger_text)
            self.assertIn('"pass"', ledger_text)

    @patch("gzkit.cli.main.run_command")
    def test_gate_failure_halts_pipeline(self, mock_run):
        """Pipeline halts on first gate failure with exit 1 (REQ-02)."""
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("gate_checked", ledger_text)
            self.assertIn('"fail"', ledger_text)

    @patch("gzkit.cli.main.run_command")
    def test_partial_gate_results_recorded_on_failure(self, mock_run):
        """Partial gate results are recorded when a later gate fails (REQ-02)."""
        call_count = 0

        def side_effect(command, cwd=None):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return _make_qr(success=True, command=command)
            return _make_qr(success=False, command=command, returncode=1)

        mock_run.side_effect = side_effect
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            gate_lines = [ln for ln in ledger_text.splitlines() if "gate_checked" in ln]
            self.assertGreaterEqual(len(gate_lines), 2, "Both pass and fail gate events recorded")


class TestCloseoutPipelineAttestation(unittest.TestCase):
    """Closeout prompts for attestation after gates pass (REQ-03)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_attestation_recorded_in_ledger(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("attested", ledger_text)
            self.assertIn("completed", ledger_text)

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_attestation_never_skipped(self, mock_input, mock_run):
        """Attestation prompt must always execute — never skipped (REQ-08)."""
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["closeout", "ADR-0.1.0"])
            mock_input.assert_called_once()


class TestCloseoutPipelineVersionBump(unittest.TestCase):
    """Closeout bumps version when ADR semver exceeds project (REQ-04)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_version_bump_when_needed(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            # Create pyproject.toml with lower version
            Path("pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.0.1"\n', encoding="utf-8"
            )
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            content = Path("pyproject.toml").read_text(encoding="utf-8")
            self.assertIn('version = "0.1.0"', content)


class TestCloseoutPipelineCompletion(unittest.TestCase):
    """Closeout marks ADR Completed after attestation (REQ-05)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_adr_marked_completed(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("lifecycle_transition", ledger_text)
            self.assertIn("Completed", ledger_text)


class TestCloseoutDryRun(unittest.TestCase):
    """--dry-run shows pipeline plan without executing (REQ-06)."""

    def test_dry_run_shows_plan_no_execution(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Dry run", result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("gate_checked", ledger_text)
            self.assertNotIn("attested", ledger_text)

    def test_dry_run_json_includes_version_sync(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            Path("pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.0.1"\n', encoding="utf-8"
            )
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("version_sync", data)
            self.assertTrue(data["version_sync"]["needs_bump"])


class TestCloseoutJsonOutput(unittest.TestCase):
    """--json emits structured JSON with all pipeline results (REQ-07)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_json_output_contains_all_stages(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("gate_results", data)
            self.assertIn("attestation", data)
            self.assertIn("version_sync", data)
            self.assertIn("status_transition", data)

    @patch("gzkit.cli.main.run_command")
    def test_json_output_on_gate_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 1)
            data = json.loads(result.output)
            self.assertIn("gate_results", data)
            self.assertTrue(data["halted"])


class TestCloseoutExitCodes(unittest.TestCase):
    """Exit code 0 = full success, exit code 1 = failure (REQ-10)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_exit_0_on_success(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)

    @patch("gzkit.cli.main.run_command")
    def test_exit_1_on_gate_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
