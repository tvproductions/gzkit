"""Tests proving gate checks pass regardless of Layer 3 artifact state.

REQ-0.0.9-05-01: No gate check reads pipeline markers as sole evidence.
REQ-0.0.9-05-02: Gates pass after deleting all .gzkit/markers/.
REQ-0.0.9-05-03: L3 artifacts produce warnings only, never gate failures.
"""

import ast
import importlib.util
import json
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


def _plan_adr(runner: CliRunner) -> None:
    """Invoke gz plan to register an ADR so gate 1 has an L1 artifact to find."""
    runner.invoke(main, ["plan", "0.1.0"])


class TestGate1WithoutMarkersDirectory(unittest.TestCase):
    """REQ-0.0.9-05-01 / REQ-0.0.9-05-02: gate 1 passes with no markers dir."""

    def test_gate1_passes_without_markers_directory(self) -> None:
        """Gate 1 passes when .gzkit/markers/ has never been created."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _plan_adr(runner)

            markers_dir = Path(".gzkit/markers")
            self.assertFalse(markers_dir.exists(), "Precondition: markers dir must not exist")

            result = runner.invoke(main, ["gates", "--gate", "1"])
            self.assertEqual(result.exit_code, 0)


class TestGate1WithMarkersDirectoryPresent(unittest.TestCase):
    """REQ-0.0.9-05-03: pre-existing marker files do not affect gate outcome."""

    def test_gate1_passes_with_markers_directory_present(self) -> None:
        """Gate 1 passes even when .gzkit/markers/ contains fake marker files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _plan_adr(runner)

            markers_dir = Path(".gzkit/markers")
            markers_dir.mkdir(parents=True, exist_ok=True)
            fake_payload = json.dumps({"fake": "marker", "stage": "implement"})
            (markers_dir / "fake-marker.json").write_text(fake_payload, encoding="utf-8")
            (markers_dir / "another-marker.json").write_text(fake_payload, encoding="utf-8")

            result = runner.invoke(main, ["gates", "--gate", "1"])
            self.assertEqual(result.exit_code, 0)


class TestGate1AfterMarkersDeletion(unittest.TestCase):
    """REQ-0.0.9-05-02: gate still passes after markers directory is deleted."""

    def test_gate1_passes_after_markers_deleted(self) -> None:
        """Gate 1 result is identical before and after deleting .gzkit/markers/."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _plan_adr(runner)

            markers_dir = Path(".gzkit/markers")
            markers_dir.mkdir(parents=True, exist_ok=True)
            (markers_dir / "marker.json").write_text("{}", encoding="utf-8")

            result_before = runner.invoke(main, ["gates", "--gate", "1"])
            self.assertEqual(result_before.exit_code, 0, "Gate 1 should pass before deletion")

            (markers_dir / "marker.json").unlink()
            markers_dir.rmdir()
            self.assertFalse(markers_dir.exists(), "Markers dir must be deleted")

            result_after = runner.invoke(main, ["gates", "--gate", "1"])
            self.assertEqual(
                result_after.exit_code,
                result_before.exit_code,
                "Gate 1 exit code must be unchanged after markers deletion",
            )


class TestGateIndependentOfPipelineActiveMarkers(unittest.TestCase):
    """REQ-0.0.9-05-01: .claude/plans pipeline markers do not affect gate 1."""

    def test_gates_independent_of_pipeline_active_markers(self) -> None:
        """Gate 1 exit code is the same whether pipeline-active markers exist or not."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _plan_adr(runner)

            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            marker_payload = json.dumps(
                {
                    "obpi_id": "OBPI-0.1.0-01",
                    "current_stage": "implement",
                    "receipt_state": "missing",
                }
            )
            active_marker = plans_dir / ".pipeline-active-OBPI-0.1.0-01.json"
            active_marker.write_text(marker_payload, encoding="utf-8")

            result_with_marker = runner.invoke(main, ["gates", "--gate", "1"])

            active_marker.unlink()
            self.assertFalse(active_marker.exists())

            result_without_marker = runner.invoke(main, ["gates", "--gate", "1"])

            self.assertEqual(
                result_with_marker.exit_code,
                result_without_marker.exit_code,
                "Gate 1 exit code must not change when pipeline-active markers are removed",
            )
            self.assertEqual(result_without_marker.exit_code, 0)


class TestGateImportsExcludePipelineMarkers(unittest.TestCase):
    """REQ-0.0.9-05-01: static analysis guard — gates.py must not import pipeline_markers."""

    def test_gate_imports_exclude_pipeline_markers(self) -> None:
        """gates.py source must not import from the pipeline_markers module."""
        spec = importlib.util.find_spec("gzkit.commands.gates")
        self.assertIsNotNone(spec, "gzkit.commands.gates module must be locatable")
        assert spec is not None  # narrow type for mypy
        origin = spec.origin
        self.assertIsNotNone(origin, "gates module must have a file origin")
        assert origin is not None

        source = Path(origin).read_text(encoding="utf-8")
        tree = ast.parse(source)

        imported_modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        for mod in imported_modules:
            self.assertNotIn(
                "pipeline_markers",
                mod,
                f"gates.py must not import from pipeline_markers; found import: {mod}",
            )
