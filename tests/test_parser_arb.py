"""Parser registration tests for gz arb.

@covers REQ-0.25.0-33-03
"""

import argparse
import unittest

from gzkit.cli.main import _build_parser


class TestArbParserRegistration(unittest.TestCase):
    """gz arb is registered with all seven sub-verbs."""

    def setUp(self) -> None:
        self.parser = _build_parser()

    def _subparser_choices(
        self,
        parser: argparse.ArgumentParser,
    ) -> dict[str, argparse.ArgumentParser]:
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return action.choices
        self.fail("parser has no subparsers")
        return {}

    def test_arb_is_registered_on_top_level(self) -> None:
        commands = self._subparser_choices(self.parser)
        self.assertIn("arb", commands)

    def test_arb_exposes_all_seven_verbs(self) -> None:
        commands = self._subparser_choices(self.parser)
        arb_commands = self._subparser_choices(commands["arb"])
        expected = {"ruff", "step", "ty", "coverage", "validate", "advise", "patterns"}
        self.assertEqual(set(arb_commands.keys()), expected)

    def test_each_verb_has_help(self) -> None:
        commands = self._subparser_choices(self.parser)
        arb_commands = self._subparser_choices(commands["arb"])
        for name, sub in arb_commands.items():
            self.assertTrue(sub.description, msg=f"{name} has no description")

    def test_each_verb_has_examples_epilog(self) -> None:
        commands = self._subparser_choices(self.parser)
        arb_commands = self._subparser_choices(commands["arb"])
        for name, sub in arb_commands.items():
            self.assertTrue(
                sub.epilog and "Examples" in sub.epilog,
                msg=f"{name} is missing an Examples epilog",
            )
