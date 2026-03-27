"""Tests for OutputFormatter — OBPI-0.0.3-06 and OBPI-0.0.4-06.

@covers ADR-0.0.3
@covers ADR-0.0.4
"""

import io
import json
import os
import unittest
from unittest.mock import patch

from pydantic import BaseModel, ConfigDict
from rich.table import Table

from gzkit.cli.formatters import VALID_MODES, OutputFormatter, OutputMode
from gzkit.traceability import covers


class TestOutputFormatterInit(unittest.TestCase):
    """Test formatter initialisation and mode validation."""

    @covers("REQ-0.0.3-06-02")
    def test_default_mode_is_human(self) -> None:
        fmt = OutputFormatter()
        self.assertEqual(fmt.mode, "human")

    @covers("REQ-0.0.3-06-08")
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

    @covers("REQ-0.0.4-06-01")
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

    @covers("REQ-0.0.3-06-04")
    def test_err_goes_to_stderr(self) -> None:
        fmt = OutputFormatter("human")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.err("error msg")
            self.assertIn("error msg", mock_err.getvalue())


class TestJsonMode(unittest.TestCase):
    """Test json mode — data to stdout, logs to stderr."""

    @covers("REQ-0.0.3-06-03")
    @covers("REQ-0.0.4-06-02")
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

    @covers("REQ-0.0.4-06-02")
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

    @covers("REQ-0.0.3-06-04")
    @covers("REQ-0.0.4-06-04")
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

    @covers("REQ-0.0.4-06-04")
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

    @covers("REQ-0.0.4-06-05")
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

    @covers("REQ-0.0.3-06-05")
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

    @covers("REQ-0.0.3-06-06")
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

    @covers("REQ-0.0.3-06-07")
    @covers("REQ-0.0.4-06-01")
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

    @covers("REQ-0.0.4-06-01")
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


class TestOutputModeEnum(unittest.TestCase):
    """Verify OutputMode is a proper StrEnum with the correct members.

    @covers ADR-0.0.4
    """

    @covers("REQ-0.0.4-06-02")
    def test_has_exactly_five_members(self) -> None:
        members = list(OutputMode)
        self.assertEqual(len(members), 5)

    @covers("REQ-0.0.4-06-02")
    def test_member_names(self) -> None:
        names = {m.name for m in OutputMode}
        self.assertEqual(names, {"HUMAN", "JSON", "QUIET", "VERBOSE", "DEBUG"})

    def test_member_values_are_lowercase_strings(self) -> None:
        for member in OutputMode:
            self.assertEqual(member.value, member.value.lower())

    def test_human_value_is_string_human(self) -> None:
        self.assertEqual(OutputMode.HUMAN, "human")

    def test_json_value_is_string_json(self) -> None:
        self.assertEqual(OutputMode.JSON, "json")

    def test_quiet_value_is_string_quiet(self) -> None:
        self.assertEqual(OutputMode.QUIET, "quiet")

    def test_verbose_value_is_string_verbose(self) -> None:
        self.assertEqual(OutputMode.VERBOSE, "verbose")

    def test_debug_value_is_string_debug(self) -> None:
        self.assertEqual(OutputMode.DEBUG, "debug")

    def test_valid_modes_equals_all_enum_values(self) -> None:
        expected = frozenset(m.value for m in OutputMode)
        self.assertEqual(VALID_MODES, expected)

    def test_strenum_comparison_with_plain_string(self) -> None:
        """StrEnum members must compare equal to their plain string values."""
        self.assertTrue(OutputMode.HUMAN == "human")
        self.assertTrue(OutputMode.JSON == "json")


class TestConsoleParameter(unittest.TestCase):
    """Verify the console= constructor parameter is wired correctly.

    @covers ADR-0.0.4
    """

    @covers("REQ-0.0.4-06-01")
    def test_default_creates_internal_console(self) -> None:
        fmt = OutputFormatter()
        self.assertIsNotNone(fmt.console)

    @covers("REQ-0.0.4-06-01")
    def test_provided_console_is_used(self) -> None:
        from rich.console import Console

        custom = Console(no_color=True, width=80)
        fmt = OutputFormatter(console=custom)
        self.assertIs(fmt.console, custom)

    def test_provided_console_returned_by_property(self) -> None:
        from rich.console import Console

        custom = Console(no_color=True, width=40)
        fmt = OutputFormatter("human", console=custom)
        self.assertIs(fmt.console, custom)


# ---------------------------------------------------------------------------
# Minimal Pydantic model used by TestEmitMethod
# ---------------------------------------------------------------------------


class _TestModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    count: int


class TestEmitMethod(unittest.TestCase):
    """Test emit(data) for all types and all relevant modes.

    @covers ADR-0.0.4
    """

    # ------------------------------------------------------------------
    # String payloads
    # ------------------------------------------------------------------

    @covers("REQ-0.0.4-06-01")
    def test_string_human_mode_outputs_to_console(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        fmt.emit("hello emit")
        self.assertIn("hello emit", buf.getvalue())

    def test_string_json_mode_outputs_to_stdout(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit("raw string output")
            self.assertIn("raw string output", mock_out.getvalue())

    # ------------------------------------------------------------------
    # Dict payloads
    # ------------------------------------------------------------------

    def test_dict_human_mode_outputs_to_console(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        fmt.emit({"status": "ok"})
        self.assertIn("status", buf.getvalue())

    @covers("REQ-0.0.4-06-02")
    def test_dict_json_mode_outputs_valid_json_sorted(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit({"z_key": 1, "a_key": 2})
            raw = mock_out.getvalue()
        parsed = json.loads(raw)
        self.assertEqual(parsed["z_key"], 1)
        self.assertEqual(parsed["a_key"], 2)
        # Verify sort_keys -- "a_key" appears before "z_key" in raw output
        self.assertLess(raw.index("a_key"), raw.index("z_key"))

    # ------------------------------------------------------------------
    # List payloads
    # ------------------------------------------------------------------

    def test_list_json_mode_outputs_valid_json(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit([1, 2, 3])
            raw = mock_out.getvalue()
        parsed = json.loads(raw)
        self.assertEqual(parsed, [1, 2, 3])

    # ------------------------------------------------------------------
    # Pydantic BaseModel payloads
    # ------------------------------------------------------------------

    @covers("REQ-0.0.4-06-03")
    def test_pydantic_json_mode_outputs_model_dump_json(self) -> None:
        fmt = OutputFormatter("json")
        model = _TestModel(name="gzkit", count=7)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit(model)
            raw = mock_out.getvalue().strip()
        parsed = json.loads(raw)
        self.assertEqual(parsed["name"], "gzkit")
        self.assertEqual(parsed["count"], 7)

    def test_pydantic_human_mode_outputs_formatted_dict(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        model = _TestModel(name="test", count=42)
        fmt.emit(model)
        output = buf.getvalue()
        self.assertIn("name", output)
        self.assertIn("test", output)

    # ------------------------------------------------------------------
    # Quiet mode suppression
    # ------------------------------------------------------------------

    @covers("REQ-0.0.4-06-04")
    def test_quiet_mode_suppresses_string(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit("should not appear")
            self.assertEqual(mock_out.getvalue(), "")

    @covers("REQ-0.0.4-06-04")
    def test_quiet_mode_suppresses_dict(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit({"key": "value"})
            self.assertEqual(mock_out.getvalue(), "")

    @covers("REQ-0.0.4-06-04")
    def test_quiet_mode_suppresses_pydantic_model(self) -> None:
        fmt = OutputFormatter("quiet")
        model = _TestModel(name="nope", count=0)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit(model)
            self.assertEqual(mock_out.getvalue(), "")


class TestEmitError(unittest.TestCase):
    """Test emit_error -- always writes to stderr in every mode.

    @covers ADR-0.0.4
    """

    @covers("REQ-0.0.4-06-05")
    def test_human_mode_writes_to_stderr(self) -> None:
        fmt = OutputFormatter("human")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_error("human error")
            self.assertIn("human error", mock_err.getvalue())

    @covers("REQ-0.0.4-06-05")
    def test_json_mode_writes_to_stderr(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_error("json error")
            self.assertIn("json error", mock_err.getvalue())

    @covers("REQ-0.0.4-06-05")
    def test_quiet_mode_writes_to_stderr_never_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_error("quiet error")
            self.assertIn("quiet error", mock_err.getvalue())

    @covers("REQ-0.0.4-06-05")
    def test_verbose_mode_writes_to_stderr(self) -> None:
        fmt = OutputFormatter("verbose")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_error("verbose error")
            self.assertIn("verbose error", mock_err.getvalue())

    @covers("REQ-0.0.4-06-05")
    def test_debug_mode_writes_to_stderr(self) -> None:
        fmt = OutputFormatter("debug")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_error("debug error")
            self.assertIn("debug error", mock_err.getvalue())


class TestEmitTable(unittest.TestCase):
    """Test emit_table -- human renders Rich table; json emits dict-list JSON.

    @covers ADR-0.0.4
    """

    def _make_table(self) -> Table:
        t = Table()
        t.add_column("Name")
        t.add_column("Score")
        t.add_row("alice", "10")
        t.add_row("bob", "20")
        return t

    @covers("REQ-0.0.4-06-06")
    def test_human_mode_renders_table(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        fmt.emit_table(self._make_table())
        output = buf.getvalue()
        self.assertIn("Name", output)
        self.assertIn("alice", output)

    @covers("REQ-0.0.4-06-06")
    def test_json_mode_outputs_valid_json_array(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit_table(self._make_table())
            raw = mock_out.getvalue()
        parsed = json.loads(raw)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)

    @covers("REQ-0.0.4-06-06")
    def test_json_mode_rows_have_column_keys(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit_table(self._make_table())
            raw = mock_out.getvalue()
        parsed = json.loads(raw)
        self.assertIn("Name", parsed[0])
        self.assertIn("Score", parsed[0])
        self.assertEqual(parsed[0]["Name"], "alice")
        self.assertEqual(parsed[1]["Score"], "20")

    def test_quiet_mode_suppresses_table(self) -> None:
        fmt = OutputFormatter("quiet")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit_table(self._make_table())
            self.assertEqual(mock_out.getvalue(), "")
        self.assertEqual(buf.getvalue(), "")


class TestEmitStatus(unittest.TestCase):
    """Test emit_status -- check/cross symbols in human; JSON object in json mode.

    @covers ADR-0.0.4
    """

    @covers("REQ-0.0.4-06-07")
    def test_human_mode_success_shows_checkmark(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        fmt.emit_status("Gate passed", success=True)
        self.assertIn("\u2713", buf.getvalue())

    @covers("REQ-0.0.4-06-07")
    def test_human_mode_failure_shows_cross(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        fmt.emit_status("Gate failed", success=False)
        self.assertIn("\u2717", buf.getvalue())

    def test_human_mode_label_included(self) -> None:
        fmt = OutputFormatter("human")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        fmt.emit_status("My Label", success=True)
        self.assertIn("My Label", buf.getvalue())

    @covers("REQ-0.0.4-06-07")
    def test_json_mode_success_outputs_json(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit_status("build", success=True)
            raw = mock_out.getvalue()
        parsed = json.loads(raw)
        self.assertEqual(parsed["label"], "build")
        self.assertTrue(parsed["success"])

    @covers("REQ-0.0.4-06-07")
    def test_json_mode_failure_outputs_json(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit_status("lint", success=False)
            raw = mock_out.getvalue()
        parsed = json.loads(raw)
        self.assertEqual(parsed["label"], "lint")
        self.assertFalse(parsed["success"])

    def test_quiet_mode_suppresses_status(self) -> None:
        fmt = OutputFormatter("quiet")
        buf = io.StringIO()
        fmt._console = __import__("rich.console", fromlist=["Console"]).Console(
            file=buf, no_color=True, width=120
        )
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            fmt.emit_status("should not appear", success=True)
            self.assertEqual(mock_out.getvalue(), "")
        self.assertEqual(buf.getvalue(), "")


class TestEmitBlocker(unittest.TestCase):
    """Test emit_blocker -- always writes BLOCKERS message to stderr.

    @covers ADR-0.0.4
    """

    @covers("REQ-0.0.4-06-08")
    def test_human_mode_writes_blockers_to_stderr(self) -> None:
        fmt = OutputFormatter("human")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_blocker("missing config")
            self.assertIn("BLOCKERS: missing config", mock_err.getvalue())

    @covers("REQ-0.0.4-06-08")
    def test_json_mode_writes_blockers_to_stderr(self) -> None:
        fmt = OutputFormatter("json")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_blocker("invalid schema")
            self.assertIn("BLOCKERS: invalid schema", mock_err.getvalue())

    @covers("REQ-0.0.4-06-08")
    def test_quiet_mode_writes_blockers_to_stderr_never_suppressed(self) -> None:
        fmt = OutputFormatter("quiet")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_blocker("gate failure")
            self.assertIn("BLOCKERS: gate failure", mock_err.getvalue())

    @covers("REQ-0.0.4-06-08")
    def test_verbose_mode_writes_blockers_to_stderr(self) -> None:
        fmt = OutputFormatter("verbose")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_blocker("verbose blocker")
            self.assertIn("BLOCKERS: verbose blocker", mock_err.getvalue())

    @covers("REQ-0.0.4-06-08")
    def test_debug_mode_writes_blockers_to_stderr(self) -> None:
        fmt = OutputFormatter("debug")
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            fmt.emit_blocker("debug blocker")
            self.assertIn("BLOCKERS: debug blocker", mock_err.getvalue())

    @covers("REQ-0.0.4-06-08")
    def test_blockers_prefix_always_present(self) -> None:
        """The 'BLOCKERS: ' prefix must always appear, in every mode."""
        for mode in ("human", "json", "quiet", "verbose", "debug"):
            fmt = OutputFormatter(mode)  # type: ignore[arg-type]
            with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
                fmt.emit_blocker("check this")
                self.assertIn(
                    "BLOCKERS: check this",
                    mock_err.getvalue(),
                    f"Prefix missing in {mode} mode",
                )


if __name__ == "__main__":
    unittest.main()
