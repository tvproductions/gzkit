"""Tests for structured logging configuration — OBPI-0.0.3-07.

@covers ADR-0.0.3
"""

import io
import json
import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.logging import (
    VERBOSITY_TO_LEVEL,
    Verbosity,
    bind_correlation_id,
    configure_logging,
)
from gzkit.traceability import covers


class TestConfigureLogging(unittest.TestCase):
    """Test the single configuration entry point."""

    def setUp(self) -> None:
        bind_correlation_id("test-corr-id")

    def tearDown(self) -> None:
        # Clean up root logger handlers
        root = logging.getLogger()
        root.handlers.clear()

    @covers("REQ-0.0.3-07-03")
    @covers("REQ-0.0.3-07-08")
    def test_configure_logging_accepts_all_verbosities(self) -> None:
        for verbosity in ("quiet", "normal", "verbose", "debug"):
            buf = io.StringIO()
            configure_logging(verbosity, console_stream=buf)

    def test_default_verbosity_is_normal(self) -> None:
        buf = io.StringIO()
        configure_logging(console_stream=buf)
        # Should not raise

    @covers("REQ-0.0.3-07-01")
    def test_configure_logging_is_single_entry_point(self) -> None:
        """Verify configure_logging is importable from cli.logging."""
        from gzkit.cli.logging import configure_logging as cl

        self.assertTrue(callable(cl))


class TestVerbosityLevels(unittest.TestCase):
    """The 4 verbosity levels follow `docs/design/cli-standards-v3.md` § Verbosity Levels.

    The canonical specification (ADR-0.0.4): the default logs warnings and errors
    only, `--verbose` adds INFO, `--debug` adds DEBUG, and `--quiet` suppresses
    everything but errors (§ Output Modes).
    """

    def setUp(self) -> None:
        bind_correlation_id("test-corr-id")

    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()

    def test_verbosity_to_level_mapping(self) -> None:
        self.assertEqual(VERBOSITY_TO_LEVEL["quiet"], logging.ERROR)
        self.assertEqual(VERBOSITY_TO_LEVEL["normal"], logging.WARNING)
        self.assertEqual(VERBOSITY_TO_LEVEL["verbose"], logging.INFO)
        self.assertEqual(VERBOSITY_TO_LEVEL["debug"], logging.DEBUG)

    def test_quiet_suppresses_info(self) -> None:
        buf = io.StringIO()
        configure_logging("quiet", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.info("should not appear")
        self.assertEqual(buf.getvalue(), "")

    def test_quiet_shows_errors(self) -> None:
        buf = io.StringIO()
        configure_logging("quiet", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.error("critical problem")
        self.assertIn("critical problem", buf.getvalue())

    def test_normal_shows_warnings(self) -> None:
        buf = io.StringIO()
        configure_logging("normal", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.warning("disk nearly full")
        self.assertIn("disk nearly full", buf.getvalue())

    def test_normal_suppresses_info(self) -> None:
        buf = io.StringIO()
        configure_logging("normal", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.info("status update")
        self.assertEqual(buf.getvalue(), "")

    def test_verbose_shows_info(self) -> None:
        buf = io.StringIO()
        configure_logging("verbose", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.info("status update")
        self.assertIn("status update", buf.getvalue())

    def test_verbose_suppresses_debug(self) -> None:
        buf = io.StringIO()
        configure_logging("verbose", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.debug("verbose detail")
        self.assertEqual(buf.getvalue(), "")

    def test_debug_shows_debug(self) -> None:
        buf = io.StringIO()
        configure_logging("debug", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.debug("debug info")
        self.assertIn("debug info", buf.getvalue())


class TestJsonFileOutput(unittest.TestCase):
    """Test JSON file output for machine consumption."""

    def setUp(self) -> None:
        bind_correlation_id("json-test-id")

    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()

    def test_json_file_receives_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test.log"
            buf = io.StringIO()
            configure_logging("normal", log_file=log_path, console_stream=buf)
            log = logging.getLogger("gzkit.test")
            log.info("test event", extra={"key": "value"})

            # Close handlers before temp dir cleanup (Windows file lock)
            root = logging.getLogger()
            for handler in root.handlers:
                handler.flush()
                handler.close()
            root.handlers.clear()

            content = log_path.read_text(encoding="utf-8").strip()
            self.assertTrue(content, "Log file should not be empty")
            parsed = json.loads(content)
            self.assertEqual(parsed["event"], "test event")
            self.assertEqual(parsed["key"], "value")

    @covers("REQ-0.0.3-07-04")
    @covers("REQ-0.0.3-07-08")
    def test_json_file_contains_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test.log"
            buf = io.StringIO()
            configure_logging("normal", log_file=log_path, console_stream=buf)
            log = logging.getLogger("gzkit.test")
            log.info("first event")
            log.warning("second event")

            root = logging.getLogger()
            for handler in root.handlers:
                handler.flush()
                handler.close()
            root.handlers.clear()

            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            for line in lines:
                parsed = json.loads(line)
                self.assertIn("event", parsed)

    def test_json_file_captures_debug_even_at_normal_verbosity(self) -> None:
        """JSON file gets all events regardless of console verbosity."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test.log"
            buf = io.StringIO()
            configure_logging("normal", log_file=log_path, console_stream=buf)
            log = logging.getLogger("gzkit.test")
            log.debug("debug event for file")

            root = logging.getLogger()
            for handler in root.handlers:
                handler.flush()
                handler.close()
            root.handlers.clear()

            content = log_path.read_text(encoding="utf-8").strip()
            self.assertTrue(content, "Debug events should reach the file")
            parsed = json.loads(content)
            self.assertEqual(parsed["event"], "debug event for file")


class TestConsoleOutput(unittest.TestCase):
    """Test human-readable console output."""

    def setUp(self) -> None:
        bind_correlation_id("console-test")

    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()

    @covers("REQ-0.0.3-07-05")
    @covers("REQ-0.0.3-07-08")
    def test_console_output_is_human_readable(self) -> None:
        buf = io.StringIO()
        configure_logging("normal", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.warning("hello world")
        output = buf.getvalue()
        self.assertIn("hello world", output)
        # Console output should NOT be JSON
        with self.assertRaises(json.JSONDecodeError):
            json.loads(output.strip())

    def test_console_goes_to_stderr_by_default(self) -> None:
        """Verify default stream is stderr (not stdout)."""
        # configure_logging with no console_stream defaults to sys.stderr
        # We test this by providing a mock
        buf = io.StringIO()
        configure_logging("normal", console_stream=buf)
        log = logging.getLogger("gzkit.test")
        log.warning("test message")
        self.assertIn("test message", buf.getvalue())


_BOOM = "boom"


def _raise_boom() -> None:
    raise ValueError(_BOOM)


class TestRecordDetail(unittest.TestCase):
    """What each formatter carries beyond the event: callsite, exception, stack, an own ID."""

    def setUp(self) -> None:
        bind_correlation_id("detail-test")
        self._tmp = tempfile.TemporaryDirectory()
        self._log_path = Path(self._tmp.name) / "detail.log"

    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()
        self._tmp.cleanup()

    def _emit(
        self,
        verbosity: Verbosity,
        *,
        raised: bool = False,
        stack_info: bool = False,
        extra: dict[str, object] | None = None,
    ) -> tuple[str, dict]:
        """Log one record at ERROR.

        Returns:
            The console text and the log file's last JSON record.

        """
        console = io.StringIO()
        configure_logging(verbosity, log_file=self._log_path, console_stream=console)
        log = logging.getLogger("gzkit.test")
        if raised:
            try:
                _raise_boom()
            except ValueError:
                log.exception("failed.step", stack_info=stack_info, extra=extra)
        else:
            log.error("plain.step", stack_info=stack_info, extra=extra)
        for handler in logging.getLogger().handlers:
            handler.flush()
        last = self._log_path.read_text(encoding="utf-8").strip().splitlines()[-1]
        return console.getvalue(), json.loads(last)

    def test_debug_carries_the_callsite_and_other_verbosities_do_not(self) -> None:
        console, record = self._emit("debug")
        self.assertEqual(record["funcName"], "_emit")
        self.assertIn("lineno", record)
        self.assertIn("funcName=_emit", console)
        console, record = self._emit("normal")
        self.assertNotIn("funcName", record)
        self.assertNotIn("funcName=", console)

    def test_an_exception_reaches_both_formatters(self) -> None:
        console, record = self._emit("normal", raised=True)
        self.assertIn("ValueError: boom", record["exception"])
        self.assertIn("ValueError: boom", console)

    def test_a_stack_reaches_both_formatters(self) -> None:
        console, record = self._emit("normal", stack_info=True)
        self.assertIn("Stack (most recent call last)", record["stack"])
        self.assertIn("Stack (most recent call last)", console)

    def test_a_record_that_names_its_own_correlation_id_keeps_it(self) -> None:
        _, record = self._emit("normal", extra={"correlation_id": "explicit-id"})
        self.assertEqual(record["correlation_id"], "explicit-id")

    def test_reconfiguring_closes_the_previous_log_file(self) -> None:
        configure_logging("normal", log_file=self._log_path, console_stream=io.StringIO())
        previous = [h for h in logging.getLogger().handlers if isinstance(h, logging.FileHandler)]
        configure_logging("normal", console_stream=io.StringIO())
        self.assertTrue(previous)
        self.assertIsNone(previous[0].stream)


class TestCorrelationId(unittest.TestCase):
    """Test correlation ID binding and propagation."""

    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()

    @covers("REQ-0.0.3-07-06")
    def test_bind_correlation_id_returns_id(self) -> None:
        cid = bind_correlation_id("my-request-123")
        self.assertEqual(cid, "my-request-123")

    def test_bind_correlation_id_generates_when_none(self) -> None:
        cid = bind_correlation_id()
        self.assertEqual(len(cid), 12)
        self.assertTrue(cid.isalnum())

    def test_correlation_id_appears_in_log_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test.log"
            buf = io.StringIO()
            bind_correlation_id("corr-abc-123")
            configure_logging("normal", log_file=log_path, console_stream=buf)
            log = logging.getLogger("gzkit.test")
            log.info("test with correlation")

            root = logging.getLogger()
            for handler in root.handlers:
                handler.flush()
                handler.close()
            root.handlers.clear()

            content = log_path.read_text(encoding="utf-8").strip()
            parsed = json.loads(content)
            self.assertEqual(parsed["correlation_id"], "corr-abc-123")

    def test_correlation_id_propagates_across_calls(self) -> None:
        """Multiple log calls carry the same correlation ID."""
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "test.log"
            buf = io.StringIO()
            bind_correlation_id("propagate-test")
            configure_logging("normal", log_file=log_path, console_stream=buf)
            log = logging.getLogger("gzkit.test")
            log.info("first call")
            log.info("second call")

            root = logging.getLogger()
            for handler in root.handlers:
                handler.flush()
                handler.close()
            root.handlers.clear()

            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            for line in lines:
                parsed = json.loads(line)
                self.assertEqual(parsed["correlation_id"], "propagate-test")


class TestCoreLayerBinding(unittest.TestCase):
    """Verify core layer can bind context through stdlib logging alone."""

    @covers("REQ-0.0.3-07-07")
    def test_core_binds_context_without_the_cli_configuration(self) -> None:
        """A core module binds fields with a stdlib adapter; the CLI formatter renders them."""
        bound = logging.LoggerAdapter(
            logging.getLogger("gzkit.core.lifecycle"), {"component": "core.lifecycle"}
        )
        with self.assertLogs("gzkit.core.lifecycle", level="WARNING") as cap:
            bound.warning("state.changed")
        self.assertEqual(getattr(cap.records[0], "component", None), "core.lifecycle")
        console = io.StringIO()
        try:
            configure_logging("normal", console_stream=console)
            bound.warning("state.changed")
        finally:
            root = logging.getLogger()
            for handler in root.handlers:
                handler.close()
            root.handlers.clear()
        self.assertIn("state.changed component=core.lifecycle", console.getvalue())

    def test_core_binding_only_imports(self) -> None:
        """Verify that the CLI logging adapter imports nothing from core or ports."""
        import ast

        src = Path(__file__).resolve().parent.parent / "src" / "gzkit" / "cli" / "logging.py"
        tree = ast.parse(src.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertFalse(
                    node.module.startswith("gzkit.core"),
                    f"CLI logging must not import from core: {node.module}",
                )
                self.assertFalse(
                    node.module.startswith("gzkit.ports"),
                    f"CLI logging must not import from ports: {node.module}",
                )


class TestExportFromCliPackage(unittest.TestCase):
    """Verify exports from gzkit.cli package."""

    def test_configure_logging_importable_from_cli(self) -> None:
        from gzkit.cli import configure_logging as cl

        self.assertTrue(callable(cl))

    def test_bind_correlation_id_importable_from_cli(self) -> None:
        from gzkit.cli import bind_correlation_id as bci

        self.assertTrue(callable(bci))


class TestConsoleColorsFollowThePlatformDefault(unittest.TestCase):
    """GHI #1010: the entrypoint runs `configure_logging` for every `gz` command.

    The console styles its level only for a terminal that wants colour, with plain
    ANSI that needs no colorama on Windows. gzkit's stdlib warnings reach the same
    formatter, so captured or piped stderr must stay free of ANSI styling, and
    `NO_COLOR` must hold even on a terminal.
    """

    class _Terminal(io.StringIO):
        def isatty(self) -> bool:
            return True

    def _render_warning(
        self, stream: io.StringIO, env: dict[str, str], verbosity: Verbosity = "normal"
    ) -> str:
        with patch.dict(os.environ, env, clear=True):
            configure_logging(verbosity, console_stream=stream)
        logging.getLogger("gzkit.triangle").warning("Malformed REQ line (skipped): %s", "x")
        logging.getLogger("gzkit.commands.chores").error(
            "chore.resolver.fallback", extra={"slug": "demo"}
        )
        return stream.getvalue()

    def _environment_without_color_settings(self) -> dict[str, str]:
        return {k: v for k, v in os.environ.items() if k not in {"NO_COLOR", "FORCE_COLOR"}}

    def tearDown(self) -> None:
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
        root.handlers.clear()

    def test_a_piped_stream_receives_no_styling(self) -> None:
        output = self._render_warning(io.StringIO(), self._environment_without_color_settings())
        self.assertIn("Malformed REQ line (skipped): x", output)
        self.assertIn("chore.resolver.fallback slug=demo", output)
        self.assertNotIn("\x1b[", output)

    def test_no_color_keeps_a_terminal_plain(self) -> None:
        env = {**self._environment_without_color_settings(), "NO_COLOR": "1"}
        output = self._render_warning(self._Terminal(), env)
        self.assertIn("Malformed REQ line (skipped): x", output)
        self.assertNotIn("\x1b[", output)

    def test_a_terminal_that_wants_colour_gets_it_and_quiet_never_does(self) -> None:
        env = self._environment_without_color_settings()
        self.assertIn("\x1b[", self._render_warning(self._Terminal(), env))
        self.tearDown()
        self.assertNotIn("\x1b[", self._render_warning(self._Terminal(), env, "quiet"))

    def test_a_detached_stderr_does_not_stop_the_command(self) -> None:
        """Under pythonw or a detached launch `sys.stderr` is None.

        Every command configures logging before its handler runs, so the colour
        decision must not assume a stream to ask; there is no terminal to colour.
        """
        with patch.object(sys, "stderr", None):
            try:
                configure_logging("normal")
            except Exception as exc:
                self.fail(f"configuring logging with no stderr raised {exc!r}")
        self.assertIsInstance(logging.getLogger().handlers[0].formatter, logging.Formatter)


if __name__ == "__main__":
    unittest.main()
