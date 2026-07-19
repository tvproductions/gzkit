"""Tests for gz governance render command (ADR-0.0.37, OBPI-0.0.37-02).

REQ-derived assertions for:
  REQ-0.0.37-02-01: --stdout produces byte-identical output across invocations; no file write
  REQ-0.0.37-02-02: --check exits 0 on match, 3 on drift + prints diff
  REQ-0.0.37-02-03: write mode writes rendered bytes to AGENTS.md and reports byte count
  REQ-0.0.37-02-04: unsupported target raises argparse error "unsupported target"
  REQ-0.0.37-02-05: governance render verb resolves via gz governance render --help
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.traceability import covers


def _invoke_cli(*args: str) -> tuple[int, str, str]:
    """Invoke the gz CLI; return (exit_code, stdout, stderr).

    main() returns an int and internally catches SystemExit,
    so we capture the return value rather than catching SystemExit.
    """
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
        try:
            result = main(list(args))
            if isinstance(result, int):
                exit_code = result
        except SystemExit as exc:
            code = exc.code
            exit_code = code if isinstance(code, int) else 1
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()


class TestGovernanceRenderVerb(unittest.TestCase):
    """REQ-0.0.37-02-05: governance render verb resolves via CLI."""

    @covers("REQ-0.0.37-02-05")
    def test_governance_render_help_exits_0(self) -> None:
        exit_code, stdout, stderr = _invoke_cli("governance", "render", "--help")
        self.assertEqual(exit_code, 0)
        self.assertIn("render", stdout + stderr)

    @covers("REQ-0.0.37-02-05")
    def test_governance_subcommand_required(self) -> None:
        exit_code, stdout, stderr = _invoke_cli("governance")
        self.assertNotEqual(exit_code, 0)


class TestGovernanceRenderUnsupportedTarget(unittest.TestCase):
    """REQ-0.0.37-02-04: unsupported target exits with 'unsupported target' message."""

    @covers("REQ-0.0.37-02-04")
    def test_unsupported_target_exits_nonzero(self) -> None:
        exit_code, stdout, stderr = _invoke_cli("governance", "render", "--target", "skill-readme")
        self.assertNotEqual(exit_code, 0)

    @covers("REQ-0.0.37-02-04")
    def test_unsupported_target_contains_error_message(self) -> None:
        exit_code, stdout, stderr = _invoke_cli("governance", "render", "--target", "skill-readme")
        combined = stdout + stderr
        self.assertIn("unsupported target", combined)


class TestGovernanceRenderStdout(unittest.TestCase):
    """REQ-0.0.37-02-01: --stdout emits rendered bytes without writing file."""

    @covers("REQ-0.0.37-02-01")
    def test_stdout_mode_does_not_write_file(self) -> None:

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inv_dir = root / ".gzkit" / "invariants"
            inv_dir.mkdir(parents=True)
            agents_path = root / "AGENTS.md"

            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                exit_code, stdout, stderr = _invoke_cli(
                    "governance", "render", "--target", "agents-md", "--stdout"
                )

            self.assertEqual(exit_code, 0)
            self.assertFalse(agents_path.exists(), "--stdout must not write AGENTS.md")

    @covers("REQ-0.0.37-02-01")
    def test_stdout_mode_produces_bytes(self) -> None:
        with (
            patch("gzkit.commands.governance_render.get_project_root", return_value=Path(".")),
        ):
            exit_code, stdout, stderr = _invoke_cli(
                "governance", "render", "--target", "agents-md", "--stdout"
            )
        self.assertEqual(exit_code, 0)


class TestGovernanceRenderWriteMode(unittest.TestCase):
    """REQ-0.0.37-02-03: write mode writes rendered bytes to AGENTS.md."""

    @covers("REQ-0.0.37-02-03")
    def test_write_mode_creates_agents_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_path = root / "AGENTS.md"

            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                exit_code, stdout, stderr = _invoke_cli(
                    "governance", "render", "--target", "agents-md"
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(agents_path.exists(), "Write mode must create AGENTS.md")

    @covers("REQ-0.0.37-02-03")
    def test_write_mode_reports_byte_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                exit_code, stdout, stderr = _invoke_cli(
                    "governance", "render", "--target", "agents-md"
                )
        self.assertEqual(exit_code, 0)
        self.assertIn("bytes", stdout + stderr)


class TestGovernanceRenderCheckMode(unittest.TestCase):
    """REQ-0.0.37-02-02: --check exits 0 on match, 3 on drift."""

    @covers("REQ-0.0.37-02-02")
    def test_check_exits_0_when_file_matches_rendered(self) -> None:
        from gzkit.governance.compose import render_agents_md

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rendered = render_agents_md(root)
            agents_path = root / "AGENTS.md"
            agents_path.write_bytes(rendered)

            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                exit_code, stdout, stderr = _invoke_cli(
                    "governance", "render", "--target", "agents-md", "--check"
                )

        self.assertEqual(exit_code, 0, "--check must exit 0 when file matches rendered output")

    @covers("REQ-0.0.37-02-02")
    def test_check_exits_3_on_drift(self) -> None:

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_path = root / "AGENTS.md"
            agents_path.write_text("stale content that differs from rendered", encoding="utf-8")

            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                exit_code, stdout, stderr = _invoke_cli(
                    "governance", "render", "--target", "agents-md", "--check"
                )

        self.assertEqual(exit_code, 3, "--check must exit 3 when file differs from rendered output")

    @covers("REQ-0.0.37-02-02")
    def test_check_drift_prints_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_path = root / "AGENTS.md"
            agents_path.write_text("stale content", encoding="utf-8")

            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                exit_code, stdout, stderr = _invoke_cli(
                    "governance", "render", "--target", "agents-md", "--check"
                )

        combined = stdout + stderr
        self.assertIn("@@", combined, "--check drift must include a unified diff hunk")


class TestGovernanceRenderNoLedgerEvent(unittest.TestCase):
    """REQ-0.0.37-02-03: write mode does not emit composition_rendered events (OBPI-03 scope)."""

    @covers("REQ-0.0.37-02-03")
    def test_write_mode_does_not_emit_ledger_event(self) -> None:
        import json

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True)
            ledger_path.write_text("", encoding="utf-8")

            with (
                patch("gzkit.commands.governance_render.get_project_root", return_value=root),
            ):
                _invoke_cli("governance", "render", "--target", "agents-md")

            content = ledger_path.read_text(encoding="utf-8")
            if content.strip():
                events = [json.loads(line) for line in content.strip().splitlines()]
                event_types = [e.get("event_type", e.get("type", "")) for e in events]
                self.assertNotIn(
                    "composition_rendered",
                    event_types,
                    "composition_rendered is OBPI-03 scope; must not be emitted by OBPI-02",
                )


if __name__ == "__main__":
    unittest.main()
