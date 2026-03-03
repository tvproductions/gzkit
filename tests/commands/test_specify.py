import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner


class TestSpecifyCommand(unittest.TestCase):
    """Tests for gz specify command."""

    def test_specify_creates_obpi_file(self) -> None:
        """specify creates OBPI file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/adr/obpis/OBPI-0.1.0-01-core-feature.md").exists())

    def test_specify_rejects_pool_parent(self) -> None:
        """specify blocks pool ADR parents until promotion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(
                main,
                ["specify", "core-feature", "--parent", "ADR-pool.sample", "--item", "1"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot receive OBPIs until promoted", result.output)
