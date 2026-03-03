import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner


class TestPlanCommand(unittest.TestCase):
    """Tests for gz plan command."""

    def test_plan_creates_file(self) -> None:
        """plan creates ADR file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["plan", "0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/adr/ADR-0.1.0.md").exists())
