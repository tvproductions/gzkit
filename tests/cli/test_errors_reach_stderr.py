"""The entrypoint reports a failed command on stderr, never stdout (cli-standards-v3.md).

`docs/design/cli-standards-v3.md` § Output Rules: *"Errors and diagnostics go to
stderr. Always. No exceptions."* Every `gz` verb shares one error boundary in
`gzkit.cli.main.main`, which caught `GzkitError`, any other exception and an
interrupt, and printed each through the shared stdout console. So a failing
`--json` command put human text where its consumer parses a document, and a
human-mode failure could not be separated from the command's output.
"""

from __future__ import annotations

import io
import logging
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import structlog

from gzkit.cli.main import main
from gzkit.commands import task
from tests.commands.common import CliRunner


class TestTheErrorBoundaryWritesToStderr(unittest.TestCase):
    """Each failure branch of `main()` leaves stdout empty and reports on stderr."""

    def setUp(self) -> None:
        root = logging.getLogger()
        self._root_handlers = list(root.handlers)
        self._root_level = root.level

    def tearDown(self) -> None:
        structlog.reset_defaults()
        root = logging.getLogger()
        root.handlers[:] = self._root_handlers
        root.setLevel(self._root_level)

    def _run(self, *argv: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with CliRunner().isolated_filesystem(), redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_a_gzkit_error_under_json(self) -> None:
        # No `.gzkit.json` in the isolated directory: ensure_initialized raises GzCliError.
        code, stdout, stderr = self._run("task", "list", "OBPI-0.1.0-01", "--json")

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("not initialized", stderr)

    def test_a_gzkit_error_in_human_mode(self) -> None:
        code, stdout, stderr = self._run("task", "list", "OBPI-0.1.0-01")

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("not initialized", stderr)

    def test_an_unexpected_exception(self) -> None:
        with patch.object(task, "ensure_initialized", side_effect=RuntimeError("disk vanished")):
            code, stdout, stderr = self._run("task", "list", "OBPI-0.1.0-01", "--json")

        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("disk vanished", stderr)

    def test_an_interrupt(self) -> None:
        with patch.object(task, "ensure_initialized", side_effect=KeyboardInterrupt):
            code, stdout, stderr = self._run("task", "list", "OBPI-0.1.0-01", "--json")

        self.assertEqual(code, 130)
        self.assertEqual(stdout, "")
        self.assertIn("Interrupted", stderr)


if __name__ == "__main__":
    unittest.main()
