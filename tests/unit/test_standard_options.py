"""Unit tests for gzkit.cli.helpers.standard_options."""

import argparse
import unittest

from gzkit.cli.helpers.standard_options import (
    _option_exists,
    add_adr_option,
    add_dry_run_flag,
    add_force_flag,
    add_json_flag,
    add_table_flag,
)

# ---------------------------------------------------------------------------
# _option_exists
# ---------------------------------------------------------------------------


class TestOptionExists(unittest.TestCase):
    """_option_exists returns True/False correctly."""

    def test_returns_false_for_unregistered_option(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        self.assertFalse(_option_exists(parser, "--json"))

    def test_returns_true_after_registration(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        parser.add_argument("--json", action="store_true")
        self.assertTrue(_option_exists(parser, "--json"))

    def test_returns_false_for_help_option_absent(self) -> None:
        """--help is always registered; verify the check works for known flags."""
        parser = argparse.ArgumentParser(prog="test")
        self.assertTrue(_option_exists(parser, "--help"))

    def test_returns_false_for_unknown_flag(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        self.assertFalse(_option_exists(parser, "--nonexistent-flag"))


# ---------------------------------------------------------------------------
# Flag registration (table-driven)
# ---------------------------------------------------------------------------


class TestFlagRegistration(unittest.TestCase):
    """Each factory registers its flag and returns the parser."""

    CASES = [
        ("add_json_flag", add_json_flag, "--json", []),
        ("add_dry_run_flag", add_dry_run_flag, "--dry-run", []),
        ("add_force_flag", add_force_flag, "--force", []),
        ("add_table_flag", add_table_flag, "--table", []),
    ]

    def test_flag_registered(self) -> None:
        for name, factory, flag, _ in self.CASES:
            with self.subTest(factory=name):
                parser = argparse.ArgumentParser(prog="test")
                factory(parser)
                self.assertTrue(
                    _option_exists(parser, flag), msg=f"{flag} not registered by {name}"
                )

    def test_returns_parser_for_chaining(self) -> None:
        for name, factory, _flag, _ in self.CASES:
            with self.subTest(factory=name):
                parser = argparse.ArgumentParser(prog="test")
                result = factory(parser)
                self.assertIs(result, parser, msg=f"{name} should return the same parser")

    def test_flag_parses_correctly(self) -> None:
        for name, factory, flag, _ in self.CASES:
            with self.subTest(factory=name):
                parser = argparse.ArgumentParser(prog="test")
                factory(parser)
                ns = parser.parse_args([flag])
                # derive dest from flag: --dry-run -> dry_run, --json -> json, etc.
                dest = flag.lstrip("-").replace("-", "_")
                # special case: --json uses dest="as_json"
                if flag == "--json":
                    dest = "as_json"
                self.assertTrue(getattr(ns, dest), msg=f"{flag} did not set {dest}=True")

    def test_default_is_false(self) -> None:
        for name, factory, flag, _ in self.CASES:
            with self.subTest(factory=name):
                parser = argparse.ArgumentParser(prog="test")
                factory(parser)
                ns = parser.parse_args([])
                dest = flag.lstrip("-").replace("-", "_")
                if flag == "--json":
                    dest = "as_json"
                self.assertFalse(getattr(ns, dest), msg=f"{dest} should default to False")


# ---------------------------------------------------------------------------
# Idempotency (table-driven)
# ---------------------------------------------------------------------------


class TestIdempotency(unittest.TestCase):
    """Calling any factory twice on the same parser must not raise."""

    FACTORIES = [
        ("add_json_flag", add_json_flag),
        ("add_dry_run_flag", add_dry_run_flag),
        ("add_force_flag", add_force_flag),
        ("add_table_flag", add_table_flag),
    ]

    def test_double_call_does_not_raise(self) -> None:
        for name, factory in self.FACTORIES:
            with self.subTest(factory=name):
                parser = argparse.ArgumentParser(prog="test")
                factory(parser)
                # Must not raise
                factory(parser)

    def test_adr_double_call_does_not_raise(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser)
        add_adr_option(parser)


# ---------------------------------------------------------------------------
# help_override (table-driven)
# ---------------------------------------------------------------------------


class TestHelpOverride(unittest.TestCase):
    """help_override parameter replaces the default help text."""

    CASES = [
        ("add_json_flag", add_json_flag, "Custom JSON help"),
        ("add_dry_run_flag", add_dry_run_flag, "Custom dry-run help"),
        ("add_force_flag", add_force_flag, "Custom force help"),
        ("add_table_flag", add_table_flag, "Custom table help"),
        ("add_adr_option", add_adr_option, "Custom ADR help"),
    ]

    def test_help_override_appears_in_format_help(self) -> None:
        for name, factory, custom_text in self.CASES:
            with self.subTest(factory=name):
                parser = argparse.ArgumentParser(prog="test")
                factory(parser, help_override=custom_text)
                help_text = parser.format_help()
                self.assertIn(
                    custom_text,
                    help_text,
                    msg=f"Expected '{custom_text}' in help for {name}",
                )

    def test_default_help_present_without_override(self) -> None:
        """Default help strings should appear when no override is given."""
        cases = [
            (add_json_flag, "--json", "Output as JSON"),
            (add_dry_run_flag, "--dry-run", "Show planned actions without executing"),
            (add_force_flag, "--force", "Override safety checks"),
            (add_table_flag, "--table", "Display output as a table"),
            (add_adr_option, "--adr", "ADR identifier"),
        ]
        for factory, flag, expected_text in cases:
            with self.subTest(flag=flag):
                parser = argparse.ArgumentParser(prog="test")
                factory(parser)
                help_text = parser.format_help()
                self.assertIn(expected_text, help_text)


# ---------------------------------------------------------------------------
# add_adr_option specifics
# ---------------------------------------------------------------------------


class TestAddAdrOption(unittest.TestCase):
    """Specific behaviour of add_adr_option."""

    def test_registers_adr_flag(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser)
        self.assertTrue(_option_exists(parser, "--adr"))

    def test_returns_parser(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        result = add_adr_option(parser)
        self.assertIs(result, parser)

    def test_adr_value_is_captured(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser)
        ns = parser.parse_args(["--adr", "ADR-0.0.4"])
        self.assertEqual(ns.adr, "ADR-0.0.4")

    def test_adr_defaults_to_none(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser)
        ns = parser.parse_args([])
        self.assertIsNone(ns.adr)

    def test_required_true_raises_when_omitted(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser, required=True)
        with self.assertRaises(SystemExit) as ctx:
            parser.parse_args([])
        self.assertEqual(ctx.exception.code, 2)

    def test_required_true_succeeds_when_provided(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser, required=True)
        ns = parser.parse_args(["--adr", "ADR-1.2.3"])
        self.assertEqual(ns.adr, "ADR-1.2.3")

    def test_required_false_is_default(self) -> None:
        """required=False (default) allows omitting --adr."""
        parser = argparse.ArgumentParser(prog="test")
        add_adr_option(parser, required=False)
        # Should not raise
        ns = parser.parse_args([])
        self.assertIsNone(ns.adr)


# ---------------------------------------------------------------------------
# add_json_flag dest specifics
# ---------------------------------------------------------------------------


class TestAddJsonFlagDest(unittest.TestCase):
    """add_json_flag must use dest='as_json'."""

    def test_dest_is_as_json(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_json_flag(parser)
        ns = parser.parse_args(["--json"])
        self.assertTrue(ns.as_json)

    def test_dest_as_json_default_false(self) -> None:
        parser = argparse.ArgumentParser(prog="test")
        add_json_flag(parser)
        ns = parser.parse_args([])
        self.assertFalse(ns.as_json)

    def test_attribute_json_does_not_exist(self) -> None:
        """Confirm the attribute is 'as_json', not 'json'."""
        parser = argparse.ArgumentParser(prog="test")
        add_json_flag(parser)
        ns = parser.parse_args(["--json"])
        self.assertFalse(hasattr(ns, "json"))


if __name__ == "__main__":
    unittest.main()
