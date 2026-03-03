import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import (
    Ledger,
    gate_checked_event,
)
from tests.commands.common import CliRunner


class TestDryRunCommands(unittest.TestCase):
    """Tests for dry-run behavior."""

    def test_init_dry_run_creates_nothing(self) -> None:
        """init --dry-run does not create files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path(".gzkit").exists())

    def test_prd_dry_run_does_not_write(self) -> None:
        """prd --dry-run does not create PRD or ledger event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["prd", "TEST-1.0.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path("design/prd/PRD-TEST-1.0.0.md").exists())
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("prd_created", ledger_content)

    def test_attest_dry_run_does_not_write(self) -> None:
        """attest --dry-run does not record attestation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            result = runner.invoke(
                main, ["attest", "ADR-0.1.0", "--status", "completed", "--dry-run"]
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("attested", ledger_content)
