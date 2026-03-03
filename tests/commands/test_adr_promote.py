import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
)
from tests.commands.common import CliRunner


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
            f"# {adr_id}: Sample Work\n"
        )
        return pool_file

    def test_adr_promote_dry_run_reports_actions(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
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

    def test_adr_promote_writes_files_and_ledger_rename(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_file = self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-pool.sample-work", "--semver", "0.6.0"],
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
            target_content = target_file.read_text()
            self.assertIn("promoted_from: ADR-pool.sample-work", target_content)

            updated_pool = pool_file.read_text()
            self.assertIn("status: Superseded", updated_pool)
            self.assertIn("promoted_to: ADR-0.6.0-sample-work", updated_pool)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text()
            self.assertIn('"event":"artifact_renamed"', ledger_content)
            self.assertIn('"id":"ADR-pool.sample-work"', ledger_content)
            self.assertIn('"new_id":"ADR-0.6.0-sample-work"', ledger_content)

    def test_adr_promote_rejects_non_pool_source(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.6.0"])
            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-0.6.0", "--semver", "0.6.1"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not a pool entry", result.output)
