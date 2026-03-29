import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger
from tests.commands.common import CliRunner, _quick_init


class TestPlanCommand(unittest.TestCase):
    """Tests for gz plan command."""

    def test_plan_creates_file(self) -> None:
        """plan creates ADR file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["plan", "0.1.0"])
            self.assertEqual(result.exit_code, 0)
            adr_path = Path("design/adr/ADR-0.1.0.md")
            self.assertTrue(adr_path.exists())
            content = adr_path.read_text(encoding="utf-8")
            self.assertIn("## Decomposition Scorecard", content)
            self.assertIn("- Final Target OBPI Count: 1", content)
            self.assertEqual(content.count("- [ ] OBPI-0.1.0-"), 1)

    def test_plan_registers_adr_in_ledger(self) -> None:
        """plan creates both the file and the ledger event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["plan", "my-feature", "--semver", "0.2.0"])
            self.assertEqual(result.exit_code, 0)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            graph = ledger.get_artifact_graph()
            self.assertIn("ADR-0.2.0", graph)
            self.assertEqual(graph["ADR-0.2.0"]["type"], "adr")
