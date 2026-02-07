"""Tests for gzkit CLI integration."""

import subprocess
import unittest
from pathlib import Path

from click.testing import CliRunner

from gzkit.cli import main, resolve_adr_file
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event, gate_checked_event


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


class TestDryRunCommands(unittest.TestCase):
    """Tests for dry-run behavior."""

    def test_init_dry_run_creates_nothing(self) -> None:
        """init --dry-run does not create files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path(".gzkit").exists())

    def test_prd_dry_run_does_not_write(self) -> None:
        """prd --dry-run does not create PRD or ledger event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["prd", "TEST-1.0.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path("design/prd/PRD-TEST-1.0.0.md").exists())
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("prd_created", ledger_content)

    def test_attest_dry_run_does_not_write(self) -> None:
        """attest --dry-run does not record attestation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main, ["attest", "ADR-0.1.0", "--status", "completed", "--dry-run"]
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("attested", ledger_content)


class TestGateCommands(unittest.TestCase):
    """Tests for gate verification commands."""

    def test_gates_gate1_records_event(self) -> None:
        """gates --gate 1 records gate_checked event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["gates", "--gate", "1"])
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn("gate_checked", ledger_content)


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

    def test_status_shows_gate2_pass_from_ledger(self) -> None:
        """status shows Gate 2 PASS when latest gate check passed."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):   PASS", result.output)

    def test_status_shows_gate2_fail_from_ledger(self) -> None:
        """status shows Gate 2 FAIL when latest gate check failed."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "fail", "test", 1))

            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):   FAIL", result.output)


class TestMigrateSemverCommand(unittest.TestCase):
    """Tests for gz migrate-semver command."""

    def test_migrate_semver_renames_status_output(self) -> None:
        """migrate-semver records rename events used by status."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.2.1-pool.gz-chores-system", "", "heavy"))

            migrate_result = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(migrate_result.exit_code, 0)
            self.assertIn(
                "ADR-0.2.1-pool.gz-chores-system -> ADR-0.6.0-pool.gz-chores-system",
                migrate_result.output,
            )

            status_result = runner.invoke(main, ["status"])
            self.assertEqual(status_result.exit_code, 0)
            self.assertIn("ADR-0.6.0-pool.gz-chores-system", status_result.output)
            self.assertNotIn("ADR-0.2.1-pool.gz-chores-system", status_result.output)


class TestGitSyncCommand(unittest.TestCase):
    """Tests for git sync ritual commands."""

    def test_git_sync_fails_outside_git_repo(self) -> None:
        """git-sync returns error when cwd is not a git repo."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["git-sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not a git repository", result.output.lower())

    def test_git_sync_dry_run_in_git_repo(self) -> None:
        """git-sync dry-run works in a local git repo."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(["git", "add", "-A"], check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "chore: initial"],
                check=True,
                capture_output=True,
                text=True,
            )

            result = runner.invoke(main, ["git-sync"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Git sync plan", result.output)

            alias_result = runner.invoke(main, ["sync-repo"])
            self.assertEqual(alias_result.exit_code, 0)
            self.assertIn("Git sync plan", alias_result.output)


class TestAdrResolution(unittest.TestCase):
    """Tests for ADR file resolution."""

    def test_resolve_adr_file_matches_suffixed_filename(self) -> None:
        """Resolves nested ADR files by stem when header uses short SemVer ID."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pool"
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_path = adr_dir / "ADR-0.6.0-pool.gz-chores-system.md"
            adr_path.write_text("# ADR-0.6.0: pool.gz-chores-system\n")

            resolved_path, resolved_id = resolve_adr_file(
                Path.cwd(), config, "ADR-0.6.0-pool.gz-chores-system"
            )

            self.assertEqual(resolved_path.resolve(), adr_path.resolve())
            self.assertEqual(resolved_id, "ADR-0.6.0-pool.gz-chores-system")


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
