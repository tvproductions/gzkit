"""Tests for light TUI affordances (OBPI-0.0.34-05).

Covers:
  REQ-0.0.34-05-01 — `gz content render <id>` on TTY → Rich status line on stderr
  REQ-0.0.34-05-02 — `gz content list` on TTY → Rich table; piped → ANSI-free plain text
  REQ-0.0.34-05-03 — `gz content show <id>` on TTY → Rich panel; --plain suppresses
  REQ-0.0.34-05-04 — No Textual imports; no Textual top-level dep
  REQ-0.0.34-05-05 — `gz content --help` shows no new subcommand added
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.traceability import covers


class TestStatusLineTUI(unittest.TestCase):
    """Status line TUI tests (REQ-0.0.34-05-01)."""

    @covers("REQ-0.0.34-05-01")
    def test_render_tty_emits_status_to_stderr(self) -> None:
        """When stdout.isatty() is True, render_status_line writes to stderr."""
        # Arrange: capture stderr
        import io

        from gzkit.content.tui.status import render_status_line

        stderr_capture = io.StringIO()

        # Act: call render_status_line with mocked stderr
        with patch("sys.stderr", stderr_capture):
            render_status_line(
                operation="rendered",
                source="test.md",
                result="markdown",
                byte_count=1024,
            )

        # Assert: stderr contains expected content
        output = stderr_capture.getvalue()
        self.assertIn("rendered", output.lower())
        self.assertIn("test.md", output)
        self.assertIn("markdown", output)

    @covers("REQ-0.0.34-05-01")
    def test_render_status_line_formats_byte_count(self) -> None:
        """render_status_line formats byte count with units (B, KiB, etc)."""
        import io

        from gzkit.content.tui.status import render_status_line

        stderr_capture = io.StringIO()

        with patch("sys.stderr", stderr_capture):
            render_status_line(
                operation="rendered",
                source="large.md",
                result="markdown",
                byte_count=2560,  # 2.5 KiB
            )

        output = stderr_capture.getvalue()
        # Should contain a size representation (KiB or B)
        self.assertRegex(output, r"(\d+\.?\d*\s*(B|KiB|MiB|GiB)|size)")


class TestTableRendererTUI(unittest.TestCase):
    """Rich table renderer tests (REQ-0.0.34-05-02)."""

    @covers("REQ-0.0.34-05-02")
    def test_list_tty_uses_rich_table(self) -> None:
        """When stdout.isatty() is True, list renders a Rich table."""
        import io

        from gzkit.content.tui.tables import render_content_table

        stdout_capture = io.StringIO()

        rows = [
            {"type": "Skill", "description": "A skill definition"},
            {"type": "Rule", "description": "A governance rule"},
        ]

        with patch("sys.stdout", stdout_capture):
            render_content_table(rows)

        output = stdout_capture.getvalue()
        # Rich output typically contains ANSI escape codes or box-drawing chars
        # We check for either ANSI codes (ESC sequences) or readable text
        self.assertGreater(len(output), 0)
        # Either contains ANSI codes or box-drawing characters
        has_ansi = "\x1b[" in output or "\033[" in output
        has_box = "┌" in output or "─" in output or "│" in output
        self.assertTrue(has_ansi or has_box, "Expected Rich-formatted output")

    @covers("REQ-0.0.34-05-02")
    def test_list_non_tty_produces_no_ansi(self) -> None:
        """When stdout.isatty() is False, list produces plain text with no ANSI codes."""
        import io

        from gzkit.commands.content.list import content_list_cmd

        stdout_capture = io.StringIO()

        with patch("sys.stdout", stdout_capture), patch("sys.stdout.isatty", return_value=False):
            content_list_cmd(type_filter=None, as_json=False)

        output = stdout_capture.getvalue()
        # No ANSI escape sequences
        self.assertNotRegex(output, r"\x1b\[", "Output should not contain ANSI codes")
        self.assertNotRegex(output, r"\033\[", "Output should not contain ESC codes")
        # Should contain expected content
        self.assertIn("Type", output)
        self.assertIn("Description", output)


class TestPanelRendererTUI(unittest.TestCase):
    """Rich panel renderer tests (REQ-0.0.34-05-03)."""

    @covers("REQ-0.0.34-05-03")
    def test_show_tty_uses_rich_panel(self) -> None:
        """When stdout.isatty() is True, show renders a Rich panel."""
        import io

        from gzkit.content.tui.panels import render_content_panel

        stdout_capture = io.StringIO()

        with patch("sys.stdout", stdout_capture):
            render_content_panel(title="Test Content", body="This is test content")

        output = stdout_capture.getvalue()
        # Rich panel output contains box-drawing or ANSI codes
        has_ansi = "\x1b[" in output or "\033[" in output
        has_box = "┌" in output or "─" in output or "│" in output
        self.assertTrue(has_ansi or has_box, "Expected Rich panel formatting")

    @covers("REQ-0.0.34-05-03")
    def test_plain_flag_suppresses_rich_on_tty(self) -> None:
        """Even when isatty() is True, --plain flag suppresses Rich formatting."""
        import io
        import tempfile

        from gzkit.commands.content.show import content_show_cmd
        from gzkit.content.models import Rule
        from gzkit.content.render import render

        # Use canonical Rule rendered format (not raw YAML frontmatter)
        model = Rule(title="Test Rule", version="1.0.0", paths=[], body=[])
        canonical_content = render(model, "claude").decode("utf-8")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(canonical_content)
            tmp_path = tmp.name

        try:
            stdout_capture = io.StringIO()

            with patch("sys.stdout", stdout_capture), patch("sys.stdout.isatty", return_value=True):
                # plain=True suppresses Rich even on a TTY
                content_show_cmd(file=tmp_path, as_type="Rule", as_json=False, plain=True)

            output = stdout_capture.getvalue()
            # plain=True must suppress ANSI codes
            self.assertNotRegex(output, r"\x1b\[", "plain=True should suppress ANSI codes")
            self.assertNotRegex(output, r"\033\[", "plain=True should suppress ESC codes")
            # Content should still be present
            self.assertGreater(len(output), 0)
        finally:
            Path(tmp_path).unlink()


class TestTextualAbsence(unittest.TestCase):
    """Textual dependency tests (REQ-0.0.34-05-04)."""

    @covers("REQ-0.0.34-05-04")
    def test_no_textual_import_in_src(self) -> None:
        """No source files import textual or Textual."""
        from pathlib import Path

        # Use Python-based check (grep not guaranteed on Windows)
        # Resolve project root from test file location
        test_file = Path(__file__)
        # tests/content/test_tui_affordances.py -> project_root
        project_root = test_file.parent.parent.parent
        src_root = project_root / "src"

        for py_file in src_root.glob("**/*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import textual", content, f"Found in {py_file}")
            self.assertNotIn("from textual", content, f"Found in {py_file}")

    @covers("REQ-0.0.34-05-04")
    def test_no_textual_import_in_tests(self) -> None:
        """No test files import textual or Textual (excluding test file docstrings)."""
        import ast
        from pathlib import Path

        # Use Python-based check with AST to avoid docstring false positives
        test_file = Path(__file__)
        project_root = test_file.parent.parent.parent
        tests_root = project_root / "tests"

        for py_file in tests_root.glob("**/*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertFalse(
                                alias.name.startswith("textual"),
                                f"Found textual import in {py_file}",
                            )
                    elif isinstance(node, ast.ImportFrom):
                        self.assertFalse(
                            node.module and node.module.startswith("textual"),
                            f"Found textual import in {py_file}",
                        )
            except SyntaxError:
                # Skip files with syntax errors
                pass

    @covers("REQ-0.0.34-05-04")
    def test_no_textual_top_level_dep(self) -> None:
        """pyproject.toml does not list textual as a top-level dependency."""
        from pathlib import Path

        test_file = Path(__file__)
        project_root = test_file.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"
        content = pyproject_path.read_text(encoding="utf-8")

        # Look for "textual" as a dependency (not as a comment)
        # Fail-safe: check the [project] dependencies section
        lines = content.split("\n")
        in_dependencies = False
        for line in lines:
            if "[project]" in line or "dependencies" in line:
                in_dependencies = True
            if in_dependencies and "textual" in line.lower() and not line.strip().startswith("#"):
                self.fail(f"Found textual dependency in pyproject.toml: {line}")


class TestCommandSurfaceUnchanged(unittest.TestCase):
    """Command surface tests (REQ-0.0.34-05-05)."""

    @covers("REQ-0.0.34-05-05")
    def test_no_new_subcommands_added(self) -> None:
        """No new subcommand is added to `gz content`; allowed subcommands unchanged.

        REQ-0.0.34-05-05 fenced the OBPI-0.0.34-05 TUI surface against unplanned
        subcommand growth. `remember` was added intentionally by OBPI-0.0.37-19
        (corpus capture write path); the fence is updated to admit it, not relaxed.
        """
        # Expected subcommands for `gz content` (remember added by OBPI-0.0.37-19;
        # compose by OBPI-0.0.37-21; commit by OBPI-0.0.37-22; advise-rendition by
        # OBPI-0.0.37-24)
        expected_subcommands = {
            "import",
            "list",
            "show",
            "render",
            "edit",
            "remember",
            "compose",
            "commit",
            "advise-rendition",
        }

        # Run `gz content --help` via uv run (gzkit has no __main__.py)
        result = subprocess.run(
            ["uv", "run", "gz", "content", "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent),
        )

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, f"Help command failed: {output}")

        # Extract subcommand names from help text
        # Pattern: "  {subcommand}" or similar
        found_subcommands = set()
        for match in re.finditer(r"\{([^}]+)\}", output):
            candidates = match.group(1).split(",")
            for candidate in candidates:
                candidate = candidate.strip()
                if candidate and not candidate.startswith("-"):
                    found_subcommands.add(candidate)

        # Alternative: check for explicit subcommand list in positional args
        # or check the parser structure if available
        self.assertTrue(
            len(found_subcommands) > 0,
            "Could not extract subcommands from help; help output: " + output[:500],
        )

        # The implementation should show subcommands that match expected set
        # We are not enforcing exact equality here since parser help formatting varies
        # Just verify that no NEW subcommands beyond the expected set are present
        unexpected = found_subcommands - expected_subcommands
        self.assertEqual(
            unexpected,
            set(),
            f"Found unexpected new subcommands: {unexpected}. "
            f"This OBPI (REQ-05) must not add new subcommands.",
        )


if __name__ == "__main__":
    unittest.main()
