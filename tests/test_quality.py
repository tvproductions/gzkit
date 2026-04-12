"""Tests for gzkit quality module."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.quality import QualityResult, run_adr_path_contract_lint, run_command, run_skill_audit


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


class TestSkillAuditQualityIntegration(unittest.TestCase):
    """Tests for quality integration command wiring."""

    def test_run_skill_audit_uses_non_strict_default_command(self) -> None:
        """run_skill_audit should call CLI without --strict for default check behavior."""
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = QualityResult(
                success=True,
                command="uv run gz skill audit",
                stdout="ok",
                stderr="",
                returncode=0,
            )
            run_skill_audit(Path(tmpdir))
            mock_run_command.assert_called_once_with(
                "uv run gz skill audit",
                cwd=Path(tmpdir),
            )


class TestCanonicalQualityPath(unittest.TestCase):
    """run_all_checks must include cli audit and preflight (#133, #139)."""

    @staticmethod
    def _ok(command: str) -> QualityResult:
        return QualityResult(success=True, command=command, stdout="ok", stderr="", returncode=0)

    def test_run_all_checks_invokes_cli_audit_and_preflight(self) -> None:
        """The canonical path must wire both workflow-integrity checks."""
        from gzkit.quality import run_all_checks

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_lint", return_value=self._ok("lint")),
            patch("gzkit.quality.run_format_check", return_value=self._ok("format")),
            patch("gzkit.quality.run_typecheck", return_value=self._ok("typecheck")),
            patch("gzkit.quality.run_tests", return_value=self._ok("test")),
            patch("gzkit.quality.run_behave", return_value=self._ok("behave")),
            patch("gzkit.quality.run_skill_audit", return_value=self._ok("skill audit")),
            patch("gzkit.quality.run_parity_check", return_value=self._ok("parity")),
            patch("gzkit.quality.run_readiness_audit", return_value=self._ok("readiness")),
            patch("gzkit.quality.run_cli_audit", return_value=self._ok("cli audit")) as cli_audit,
            patch("gzkit.quality.run_preflight", return_value=self._ok("preflight")) as preflight,
            patch("gzkit.quality.run_drift_advisory") as drift,
        ):
            drift.return_value = None
            result = run_all_checks(Path(tmpdir))

            cli_audit.assert_called_once_with(Path(tmpdir))
            preflight.assert_called_once_with(Path(tmpdir))
            self.assertTrue(result.success)
            self.assertEqual(result.cli_audit.command, "cli audit")
            self.assertEqual(result.preflight.command, "preflight")

    def test_run_all_checks_fails_when_cli_audit_fails(self) -> None:
        """A failing CLI audit must flip overall success to False."""
        from gzkit.quality import run_all_checks

        failing = QualityResult(
            success=False,
            command="uv run gz cli audit",
            stdout="",
            stderr="gap",
            returncode=1,
        )
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_lint", return_value=self._ok("lint")),
            patch("gzkit.quality.run_format_check", return_value=self._ok("format")),
            patch("gzkit.quality.run_typecheck", return_value=self._ok("typecheck")),
            patch("gzkit.quality.run_tests", return_value=self._ok("test")),
            patch("gzkit.quality.run_behave", return_value=self._ok("behave")),
            patch("gzkit.quality.run_skill_audit", return_value=self._ok("skill audit")),
            patch("gzkit.quality.run_parity_check", return_value=self._ok("parity")),
            patch("gzkit.quality.run_readiness_audit", return_value=self._ok("readiness")),
            patch("gzkit.quality.run_cli_audit", return_value=failing),
            patch("gzkit.quality.run_preflight", return_value=self._ok("preflight")),
            patch("gzkit.quality.run_drift_advisory") as drift,
        ):
            drift.return_value = None
            result = run_all_checks(Path(tmpdir))
            self.assertFalse(result.success)

    def test_run_all_checks_fails_when_preflight_fails(self) -> None:
        """A failing preflight scan must flip overall success to False."""
        from gzkit.quality import run_all_checks

        failing = QualityResult(
            success=False,
            command="uv run gz preflight",
            stdout="",
            stderr="stale markers",
            returncode=1,
        )
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_lint", return_value=self._ok("lint")),
            patch("gzkit.quality.run_format_check", return_value=self._ok("format")),
            patch("gzkit.quality.run_typecheck", return_value=self._ok("typecheck")),
            patch("gzkit.quality.run_tests", return_value=self._ok("test")),
            patch("gzkit.quality.run_behave", return_value=self._ok("behave")),
            patch("gzkit.quality.run_skill_audit", return_value=self._ok("skill audit")),
            patch("gzkit.quality.run_parity_check", return_value=self._ok("parity")),
            patch("gzkit.quality.run_readiness_audit", return_value=self._ok("readiness")),
            patch("gzkit.quality.run_cli_audit", return_value=self._ok("cli audit")),
            patch("gzkit.quality.run_preflight", return_value=failing),
            patch("gzkit.quality.run_drift_advisory") as drift,
        ):
            drift.return_value = None
            result = run_all_checks(Path(tmpdir))
            self.assertFalse(result.success)

    def test_run_cli_audit_command_shape(self) -> None:
        """run_cli_audit calls the CLI directly."""
        from gzkit.quality import run_cli_audit

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = self._ok("cli audit")
            run_cli_audit(Path(tmpdir))
            mock_run_command.assert_called_once_with(
                "uv run gz cli audit",
                cwd=Path(tmpdir),
            )

    def test_run_preflight_command_shape(self) -> None:
        """run_preflight calls the CLI without --apply (detection only)."""
        from gzkit.quality import run_preflight

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("gzkit.quality.run_command") as mock_run_command,
        ):
            mock_run_command.return_value = self._ok("preflight")
            run_preflight(Path(tmpdir))
            mock_run_command.assert_called_once_with(
                "uv run gz preflight",
                cwd=Path(tmpdir),
            )


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
