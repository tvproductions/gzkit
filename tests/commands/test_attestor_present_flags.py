"""The ``--attestor-present`` flags after the TTY authenticity gate's removal (GHI #1308).

The flag on ``gz adr emit-receipt`` and ``gz obpi emit-receipt`` fed only the removed
gate, so it is accepted and inert (operator ruling on GHI #1308's scope, verbatim
"Keep the flags (Recommended)"; removal tracked in GHI #1310). The flag on
``gz obpi complete`` still opens the ``--accept-uncovered`` agent-relayed path. An
operator reads which is which from ``--help``, so the help text is the contract here.
"""

import unittest

from gzkit.cli.main import _build_parser
from tests.commands.common import subcommand_parser


def _flag_help(*path: str) -> str:
    """Return the ``--attestor-present`` help string registered on the parser at ``path``."""
    parser = subcommand_parser(_build_parser(), *path)
    action = next(a for a in parser._actions if "--attestor-present" in a.option_strings)
    return action.help or ""


class TestAttestorPresentFlagOutputContract(unittest.TestCase):
    """The help text says which ``--attestor-present`` flags still do something."""

    # output-contract: an operator reads the flag's effect from --help (GHI #1308).
    def test_emit_receipt_flags_parse_and_read_as_inert(self) -> None:
        argv_by_verb = {
            ("adr", "emit-receipt"): ["adr", "emit-receipt", "ADR-0.1.0"],
            ("obpi", "emit-receipt"): ["obpi", "emit-receipt", "OBPI-0.1.0-01"],
        }
        for path, argv in argv_by_verb.items():
            with self.subTest(verb=" ".join(path)):
                args = _build_parser().parse_args(
                    [*argv, "--event", "validated", "--attestor", "g0", "--attestor-present"]
                )
                self.assertTrue(args.attestor_present)
                help_text = _flag_help(*path)
                self.assertIn("inert", help_text)
                self.assertIn("GHI #1308", help_text)

    # output-contract: the live flag keeps describing the gate it opens.
    def test_obpi_complete_flag_still_describes_the_marker_gate(self) -> None:
        help_text = _flag_help("obpi", "complete")
        self.assertIn("pipeline marker", help_text)
        self.assertNotIn("inert", help_text)


if __name__ == "__main__":
    unittest.main()
