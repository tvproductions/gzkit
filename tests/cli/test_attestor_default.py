"""An omitted `--attestor` takes the project's configured handle (GHI #1036).

`.gzkit.json` § `authorship.attestor_handle` is the single source for the value
`--attestor` records when a caller omits it. Operator ruling on GHI #1036,
verbatim: "All but the 7 human-act (Recommended)" — eleven verbs whose attestor
is an identity take the default; the seven whose own contract declares the
attester's act keep a typed attestor. With no handle configured every verb
behaves exactly as before, and an explicit value always wins.
"""

import argparse
import json
import os
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from gzkit.attestor import ATTESTOR_TOKEN, attestor_hint, configured_attestor_handle
from gzkit.cli.helpers.attestor_default import apply_configured_attestor
from gzkit.cli.main import _get_parser
from gzkit.config import GzkitConfig

_HANDLE = "test-handle"

# The ruling's two classes, by program name. Every parser that takes
# --attestor must sit in exactly one of them.
_DEFAULTING = frozenset(
    {
        "gz obpi complete",
        "gz obpi pipeline",
        "gz obpi emit-receipt",
        "gz adr emit-receipt",
        "gz content retire",
        "gz content unown",
        "gz content own",
        "gz content commit",
        "gz validate",
        "gz obpi brief-drift",
        "gz complexity advise",
    }
)
_HUMAN_ACT = frozenset(
    {
        "gz obpi repudiate",
        "gz obpi withdraw",
        "gz obpi supersede",
        "gz mx enter",
        "gz mx exit",
        "gz ledger correct",
        "gz obpi acceptance",
    }
)


@contextmanager
def _project(handle: str | None) -> Iterator[Path]:
    """A working directory holding a `.gzkit.json` with the given handle."""
    previous = Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        GzkitConfig().save(root / ".gzkit.json")
        if handle is not None:
            data = json.loads((root / ".gzkit.json").read_text(encoding="utf-8"))
            data.setdefault("authorship", {})["attestor_handle"] = handle
            (root / ".gzkit.json").write_text(json.dumps(data), encoding="utf-8")
        os.chdir(root)
        try:
            yield root
        finally:
            os.chdir(previous)


def _resolve(argv: list[str]) -> argparse.Namespace:
    """Parse as `main()` does, then apply the configured default."""
    args = _get_parser().parse_args(argv)
    apply_configured_attestor(args)
    return args


def _attestor_parsers() -> Iterator[tuple[str, argparse.ArgumentParser]]:
    def walk(parser: argparse.ArgumentParser) -> Iterator[argparse.ArgumentParser]:
        yield parser
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for child in action.choices.values():
                    yield from walk(child)

    for parser in walk(_get_parser()):
        if any("--attestor" in action.option_strings for action in parser._actions):
            yield parser.prog, parser


_COMPLETE = ["obpi", "complete", "OBPI-0.1.0-01", "--attestation-text", "ok"]
_UNOWN = ["content", "unown", "AGENTS.md", "--section", "s", "--reason", "r"]


class ConfiguredHandleFillsAnOmittedAttestor(unittest.TestCase):
    """Acceptance (1) and (3): the default fills an omission and never an explicit value."""

    def test_formerly_required_verb_records_the_configured_handle(self) -> None:
        with _project(_HANDLE):
            self.assertEqual(_resolve(_COMPLETE).attestor, _HANDLE)

    def test_optional_verb_records_the_configured_handle(self) -> None:
        with _project(_HANDLE):
            self.assertEqual(_resolve(_UNOWN).attestor, _HANDLE)
            self.assertEqual(_resolve(["obpi", "pipeline", "OBPI-0.1.0-01"]).attestor, _HANDLE)

    def test_a_verb_with_its_own_dest_records_the_configured_handle(self) -> None:
        with _project(_HANDLE):
            self.assertEqual(_resolve(["validate"]).recalibrate_attestor, _HANDLE)

    def test_explicit_attestor_wins(self) -> None:
        with _project(_HANDLE):
            self.assertEqual(_resolve([*_COMPLETE, "--attestor", "other"]).attestor, "other")

    def test_explicit_whitespace_is_kept_for_the_handler_to_refuse(self) -> None:
        with _project(_HANDLE):
            self.assertEqual(_resolve([*_UNOWN, "--attestor", "  "]).attestor, "  ")


class UnconfiguredBehavesAsBefore(unittest.TestCase):
    """Acceptance (2): with no handle, each verb keeps its former required-ness and default."""

    def test_formerly_required_verb_still_refuses_an_omission(self) -> None:
        with _project(None), self.assertRaises(SystemExit) as caught:
            _resolve(_COMPLETE)
        self.assertEqual(caught.exception.code, 2)

    def test_optional_verbs_keep_their_former_defaults(self) -> None:
        with _project(None):
            self.assertEqual(_resolve(_UNOWN).attestor, "")
            self.assertIsNone(_resolve(["obpi", "pipeline", "OBPI-0.1.0-01"]).attestor)
            self.assertEqual(_resolve(["validate"]).recalibrate_attestor, "")


class HumanActVerbsNeverDefault(unittest.TestCase):
    """Acceptance (5): the seven human-act verbs keep a typed attestor even when configured."""

    def test_withdraw_still_requires_a_typed_attestor(self) -> None:
        with _project(_HANDLE), self.assertRaises(SystemExit) as caught:
            _resolve(["obpi", "withdraw", "OBPI-0.1.0-01", "--reason", "r"])
        self.assertEqual(caught.exception.code, 2)

    def test_every_attestor_verb_is_classified_by_the_ruling(self) -> None:
        """A new verb taking --attestor must be classified, not silently left out."""
        found = dict(_attestor_parsers())
        self.assertEqual(set(found), _DEFAULTING | _HUMAN_ACT)
        marked = {
            prog for prog, parser in found.items() if parser.get_default("attestor_default_dest")
        }
        self.assertEqual(marked, _DEFAULTING)


class RemediesShowTheConfiguredHandle(unittest.TestCase):
    """Acceptance (4): a remedy prints the handle when configured and the token when not."""

    def test_hint_is_the_handle_when_configured(self) -> None:
        with _project(_HANDLE) as root:
            self.assertEqual(configured_attestor_handle(root), _HANDLE)
            self.assertEqual(attestor_hint(root), _HANDLE)

    def test_hint_is_the_token_when_unset(self) -> None:
        with _project(None) as root:
            self.assertIsNone(configured_attestor_handle(root))
            self.assertEqual(attestor_hint(root), ATTESTOR_TOKEN)

    def test_hint_is_the_token_outside_a_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(attestor_hint(Path(tmp)), ATTESTOR_TOKEN)


if __name__ == "__main__":
    unittest.main()
