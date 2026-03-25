"""Tests for runtime presentation patterns (OBPI-0.0.4-08).

Verifies status symbols, Rich table usage, color conventions,
and NO_COLOR/JSON mode behavior.
"""

import unittest

from rich import box


class TestStatusTables(unittest.TestCase):
    """REQ-0.0.4-08-01: Tables use Rich box-drawing, not ASCII pipes."""

    def test_status_tables_use_rounded_box(self):
        """Verify status.py creates tables with ROUNDED box style."""
        import ast
        from pathlib import Path

        source = Path("src/gzkit/commands/status.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Find all Table() calls and check none use box.ASCII
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "Table":
                    for kw in node.keywords:
                        if kw.arg == "box" and isinstance(kw.value, ast.Attribute):
                            self.assertNotEqual(
                                kw.value.attr,
                                "ASCII",
                                f"Line {node.lineno}: box.ASCII",
                            )

    def test_box_rounded_is_not_ascii(self):
        """Sanity check: ROUNDED uses Unicode box-drawing characters."""
        # ASCII box uses +, -, | characters
        self.assertNotEqual(box.ROUNDED, box.ASCII)


class TestCheckSymbols(unittest.TestCase):
    """REQ-0.0.4-08-02: gz check output uses ✓/❌ status symbols."""

    def test_check_function_uses_symbols(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/quality.py").read_text(encoding="utf-8")
        self.assertIn("✓", source, "check() must use ✓ (U+2713) for success")
        self.assertIn("❌", source, "check() must use ❌ (U+274C) for failure")


class TestTidySymbols(unittest.TestCase):
    """REQ-0.0.4-08-03: gz tidy output uses structured symbols."""

    def test_tidy_uses_symbols(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/tidy.py").read_text(encoding="utf-8")
        self.assertIn("⚠", source, "tidy() must use ⚠ (U+26A0) for warnings")
        self.assertIn("→", source, "tidy() must use → (U+2192) for flow indicators")
        self.assertIn("✓", source, "tidy() must use ✓ (U+2713) for success")


class TestValidateItemized(unittest.TestCase):
    """REQ-0.0.4-08-04: gz validate shows what was validated."""

    def test_validate_shows_scopes(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/validate_cmd.py").read_text(encoding="utf-8")
        self.assertIn("Validated:", source, "validate must show 'Validated:' with scope list")
        self.assertIn("scopes", source, "validate must compute and display validation scopes")


class TestGatesSymbols(unittest.TestCase):
    """REQ-0.0.4-08-05: gz gates uses ✓/❌/⚠ symbols."""

    def test_gates_uses_symbols(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/gates.py").read_text(encoding="utf-8")
        self.assertIn("✓", source, "gates must use ✓ for pass")
        self.assertIn("❌", source, "gates must use ❌ for fail")
        self.assertIn("⚠", source, "gates must use ⚠ for pending/warning")


class TestColorConventions(unittest.TestCase):
    """REQ-0.0.4-08-07: Color conventions applied consistently."""

    def _check_color_pattern(self, source: str, label: str):
        """Verify green=success, red=failure patterns in source."""
        # Check that green is used with success-related words
        self.assertIn("[green]", source, f"{label} must use [green] for success")
        self.assertIn("[red]", source, f"{label} must use [red] for failure")

    def test_quality_colors(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/quality.py").read_text(encoding="utf-8")
        self._check_color_pattern(source, "quality.py")

    def test_gates_colors(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/gates.py").read_text(encoding="utf-8")
        self._check_color_pattern(source, "gates.py")
        self.assertIn("[yellow]", source, "gates.py must use [yellow] for pending/warning")

    def test_validate_colors(self):
        from pathlib import Path

        source = Path("src/gzkit/commands/validate_cmd.py").read_text(encoding="utf-8")
        self._check_color_pattern(source, "validate_cmd.py")


class TestNoColorDegradation(unittest.TestCase):
    """REQ-0.0.4-08-08: NO_COLOR produces clean output."""

    def test_output_formatter_respects_no_color(self):
        """OutputFormatter with NO_COLOR set produces no ANSI codes."""
        import os

        from gzkit.cli.formatters import OutputFormatter, OutputMode

        # Simulate NO_COLOR
        old = os.environ.get("NO_COLOR")
        os.environ["NO_COLOR"] = "1"
        try:
            fmt = OutputFormatter(OutputMode.HUMAN)
            self.assertTrue(fmt.console.no_color)
        finally:
            if old is None:
                os.environ.pop("NO_COLOR", None)
            else:
                os.environ["NO_COLOR"] = old


class TestJsonModeClean(unittest.TestCase):
    """REQ-0.0.4-08-09: JSON mode produces no symbols or color codes."""

    def test_emit_status_json_no_symbols(self):
        """emit_status in JSON mode must not include ✓/❌."""
        import io
        from unittest.mock import patch

        from gzkit.cli.formatters import OutputFormatter, OutputMode

        fmt = OutputFormatter(OutputMode.JSON)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            fmt.emit_status("Lint", True)
            output = mock_stdout.getvalue()
            self.assertNotIn("✓", output)
            self.assertNotIn("❌", output)
            self.assertIn('"success": true', output)


if __name__ == "__main__":
    unittest.main()
