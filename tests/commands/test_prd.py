import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner


class TestPrdCommand(unittest.TestCase):
    """Tests for gz prd command."""

    def test_prd_creates_file(self) -> None:
        """prd creates PRD file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["prd", "TEST-1.0.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/prd/PRD-TEST-1.0.0.md").exists())

    def test_prd_records_event(self) -> None:
        """prd records event in ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["prd", "TEST-1.0.0"])
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn("prd_created", ledger_content)
