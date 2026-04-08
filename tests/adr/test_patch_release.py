"""Tests for gz patch release CLI scaffold (OBPI-0.0.15-01).

Validates that the patch release command scaffold accepts --dry-run and
--json flags, exits cleanly, and is registered in the governance parser.
"""

import json
import unittest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

_quiet_console = Console(file=StringIO())


class TestPatchReleaseCmd(unittest.TestCase):
    """Unit tests for patch_release_cmd function."""

    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_default_mode_exits_zero(self) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        patch_release_cmd(dry_run=False, as_json=False)

    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_dry_run_exits_zero(self) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        patch_release_cmd(dry_run=True, as_json=False)

    @patch("gzkit.commands.patch_release.console", _quiet_console)
    def test_dry_run_prints_placeholder(self) -> None:
        buf = StringIO()
        quiet = Console(file=buf)
        with patch("gzkit.commands.patch_release.console", quiet):
            from gzkit.commands.patch_release import patch_release_cmd

            patch_release_cmd(dry_run=True, as_json=False)
        output = buf.getvalue()
        self.assertIn("patch release", output.lower())

    def test_json_outputs_valid_json(self) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=False, as_json=True)
        raw = mock_print.call_args[0][0]
        payload = json.loads(raw)
        self.assertIsInstance(payload, dict)
        self.assertEqual(payload["status"], "not_implemented")

    def test_json_dry_run_includes_dry_run_key(self) -> None:
        from gzkit.commands.patch_release import patch_release_cmd

        with patch("builtins.print") as mock_print:
            patch_release_cmd(dry_run=True, as_json=True)
        payload = json.loads(mock_print.call_args[0][0])
        self.assertTrue(payload["dry_run"])


class TestPatchReleaseParserRegistration(unittest.TestCase):
    """Verify gz patch release is registered in the governance parser."""

    def test_help_exits_zero(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["patch", "release", "--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_help_contains_flags_and_example(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        buf = StringIO()
        with self.assertRaises(SystemExit):
            import sys

            old_stdout = sys.stdout
            sys.stdout = buf
            try:
                parser.parse_args(["patch", "release", "--help"])
            finally:
                sys.stdout = old_stdout
        output = buf.getvalue()
        self.assertIn("--dry-run", output)
        self.assertIn("--json", output)


if __name__ == "__main__":
    unittest.main()
