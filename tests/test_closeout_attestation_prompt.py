"""Semantics of the interactive closeout attestation prompt (GHI #1211).

The prompt offers three choices: Completed, Completed - Partial (requires reason)
and Dropped (requires reason). A choice that requires a reason returns the reason
when one is given and refuses with ``GzCliError`` when it is empty. GHI #1211:
the Partial branch raised unconditionally, so it refused with a reason given and
crashed with ``UnboundLocalError`` instead of returning ``("partial", reason)``.
"""

import unittest
from unittest import mock

from gzkit.commands.closeout import _prompt_closeout_attestation
from gzkit.commands.common import GzCliError


def _answer(*replies: str, quiet: bool) -> tuple[str, str | None]:
    """Run the prompt with ``replies`` fed to ``input`` in order."""
    with mock.patch("builtins.input", side_effect=list(replies)), mock.patch("builtins.print"):
        return _prompt_closeout_attestation(quiet=quiet)


class TestCloseoutAttestationPrompt(unittest.TestCase):
    def test_partial_with_reason_returns_partial_and_the_reason(self) -> None:
        for quiet in (True, False):
            with self.subTest(quiet=quiet):
                self.assertEqual(
                    _answer("2", "docs deferred", quiet=quiet), ("partial", "docs deferred")
                )

    def test_reason_required_choices_refuse_an_empty_reason(self) -> None:
        for selection, word in (("2", "partial"), ("3", "dropped")):
            for quiet in (True, False):
                with self.subTest(selection=selection, quiet=quiet):
                    with self.assertRaises(GzCliError) as caught:
                        _answer(selection, "   ", quiet=quiet)
                    self.assertIn(f"Reason required for {word} attestation", str(caught.exception))

    def test_dropped_with_reason_returns_dropped_and_the_reason(self) -> None:
        self.assertEqual(_answer("3", "scope pulled", quiet=True), ("dropped", "scope pulled"))

    def test_completed_needs_no_reason(self) -> None:
        self.assertEqual(_answer("1", quiet=True), ("completed", None))

    def test_an_unknown_selection_is_refused(self) -> None:
        with self.assertRaises(GzCliError):
            _answer("4", quiet=True)


if __name__ == "__main__":
    unittest.main()
