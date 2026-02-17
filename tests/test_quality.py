"""Tests for gzkit quality module."""

import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.quality import QualityResult, run_adr_path_contract_lint, run_command


class TestQualityResult(unittest.TestCase):
    """Tests for QualityResult dataclass."""

    def test_to_dict(self) -> None:
        """Result converts to dictionary."""
        result = QualityResult(
            success=True,
            command="test command",
            stdout="output",
            stderr="",
            returncode=0,
        )
        d = result.to_dict()
        self.assertEqual(d["success"], True)
        self.assertEqual(d["command"], "test command")
        self.assertEqual(d["returncode"], 0)


class TestRunCommand(unittest.TestCase):
    """Tests for command execution."""

    def test_successful_command(self) -> None:
        """Successful command returns success=True."""
        result = run_command("echo hello")
        self.assertTrue(result.success)
        self.assertIn("hello", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_failed_command(self) -> None:
        """Failed command returns success=False."""
        result = run_command("exit 1")
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 1)

    def test_command_with_cwd(self) -> None:
        """Command runs in specified directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            command = f'"{sys.executable}" -c "import os; print(os.getcwd())"'
            result = run_command(command, cwd=Path(tmpdir))
            self.assertTrue(result.success)
            self.assertEqual(Path(result.stdout.strip()).resolve(), Path(tmpdir).resolve())


class TestAdrPathContractLint(unittest.TestCase):
    """Tests for ADR path contract linting."""

    def test_passes_for_current_path_style(self) -> None:
        """Current ADR package paths pass lint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc = root / "docs/design/roadmap/ROADMAP.md"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "[ADR-0.2.0](../adr/pre-release/ADR-0.2.0-gate-verification/"
                "ADR-0.2.0-gate-verification.md)\n"
            )

            result = run_adr_path_contract_lint(root)
            self.assertTrue(result.success)
            self.assertEqual(result.returncode, 0)

    def test_fails_for_legacy_series_folder_paths(self) -> None:
        """Legacy adr-0.x.x path references fail lint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc = root / "docs/design/roadmap/ROADMAP.md"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "[ADR-0.2.0](../adr/adr-0.2.x/ADR-0.2.0-gate-verification/"
                "ADR-0.2.0-gate-verification.md)\n"
            )

            result = run_adr_path_contract_lint(root)
            self.assertFalse(result.success)
            self.assertEqual(result.returncode, 1)
            self.assertIn("docs/design/roadmap/ROADMAP.md:1:", result.stdout)

    def test_allows_airlineops_historical_reference(self) -> None:
        """Historical airlineops reference is allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc = root / "docs/design/lodestar/example.md"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "The canonical example is "
                "`airlineops/docs/design/adr/adr-0.0.x/ADR-0.0.0-reset-organizing-doctrine.md`.\n"
            )

            result = run_adr_path_contract_lint(root)
            self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
