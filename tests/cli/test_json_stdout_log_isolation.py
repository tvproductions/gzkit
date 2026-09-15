"""`--json` stdout carries only JSON; logs go to stderr (GHI #1010).

`.gzkit/rules/cli.md` § Output Contracts: `--json` is *"Valid JSON to stdout;
logs to stderr"*. structlog's unconfigured default logger prints to stdout, so
while the entrypoint never applied `configure_logging`, every structlog event a
`--json` command emitted landed inside the document its consumer parses —
`scripts/session_orientation.py` parses `gz chores status --json`.

The producer exercised here is real: in a project with no `.gzkit/chores/`
overlay, the chores resolver falls back to the package copy and logs
`chore.resolver.fallback` at INFO. Stdout and stderr are captured separately,
because `tests.commands.common.CliRunner` merges them and so cannot see which
stream a line reached.
"""

from __future__ import annotations

import io
import logging
import unittest
from contextlib import redirect_stderr, redirect_stdout

import structlog

from gzkit.cli.main import main
from tests.commands.common import CliRunner, parse_json_document

_FALLBACK_EVENT = "chore.resolver.fallback"


class TestJsonStdoutCarriesOnlyJson(unittest.TestCase):
    """A structlog event emitted during a `--json` command never reaches stdout."""

    def setUp(self) -> None:
        # Start from structlog's unconfigured default: that is the state a fresh
        # `gz` process is in, and the state that wrote logs to stdout.
        structlog.reset_defaults()
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

    def test_chores_status_json_parses_while_the_fallback_log_reaches_stderr(self) -> None:
        code, stdout, stderr = self._run("chores", "status", "--json", "--verbose")

        self.assertEqual(code, 0, msg=stderr)
        payload = parse_json_document(self, stdout)
        self.assertIsInstance(payload.get("chores"), list)
        # The log is relocated, never swallowed: the fallback stays observable.
        self.assertIn(_FALLBACK_EVENT, stderr)

    def test_default_verbosity_keeps_an_info_event_off_both_streams(self) -> None:
        """cli-standards-v3.md § Verbosity Levels: the default logs warnings and errors only."""
        code, stdout, stderr = self._run("chores", "status", "--json")

        self.assertEqual(code, 0, msg=stderr)
        parse_json_document(self, stdout)
        self.assertNotIn(_FALLBACK_EVENT, stderr)

    def test_human_mode_moves_the_log_line_off_stdout(self) -> None:
        code, stdout, stderr = self._run("chores", "status", "--verbose")

        self.assertEqual(code, 0, msg=stderr)
        self.assertNotIn(_FALLBACK_EVENT, stdout)
        self.assertIn(_FALLBACK_EVENT, stderr)

    def test_quiet_keeps_an_info_event_off_both_streams(self) -> None:
        """`--quiet` is "Errors only" (cli.md § Flag Conventions); the fallback is INFO."""
        code, stdout, stderr = self._run("chores", "status", "--json", "--quiet")

        self.assertEqual(code, 0, msg=stderr)
        parse_json_document(self, stdout)
        self.assertNotIn(_FALLBACK_EVENT, stderr)

    def test_debug_outranks_quiet(self) -> None:
        """`--debug` promises DEBUG-level logging (common_flags), so `--quiet` cannot mute it."""
        code, stdout, stderr = self._run("chores", "status", "--json", "--quiet", "--debug")

        self.assertEqual(code, 0, msg=stderr)
        parse_json_document(self, stdout)
        self.assertIn(_FALLBACK_EVENT, stderr)


if __name__ == "__main__":
    unittest.main()
