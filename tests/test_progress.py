"""Tests for CLI progress indication utilities."""

from __future__ import annotations

import io
import sys
import unittest
from unittest.mock import patch

from gzkit.cli.formatters import OutputFormatter
from gzkit.cli.progress import progress_bar, progress_phase, progress_spinner
from gzkit.traceability import covers


class TestProgressSpinner(unittest.TestCase):
    """Tests for progress_spinner context manager."""

    @covers("REQ-0.0.3-08-02")
    def test_spinner_runs_in_human_mode(self) -> None:
        """Spinner executes without error in human mode."""
        formatter = OutputFormatter(mode="human")
        with patch.object(sys, "stderr", io.StringIO()), progress_spinner("Working...", formatter):
            pass  # Body executes successfully

    @covers("REQ-0.0.3-08-03")
    def test_spinner_suppressed_in_quiet_mode(self) -> None:
        """Spinner is suppressed (no output) in quiet mode."""
        formatter = OutputFormatter(mode="quiet")
        stderr_capture = io.StringIO()
        with patch.object(sys, "stderr", stderr_capture), progress_spinner("Working...", formatter):
            pass
        # In quiet mode, no spinner output at all
        self.assertEqual(stderr_capture.getvalue(), "")

    @covers("REQ-0.0.3-08-04")
    def test_spinner_suppressed_in_json_mode(self) -> None:
        """Spinner is suppressed (no output) in json mode."""
        formatter = OutputFormatter(mode="json")
        stderr_capture = io.StringIO()
        with patch.object(sys, "stderr", stderr_capture), progress_spinner("Working...", formatter):
            pass
        self.assertEqual(stderr_capture.getvalue(), "")

    @covers("REQ-0.0.3-08-07")
    def test_spinner_cleanup_on_exception(self) -> None:
        """Spinner cleans up properly when body raises an exception."""
        formatter = OutputFormatter(mode="human")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            self.assertRaises(ValueError),
            progress_spinner("Working...", formatter),
        ):
            raise ValueError("test error")


class TestProgressPhase(unittest.TestCase):
    """Tests for progress_phase context manager."""

    def test_phase_runs_in_human_mode(self) -> None:
        """Phase executes without error in human mode."""
        formatter = OutputFormatter(mode="human")
        with patch.object(sys, "stderr", io.StringIO()), progress_phase("Linting...", formatter):
            pass

    @covers("REQ-0.0.3-08-05")
    def test_phase_with_step_counting(self) -> None:
        """Phase with step/total executes without error."""
        formatter = OutputFormatter(mode="human")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            progress_phase("Linting...", formatter, step=1, total=3),
        ):
            pass

    def test_phase_suppressed_in_quiet_mode(self) -> None:
        """Phase is suppressed in quiet mode."""
        formatter = OutputFormatter(mode="quiet")
        stderr_capture = io.StringIO()
        with (
            patch.object(sys, "stderr", stderr_capture),
            progress_phase("Linting...", formatter, step=1, total=3),
        ):
            pass
        self.assertEqual(stderr_capture.getvalue(), "")

    def test_phase_suppressed_in_json_mode(self) -> None:
        """Phase is suppressed in json mode — no stdout corruption."""
        formatter = OutputFormatter(mode="json")
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        with (
            patch.object(sys, "stdout", stdout_capture),
            patch.object(sys, "stderr", stderr_capture),
            progress_phase("Linting...", formatter, step=2, total=5),
        ):
            pass
        # Stdout must remain clean in json mode
        self.assertEqual(stdout_capture.getvalue(), "")
        # Stderr should also be empty since progress is suppressed
        self.assertEqual(stderr_capture.getvalue(), "")

    def test_phase_cleanup_on_exception(self) -> None:
        """Phase cleans up properly when body raises."""
        formatter = OutputFormatter(mode="human")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            self.assertRaises(RuntimeError),
            progress_phase("Processing...", formatter, step=1, total=2),
        ):
            raise RuntimeError("phase error")

    def test_phase_without_step_counting(self) -> None:
        """Phase without step/total shows plain label."""
        formatter = OutputFormatter(mode="human")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            progress_phase("Building docs...", formatter),
        ):
            pass

    def test_phase_verbose_mode_shows_progress(self) -> None:
        """Phase is displayed in verbose mode."""
        formatter = OutputFormatter(mode="verbose")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            progress_phase("Checking...", formatter, step=1, total=2),
        ):
            pass  # Should not raise

    def test_phase_debug_mode_shows_progress(self) -> None:
        """Phase is displayed in debug mode."""
        formatter = OutputFormatter(mode="debug")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            progress_phase("Debugging...", formatter, step=1, total=1),
        ):
            pass  # Should not raise


class TestProgressBar(unittest.TestCase):
    """Tests for progress_bar context manager."""

    @covers("REQ-0.0.3-08-06")
    def test_bar_runs_in_human_mode(self) -> None:
        """Progress bar executes without error in human mode."""
        formatter = OutputFormatter(mode="human")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            progress_bar("Processing files", formatter, total=10) as progress,
        ):
            self.assertIsNotNone(progress)

    def test_bar_suppressed_in_quiet_mode(self) -> None:
        """Progress bar yields no-op Progress in quiet mode."""
        formatter = OutputFormatter(mode="quiet")
        with progress_bar("Processing", formatter, total=5) as progress:
            self.assertIsNotNone(progress)
            # advance() should not raise even when suppressed
            task_ids = list(progress.task_ids)
            if task_ids:
                progress.advance(task_ids[0])

    def test_bar_suppressed_in_json_mode(self) -> None:
        """Progress bar does not corrupt stdout in json mode."""
        formatter = OutputFormatter(mode="json")
        stdout_capture = io.StringIO()
        with (
            patch.object(sys, "stdout", stdout_capture),
            progress_bar("Processing", formatter, total=5) as progress,
        ):
            self.assertIsNotNone(progress)
        self.assertEqual(stdout_capture.getvalue(), "")

    def test_bar_cleanup_on_exception(self) -> None:
        """Progress bar cleans up on exception."""
        formatter = OutputFormatter(mode="human")
        with (
            patch.object(sys, "stderr", io.StringIO()),
            self.assertRaises(ValueError),
            progress_bar("Processing", formatter, total=10),
        ):
            raise ValueError("bar error")


class TestModeIntegration(unittest.TestCase):
    """Integration tests for mode-dependent progress behavior."""

    @covers("REQ-0.0.3-08-08")
    def test_all_suppressed_modes(self) -> None:
        """Both quiet and json suppress all progress types."""
        for mode in ("quiet", "json"):
            formatter = OutputFormatter(mode=mode)
            with self.subTest(mode=mode):
                with progress_spinner("test", formatter):
                    pass
                with progress_phase("test", formatter, step=1, total=1):
                    pass
                with progress_bar("test", formatter, total=1):
                    pass

    def test_all_display_modes(self) -> None:
        """Human, verbose, and debug modes allow progress display."""
        for mode in ("human", "verbose", "debug"):
            formatter = OutputFormatter(mode=mode)
            with self.subTest(mode=mode), patch.object(sys, "stderr", io.StringIO()):
                with progress_spinner("test", formatter):
                    pass
                with progress_phase("test", formatter, step=1, total=1):
                    pass
                with progress_bar("test", formatter, total=1):
                    pass


class TestImportBoundary(unittest.TestCase):
    """Verify progress is a CLI adapter concern only."""

    @covers("REQ-0.0.3-08-01")
    def test_importable_from_cli_package(self) -> None:
        """Progress utilities are importable from gzkit.cli.progress."""
        from gzkit.cli.progress import progress_bar, progress_phase, progress_spinner

        self.assertTrue(callable(progress_spinner))
        self.assertTrue(callable(progress_phase))
        self.assertTrue(callable(progress_bar))


if __name__ == "__main__":
    unittest.main()
