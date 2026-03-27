"""Tests for the epilog builder and epilog presence on all CLI commands.

Covers OBPI-0.0.4-05 requirements:
  REQ-0.0.4-05-01: build_epilog() helper exists with correct signature
  REQ-0.0.4-05-02: All top-level commands have non-empty .epilog values
  REQ-0.0.4-05-03: All subcommands have non-empty .epilog values
  REQ-0.0.4-05-04: Every epilog contains "Examples" and "Exit codes" sections
  REQ-0.0.4-05-05: All example commands in epilogs are syntactically valid gz invocations
  REQ-0.0.4-05-06: uv run gz lint passes (verified externally)
  REQ-0.0.4-05-07: uv run gz test passes (this test suite)
"""

import argparse
import inspect
import unittest

from gzkit.cli.helpers.epilog import build_epilog
from gzkit.cli.main import _build_parser
from gzkit.traceability import covers


class TestBuildEpilog(unittest.TestCase):
    """REQ-0.0.4-05-01: build_epilog() helper tests."""

    @covers("REQ-0.0.4-05-01")
    def test_signature_matches_spec(self):
        """build_epilog has the expected signature."""
        sig = inspect.signature(build_epilog)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ["examples", "exit_codes"])
        # examples is list[str], exit_codes is keyword-only with default None
        self.assertEqual(sig.parameters["exit_codes"].default, None)
        self.assertEqual(sig.parameters["exit_codes"].kind, inspect.Parameter.KEYWORD_ONLY)

    @covers("REQ-0.0.4-05-01")
    def test_basic_output(self):
        """build_epilog produces Examples and Exit codes sections."""
        result = build_epilog(["gz status --table"])
        self.assertIn("Examples", result)
        self.assertIn("gz status --table", result)
        self.assertIn("Exit codes", result)

    def test_uses_standard_exit_codes_by_default(self):
        """Default exit codes match STANDARD_EXIT_CODES_EPILOG."""
        result = build_epilog(["gz lint"])
        # The standard epilog content should appear
        self.assertIn("0   Success", result)
        self.assertIn("3   Policy breach", result)

    def test_custom_exit_codes(self):
        """Custom exit codes override the default."""
        custom = "Exit codes\n    0   All good\n    1   Not good\n"
        result = build_epilog(["gz test"], exit_codes=custom)
        self.assertIn("All good", result)
        self.assertNotIn("Policy breach", result)

    def test_multiple_examples(self):
        """Multiple examples are all included."""
        result = build_epilog(["gz status --table", "gz status --json"])
        self.assertIn("gz status --table", result)
        self.assertIn("gz status --json", result)

    def test_empty_examples_raises(self):
        """Empty examples list raises ValueError."""
        with self.assertRaises(ValueError):
            build_epilog([])

    def test_examples_indented(self):
        """Each example line is indented with 4 spaces."""
        result = build_epilog(["gz lint"])
        for line in result.splitlines():
            if line.startswith("gz "):
                self.fail(f"Example not indented: {line!r}")
        self.assertIn("    gz lint", result)


def _collect_parsers(parser, prefix=""):
    """Recursively collect (name, parser) from an argparse tree."""
    results = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, subparser in action.choices.items():
                full_name = f"{prefix} {name}".strip() if prefix else name
                results.append((full_name, subparser))
                results.extend(_collect_parsers(subparser, full_name))
    return results


class TestEpilogPresence(unittest.TestCase):
    """REQ-0.0.4-05-02/03/04: Every command and subcommand has an epilog."""

    @classmethod
    def setUpClass(cls):
        cls.parser = _build_parser()
        cls.all_parsers = _collect_parsers(cls.parser)
        # Separate into top-level and subcommands
        cls.top_level = [(n, p) for n, p in cls.all_parsers if " " not in n]
        cls.subcommands = [(n, p) for n, p in cls.all_parsers if " " in n]

    @covers("REQ-0.0.4-05-02")
    def test_top_level_commands_have_epilog(self):
        """REQ-0.0.4-05-02: All top-level commands have non-empty epilog."""
        missing = []
        for name, parser in self.top_level:
            if not parser.epilog:
                missing.append(name)
        self.assertEqual(missing, [], f"Top-level commands missing epilog: {missing}")

    @covers("REQ-0.0.4-05-03")
    def test_subcommands_have_epilog(self):
        """REQ-0.0.4-05-03: All subcommands have non-empty epilog."""
        missing = []
        for name, parser in self.subcommands:
            if not parser.epilog:
                missing.append(name)
        self.assertEqual(missing, [], f"Subcommands missing epilog: {missing}")

    @covers("REQ-0.0.4-05-04")
    def test_epilogs_contain_examples_section(self):
        """REQ-0.0.4-05-04: Every epilog has an Examples section."""
        missing = []
        for name, parser in self.all_parsers:
            if parser.epilog and "Examples" not in parser.epilog:
                missing.append(name)
        self.assertEqual(missing, [], f"Epilogs missing Examples section: {missing}")

    @covers("REQ-0.0.4-05-04")
    def test_epilogs_contain_exit_codes_section(self):
        """REQ-0.0.4-05-04: Every epilog has an Exit codes section."""
        missing = []
        for name, parser in self.all_parsers:
            if parser.epilog and "Exit codes" not in parser.epilog:
                missing.append(name)
        self.assertEqual(missing, [], f"Epilogs missing Exit codes section: {missing}")


class TestEpilogExamples(unittest.TestCase):
    """REQ-0.0.4-05-05: All example commands are valid gz invocations."""

    @classmethod
    def setUpClass(cls):
        parser = _build_parser()
        cls.all_parsers = _collect_parsers(parser)

    @covers("REQ-0.0.4-05-05")
    def test_examples_start_with_gz(self):
        """All indented example lines in epilogs start with 'gz '."""
        bad = []
        for name, parser in self.all_parsers:
            if not parser.epilog:
                continue
            in_examples = False
            for line in parser.epilog.splitlines():
                stripped = line.strip()
                if stripped == "Examples":
                    in_examples = True
                    continue
                if stripped.startswith("Exit codes"):
                    in_examples = False
                    continue
                if (
                    in_examples
                    and stripped
                    and not stripped.startswith("#")
                    and not stripped.startswith("gz ")
                ):
                    bad.append((name, stripped))
        self.assertEqual(bad, [], f"Non-gz example commands found: {bad}")


if __name__ == "__main__":
    unittest.main()
