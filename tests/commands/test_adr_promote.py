import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
)
from tests.commands.common import CliRunner, _quick_init


class TestAdrPromoteCommand(unittest.TestCase):
    """Tests for pool ADR promotion protocol and tooling."""

    @staticmethod
    def _seed_pool_adr(config: GzkitConfig, adr_id: str = "ADR-pool.sample-work") -> Path:
        pool_dir = Path(config.paths.adrs) / "pool"
        pool_dir.mkdir(parents=True, exist_ok=True)
        pool_file = pool_dir / f"{adr_id}.md"
        pool_file.write_text(
            "---\n"
            f"id: {adr_id}\n"
            "status: Pool\n"
            "parent: PRD-GZKIT-1.0.0\n"
            "lane: heavy\n"
            "---\n\n"
            f"# {adr_id}: Sample Work\n\n"
            "## Status\n\n"
            "Pool\n\n"
            "## Intent\n\n"
            "Turn sample pool work into executable tracked delivery.\n\n"
            "## Target Scope\n\n"
            "- Define runtime command contract\n"
            "- Persist machine-readable stage state\n"
            "- Expose structured stage outputs\n\n"
            "## Non-Goals\n\n"
            "- No external orchestrator\n"
        )
        return pool_file

    def test_adr_promote_dry_run_reports_actions(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-pool.sample-work", "--semver", "0.6.0", "--dry-run"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Would append artifact_renamed", result.output)
            self.assertIn("ADR-pool.sample-work -> ADR-0.6.0-sample-work", result.output)
            self.assertIn("Would create OBPIs: 3", result.output)
            self.assertIn(
                "Would append obpi_created: OBPI-0.6.0-01-define-runtime-command-contract",
                result.output,
            )

    def test_adr_promote_writes_files_and_ledger_rename(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_file = self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-pool.sample-work", "--semver", "0.6.0", "--force"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Promoted pool ADR", result.output)

            target_file = (
                Path(config.paths.adrs)
                / "pre-release"
                / "ADR-0.6.0-sample-work"
                / "ADR-0.6.0-sample-work.md"
            )
            self.assertTrue(target_file.exists())
            target_content = target_file.read_text(encoding="utf-8")
            self.assertIn("promoted_from: ADR-pool.sample-work", target_content)
            self.assertIn("Turn sample pool work into executable tracked delivery.", target_content)
            self.assertIn("- [ ] OBPI-0.6.0-01: Define runtime command contract", target_content)
            self.assertNotIn("Replace this seeded intent", target_content)
            self.assertNotIn("Define scope, constraints, and acceptance criteria", target_content)

            obpi_dir = target_file.parent / "obpis"
            first_obpi = obpi_dir / "OBPI-0.6.0-01-define-runtime-command-contract.md"
            self.assertTrue(first_obpi.exists())
            first_obpi_content = first_obpi.read_text(encoding="utf-8")
            self.assertIn("## Objective", first_obpi_content)
            self.assertIn("Define runtime command contract.", first_obpi_content)
            self.assertIn("**Status:** Draft", first_obpi_content)

            updated_pool = pool_file.read_text(encoding="utf-8")
            self.assertIn("status: Superseded", updated_pool)
            self.assertIn("promoted_to: ADR-0.6.0-sample-work", updated_pool)
            self.assertIn("## Status\n\nSuperseded\n", updated_pool)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event":"artifact_renamed"', ledger_content)
            self.assertIn('"id":"ADR-pool.sample-work"', ledger_content)
            self.assertIn('"new_id":"ADR-0.6.0-sample-work"', ledger_content)
            self.assertEqual(ledger_content.count('"event":"obpi_created"'), 3)

    def test_adr_promote_fails_without_target_scope(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "ADR-pool.missing-scope.md"
            pool_file.write_text(
                "---\n"
                "id: ADR-pool.missing-scope\n"
                "status: Pool\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: heavy\n"
                "---\n\n"
                "# ADR-pool.missing-scope: Missing Scope\n\n"
                "## Intent\n\n"
                "Missing actionable scope.\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.missing-scope", "", "heavy"))

            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-pool.missing-scope", "--semver", "0.6.0"],
            )
            self.assertNotEqual(result.exit_code, 0)
            normalized_output = " ".join(result.output.split())
            self.assertIn("missing required section", normalized_output)
            self.assertIn("Target Scope", normalized_output)
            self.assertFalse(
                (
                    Path(config.paths.adrs)
                    / "pre-release"
                    / "ADR-0.6.0-missing-scope"
                    / "ADR-0.6.0-missing-scope.md"
                ).exists()
            )

    def test_adr_promote_rejects_non_pool_source(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.6.0"])
            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-0.6.0", "--semver", "0.6.1"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not a pool entry", result.output)

    def test_adr_promote_blocks_on_non_go_eval(self) -> None:
        """Promotion fails closed when generated package does not reach GO."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-pool.sample-work", "--semver", "0.6.0"],
            )
            self.assertEqual(result.exit_code, 3)
            self.assertIn("Promotion blocked", result.output)
            self.assertIn("eval verdict CONDITIONAL GO", result.output)
