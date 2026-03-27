"""Unit tests for gzkit.cli.helpers.common_flags."""

import argparse
import contextlib
import io
import unittest

from gzkit.cli.helpers.common_flags import add_common_flags
from gzkit.traceability import covers


def _quiet_stderr() -> contextlib.redirect_stderr[io.StringIO]:
    """Redirect stderr to suppress argparse error messages during tests."""
    return contextlib.redirect_stderr(io.StringIO())


class TestAddCommonFlagsRegistration(unittest.TestCase):
    """Verify that add_common_flags registers the expected flags."""

    def _fresh(self) -> argparse.ArgumentParser:
        return argparse.ArgumentParser(prog="test")

    @covers("REQ-0.0.4-03-01")
    def test_registers_quiet(self) -> None:
        parser = self._fresh()
        add_common_flags(parser)
        ns = parser.parse_args(["--quiet"])
        self.assertTrue(ns.quiet)

    @covers("REQ-0.0.4-03-01")
    def test_registers_verbose(self) -> None:
        parser = self._fresh()
        add_common_flags(parser)
        ns = parser.parse_args(["--verbose"])
        self.assertTrue(ns.verbose)

    @covers("REQ-0.0.4-03-02")
    def test_registers_debug(self) -> None:
        parser = self._fresh()
        add_common_flags(parser)
        ns = parser.parse_args(["--debug"])
        self.assertTrue(ns.debug)

    def test_returns_parser_for_chaining(self) -> None:
        parser = self._fresh()
        result = add_common_flags(parser)
        self.assertIs(result, parser)


class TestDefaultValues(unittest.TestCase):
    """All flags default to False when not supplied."""

    def test_defaults_are_false(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args([])
        self.assertFalse(ns.quiet)
        self.assertFalse(ns.verbose)
        self.assertFalse(ns.debug)


class TestMutualExclusion(unittest.TestCase):
    """--quiet and --verbose must be mutually exclusive."""

    @covers("REQ-0.0.4-03-03")
    def test_quiet_and_verbose_together_raises(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        with _quiet_stderr(), self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["--quiet", "--verbose"])
        self.assertEqual(ctx.exception.code, 2)

    @covers("REQ-0.0.4-03-03")
    def test_verbose_and_quiet_together_raises(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        with _quiet_stderr(), self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["--verbose", "--quiet"])
        self.assertEqual(ctx.exception.code, 2)

    def test_quiet_alone_is_valid(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args(["--quiet"])
        self.assertTrue(ns.quiet)
        self.assertFalse(ns.verbose)

    def test_verbose_alone_is_valid(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args(["--verbose"])
        self.assertTrue(ns.verbose)
        self.assertFalse(ns.quiet)

    def test_debug_is_independent_of_quiet(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args(["--quiet", "--debug"])
        self.assertTrue(ns.quiet)
        self.assertTrue(ns.debug)

    def test_debug_is_independent_of_verbose(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args(["--verbose", "--debug"])
        self.assertTrue(ns.verbose)
        self.assertTrue(ns.debug)


class TestIdempotency(unittest.TestCase):
    """Calling add_common_flags twice on the same parser must not raise."""

    @covers("REQ-0.0.4-03-06")
    def test_double_call_does_not_raise(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        # Second call should be silent no-op
        add_common_flags(parser)
        ns = parser.parse_args(["--quiet"])
        self.assertTrue(ns.quiet)

    def test_double_call_preserves_mutex(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        add_common_flags(parser)
        with _quiet_stderr(), self.assertRaises(SystemExit):
            parser.parse_args(["--quiet", "--verbose"])


class TestHelpOverrides(unittest.TestCase):
    """Custom help text should appear in formatted help."""

    CASES = [
        ("quiet_help", "My quiet help", "--quiet"),
        ("verbose_help", "My verbose help", "--verbose"),
        ("debug_help", "My debug help", "--debug"),
    ]

    @covers("REQ-0.0.4-03-05")
    def test_help_overrides_appear(self) -> None:
        for kwarg, text, flag in self.CASES:
            with self.subTest(kwarg=kwarg):
                parser = argparse.ArgumentParser(prog="test")
                add_common_flags(parser, **{kwarg: text})
                help_text = parser.format_help()
                self.assertIn(text, help_text, msg=f"Expected '{text}' in help for {flag}")

    @covers("REQ-0.0.4-03-05")
    def test_default_help_present_when_no_override(self) -> None:
        """Default help strings appear when no override is supplied."""
        expected = {
            "--quiet": "Suppress non-error output",
            "--verbose": "Enable verbose output",
            "--debug": "Enable debug mode with full tracebacks",
        }
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        help_text = parser.format_help()
        for flag, text in expected.items():
            with self.subTest(flag=flag):
                self.assertIn(text, help_text)


class TestShortFlags(unittest.TestCase):
    """-q and -v short-form flags must work."""

    def test_short_q_sets_quiet(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args(["-q"])
        self.assertTrue(ns.quiet)

    def test_short_v_sets_verbose(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        ns = parser.parse_args(["-v"])
        self.assertTrue(ns.verbose)

    def test_short_q_and_v_together_raise(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_common_flags(parser)
        with _quiet_stderr(), self.assertRaises(SystemExit) as ctx:
            parser.parse_args(["-q", "-v"])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
