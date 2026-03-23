import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestSpecifyCommand(unittest.TestCase):
    """Tests for gz specify command."""

    def test_specify_creates_obpi_file(self) -> None:
        """specify creates OBPI file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            obpi_path = Path("design/adr/obpis/OBPI-0.1.0-01-core-feature.md")
            self.assertTrue(obpi_path.exists())
            content = obpi_path.read_text(encoding="utf-8")
            self.assertIn('Checklist Item:** #1 - "OBPI-0.1.0-01:', content)
            self.assertNotIn('Checklist Item:** #1 - "TBD"', content)

    def test_specify_rejects_pool_parent(self) -> None:
        """specify blocks pool ADR parents until promotion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["specify", "core-feature", "--parent", "ADR-pool.sample", "--item", "1"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot receive OBPIs until promoted", result.output)

    def test_specify_rejects_out_of_range_item(self) -> None:
        """specify rejects checklist item numbers outside scorecard-backed checklist range."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0", "--item", "2"]
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("out of range", result.output)

    def test_specify_warns_about_template_defaults(self) -> None:
        """#31: specify warns that the brief needs authoring after creation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("template defaults", result.output)
            self.assertIn("needs authoring", result.output)
