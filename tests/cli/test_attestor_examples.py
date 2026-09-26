"""Attestor examples show the value the PII rule requires, never a person (GHI #1101).

`AGENTS.md` § Execution Rules: "Record operator authorship as `g0` — never the
operator's real name — in every attestor/author identity field ... Overrides any
contrary skill/template/example." An agent filling `--attestor` from an example
copies whatever the example shows. Five verbs' `--help` showed
`--attestor "Jane Doe"`, and #899 and #1031 had each cleared a different cut of
the same rule, so this guard reads every parser in the `gz` tree. Manpages are
doc content, outside the unit tier (`.gzkit/rules/tests.md`); GHI #1101's
acceptance grep covered them.

An example value is accepted when it is `g0` (the settled worked-example form,
#1031), `agent:<name>` (the one prefix the runtime reads,
`receipt_shape.py`), or a placeholder token such as `<name>`, `{attestor}` or
`NAME`.
"""

import argparse
import re
import unittest
from collections.abc import Iterator

from gzkit.cli.main import _get_parser

# A line is an example when it is a `gz` command or a `--flag` continuation of
# one; prose that merely mentions the flag ("`--attestor` and ...") is not.
_EXAMPLE_LINE = re.compile(r"^\s*(?:\$\s+)?(?:uv run\s+)?(?:gz\s|--[a-z])")
_ATTESTOR_VALUE = re.compile(r"--attestor[= ](\"[^\"]*\"|'[^']*'|[^\s`\\)]+)")
# Empty: a refusal demo (`--attestor ""` is refused), which names no one.
_ACCEPTED = re.compile(r"^(|g0|agent:\S+|<[^>]+>|\{[^}]+\}|[A-Z_]+|…|\.\.\.)$")


def _parsers(parser: argparse.ArgumentParser) -> Iterator[tuple[str, argparse.ArgumentParser]]:
    """Yield every parser in the tree with its program name."""
    yield parser.prog, parser
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for child in action.choices.values():
                yield from _parsers(child)


def _help_texts() -> Iterator[tuple[str, str]]:
    """Every epilog, description and option help string the CLI prints."""
    for prog, parser in _parsers(_get_parser()):
        for text in (parser.epilog, parser.description):
            if text:
                yield prog, text
        for action in parser._actions:
            if action.help:
                yield prog, str(action.help)


def _person_shaped(text: str) -> list[str]:
    """Attestor example values that are neither g0, agent:, nor a placeholder."""
    values = (
        match.strip("\"'").rstrip("],.;:")
        for line in text.splitlines()
        if _EXAMPLE_LINE.match(line)
        for match in _ATTESTOR_VALUE.findall(line)
    )
    return [value for value in values if not _ACCEPTED.match(value)]


class AttestorExamplesNameNoPerson(unittest.TestCase):
    """No live example puts a person's name in an attestor field."""

    def test_the_value_filter_rejects_names_and_accepts_the_settled_forms(self) -> None:
        """Control: the filter tells a person from g0, agent:<name> and a token."""
        self.assertEqual(
            _person_shaped(
                'gz x --attestor "Jane Doe"\n'
                "  --attestor human:jeff\n"
                "$ uv run gz y --attestor alice"
            ),
            ["Jane Doe", "human:jeff", "alice"],
        )
        self.assertEqual(
            _person_shaped(
                'gz x --attestor g0 --attestor "agent:codex"\n  --attestor "<attestor-handle>"'
            ),
            [],
        )
        self.assertEqual(_person_shaped("Pass `--attestor` and a reason [--attestor NAME]."), [])

    def test_cli_help_shows_no_person_as_attestor(self) -> None:
        offenders = [
            (prog, value) for prog, text in _help_texts() for value in _person_shaped(text)
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
