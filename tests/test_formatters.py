"""Tests for OutputFormatter — OBPI-0.0.3-06.

@covers ADR-0.0.3
"""

import io
import json
import os
import unittest
from unittest.mock import patch

from rich.table import Table

from gzkit.cli.formatters import VALID_MODES, OutputFormatter


class TestOutputFormatterInit(unittest.TestCase):
    """Test formatter initialisation and mode validation."""

    def test_default_mode_is_human(self) -> None:
        fmt = OutputFormatter()
        self.assertEqual(fmt.mode, "human")

    def test_all_valid_modes_accepted(self) -> None:
        for mode in ("human", "json", "quiet", "verbose", "debug"):
            fmt = OutputFormatter(mode)
            self.assertEqual(fmt.mode, mode)

    def test_invalid_mode_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            OutputFormatter("invalid")  # type: ignore[arg-type]

    def test_valid_modes_frozenset(self) -> None:
        self.assertEqual(VALID_MODES, frozenset({"human", "json", "quiet", "verbose", "debug"}))

    def test_console_property_returns_console(self) -> None:
        fmt = OutputFormatter("human")
        self.assertIsNotNone(fmt.console)


class TestHumanMode(unittest.TestCase):
    """Test human mode — Rich tables, colors, progress."""

    def test_print_outputs_to_console(self) -> None:
        fmt = OutputFormatter("human")
        # Capture console output
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.print("hello world")
        self.assertIn("hello world", buf.getvalue())

    def test_table_renders(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        t = Table(title="Test")
        t.add_column("Col")
        t.add_row("val")
        fmt.table(t)
        output = buf.getvalue()
        self.assertIn("Col", output)
        self.assertIn("val", output)

    def test_data_renders_dict(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.data({"key": "value"})
        self.assertIn("key", buf.getvalue())

    def test_err_goes_to_stderr(self) -> None:
        fmt = OutputFormatter("human")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.err("error msg")
            self.assertIn("error msg", mock_err.getvalue())


class TestJsonMode(unittest.TestCase):
    """Test json mode — data to stdout, logs to stderr."""

    def test_data_outputs_valid_json_to_stdout(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.data({"status": "ok", "count": 42})
            output = mock_out.getvalue()
        parsed = json.loads(output)
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["count"], 42)

    def test_print_goes_to_stderr_in_json_mode(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.print("log message")
            self.assertIn("log message", mock_err.getvalue())

    def test_data_and_logs_never_mix_on_stdout(self) -> None:
        """Verify that log/print output never appears on stdout in json mode."""
        fmt = OutputFormatter("json")
        with (
            patch("sys.stdout", new_callable=io.StringIO) as mock_out,
            patch("sys.stderr", new_callable=io.StringIO) as mock_err,
        ):
            fmt.print("log line")
            fmt.log("another log")
            fmt.data({"result": True})

            stdout_content = mock_out.getvalue()
            stderr_content = mock_err.getvalue()

        # stdout should only contain the JSON data
        parsed = json.loads(stdout_content)
        self.assertEqual(parsed, {"result": True})

        # stderr should contain the log lines
        self.assertIn("log line", stderr_content)
        self.assertIn("another log", stderr_content)

    def test_table_suppressed_in_json_mode(self) -> None:
        fmt = OutputFormatter("json")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        t = Table(title="Test")
        t.add_column("Col")
        t.add_row("val")
        fmt.table(t)
        # Table should not be rendered in json mode
        self.assertEqual(buf.getvalue(), "")

    def test_err_goes_to_stderr_in_json_mode(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.err("error in json")
            self.assertIn("error in json", mock_err.getvalue())


class TestQuietMode(unittest.TestCase):
    """Test quiet mode — errors only."""

    def test_print_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.print("should not appear")
        self.assertEqual(buf.getvalue(), "")

    def test_data_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.data({"key": "value"})
            self.assertEqual(mock_out.getvalue(), "")

    def test_table_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        t = Table()
        t.add_column("Col")
        fmt.table(t)
        self.assertEqual(buf.getvalue(), "")

    def test_err_still_outputs(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.err("critical error")
            self.assertIn("critical error", mock_err.getvalue())

    def test_print_with_err_flag_outputs(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.print("error via flag", err=True)
            self.assertIn("error via flag", mock_err.getvalue())

    def test_log_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.log("should not appear")
        self.assertEqual(buf.getvalue(), "")

    def test_verbose_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.verbose("should not appear")
        self.assertEqual(buf.getvalue(), "")


class TestVerboseMode(unittest.TestCase):
    """Test verbose mode — debug-level information."""

    def test_verbose_message_shown(self) -> None:
        fmt = OutputFormatter("verbose")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.verbose("detail info")
        self.assertIn("detail info", buf.getvalue())

    def test_print_still_works(self) -> None:
        fmt = OutputFormatter("verbose")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.print("normal message")
        self.assertIn("normal message", buf.getvalue())

    def test_debug_message_suppressed_in_verbose(self) -> None:
        fmt = OutputFormatter("verbose")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.debug("should not appear")
        self.assertEqual(buf.getvalue(), "")


class TestDebugMode(unittest.TestCase):
    """Test debug mode — full diagnostic output."""

    def test_debug_message_shown(self) -> None:
        fmt = OutputFormatter("debug")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.debug("internal state")
        self.assertIn("internal state", buf.getvalue())

    def test_verbose_message_also_shown(self) -> None:
        fmt = OutputFormatter("debug")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.verbose("verbose detail")
        self.assertIn("verbose detail", buf.getvalue())

    def test_print_still_works(self) -> None:
        fmt = OutputFormatter("debug")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf,
            no_color=True,
            width=120,
        )
        fmt.print("normal message")
        self.assertIn("normal message", buf.getvalue())


class TestNoColor(unittest.TestCase):
    """Test NO_COLOR environment variable support."""

    def test_no_color_respected_in_human_mode(self) -> None:
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            fmt = OutputFormatter("human")
            self.assertTrue(fmt.console.no_color)

    def test_no_color_absent_allows_color(self) -> None:
        env = os.environ.copy()
        env.pop("NO_COLOR", None)
        env.pop("FORCE_COLOR", None)
        with patch.dict(os.environ, env, clear=True):
            fmt = OutputFormatter("human")
            self.assertFalse(fmt.console.no_color)

    def test_json_mode_always_no_color(self) -> None:
        env = os.environ.copy()
        env.pop("NO_COLOR", None)
        with patch.dict(os.environ, env, clear=True):
            fmt = OutputFormatter("json")
            self.assertTrue(fmt.console.no_color)


class TestModeFromFlags(unittest.TestCase):
    """Test mode_from_flags static method — flag priority."""

    def test_default_is_human(self) -> None:
        self.assertEqual(OutputFormatter.mode_from_flags(), "human")

    def test_json_flag(self) -> None:
        self.assertEqual(OutputFormatter.mode_from_flags(json_flag=True), "json")

    def test_quiet_flag(self) -> None:
        self.assertEqual(OutputFormatter.mode_from_flags(quiet=True), "quiet")

    def test_verbose_flag(self) -> None:
        self.assertEqual(OutputFormatter.mode_from_flags(verbose=True), "verbose")

    def test_debug_flag(self) -> None:
        self.assertEqual(OutputFormatter.mode_from_flags(debug=True), "debug")

    def test_json_takes_priority_over_quiet(self) -> None:
        self.assertEqual(
            OutputFormatter.mode_from_flags(json_flag=True, quiet=True),
            "json",
        )

    def test_quiet_takes_priority_over_verbose(self) -> None:
        self.assertEqual(
            OutputFormatter.mode_from_flags(quiet=True, verbose=True),
            "quiet",
        )

    def test_debug_takes_priority_over_verbose(self) -> None:
        self.assertEqual(
            OutputFormatter.mode_from_flags(debug=True, verbose=True),
            "debug",
        )


class TestImportBoundary(unittest.TestCase):
    """Verify OutputFormatter lives in the CLI adapter layer only."""

    def test_importable_from_gzkit_cli(self) -> None:
        from gzkit.cli import OutputFormatter as OF

        self.assertIs(OF, OutputFormatter)

    def test_formatters_does_not_import_core(self) -> None:
        """Verify formatters.py has no imports from gzkit.core or gzkit.ports."""
        import ast
        from pathlib import Path

        src = Path(__file__).resolve().parent.parent / "src" / "gzkit" / "cli" / "formatters.py"
        tree = ast.parse(src.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertFalse(
                    node.module.startswith("gzkit.core"),
                    f"Forbidden import: {node.module}",
                )
                self.assertFalse(
                    node.module.startswith("gzkit.ports"),
                    f"Forbidden import: {node.module}",
                )


if __name__ == "__main__":
    unittest.main()
