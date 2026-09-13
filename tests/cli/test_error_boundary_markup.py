"""The CLI error boundary prints a GzkitError's message as text, never as markup.

Error messages routinely carry bracketed text — ``chores[<slug>].title``,
list reprs, option spellings — and the boundary wraps them in a colour tag.
Interpolating the message into markup unescaped let Rich consume every
bracketed span as a tag, so a blocker lost exactly the part naming what
failed.
"""

import argparse
import importlib
import unittest
from unittest.mock import patch

from gzkit.commands.common import GzCliError
from tests.commands.common import CliRunner

# ``gzkit.cli`` re-exports the ``main`` function, which shadows the module name.
cli_main = importlib.import_module("gzkit.cli.main")


def _parser_raising(message: str) -> argparse.ArgumentParser:
    def handler(_args: argparse.Namespace) -> None:
        raise GzCliError(message)

    parser = argparse.ArgumentParser(prog="gz")
    parser.set_defaults(func=handler)
    return parser


class TestErrorBoundaryPreservesBracketedText(unittest.TestCase):
    def test_bracketed_spans_in_an_error_message_reach_the_operator(self) -> None:
        message = "BLOCKERS:\n- chores[demo-chore].title must be a non-empty string."
        runner = CliRunner()
        with (
            runner.isolated_filesystem(),
            patch.object(cli_main, "_get_parser", return_value=_parser_raising(message)),
        ):
            result = runner.invoke(cli_main.main, [])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("chores[demo-chore].title", result.output)


if __name__ == "__main__":
    unittest.main()
