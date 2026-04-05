"""Tests for gz state --repair (OBPI-0.0.9-03: State Repair Command).

Validates that state_repair force-reconciles frontmatter status from
ledger-derived state, reports changes, and is idempotent.
"""

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.commands.state import _derive_expected_status, _scan_obpi_briefs, state_repair

_quiet_console = Console(file=StringIO())


class TestDeriveExpectedStatus(unittest.TestCase):
    """Unit tests for mapping ledger graph info to expected frontmatter status."""

    def test_completed_obpi(self) -> None:
        info = {"type": "obpi", "ledger_completed": True, "withdrawn": False}
        self.assertEqual(_derive_expected_status(info), "Completed")

    def test_withdrawn_obpi(self) -> None:
        info = {"type": "obpi", "ledger_completed": False, "withdrawn": True}
        self.assertEqual(_derive_expected_status(info), "Abandoned")

    def test_withdrawn_takes_precedence_over_completed(self) -> None:
        info = {"type": "obpi", "ledger_completed": True, "withdrawn": True}
        self.assertEqual(_derive_expected_status(info), "Abandoned")

    def test_pending_obpi_returns_none(self) -> None:
        info = {"type": "obpi", "ledger_completed": False, "withdrawn": False}
        self.assertIsNone(_derive_expected_status(info))

    def test_non_obpi_returns_none(self) -> None:
        info = {"type": "adr", "attested": False}
        self.assertIsNone(_derive_expected_status(info))


class TestScanObpiBriefs(unittest.TestCase):
    """Unit tests for OBPI brief file scanning."""

    def test_scan_finds_obpi_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp) / "docs" / "design" / "adr" / "ADR-0.1.0" / "obpis"
            adr_dir.mkdir(parents=True)
            brief = adr_dir / "OBPI-0.1.0-01-test.md"
            brief.write_text(
                "---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
                "item: 1\nlane: lite\nstatus: Draft\n---\n# Test\n",
                encoding="utf-8",
            )
            result = _scan_obpi_briefs(Path(tmp), "docs/design")
            self.assertEqual(len(result), 1)
            self.assertIn("OBPI-0.1.0-01", result)
            self.assertEqual(result["OBPI-0.1.0-01"]["frontmatter_status"], "Draft")

    def test_scan_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _scan_obpi_briefs(Path(tmp), "docs/design")
            self.assertEqual(result, {})


@patch("gzkit.commands.state.console", _quiet_console)
class TestStateRepairIdempotency(unittest.TestCase):
    """Verify repair is idempotent: second run produces no changes."""

    def _setup_brief(self, tmp: str, status: str = "Draft") -> Path:
        adr_dir = Path(tmp) / "docs" / "design" / "adr" / "ADR-0.1.0" / "obpis"
        adr_dir.mkdir(parents=True)
        brief = adr_dir / "OBPI-0.1.0-01-test.md"
        brief.write_text(
            f"---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
            f"item: 1\nlane: lite\nstatus: {status}\n---\n# Test\n",
            encoding="utf-8",
        )
        return brief

    def _make_graph(self, completed: bool = True) -> dict:
        return {
            "OBPI-0.1.0-01": {
                "type": "obpi",
                "ledger_completed": completed,
                "withdrawn": False,
                "parent": "ADR-0.1.0",
            },
        }

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_updates_frontmatter(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._setup_brief(tmp, status="Draft")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            state_repair(as_json=False)

            updated = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", updated)

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_is_idempotent(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._setup_brief(tmp, status="Completed")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            # Should produce no changes
            state_repair(as_json=False)

            updated = brief.read_text(encoding="utf-8")
            self.assertIn("status: Completed", updated)

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_json_output(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._setup_brief(tmp, status="Draft")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            with patch("builtins.print") as mock_print:
                state_repair(as_json=True)
                output = mock_print.call_args[0][0]
                data = json.loads(output)
                self.assertIsInstance(data, dict)
                self.assertIn("changes", data)
                self.assertEqual(len(data["changes"]), 1)
                self.assertEqual(data["changes"][0]["old_status"], "Draft")
                self.assertEqual(data["changes"][0]["new_status"], "Completed")

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_repair_withdrawn_obpi(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._setup_brief(tmp, status="Draft")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            graph = {
                "OBPI-0.1.0-01": {
                    "type": "obpi",
                    "ledger_completed": False,
                    "withdrawn": True,
                    "parent": "ADR-0.1.0",
                },
            }
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = graph
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            state_repair(as_json=False)

            updated = brief.read_text(encoding="utf-8")
            self.assertIn("status: Abandoned", updated)

    @patch("gzkit.commands.state.ensure_initialized")
    @patch("gzkit.commands.state.get_project_root")
    @patch("gzkit.commands.state.Ledger")
    def test_no_changes_when_already_aligned(
        self, mock_ledger_cls: MagicMock, mock_root: MagicMock, mock_init: MagicMock
    ) -> None:
        """No changes reported when frontmatter already matches ledger."""
        with tempfile.TemporaryDirectory() as tmp:
            self._setup_brief(tmp, status="Completed")
            config = MagicMock()
            config.paths.ledger = ".gzkit/ledger.jsonl"
            config.paths.design_root = "docs/design"
            mock_init.return_value = config
            mock_root.return_value = Path(tmp)
            mock_ledger = MagicMock()
            mock_ledger.get_artifact_graph.return_value = self._make_graph(completed=True)
            mock_ledger.canonicalize_id.side_effect = lambda x: x
            mock_ledger_cls.return_value = mock_ledger

            with patch("builtins.print") as mock_print:
                state_repair(as_json=True)
                output = mock_print.call_args[0][0]
                data = json.loads(output)
                self.assertEqual(len(data["changes"]), 0)


if __name__ == "__main__":
    unittest.main()
