"""Tests for the end-to-end audit pipeline (OBPI-0.19.0-02).

Verifies that ``gz audit ADR-X.Y.Z`` emits a validation receipt,
transitions the ADR to Validated when all checks pass, and preserves
the attestation guard.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.ledger import Ledger, attested_event, gate_checked_event
from gzkit.quality import QualityResult
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _make_qr(success: bool = True, command: str = "test", returncode: int = 0) -> QualityResult:
    return QualityResult(
        success=success,
        command=command,
        stdout="OK" if success else "",
        stderr="" if success else "FAIL",
        returncode=returncode,
    )


def _setup_attested_adr(runner: CliRunner) -> None:
    """Create an ADR that has been attested (ready for audit)."""
    _init_git_repo(Path.cwd())
    _quick_init()
    runner.invoke(main, ["plan", "0.1.0"])
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
    ledger.append(attested_event("ADR-0.1.0", "completed", "Test User"))


class TestAuditAttestationGuard(unittest.TestCase):
    """Audit blocks when ADR is not attested (REQ-01, REQ-09)."""

    def test_audit_blocks_without_attestation(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("attestation", result.output.lower())


class TestAuditArtifacts(unittest.TestCase):
    """Audit creates artifacts and runs commands (REQ-02)."""

    @patch("gzkit.cli.run_command")
    def test_audit_creates_artifacts(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            adr_dir = next(Path("design/adr").rglob("ADR-0.1.0*.md")).parent
            audit_dir = adr_dir / "audit"
            self.assertTrue(audit_dir.exists())
            self.assertTrue((audit_dir / "AUDIT_PLAN.md").exists())
            self.assertTrue((audit_dir / "AUDIT.md").exists())
            self.assertTrue((audit_dir / "proofs").exists())


class TestAuditReceiptEmission(unittest.TestCase):
    """Audit emits a validation receipt to the ledger (REQ-03)."""

    @patch("gzkit.cli.run_command")
    def test_validation_receipt_in_ledger(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("audit_receipt_emitted", ledger_text)
            self.assertIn("validated", ledger_text)


class TestAuditStatusTransition(unittest.TestCase):
    """Audit transitions ADR to Validated when all pass (REQ-04)."""

    @patch("gzkit.cli.run_command")
    def test_adr_transitions_to_validated(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("lifecycle_transition", ledger_text)
            self.assertIn("Validated", ledger_text)


class TestAuditFailureNoTransition(unittest.TestCase):
    """Audit does NOT transition ADR on failure (REQ-05, REQ-08)."""

    @patch("gzkit.cli.run_command")
    def test_no_transition_on_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            # Receipt should still be emitted (with failure recorded)
            self.assertIn("audit_receipt_emitted", ledger_text)
            # But no lifecycle transition
            self.assertNotIn("lifecycle_transition", ledger_text)

    @patch("gzkit.cli.run_command")
    def test_artifacts_still_written_on_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            runner.invoke(main, ["audit", "ADR-0.1.0"])
            adr_dir = next(Path("design/adr").rglob("ADR-0.1.0*.md")).parent
            self.assertTrue((adr_dir / "audit" / "AUDIT.md").exists())


class TestAuditDryRun(unittest.TestCase):
    """--dry-run shows full plan without executing (REQ-06)."""

    def test_dry_run_shows_receipt_and_transition_plan(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Dry run", result.output)
            self.assertIn("receipt", result.output.lower())
            self.assertIn("Validated", result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("audit_receipt_emitted", ledger_text)

    def test_dry_run_json_includes_receipt_and_transition(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("validation_receipt", data)
            self.assertIn("status_transition", data)


class TestAuditJsonOutput(unittest.TestCase):
    """--json emits structured output with all stages (REQ-07)."""

    @patch("gzkit.cli.run_command")
    def test_json_contains_all_fields(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("results", data)
            self.assertIn("validation_receipt", data)
            self.assertIn("status_transition", data)
            self.assertTrue(data["passed"])
