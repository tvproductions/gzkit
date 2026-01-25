"""Tests for gzkit CLI integration."""

import unittest
from pathlib import Path

from click.testing import CliRunner

from gzkit.cli import main


class TestInitCommand(unittest.TestCase):
    """Tests for gz init command."""

    def test_init_creates_gzkit_dir(self) -> None:
        """init creates .gzkit directory."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit").exists())

    def test_init_creates_ledger(self) -> None:
        """init creates ledger file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit/ledger.jsonl").exists())

    def test_init_creates_manifest(self) -> None:
        """init creates manifest file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit/manifest.json").exists())

    def test_init_creates_design_directories(self) -> None:
        """init creates design directories."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/prd").exists())
            self.assertTrue(Path("design/constitutions").exists())
            self.assertTrue(Path("design/obpis").exists())
            self.assertTrue(Path("design/adr").exists())

    def test_init_fails_if_already_initialized(self) -> None:
        """init fails if already initialized."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["init"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("already initialized", result.output)

    def test_init_with_force(self) -> None:
        """init --force reinitializes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["init", "--force"])
            self.assertEqual(result.exit_code, 0)


class TestPrdCommand(unittest.TestCase):
    """Tests for gz prd command."""

    def test_prd_creates_file(self) -> None:
        """prd creates PRD file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["prd", "TEST-1.0.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/prd/PRD-TEST-1.0.0.md").exists())

    def test_prd_records_event(self) -> None:
        """prd records event in ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["prd", "TEST-1.0.0"])
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn("prd_created", ledger_content)


class TestSpecifyCommand(unittest.TestCase):
    """Tests for gz specify command."""

    def test_specify_creates_obpi_file(self) -> None:
        """specify creates OBPI file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/obpis/OBPI-0.1.0-01-core-feature.md").exists())


class TestPlanCommand(unittest.TestCase):
    """Tests for gz plan command."""

    def test_plan_creates_file(self) -> None:
        """plan creates ADR file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["plan", "0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/adr/ADR-0.1.0.md").exists())


class TestStatusCommand(unittest.TestCase):
    """Tests for gz status command."""

    def test_status_shows_no_adrs(self) -> None:
        """status shows message when no ADRs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No ADRs found", result.output)

    def test_status_shows_adr(self) -> None:
        """status shows ADR when present."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR-0.1.0", result.output)


class TestValidateCommand(unittest.TestCase):
    """Tests for gz validate command."""

    def test_validate_after_init(self) -> None:
        """validate passes after init (with surface errors expected)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            # Create AGENTS.md with required sections
            Path("AGENTS.md").write_text(
                """# AGENTS.md

## Project Identity

Test project

## Behavior Rules

Rules here

## Pattern Discovery

Discovery here

## Gate Covenant

Covenant here

## Execution Rules

Rules here
"""
            )
            result = runner.invoke(main, ["validate"])
            # May have some validation issues but should not crash
            self.assertIn("validation", result.output.lower())


class TestSyncCommand(unittest.TestCase):
    """Tests for gz sync command."""

    def test_sync_updates_surfaces(self) -> None:
        """sync updates control surfaces."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["sync"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Sync complete", result.output)


class TestLintCommand(unittest.TestCase):
    """Tests for gz lint command."""

    def test_lint_runs(self) -> None:
        """lint command runs (may fail without src/tests)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            # Create minimal structure
            Path("src").mkdir()
            Path("tests").mkdir()
            result = runner.invoke(main, ["lint"])
            # Command runs regardless of result
            self.assertIn("lint", result.output.lower())


class TestSkillCommands(unittest.TestCase):
    """Tests for skill subcommands."""

    def test_skill_list(self) -> None:
        """skill list shows scaffolded skills."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "list"])
            self.assertEqual(result.exit_code, 0)
            # Should show core skills from init
            self.assertIn("lint", result.output)

    def test_skill_new(self) -> None:
        """skill new creates skill."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "new", "my-skill"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".github/skills/my-skill/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
