"""Tests for runtime presentation patterns (OBPI-0.0.4-08).

Verifies status symbols, Rich table usage, color conventions,
and NO_COLOR/JSON mode behavior.
"""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rich import box
from rich.table import Table

from gzkit.quality import QualityResult
from gzkit.traceability import covers


class _CaptureConsole:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def print(self, *values: object, **_: object) -> None:
        self.messages.append(" ".join(str(value) for value in values))

    @property
    def text(self) -> str:
        return "\n".join(self.messages)


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[object] = []

    def append(self, event: object) -> None:
        self.events.append(event)


def _result(success: bool, returncode: int = 0) -> QualityResult:
    """Build a faithful step result.

    Previously a partial ``SimpleNamespace``. ``check()`` consumes more of
    ``QualityResult`` than the fields any one assertion touches — the advisory
    renderer reads ``.command`` and the captured streams (GHI #713) — so a stub
    modelling only today's fields breaks whenever the consumer grows. Using the
    real model makes that class of drift impossible.
    """
    return QualityResult(
        success=success,
        command="uv run gz stub",
        stdout="",
        stderr="",
        returncode=returncode,
    )


class _SilentProgress:
    def __enter__(self) -> "_SilentProgress":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def advance(self, _step: str) -> None:
        return None


class _SilentFormatter:
    def progress_context(self, _total: int, _label: str) -> _SilentProgress:
        return _SilentProgress()


class TestStatusTables(unittest.TestCase):
    """REQ-0.0.4-08-01: Tables use Rich box-drawing, not ASCII pipes."""

    @covers("REQ-0.0.4-08-01")
    def test_status_tables_use_rounded_box(self):
        """Verify status table rendering constructs Rich tables with ROUNDED box style."""
        from gzkit.commands import status_render

        printed: list[object] = []

        with patch.object(
            status_render.console,
            "print",
            side_effect=lambda value="", *_, **__: printed.append(value),
        ):
            status_render._render_adr_table(
                "Foundation ADRs",
                [
                    (
                        "ADR-0.0.1",
                        {
                            "lane": "lite",
                            "gates": {"2": "pass"},
                            "obpi_summary": {
                                "total": 0,
                                "completed": 0,
                                "unit_status": "unscoped",
                            },
                            "lifecycle_status": "Pending",
                        },
                    )
                ],
                "lite",
            )

        tables = [value for value in printed if isinstance(value, Table)]
        self.assertGreaterEqual(len(tables), 1)
        self.assertIs(tables[0].box, box.ROUNDED)

    def test_box_rounded_is_not_ascii(self):
        """Sanity check: ROUNDED uses Unicode box-drawing characters."""
        # ASCII box uses +, -, | characters
        self.assertNotEqual(box.ROUNDED, box.ASCII)


class TestCheckSymbols(unittest.TestCase):
    """REQ-0.0.4-08-02: gz check output uses check/cross status symbols."""

    def setUp(self) -> None:
        """Root `check()` at a scratch dir, never the real repo.

        `check()` writes `.gzkit/cache/check-verified.json` on a full-scope pass
        -- the receipt the pre-push gate reuses. These cases are only safe today
        because one stubbed step FAILS, which is incidental isolation: making the
        stubs pass would silently mint a verification receipt for the developer's
        staged tree (the GHI #949 defect, found in a sibling module).
        """
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._root = Path(self._tmp.name)

    @covers("REQ-0.0.4-08-02")
    def test_check_output_uses_symbols(self):
        from gzkit.commands import quality

        console = _CaptureConsole()
        steps = [
            ("Passing step", lambda _: _result(True)),
            ("Failing step", lambda _: _result(False, 1)),
        ]

        with (
            patch.object(quality, "console", console),
            patch.object(quality, "get_project_root", return_value=self._root),
            patch.object(quality, "_build_check_steps", return_value=steps),
            patch("gzkit.cli.formatters.OutputFormatter", _SilentFormatter),
            patch(
                "gzkit.quality.run_drift_advisory",
                return_value=SimpleNamespace(has_drift=False),
            ),
            patch("gzkit.flags.registry.load_registry", side_effect=RuntimeError("skip flags")),
            self.assertRaises(SystemExit),
        ):
            quality.check()

        self.assertIn("\u2713", console.text)
        self.assertIn("\u274c", console.text)


class TestTidySymbols(unittest.TestCase):
    """REQ-0.0.4-08-03: gz tidy output uses structured symbols."""

    @covers("REQ-0.0.4-08-03")
    def test_tidy_output_uses_warning_flow_and_success_symbols(self):
        from gzkit.commands import tidy

        config = SimpleNamespace(paths=SimpleNamespace(ledger=".gzkit/ledger.jsonl"))
        warning_console = _CaptureConsole()
        clean_console = _CaptureConsole()

        with (
            patch.object(tidy, "console", warning_console),
            patch.object(tidy, "ensure_initialized", return_value=config),
            patch.object(tidy, "get_project_root", return_value=Path(".")),
            patch.object(
                tidy,
                "validate_all",
                return_value=SimpleNamespace(
                    errors=[SimpleNamespace(type="demo", message="broken fixture")]
                ),
            ),
            patch.object(
                tidy,
                "Ledger",
                return_value=SimpleNamespace(
                    get_artifact_graph=lambda: {},
                    get_pending_attestations=lambda: [],
                ),
            ),
        ):
            tidy.tidy(check_only=False, fix=True, dry_run=True)

        self.assertIn("\u26a0", warning_console.text)
        self.assertIn("\u2192", warning_console.text)

        with (
            patch.object(tidy, "console", clean_console),
            patch.object(tidy, "ensure_initialized", return_value=config),
            patch.object(tidy, "get_project_root", return_value=Path(".")),
            patch.object(tidy, "validate_all", return_value=SimpleNamespace(errors=[])),
            patch.object(
                tidy,
                "Ledger",
                return_value=SimpleNamespace(
                    get_artifact_graph=lambda: {},
                    get_pending_attestations=lambda: [],
                ),
            ),
        ):
            tidy.tidy(check_only=True, fix=False, dry_run=False)

        self.assertIn("\u2713", clean_console.text)


class TestValidateItemized(unittest.TestCase):
    """REQ-0.0.4-08-04: gz validate shows what was validated."""

    @covers("REQ-0.0.4-08-04")
    def test_validate_output_shows_resolved_scopes(self):
        from gzkit.commands import validate_cmd

        console = _CaptureConsole()
        with (
            patch.object(validate_cmd, "console", console),
            patch.object(validate_cmd, "get_project_root", return_value=Path(".")),
            patch.object(validate_cmd, "_dispatch_early_return_scopes", return_value=False),
            patch.object(validate_cmd, "_collect_errors", return_value=[]),
        ):
            validate_cmd.validate(True, False, False, False, False, False)

        self.assertIn("Validated:", console.text)
        self.assertIn("manifest", console.text)
        self.assertIn("1 scopes", console.text)


class TestGatesSymbols(unittest.TestCase):
    """REQ-0.0.4-08-05: gz gates uses check/cross/warning symbols."""

    @covers("REQ-0.0.4-08-05")
    def test_gates_output_uses_pass_fail_and_warning_symbols(self):
        from gzkit.commands import gates

        console = _CaptureConsole()
        cli = SimpleNamespace(run_command=lambda *_args, **_kwargs: _result(True))
        with (
            patch.object(gates, "console", console),
            patch.object(gates, "_cli_main", return_value=cli),
        ):
            self.assertTrue(gates._run_gate_2(Path("."), _FakeLedger(), "ADR-0.1.0", "test"))
            gates._run_gate_5()

        failing_console = _CaptureConsole()
        failing_cli = SimpleNamespace(run_command=lambda *_args, **_kwargs: _result(False, 1))
        with (
            patch.object(gates, "console", failing_console),
            patch.object(gates, "_cli_main", return_value=failing_cli),
        ):
            self.assertFalse(gates._run_gate_2(Path("."), _FakeLedger(), "ADR-0.1.0", "test"))

        self.assertIn("\u2713", console.text)
        self.assertIn("\u26a0", console.text)
        self.assertIn("\u274c", failing_console.text)


class TestBlockersPrefix(unittest.TestCase):
    """REQ-0.0.4-08-06: All error output uses BLOCKERS: prefix."""

    @covers("REQ-0.0.4-08-06")
    def test_parser_error_uses_blockers_prefix(self):
        """StableArgumentParser.error() emits BLOCKERS: prefix."""
        import io
        import sys

        from gzkit.cli.parser import StableArgumentParser

        parser = StableArgumentParser(prog="gz")
        captured = io.StringIO()
        old_stderr = sys.stderr
        try:
            sys.stderr = captured
            with self.assertRaises(SystemExit):
                parser.error("test error")
        finally:
            sys.stderr = old_stderr
        self.assertIn("BLOCKERS:", captured.getvalue())


class TestColorConventions(unittest.TestCase):
    """REQ-0.0.4-08-07: Color conventions applied consistently."""

    def setUp(self) -> None:
        """Root `check()` at a scratch dir, never the real repo.

        `check()` writes `.gzkit/cache/check-verified.json` on a full-scope pass
        -- the receipt the pre-push gate reuses. These cases are only safe today
        because one stubbed step FAILS, which is incidental isolation: making the
        stubs pass would silently mint a verification receipt for the developer's
        staged tree (the GHI #949 defect, found in a sibling module).
        """
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._root = Path(self._tmp.name)

    def test_quality_colors(self):
        from gzkit.commands import quality

        console = _CaptureConsole()
        steps = [
            ("Passing step", lambda _: _result(True)),
            ("Failing step", lambda _: _result(False, 1)),
        ]
        with (
            patch.object(quality, "console", console),
            patch.object(quality, "get_project_root", return_value=self._root),
            patch.object(quality, "_build_check_steps", return_value=steps),
            patch("gzkit.cli.formatters.OutputFormatter", _SilentFormatter),
            patch(
                "gzkit.quality.run_drift_advisory",
                return_value=SimpleNamespace(has_drift=False),
            ),
            patch("gzkit.flags.registry.load_registry", side_effect=RuntimeError("skip flags")),
            self.assertRaises(SystemExit),
        ):
            quality.check()

        self.assertIn("[green]", console.text)
        self.assertIn("[red]", console.text)

    def test_gates_colors(self):
        from gzkit.commands import gates

        console = _CaptureConsole()
        cli = SimpleNamespace(run_command=lambda *_args, **_kwargs: _result(True))
        failing_console = _CaptureConsole()
        failing_cli = SimpleNamespace(run_command=lambda *_args, **_kwargs: _result(False, 1))

        with (
            patch.object(gates, "console", console),
            patch.object(gates, "_cli_main", return_value=cli),
        ):
            gates._run_gate_2(Path("."), _FakeLedger(), "ADR-0.1.0", "test")
            gates._run_gate_5()

        with (
            patch.object(gates, "console", failing_console),
            patch.object(gates, "_cli_main", return_value=failing_cli),
        ):
            gates._run_gate_2(Path("."), _FakeLedger(), "ADR-0.1.0", "test")

        self.assertIn("[green]", console.text)
        self.assertIn("[yellow]", console.text)
        self.assertIn("[red]", failing_console.text)

    def test_validate_colors(self):
        from gzkit.commands import validate_cmd
        from gzkit.validate import ValidationError

        clean_console = _CaptureConsole()
        error_console = _CaptureConsole()
        error = ValidationError(type="demo", artifact="x", message="broken")

        with patch.object(validate_cmd, "console", clean_console):
            validate_cmd._print_validation_result([], ["manifest"])

        with (
            patch.object(validate_cmd, "console", error_console),
            self.assertRaises(SystemExit),
        ):
            validate_cmd._print_validation_result([error], ["manifest"])

        self.assertIn("[green]", clean_console.text)
        self.assertIn("[red]", error_console.text)


class TestNoColorDegradation(unittest.TestCase):
    """REQ-0.0.4-08-08: NO_COLOR produces clean output."""

    @covers("REQ-0.0.4-08-08")
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

    @covers("REQ-0.0.4-08-09")
    def test_emit_status_json_no_symbols(self):
        """emit_status in JSON mode must not include check/cross symbols."""
        import io
        from unittest.mock import patch

        from gzkit.cli.formatters import OutputFormatter, OutputMode

        fmt = OutputFormatter(OutputMode.JSON)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            fmt.emit_status("Lint", True)
            output = mock_stdout.getvalue()
            self.assertNotIn("\u2713", output)
            self.assertNotIn("\u274c", output)
            self.assertIn('"success": true', output)


if __name__ == "__main__":
    unittest.main()
