"""Tests for progress indication (OBPI-0.0.4-09).

Verifies progress_context on OutputFormatter: stderr output,
suppression in quiet/JSON modes, and non-TTY degradation.
"""

import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gzkit.cli.formatters import OutputFormatter, OutputMode, ProgressContext
from gzkit.quality import QualityResult


class _ProgressSpy:
    def __init__(self, total: int, label: str) -> None:
        self.total = total
        self.label = label
        self.advanced: list[str] = []

    def __enter__(self) -> "_ProgressSpy":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def advance(self, step: str) -> None:
        self.advanced.append(step)


class _FormatterSpy:
    instances: list["_FormatterSpy"] = []

    def __init__(self) -> None:
        self.progress: _ProgressSpy | None = None
        self.__class__.instances.append(self)

    def progress_context(self, total: int, label: str) -> _ProgressSpy:
        self.progress = _ProgressSpy(total, label)
        return self.progress


def _result(success: bool) -> QualityResult:
    """Build a faithful step result.

    Previously a ``SimpleNamespace(success=...)`` partial fake. ``check()``
    consumes more of ``QualityResult`` than ``.success`` — the advisory renderer
    reads the captured streams (GHI #713) — and a stub that models only the
    field today's assertions touch fails whenever the consumer grows. Using the
    real model makes that class of drift impossible.
    """
    return QualityResult(
        success=success,
        command="uv run gz stub",
        stdout="",
        stderr="",
        returncode=0 if success else 1,
    )


class TestProgressContextExists(unittest.TestCase):
    """REQ-0.0.4-09-06: progress_context is the single entry point."""

    def test_progress_context_method_exists(self):
        fmt = OutputFormatter()
        self.assertTrue(hasattr(fmt, "progress_context"))

    def test_progress_context_returns_context_manager(self):
        fmt = OutputFormatter()
        ctx = fmt.progress_context(3, "test")
        self.assertIsInstance(ctx, ProgressContext)
        self.assertTrue(hasattr(ctx, "__enter__"))
        self.assertTrue(hasattr(ctx, "__exit__"))


class TestProgressSuppression(unittest.TestCase):
    """REQ-0.0.4-09-02 / REQ-0.0.4-09-03: Suppressed in quiet and JSON modes."""

    def test_quiet_mode_suppresses_progress(self):
        fmt = OutputFormatter(OutputMode.QUIET)
        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture), fmt.progress_context(3, "test") as ctx:
            ctx.advance("step 1")
            ctx.advance("step 2")
            ctx.advance("step 3")
        self.assertEqual(stderr_capture.getvalue(), "")

    def test_json_mode_suppresses_progress(self):
        fmt = OutputFormatter(OutputMode.JSON)
        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture), fmt.progress_context(3, "test") as ctx:
            ctx.advance("step 1")
            ctx.advance("step 2")
            ctx.advance("step 3")
        self.assertEqual(stderr_capture.getvalue(), "")


class TestProgressStdout(unittest.TestCase):
    """REQ-0.0.4-09-04 / REQ-0.0.4-09-05: Progress never writes to stdout."""

    def test_progress_never_writes_stdout(self):
        """progress_context must never write to stdout in any mode."""
        for mode in OutputMode:
            fmt = OutputFormatter(mode)
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            with (
                patch("sys.stdout", stdout_capture),
                patch("sys.stderr", stderr_capture),
                fmt.progress_context(2, "test") as ctx,
            ):
                ctx.advance("a")
                ctx.advance("b")
            self.assertEqual(
                stdout_capture.getvalue(),
                "",
                f"stdout should be empty in {mode} mode",
            )


class TestProgressNonTTY(unittest.TestCase):
    """REQ-0.0.4-09-06: Non-TTY gets status lines to stderr."""

    def test_non_tty_prints_status_lines(self):
        """Non-TTY stderr gets [step/total] lines instead of progress bars."""
        fmt = OutputFormatter(OutputMode.HUMAN)
        stderr_capture = io.StringIO()
        # Force non-TTY by using StringIO for stderr (isatty() returns False)
        with patch("sys.stderr", stderr_capture), fmt.progress_context(3, "checks") as ctx:
            ctx.advance("Lint")
            ctx.advance("Test")
            ctx.advance("Build")
        output = stderr_capture.getvalue()
        self.assertIn("[1/3] Lint", output)
        self.assertIn("[2/3] Test", output)
        self.assertIn("[3/3] Build", output)


class TestProgressKnownSteps(unittest.TestCase):
    """REQ-0.0.4-09-08: Progress uses known step counts."""

    def test_progress_context_requires_total(self):
        """progress_context requires an integer total parameter."""
        fmt = OutputFormatter()
        ctx = fmt.progress_context(5, "work")
        self.assertEqual(ctx._total, 5)

    def test_advance_increments_count(self):
        """advance() tracks step count internally."""
        fmt = OutputFormatter(OutputMode.QUIET)
        with fmt.progress_context(3, "test") as ctx:
            self.assertEqual(ctx._current, 0)
            ctx.advance("a")
            self.assertEqual(ctx._current, 1)
            ctx.advance("b")
            self.assertEqual(ctx._current, 2)


class TestCheckIntegration(unittest.TestCase):
    """REQ-0.0.4-09-01: gz check uses progress_context."""

    def test_check_function_advances_progress_for_each_step(self):
        """check() advances the formatter progress context for each quality step."""
        from gzkit.commands import quality

        _FormatterSpy.instances.clear()
        steps = [
            ("Lint", lambda _: _result(True)),
            ("Test", lambda _: _result(True)),
        ]

        with (
            patch("gzkit.cli.formatters.OutputFormatter", _FormatterSpy),
            patch.object(quality, "console", SimpleNamespace(print=lambda *_args, **_kwargs: None)),
            patch.object(quality, "get_project_root", return_value=Path(".")),
            patch.object(quality, "_build_check_steps", return_value=steps),
            patch(
                "gzkit.quality.run_drift_advisory",
                return_value=SimpleNamespace(has_drift=False),
            ),
            patch("gzkit.flags.registry.load_registry", side_effect=RuntimeError("skip flags")),
        ):
            quality.check()

        formatter = _FormatterSpy.instances[-1]
        self.assertIsNotNone(formatter.progress)
        self.assertEqual(formatter.progress.total, 2)
        self.assertEqual(formatter.progress.label, "Running quality checks")
        self.assertEqual(formatter.progress.advanced, ["Lint", "Test"])


if __name__ == "__main__":
    unittest.main()
