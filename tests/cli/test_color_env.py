"""Color-decision env semantics honor NO_COLOR / FORCE_COLOR conventions.

GHI #663 part (1): both console-construction sites decided colour by *presence*
(``os.environ.get("FORCE_COLOR") is not None``), so ``FORCE_COLOR=0`` — the
conventional way to turn forcing OFF — evaluated truthy and forced colour ON.
``NO_COLOR`` never suppressed ``force_terminal``, so Rich still emitted bold SGR
codes into non-TTY captures even with colour nominally disabled.

Conventions asserted here:
  * https://no-color.org — ``NO_COLOR`` set to a non-empty value disables colour.
  * ``FORCE_COLOR=0`` / ``false`` disables forcing; ``1``/``2``/``3``/``true``
    enables it.

Tests pass the environment in explicitly rather than mutating ``os.environ``,
per `.claude/rules/hexagonal-architecture.md` § operative rule 4 ("take a
parameter for any external object you wish to access").
"""

from __future__ import annotations

import unittest

from gzkit.color_env import should_disable_color, should_force_terminal


class TestForceColorValueSemantics(unittest.TestCase):
    """``FORCE_COLOR`` is read by value, never by mere presence."""

    def test_force_color_zero_does_not_force(self) -> None:
        """``FORCE_COLOR=0`` is the conventional OFF switch.

        The pre-fix presence check made ``"0" is not None`` → ``True``, so the
        documented way to disable forcing turned it on instead.
        """
        self.assertFalse(should_force_terminal({"FORCE_COLOR": "0"}))

    def test_force_color_false_does_not_force(self) -> None:
        """``false`` (any case) is treated as OFF alongside ``0``."""
        for value in ("false", "FALSE", "False"):
            with self.subTest(value=value):
                self.assertFalse(should_force_terminal({"FORCE_COLOR": value}))

    def test_force_color_levels_do_force(self) -> None:
        """``1``/``2``/``3``/``true`` are the conventional ON values."""
        for value in ("1", "2", "3", "true", "TRUE"):
            with self.subTest(value=value):
                self.assertTrue(should_force_terminal({"FORCE_COLOR": value}))

    def test_absent_force_color_does_not_force(self) -> None:
        """No ``FORCE_COLOR`` → Rich auto-detects; never forced."""
        self.assertFalse(should_force_terminal({}))


class TestNoColorPrecedence(unittest.TestCase):
    """``NO_COLOR`` suppresses forcing, not merely the colour codes."""

    def test_no_color_beats_truthy_force_color(self) -> None:
        """``NO_COLOR`` wins over ``FORCE_COLOR=3``.

        This is the load-bearing case: Rich's ``no_color=True`` alone still
        emits *bold* SGR when ``force_terminal=True``, so an operator setting
        ``NO_COLOR`` still got escape codes into captured output.
        """
        env = {"NO_COLOR": "1", "FORCE_COLOR": "3"}
        self.assertTrue(should_disable_color(env))
        self.assertFalse(should_force_terminal(env))

    def test_empty_no_color_is_not_set(self) -> None:
        """Per no-color.org, ``NO_COLOR`` must be non-empty to apply."""
        self.assertFalse(should_disable_color({"NO_COLOR": ""}))

    def test_absent_no_color_does_not_disable(self) -> None:
        self.assertFalse(should_disable_color({}))


class TestFormatterHonorsConventions(unittest.TestCase):
    """The end-to-end consumer renders plain text when the env says so."""

    def _render(self, env: dict[str, str]) -> str:
        from gzkit.cli.formatters import OutputFormatter, OutputMode

        formatter = OutputFormatter(mode=OutputMode.HUMAN, env=env)
        with formatter.console.capture() as capture:
            formatter.console.print("[red]hello[/red]")
        return capture.get()

    def test_force_color_zero_yields_no_ansi(self) -> None:
        """``FORCE_COLOR=0`` must produce clean text, not escape codes."""
        self.assertNotIn("\x1b[", self._render({"FORCE_COLOR": "0"}))

    def test_no_color_yields_no_ansi_even_under_force_color(self) -> None:
        """``NO_COLOR`` must win end-to-end, bold included."""
        rendered = self._render({"NO_COLOR": "1", "FORCE_COLOR": "3"})
        self.assertNotIn("\x1b[", rendered)


if __name__ == "__main__":
    unittest.main()
