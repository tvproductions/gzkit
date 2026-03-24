"""Tests for the gz roles CLI command."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from gzkit.commands.roles import roles_cmd
from gzkit.pipeline_runtime import (
    aggregate_dispatch_results,
    complete_subagent_dispatch_record,
    create_subagent_dispatch_record,
    persist_dispatch_summary,
)


class TestRolesDefaultOutput(unittest.TestCase):
    """Test gz roles default table output."""

    @patch("gzkit.commands.roles.get_project_root")
    def test_output_contains_all_four_roles(self, mock_root: object) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_agent_files(root)
            mock_root.return_value = root  # type: ignore[union-attr]
            # Capture console output via --json for easier assertion
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                roles_cmd(as_json=True)
                output = mock_stdout.getvalue()

        data = json.loads(output)
        role_names = [r["role"] for r in data]
        self.assertIn("Planner", role_names)
        self.assertIn("Implementer", role_names)
        self.assertIn("Reviewer", role_names)
        self.assertIn("Narrator", role_names)


class TestRolesJsonOutput(unittest.TestCase):
    """Test gz roles --json produces valid JSON."""

    @patch("gzkit.commands.roles.get_project_root")
    def test_json_is_valid(self, mock_root: object) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _create_agent_files(root)
            mock_root.return_value = root  # type: ignore[union-attr]
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                roles_cmd(as_json=True)
                output = mock_stdout.getvalue()

        data = json.loads(output)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 4)
        for role in data:
            self.assertIn("role", role)
            self.assertIn("description", role)
            self.assertIn("stages", role)
            self.assertIn("can_write", role)


class TestRolesPipelineOutput(unittest.TestCase):
    """Test gz roles --pipeline with dispatch summary."""

    @patch("gzkit.commands.roles.get_project_root")
    def test_pipeline_with_summary(self, mock_root: object) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            mock_root.return_value = root  # type: ignore[union-attr]

            # Create a dispatch summary
            obpi_id = "OBPI-0.18.0-05"
            record = create_subagent_dispatch_record(1, "Implementer", "sonnet")
            completed = complete_subagent_dispatch_record(record, "done")
            agg = aggregate_dispatch_results([completed])
            persist_dispatch_summary(plans_dir, obpi_id, agg, [completed])

            # Patch pipeline_plans_dir to return our temp dir
            with (
                patch("gzkit.commands.roles.pipeline_plans_dir", return_value=plans_dir),
                patch("sys.stdout", new_callable=StringIO) as mock_stdout,
            ):
                roles_cmd(pipeline=obpi_id, as_json=True)
                output = mock_stdout.getvalue()

            data = json.loads(output)
            self.assertEqual(data["obpi_id"], obpi_id)
            self.assertEqual(len(data["records"]), 1)

    @patch("gzkit.commands.roles.get_project_root")
    def test_pipeline_not_found_exits(self, mock_root: object) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            mock_root.return_value = root  # type: ignore[union-attr]

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.roles.pipeline_plans_dir", return_value=plans_dir),
                patch("gzkit.commands.roles.console", quiet_console),
                self.assertRaises(SystemExit) as ctx,
            ):
                roles_cmd(pipeline="OBPI-NONEXISTENT")
            self.assertEqual(ctx.exception.code, 1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_agent_files(root: Path) -> None:
    """Create minimal agent files for test validation."""
    agents_dir = root / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    for fname in ["implementer.md", "spec-reviewer.md", "quality-reviewer.md", "narrator.md"]:
        (agents_dir / fname).write_text(
            "---\nname: test\ntools: Read, Glob\n---\nContent\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
