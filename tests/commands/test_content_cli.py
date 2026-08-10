"""CLI smoke tests for gz content list/show/render/edit — OBPI-0.0.34-04."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import main
from gzkit.content.models import Rule
from gzkit.content.render import render
from gzkit.traceability import covers
from tests.commands.common import CliRunner


class TestContentCliSubcommands(unittest.TestCase):
    """CLI smoke tests for gz content list/show/render/edit subcommands."""

    def setUp(self) -> None:
        self._runner = CliRunner()
        self._tempdir = tempfile.TemporaryDirectory()
        self._tmp = Path(self._tempdir.name)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _canonical_rule_path(self) -> Path:
        rule = Rule(title="Test Rule", version="1.0.0", paths=[], body=[])
        p = self._tmp / "rule.md"
        p.write_bytes(render(rule, "claude"))
        return p

    # REQ-0.0.34-04-01 --------------------------------------------------------

    @covers("REQ-0.0.34-04-01")
    def test_list_emits_table_not_raw_json(self) -> None:
        """gz content list emits a human-readable table, never raw JSON."""
        result = self._runner.invoke(main, ["content", "list"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        # Output must NOT be valid JSON
        with self.assertRaises(json.JSONDecodeError):
            json.loads(result.output)
        # Output should contain at least one type name
        self.assertTrue(
            any(name in result.output for name in ("Rule", "Skill", "AgentContract")),
            msg=f"Expected type names in output; got: {result.output!r}",
        )

    @covers("REQ-0.0.34-04-01")
    def test_list_json_flag_emits_valid_json(self) -> None:
        """gz content list --json emits a valid JSON list with 'type' keys."""
        result = self._runner.invoke(main, ["content", "list", "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        data = json.loads(result.output)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0, msg="Expected at least one item in list output")
        for item in data:
            self.assertIn("type", item, msg=f"Item missing 'type' key: {item!r}")

    # REQ-0.0.34-04-02 --------------------------------------------------------

    @covers("REQ-0.0.34-04-02")
    def test_show_emits_prose_summary(self) -> None:
        """gz content show <path> --as Rule emits prose summary (not raw JSON)."""
        rule_path = self._canonical_rule_path()
        result = self._runner.invoke(main, ["content", "show", str(rule_path), "--as", "Rule"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        # Output must contain the type name
        self.assertIn("Rule", result.output)
        # Output must NOT start with raw JSON delimiters
        stripped = result.output.strip()
        self.assertFalse(
            stripped.startswith("{") or stripped.startswith("["),
            msg=f"show must not emit raw JSON by default; got: {result.output!r}",
        )

    @covers("REQ-0.0.34-04-02")
    def test_show_json_flag_emits_valid_json(self) -> None:
        """gz content show <path> --as Rule --json emits valid JSON with model fields."""
        rule_path = self._canonical_rule_path()
        result = self._runner.invoke(
            main, ["content", "show", str(rule_path), "--as", "Rule", "--json"]
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        data = json.loads(result.output)
        self.assertIsInstance(data, dict)
        self.assertIn("title", data)

    # REQ-0.0.34-04-03 --------------------------------------------------------

    @covers("REQ-0.0.34-04-03")
    def test_edit_invalid_content_aborts_no_partial_write(self) -> None:
        """gz content edit aborts non-zero on invalid editor output; original file unchanged."""
        rule_path = self._canonical_rule_path()
        original_bytes = rule_path.read_bytes()

        def fake_editor(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess:
            # args[-1] is the temp file path the edit command passes to $EDITOR
            temp_path = Path(args[-1])
            temp_path.write_bytes(b"INVALID YAML CONTENT NOT A RULE")
            return subprocess.CompletedProcess(args=args, returncode=0)

        with patch("subprocess.run", side_effect=fake_editor):
            result = self._runner.invoke(main, ["content", "edit", str(rule_path), "--as", "Rule"])

        self.assertNotEqual(
            result.exit_code,
            0,
            msg=f"Expected non-zero exit; got: {result.output!r}",
        )
        # Original file must be unchanged
        self.assertEqual(
            rule_path.read_bytes(),
            original_bytes,
            msg="Original file was modified; edit must never perform a partial write",
        )

    # REQ-0.0.34-04-04 --------------------------------------------------------

    @covers("REQ-0.0.34-04-04")
    def test_render_output_matches_render_function(self) -> None:
        """gz content render <path> --as Rule emits bytes matching render(rule, vendor)."""
        rule = Rule(title="Render Test", version="2.0.0", paths=[], body=[])
        rule_path = self._tmp / "render_rule.md"
        rule_path.write_bytes(render(rule, "claude"))

        result = self._runner.invoke(main, ["content", "render", str(rule_path), "--as", "Rule"])
        self.assertEqual(result.exit_code, 0, msg=result.output)

        expected = render(rule, "claude").decode("utf-8")
        self.assertEqual(
            result.output,
            expected,
            msg="render subcommand output must be byte-identical to render(model, vendor)",
        )

    # REQ-0.0.34-04-05 --------------------------------------------------------

    @covers("REQ-0.0.34-04-05")
    def test_help_lists_all_subcommands(self) -> None:
        """gz content --help lists all subcommands: edit, render, list, show, import."""
        result = self._runner.invoke(main, ["content", "--help"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        for subcommand in ("edit", "render", "list", "show", "import"):
            self.assertIn(
                subcommand,
                result.output,
                msg=f"Expected '{subcommand}' in help output; got: {result.output!r}",
            )
