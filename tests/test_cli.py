"""Tests for gzkit CLI integration."""

import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from gzkit.cli import COMMAND_DOCS, main, resolve_adr_file
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    attested_event,
    audit_receipt_emitted_event,
    gate_checked_event,
    obpi_created_event,
)


@dataclass
class CliResult:
    """Simple CLI invocation result."""

    exit_code: int
    output: str


class CliRunner:
    """Minimal stdlib-only CLI test runner."""

    @contextmanager
    def isolated_filesystem(self):
        cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                yield
            finally:
                os.chdir(cwd)

    def invoke(self, command, args):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            try:
                exit_code = command(args)
            except SystemExit as exc:
                code = exc.code
                exit_code = code if isinstance(code, int) else 1
        return CliResult(
            exit_code=0 if exit_code is None else int(exit_code),
            output=output.getvalue(),
        )


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
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            result = runner.invoke(
                main, ["attest", "ADR-0.1.0", "--status", "completed", "--dry-run"]
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("attested", ledger_content)


class TestAttestSemantics(unittest.TestCase):
    """Tests for strict attestation prerequisites and canonical term mapping."""

    def test_attest_lite_requires_gate2(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Gate 2 must pass", result.output)

    def test_attest_heavy_requires_gate3(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Gate 3 must pass", result.output)

    def test_attest_heavy_allows_gate4_na_when_features_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 3, "pass", "docs", 0))

            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Term: Completed", result.output)

    def test_attest_force_bypass_requires_reason(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                ["attest", "ADR-0.1.0", "--status", "completed", "--force"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("--reason required", result.output)

    def test_attest_force_with_reason_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-0.1.0",
                    "--status",
                    "completed",
                    "--force",
                    "--reason",
                    "manual override for reconciliation",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn("attested", ledger_content)
            self.assertIn("manual override for reconciliation", ledger_content)

    def test_attest_rejects_pool_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_adr = pool_dir / "ADR-pool.sample.md"
            pool_adr.write_text("---\nid: ADR-pool.sample\n---\n\n# ADR-pool.sample\n")

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample", "", "heavy"))
            ledger.append(gate_checked_event("ADR-pool.sample", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-pool.sample", 3, "pass", "docs", 0))

            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-pool.sample",
                    "--status",
                    "completed",
                    "--force",
                    "--reason",
                    "override",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot be attested", result.output)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn('"event":"attested","id":"ADR-pool.sample"', ledger_content)


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
                "ADR-0.2.1-pool.gz-chores-system -> ADR-pool.gz-chores-system",
                migrate_result.output,
            )

            status_result = runner.invoke(main, ["status"])
            self.assertEqual(status_result.exit_code, 0)
            self.assertIn("ADR-pool.gz-chores-system", status_result.output)
            self.assertNotIn("ADR-0.2.1-pool.gz-chores-system", status_result.output)

    def test_migrate_semver_renames_release_hardening_to_non_semver_pool_id(self) -> None:
        """migrate-semver rewrites 1.0.0 pool ADR into ADR-pool.* ID."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-1.0.0-pool.release-hardening", "", "lite"))

            migrate_result = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(migrate_result.exit_code, 0)
            self.assertIn(
                "ADR-1.0.0-pool.release-hardening -> ADR-pool.release-hardening",
                migrate_result.output,
            )

            status_result = runner.invoke(main, ["status"])
            self.assertEqual(status_result.exit_code, 0)
            self.assertIn("ADR-pool.release-hardening", status_result.output)
            self.assertNotIn("ADR-1.0.0-pool.release-hardening", status_result.output)

    def test_migrate_semver_renames_pool_semver_ids_to_non_semver_ids(self) -> None:
        """migrate-semver migrates semver-labeled pool ADR IDs to ADR-pool.* IDs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.6.0-pool.gz-chores-system", "", "heavy"))

            migrate_result = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(migrate_result.exit_code, 0)
            self.assertIn(
                "ADR-0.6.0-pool.gz-chores-system -> ADR-pool.gz-chores-system",
                migrate_result.output,
            )

            status_result = runner.invoke(main, ["status"])
            self.assertEqual(status_result.exit_code, 0)
            self.assertIn("ADR-pool.gz-chores-system", status_result.output)
            self.assertNotIn("ADR-0.6.0-pool.gz-chores-system", status_result.output)


class TestRegisterAdrsCommand(unittest.TestCase):
    """Tests for gz register-adrs command."""

    def test_register_adrs_registers_missing_pool_adr(self) -> None:
        """register-adrs appends adr_created for unregistered ADR files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pool"
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_file = adr_dir / "ADR-0.3.0-pool.sample.md"
            adr_file.write_text(
                "---\n"
                "id: ADR-0.3.0-pool.sample\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: heavy\n"
                "---\n\n"
                "# ADR-0.3.0: pool.sample\n"
            )

            dry_run = runner.invoke(main, ["register-adrs", "--dry-run"])
            self.assertEqual(dry_run.exit_code, 0)
            self.assertIn("Would append adr_created: ADR-0.3.0-pool.sample", dry_run.output)

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.3.0-pool.sample", result.output)

            state_result = runner.invoke(main, ["state"])
            self.assertEqual(state_result.exit_code, 0)
            self.assertIn("ADR-0.3.0-pool.sample", state_result.output)

            repeat = runner.invoke(main, ["register-adrs"])
            self.assertEqual(repeat.exit_code, 0)
            self.assertIn("No unregistered ADRs found.", repeat.output)

    def test_register_adrs_keeps_suffixed_id_and_registers_non_semver_pool(self) -> None:
        """register-adrs keeps suffixed IDs and accepts non-semver pool IDs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pool"
            adr_dir.mkdir(parents=True, exist_ok=True)

            suffixed = adr_dir / "ADR-0.4.0-pool.heavy-lane.md"
            suffixed.write_text("# ADR-0.4.0: pool.heavy-lane\n")

            non_semver_pool = adr_dir / "ADR-pool.go-runtime-parity.md"
            non_semver_pool.write_text(
                "---\n"
                "id: ADR-pool.go-runtime-parity\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: lite\n"
                "---\n\n"
                "# ADR: pool.go-runtime-parity\n"
            )

            closeout = Path(config.paths.adrs) / "ADR-CLOSEOUT-FORM.md"
            closeout.write_text("# ADR Closeout Form\n")

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.4.0-pool.heavy-lane", result.output)
            self.assertIn("Registered ADR: ADR-pool.go-runtime-parity", result.output)
            self.assertNotIn("ADR-CLOSEOUT-FORM", result.output)

            state_result = runner.invoke(main, ["state"])
            self.assertEqual(state_result.exit_code, 0)
            self.assertIn("ADR-0.4.0-pool.heavy-lane", state_result.output)
            self.assertIn("ADR-pool.go-runtime-parity", state_result.output)
            self.assertNotIn("ADR-CLOSEOUT-FORM", state_result.output)


class TestGitSyncCommand(unittest.TestCase):
    """Tests for git sync ritual commands."""

    def test_git_sync_skill_flag_prints_skill_path(self) -> None:
        """git-sync --skill prints paired skill path without repo checks."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["git-sync", "--skill"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output.strip(), ".github/skills/git-sync/SKILL.md")

            alias_result = runner.invoke(main, ["sync-repo", "--skill"])
            self.assertEqual(alias_result.exit_code, 0)
            self.assertEqual(alias_result.output.strip(), ".github/skills/git-sync/SKILL.md")

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

    def test_validate_ledger_flag_fails_on_invalid_ledger(self) -> None:
        """--ledger performs strict ledger JSONL validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            with open(".gzkit/ledger.jsonl", "a") as ledger_file:
                ledger_file.write("{not-json}\n")

            result = runner.invoke(main, ["validate", "--ledger"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid JSON", result.output)

    def test_validate_all_includes_ledger_checks(self) -> None:
        """Default validate mode includes ledger validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            with open(".gzkit/ledger.jsonl", "a") as ledger_file:
                ledger_file.write("{not-json}\n")

            result = runner.invoke(main, ["validate"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid JSON", result.output)


class TestSyncCommand(unittest.TestCase):
    """Tests for control-surface sync commands."""

    def test_agent_sync_control_surfaces_updates_surfaces(self) -> None:
        """agent sync control-surfaces is the canonical command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Sync complete", result.output)

    def test_sync_alias_still_works(self) -> None:
        """sync alias routes to canonical command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["sync"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("deprecated", result.output.lower())
            self.assertIn("Sync complete", result.output)

    def test_agent_control_sync_alias_still_works(self) -> None:
        """agent-control-sync alias routes to canonical command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["agent-control-sync"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("deprecated", result.output.lower())
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
            self.assertIn("gz-adr-create", result.output)
            self.assertNotIn("gz-adr-manager", result.output)

    def test_skill_new(self) -> None:
        """skill new creates skill."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "new", "my-skill"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".github/skills/my-skill/SKILL.md").exists())

    def test_init_scaffolds_adr_create_and_removes_adr_manager(self) -> None:
        """core skill scaffolding uses gz-adr-create hard cutover."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self.assertTrue(Path(".github/skills/gz-adr-create/SKILL.md").exists())
            self.assertFalse(Path(".github/skills/gz-adr-manager").exists())


class TestNewCommandParsers(unittest.TestCase):
    """Parser-level tests for new command surfaces."""

    def test_new_commands_help(self) -> None:
        """All new command surfaces parse and return help."""
        runner = CliRunner()
        commands = [
            ["closeout", "--help"],
            ["audit", "--help"],
            ["adr", "--help"],
            ["adr", "status", "--help"],
            ["adr", "audit-check", "--help"],
            ["adr", "emit-receipt", "--help"],
            ["check-config-paths", "--help"],
            ["cli", "--help"],
            ["cli", "audit", "--help"],
        ]
        for args in commands:
            result = runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, msg=f"help failed for: {args}")


class TestAdrRuntimeCommands(unittest.TestCase):
    """Behavioral tests for closeout/audit-check/emit-receipt runtime surfaces."""

    @staticmethod
    def _write_obpi(path: Path, status: str, brief_status: str, implementation_line: str) -> None:
        path.write_text(
            "\n".join(
                [
                    "---",
                    "id: OBPI-0.1.0-01-demo",
                    "parent: ADR-0.1.0",
                    "item: 1",
                    "lane: Lite",
                    f"status: {status}",
                    "---",
                    "",
                    "# OBPI-0.1.0-01-demo: Demo",
                    "",
                    f"**Brief Status:** {brief_status}",
                    "",
                    "## Evidence",
                    "",
                    "### Implementation Summary",
                    f"- Files created/modified: {implementation_line}",
                    "- Validation commands run: uv run -m unittest discover tests",
                    "- Date completed: 2026-02-14",
                    "",
                ]
            )
            + "\n"
        )

    @staticmethod
    def _set_manifest_verification_noop() -> None:
        manifest_path = Path(".gzkit/manifest.json")
        manifest = json.loads(manifest_path.read_text())
        manifest["verification"] = {
            "test": "python -c \"print('ok')\"",
            "lint": "python -c \"print('ok')\"",
            "typecheck": "python -c \"print('ok')\"",
            "docs": "python -c \"print('ok')\"",
            "bdd": "python -c \"print('ok')\"",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def test_closeout_missing_adr_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["closeout", "ADR-9.9.9"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("ADR not found", result.output)

    def test_closeout_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn("closeout_initiated", ledger_content)

    def test_closeout_dry_run_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("closeout_initiated", ledger_content)

    def test_closeout_includes_canonical_attestation_choices(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Completed — Partial: [reason]", result.output)
            self.assertIn("Dropped — [reason]", result.output)

    def test_closeout_heavy_shows_gate4_na_when_features_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 4 (BDD): N/A", result.output)

    def test_closeout_heavy_includes_bdd_command_when_features_exist(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            Path("features").mkdir(exist_ok=True)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 4 (BDD):", result.output)
            self.assertIn("uv run -m behave features/", result.output)

    def test_audit_pre_attestation_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Audit blocked", result.output)

    def test_audit_after_attestation_writes_artifacts(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            self._set_manifest_verification_noop()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            attestation = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertEqual(attestation.exit_code, 0)

            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/adr/audit/AUDIT.md").exists())
            self.assertTrue(Path("design/adr/audit/AUDIT_PLAN.md").exists())
            self.assertTrue(Path("design/adr/audit/proofs/test.txt").exists())

    def test_audit_dry_run_after_attestation_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            self._set_manifest_verification_noop()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            attestation = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertEqual(attestation.exit_code, 0)

            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path("design/adr/audit").exists())

    def test_adr_audit_check_passes_for_completed_obpi_with_evidence(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.obpis) / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
            )
            result = runner.invoke(main, ["adr", "audit-check", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("PASS", result.output)

    def test_adr_audit_check_fails_for_incomplete_obpi(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.obpis) / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
            )
            result = runner.invoke(main, ["adr", "audit-check", "ADR-0.1.0"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("FAIL", result.output)

    def test_adr_emit_receipt_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-0.1.0",
                    "--event",
                    "validated",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    '{"gate":5}',
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn("audit_receipt_emitted", ledger_content)

    def test_adr_emit_receipt_invalid_json_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-0.1.0",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    "{bad json}",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid --evidence-json", result.output)

    def test_adr_emit_receipt_dry_run_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-0.1.0",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertNotIn("audit_receipt_emitted", ledger_content)


class TestLifecycleStatusSemantics(unittest.TestCase):
    """Tests for derived lifecycle semantics on status/state surfaces."""

    def test_adr_status_json_completed(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "human"))

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["lifecycle_status"], "Completed")
            self.assertEqual(payload["closeout_phase"], "attested")
            self.assertEqual(payload["attestation_term"], "Completed")

    def test_adr_status_json_validated(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "human"))
            ledger.append(audit_receipt_emitted_event("ADR-0.1.0", "validated", "human"))

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["lifecycle_status"], "Validated")
            self.assertEqual(payload["closeout_phase"], "validated")
            self.assertTrue(payload["validated"])

    def test_adr_status_json_abandoned(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "dropped", "human", "out of scope"))

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["lifecycle_status"], "Abandoned")
            self.assertEqual(payload["attestation_term"], "Dropped")

    def test_obpi_scoped_validated_receipt_does_not_set_validated_lifecycle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(
                audit_receipt_emitted_event(
                    "ADR-0.1.0",
                    "validated",
                    "human",
                    evidence={
                        "scope": "OBPI-0.1.0-01",
                        "adr_completion": "not_completed",
                        "obpi_completion": "attested_completed",
                    },
                )
            )

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["lifecycle_status"], "Pending")
            self.assertEqual(payload["closeout_phase"], "pre_closeout")
            self.assertFalse(payload["validated"])

    def test_status_json_includes_lifecycle_fields(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "partial", "human", "staged rollout"))

            result = runner.invoke(main, ["status", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-0.1.0"]
            self.assertEqual(adr_payload["lifecycle_status"], "Completed")
            self.assertEqual(adr_payload["attestation_term"], "Completed — Partial")

    def test_adr_status_json_pool_adr_ignores_attestation_for_lifecycle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_adr = pool_dir / "ADR-pool.sample.md"
            pool_adr.write_text("---\nid: ADR-pool.sample\n---\n\n# ADR-pool.sample\n")

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample", "", "heavy"))
            ledger.append(attested_event("ADR-pool.sample", "completed", "human"))

            result = runner.invoke(main, ["adr", "status", "ADR-pool.sample", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["lifecycle_status"], "Pending")
            self.assertEqual(payload["closeout_phase"], "pre_closeout")
            self.assertIsNone(payload["attestation_term"])
            self.assertFalse(payload["attested"])
            self.assertEqual(payload["gates"]["5"], "pending")

    def test_status_json_pool_adr_ignores_attestation_for_lifecycle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_adr = pool_dir / "ADR-pool.sample.md"
            pool_adr.write_text("---\nid: ADR-pool.sample\n---\n\n# ADR-pool.sample\n")

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample", "", "heavy"))
            ledger.append(attested_event("ADR-pool.sample", "completed", "human"))

            result = runner.invoke(main, ["status", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-pool.sample"]
            self.assertEqual(adr_payload["lifecycle_status"], "Pending")
            self.assertEqual(adr_payload["closeout_phase"], "pre_closeout")
            self.assertIsNone(adr_payload["attestation_term"])
            self.assertFalse(adr_payload["attested"])
            self.assertEqual(adr_payload["gates"]["5"], "pending")

    def test_adr_status_json_includes_obpi_rows(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.obpis) / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            TestAdrRuntimeCommands._write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
            )

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertIn("obpis", payload)
            self.assertEqual(len(payload["obpis"]), 1)
            row = payload["obpis"][0]
            self.assertEqual(row["id"], "OBPI-0.1.0-01-demo")
            self.assertTrue(row["found_file"])
            self.assertTrue(row["completed"])
            self.assertTrue(row["evidence_ok"])
            self.assertEqual(row["issues"], [])

    def test_adr_status_json_reports_missing_linked_obpi_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-core-feature", "ADR-0.1.0"))

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertIn("obpis", payload)
            self.assertEqual(len(payload["obpis"]), 1)
            row = payload["obpis"][0]
            self.assertEqual(row["id"], "OBPI-0.1.0-01-core-feature")
            self.assertFalse(row["found_file"])
            self.assertIn("linked in ledger but no OBPI file found", row["issues"])

    def test_state_ready_json_only_includes_gate_ready_unattested_adrs(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["plan", "0.2.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["state", "--ready", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertIn("ADR-0.1.0", payload)
            self.assertNotIn("ADR-0.2.0", payload)


class TestConfigAndCliAuditCommands(unittest.TestCase):
    """Tests for check-config-paths and cli audit commands."""

    @staticmethod
    def _prepare_docs_surface() -> None:
        index_path = Path("docs/user/commands/index.md")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        links: list[str] = []
        for command_name, doc_rel in COMMAND_DOCS.items():
            doc_path = Path(doc_rel)
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(f"# gz {command_name}\n\nStub\n")
            links.append(f"- {doc_path.name}")
        index_path.write_text("# Commands Index\n\n" + "\n".join(links) + "\n")

    def test_check_config_paths_passes_for_valid_layout(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            Path("src").mkdir(exist_ok=True)
            Path("tests").mkdir(exist_ok=True)
            Path("docs").mkdir(exist_ok=True)
            result = runner.invoke(main, ["check-config-paths"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_check_config_paths_detects_missing_path(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            Path("src").mkdir(exist_ok=True)
            Path("tests").mkdir(exist_ok=True)
            Path("docs").mkdir(exist_ok=True)
            # Break a required path.
            skill_dir = Path(".github/skills")
            if skill_dir.exists():
                for path in sorted(skill_dir.glob("**/*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                skill_dir.rmdir()
            result = runner.invoke(main, ["check-config-paths"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("failed", result.output.lower())

    def test_cli_audit_passes_with_synchronized_docs(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            result = runner.invoke(main, ["cli", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_cli_audit_detects_mismatch(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            # Corrupt one heading to trigger mismatch.
            doc_rel = COMMAND_DOCS["closeout"]
            Path(doc_rel).write_text("# wrong heading\n")
            result = runner.invoke(main, ["cli", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("failed", result.output.lower())


if __name__ == "__main__":
    unittest.main()
