import unittest

from gzkit.cli import main
from tests.commands.common import CliRunner


class TestNewCommandParsers(unittest.TestCase):
    """Parser-level tests for new command surfaces."""

    def test_new_commands_help(self) -> None:
        """All new command surfaces parse and return help."""
        runner = CliRunner()
        commands = [
            ["closeout", "--help"],
            ["audit", "--help"],
            ["adr", "--help"],
            ["adr", "status", "--help"],
            ["adr", "promote", "--help"],
            ["adr", "audit-check", "--help"],
            ["adr", "emit-receipt", "--help"],
            ["obpi", "--help"],
            ["obpi", "emit-receipt", "--help"],
            ["check-config-paths", "--help"],
            ["cli", "--help"],
            ["cli", "audit", "--help"],
            ["parity", "--help"],
            ["parity", "check", "--help"],
            ["readiness", "--help"],
            ["readiness", "audit", "--help"],
            ["skill", "audit", "--help"],
        ]
        for args in commands:
            result = runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, msg=f"help failed for: {args}")
