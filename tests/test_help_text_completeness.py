"""Recursive parser audit for CLI help text completeness.

Walks the entire ``gz`` parser tree and asserts:
- Every argument has a non-None, non-SUPPRESS ``help=`` string  (REQ-0.0.4-04-01)
- Every parser/subparser has a non-empty ``description=``         (REQ-0.0.4-04-02)
- No help text contains forbidden patterns (TODO, FIXME, XXX, print()  (REQ-0.0.4-04-03)
- All help text lines are under 80 characters                    (REQ-0.0.4-04-04)

@covers REQ-0.0.4-04-01
@covers REQ-0.0.4-04-02
@covers REQ-0.0.4-04-03
@covers REQ-0.0.4-04-04
"""

import argparse
import re
import unittest

# Forbidden patterns in help text
_FORBIDDEN_RE = re.compile(r"\bTODO\b|\bFIXME\b|\bXXX\b|print\(", re.IGNORECASE)


def _walk_parsers(parser, path="gz"):
    """Yield (path, parser) for every parser in the tree."""
    yield path, parser
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, subparser in action.choices.items():
                yield from _walk_parsers(subparser, f"{path} {name}")


def _walk_arguments(parser, path="gz"):
    """Yield (path, action) for every non-meta argument in the tree."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, subparser in action.choices.items():
                yield from _walk_arguments(subparser, f"{path} {name}")
        elif isinstance(action, (argparse._HelpAction, argparse._VersionAction)):
            continue
        else:
            yield path, action


class TestHelpTextCompleteness(unittest.TestCase):
    """Recursive parser audit for CLI help text completeness."""

    @classmethod
    def setUpClass(cls):
        from gzkit.cli.main import _build_parser

        cls.parser = _build_parser()

    # @covers REQ-0.0.4-04-01
    def test_all_arguments_have_help(self):
        """Every add_argument() call must have a non-empty help= string."""
        missing = []
        for path, action in _walk_arguments(self.parser):
            if action.help is None or action.help == argparse.SUPPRESS:
                label = action.option_strings or [action.dest]
                missing.append(f"  {path}: {label} (dest={action.dest})")

        self.assertEqual(
            missing,
            [],
            f"Arguments with missing help= ({len(missing)}):\n" + "\n".join(missing),
        )

    # @covers REQ-0.0.4-04-02
    def test_all_parsers_have_description(self):
        """Every parser and subparser must have a non-empty description= string."""
        missing = []
        for path, parser in _walk_parsers(self.parser):
            if not parser.description:
                missing.append(f"  {path}")

        self.assertEqual(
            missing,
            [],
            f"Parsers with missing description= ({len(missing)}):\n" + "\n".join(missing),
        )

    # @covers REQ-0.0.4-04-03
    def test_no_forbidden_patterns_in_help(self):
        """No help text may contain TODO, FIXME, XXX, or print(."""
        violations = []
        for path, action in _walk_arguments(self.parser):
            if action.help and _FORBIDDEN_RE.search(action.help):
                label = action.option_strings or [action.dest]
                violations.append(f"  {path}: {label} help={action.help!r}")

        for path, parser in _walk_parsers(self.parser):
            if parser.description and _FORBIDDEN_RE.search(parser.description):
                violations.append(f"  {path}: description={parser.description!r}")

        self.assertEqual(
            violations,
            [],
            f"Forbidden patterns in help text ({len(violations)}):\n" + "\n".join(violations),
        )

    # @covers REQ-0.0.4-04-04
    def test_help_text_under_80_chars(self):
        """All help text must be 80 characters or fewer."""
        violations = []
        for path, action in _walk_arguments(self.parser):
            if action.help and len(action.help) > 80:
                label = action.option_strings or [action.dest]
                violations.append(f"  {path}: {label} ({len(action.help)} chars): {action.help!r}")

        self.assertEqual(
            violations,
            [],
            f"Help text over 80 chars ({len(violations)}):\n" + "\n".join(violations),
        )

    def test_formatter_class_set(self):
        """All parsers must use NoHyphenBreaks+RawDescription formatter."""
        from gzkit.cli.parser import _NoHyphenBreaksFormatter

        violations = []
        for path, parser in _walk_parsers(self.parser):
            if parser.formatter_class is not _NoHyphenBreaksFormatter:
                violations.append(f"  {path}: {parser.formatter_class.__name__}")

        self.assertEqual(
            violations,
            [],
            f"Parsers with wrong formatter_class ({len(violations)}):\n" + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
