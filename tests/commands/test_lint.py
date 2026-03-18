import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestLintCommand(unittest.TestCase):
    """Tests for gz lint command."""

    def test_lint_runs(self) -> None:
        """lint command runs (may fail without src/tests)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # Create minimal structure
            Path("src").mkdir()
            Path("tests").mkdir()
            result = runner.invoke(main, ["lint"])
            # Command runs regardless of result
            self.assertIn("lint", result.output.lower())
