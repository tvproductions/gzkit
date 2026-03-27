"""Tests for gzkit.cli.parser and gzkit.cli.helpers.exit_codes."""

import argparse
import io
import sys
import unittest

from gzkit.cli.helpers.exit_codes import (
    EXIT_POLICY_BREACH,
    EXIT_SUCCESS,
    EXIT_SYSTEM_ERROR,
    EXIT_USER_ERROR,
    STANDARD_EXIT_CODES_EPILOG,
)
from gzkit.cli.parser import StableArgumentParser, _NoHyphenBreaksFormatter
from gzkit.traceability import covers


class TestExitCodeConstants(unittest.TestCase):
    """REQ-0.0.4-02-07: Exit code constants match CLI Doctrine 4-code map."""

    @covers("REQ-0.0.4-02-07")
    def test_exit_success_is_zero(self) -> None:
        self.assertEqual(EXIT_SUCCESS, 0)

    @covers("REQ-0.0.4-02-07")
    def test_exit_user_error_is_one(self) -> None:
        self.assertEqual(EXIT_USER_ERROR, 1)

    @covers("REQ-0.0.4-02-07")
    def test_exit_system_error_is_two(self) -> None:
        self.assertEqual(EXIT_SYSTEM_ERROR, 2)

    @covers("REQ-0.0.4-02-07")
    def test_exit_policy_breach_is_three(self) -> None:
        self.assertEqual(EXIT_POLICY_BREACH, 3)

    @covers("REQ-0.0.4-02-06")
    def test_standard_epilog_is_string(self) -> None:
        self.assertIsInstance(STANDARD_EXIT_CODES_EPILOG, str)

    @covers("REQ-0.0.4-02-06")
    def test_standard_epilog_contains_all_codes(self) -> None:
        for code in ("0", "1", "2", "3"):
            with self.subTest(code=code):
                self.assertIn(code, STANDARD_EXIT_CODES_EPILOG)

    @covers("REQ-0.0.4-02-06")
    def test_standard_epilog_contains_labels(self) -> None:
        for label in ("Success", "User/config error", "System/IO error", "Policy breach"):
            with self.subTest(label=label):
                self.assertIn(label, STANDARD_EXIT_CODES_EPILOG)


class TestStableArgumentParserError(unittest.TestCase):
    """REQ-0.0.4-02-02, REQ-0.0.4-02-03: Error format and exit code."""

    @covers("REQ-0.0.4-02-02")
    @covers("REQ-0.0.4-07-02")
    def test_error_writes_blockers_prefix_to_stderr(self) -> None:
        parser = StableArgumentParser(prog="gz")
        captured = io.StringIO()
        old_stderr = sys.stderr
        try:
            sys.stderr = captured
            with self.assertRaises(SystemExit) as ctx:
                parser.error("unrecognized arguments: --bad")
            self.assertEqual(ctx.exception.code, 2)
        finally:
            sys.stderr = old_stderr

        output = captured.getvalue()
        self.assertTrue(output.startswith("BLOCKERS: gz: error:"))
        self.assertIn("unrecognized arguments: --bad", output)

    @covers("REQ-0.0.4-02-03")
    def test_parse_error_exits_with_code_2(self) -> None:
        parser = StableArgumentParser(prog="gz")
        parser.add_argument("--flag", required=True)
        old_stderr = sys.stderr
        try:
            sys.stderr = io.StringIO()
            with self.assertRaises(SystemExit) as ctx:
                parser.parse_args([])
            self.assertEqual(ctx.exception.code, 2)
        finally:
            sys.stderr = old_stderr

    @covers("REQ-0.0.4-02-05")
    def test_parser_uses_no_hyphen_breaks_formatter_by_default(self) -> None:
        parser = StableArgumentParser(prog="gz")
        self.assertIs(parser.formatter_class, _NoHyphenBreaksFormatter)

    def test_parser_allows_formatter_override(self) -> None:
        parser = StableArgumentParser(
            prog="gz",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.assertIs(parser.formatter_class, argparse.RawDescriptionHelpFormatter)


class TestNoHyphenBreaksFormatter(unittest.TestCase):
    """REQ-0.0.4-02-04, REQ-0.0.4-02-05: Hyphen preservation."""

    @covers("REQ-0.0.4-02-04")
    def test_split_lines_preserves_hyphenated_tokens(self) -> None:
        formatter = _NoHyphenBreaksFormatter("test")
        # A line with a hyphenated token at a break point
        text = "This is a description of ADR-0.0.4 and OBPI-0.0.4-01 tokens"
        lines = formatter._split_lines(text, 40)
        # ADR-0.0.4 and OBPI-0.0.4-01 should not be split
        joined = " ".join(lines)
        self.assertIn("ADR-0.0.4", joined)
        self.assertIn("OBPI-0.0.4-01", joined)

    @covers("REQ-0.0.4-02-04")
    def test_fill_text_preserves_hyphenated_tokens(self) -> None:
        formatter = _NoHyphenBreaksFormatter("test")
        text = "Check ADR-0.0.4 and YYYY-MM-DD tokens in this text"
        result = formatter._fill_text(text, 30, "  ")
        self.assertIn("ADR-0.0.4", result)
        self.assertIn("YYYY-MM-DD", result)

    @covers("REQ-0.0.4-02-05")
    def test_split_lines_handles_dedent(self) -> None:
        formatter = _NoHyphenBreaksFormatter("test")
        text = "    indented text with ADR-0.0.4"
        lines = formatter._split_lines(text, 80)
        self.assertTrue(any("ADR-0.0.4" in line for line in lines))


class TestStableArgumentParserIntegration(unittest.TestCase):
    """REQ-0.0.4-02-01, REQ-0.0.4-02-08: Integration checks."""

    @covers("REQ-0.0.4-02-01")
    @covers("REQ-0.0.4-07-03")
    def test_parser_is_used_in_main(self) -> None:
        """Verify StableArgumentParser is the top-level parser in cli/main.py."""
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        self.assertIsInstance(parser, StableArgumentParser)

    @covers("REQ-0.0.4-02-08")
    def test_help_output_preserves_hyphens(self) -> None:
        parser = StableArgumentParser(
            prog="gz",
            description="Manages ADR-0.0.4 and OBPI-0.0.4-01 workflows.",
        )
        parser.add_argument("--adr", help="Target ADR-0.0.4 identifier")
        help_output = io.StringIO()
        parser.print_help(help_output)
        text = help_output.getvalue()
        self.assertIn("ADR-0.0.4", text)


if __name__ == "__main__":
    unittest.main()
