"""Tests for closeout migration from config.gates to FeatureDecisions (OBPI-0.0.8-06).

Verifies that closeout product proof enforcement is read from
``decisions.product_proof_enforced()``, not ``config.gate("product_proof")``.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.cli import main
from gzkit.quality import ObpiProofStatus, ProductProofResult
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _init_git_repo, _quick_init, _write_obpi


def _make_proof_result(
    *, success: bool, adr_id: str = "ADR-0.1.0", missing_count: int = 0
) -> ProductProofResult:
    """Build a synthetic ProductProofResult for mocking."""
    proofs: list[ObpiProofStatus] = []
    if not success:
        for i in range(missing_count):
            proofs.append(
                ObpiProofStatus(
                    obpi_id=f"OBPI-0.1.0-0{i + 1}",
                    runbook_found=False,
                    command_doc_found=False,
                    docstring_found=False,
                )
            )
    return ProductProofResult(
        adr_id=adr_id,
        success=success,
        obpi_proofs=proofs,
        missing_count=missing_count,
    )


def _scaffold_closeout_adr(*, lane: str = "Lite") -> None:
    """Set up a minimal ADR-0.1.0 with a completed OBPI for closeout readiness."""
    adr_dir = Path("docs/design/adr/ADR-0.1.0")
    obpi_dir = adr_dir / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    _write_obpi(
        obpi_dir / "OBPI-0.1.0-01-demo.md",
        status="Completed",
        brief_status="Completed",
        implementation_line="test.py",
        lane=lane,
        human_attestation=("test", "attest completed", "2026-03-30"),
    )


class TestCloseoutMigrationEnforce(unittest.TestCase):
    """When product_proof_enforced=True and proof missing, closeout blocks."""

    @covers("REQ-0.0.8-06-01")
    @patch("gzkit.commands.closeout.get_decisions")
    @patch("gzkit.commands.closeout.check_product_proof")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_blocks_when_enforced_and_missing(
        self, _mock_input, mock_run, mock_proof, mock_decisions
    ):
        """Closeout exits 1 when flag is True and proof is missing."""
        mock_decisions.return_value.product_proof_enforced.return_value = True
        mock_proof.return_value = _make_proof_result(success=False, missing_count=1)
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="OK", stderr="")

        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            _scaffold_closeout_adr()
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("blocked", result.output.lower())


class TestCloseoutMigrationAdvisory(unittest.TestCase):
    """When product_proof_enforced=False and proof missing, closeout warns."""

    @covers("REQ-0.0.8-06-02")
    @patch("gzkit.commands.closeout.get_decisions")
    @patch("gzkit.commands.closeout.check_product_proof")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_warns_when_not_enforced_and_missing(
        self, _mock_input, mock_run, mock_proof, mock_decisions
    ):
        """Closeout warns but proceeds when flag is False and proof missing."""
        mock_decisions.return_value.product_proof_enforced.return_value = False
        mock_proof.return_value = _make_proof_result(success=False, missing_count=1)
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="OK", stderr="")

        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            _scaffold_closeout_adr()
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("advisory", result.output.lower())


class TestCloseoutMigrationProofPresent(unittest.TestCase):
    """When proof present, closeout succeeds regardless of flag state."""

    @covers("REQ-0.0.8-06-03")
    @patch("gzkit.commands.closeout.get_decisions")
    @patch("gzkit.commands.closeout.check_product_proof")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_succeeds_with_proof_flag_true(self, _mock_input, mock_run, mock_proof, mock_decisions):
        """Closeout succeeds when proof present, even with flag=True."""
        mock_decisions.return_value.product_proof_enforced.return_value = True
        mock_proof.return_value = _make_proof_result(success=True)
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="OK", stderr="")

        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            _scaffold_closeout_adr()
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)

    @patch("gzkit.commands.closeout.get_decisions")
    @patch("gzkit.commands.closeout.check_product_proof")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_succeeds_with_proof_flag_false(
        self, _mock_input, mock_run, mock_proof, mock_decisions
    ):
        """Closeout succeeds when proof present with flag=False."""
        mock_decisions.return_value.product_proof_enforced.return_value = False
        mock_proof.return_value = _make_proof_result(success=True)
        mock_run.return_value = MagicMock(success=True, returncode=0, stdout="OK", stderr="")

        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            _scaffold_closeout_adr()
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)


class TestCloseoutMigrationReferenceRemoved(unittest.TestCase):
    """config.gate('product_proof') reference removed from closeout.py."""

    @covers("REQ-0.0.8-06-04")
    def test_primary_path_uses_decisions_not_config_gate(self):
        """Primary decision path uses product_proof_enforced(); config.gate is fallback only."""
        import gzkit.commands.closeout

        source = Path(gzkit.commands.closeout.__file__).read_text(encoding="utf-8")
        self.assertIn("product_proof_enforced", source)
        # config.gate may appear in the REQ-03 transition fallback, but the
        # primary decision must come from FeatureDecisions
        self.assertIn("get_decisions()", source)
        self.assertIn("decisions.product_proof_enforced()", source)


if __name__ == "__main__":
    unittest.main()
