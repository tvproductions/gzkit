import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from tests.commands.common import CliRunner, _quick_init


class TestRegisterAdrsCommand(unittest.TestCase):
    """Tests for gz register-adrs command."""

    def test_register_adrs_registers_missing_pool_adr(self) -> None:
        """register-adrs appends adr_created for unregistered ADR files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
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
            self.assertIn("No unregistered ADRs or OBPIs found.", repeat.output)

    def test_register_adrs_keeps_suffixed_id_and_registers_non_semver_pool(self) -> None:
        """register-adrs keeps suffixed IDs and accepts non-semver pool IDs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
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

    def test_register_adrs_all_registers_missing_obpis_for_targeted_adr_only(self) -> None:
        """register-adrs --all can backfill missing OBPI links for one ADR package."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_root = Path(config.paths.adrs) / "pre-release"
            adr_one_dir = adr_root / "ADR-0.1.0" / "obpis"
            adr_one_dir.parent.mkdir(parents=True, exist_ok=True)
            (adr_one_dir.parent / "ADR-0.1.0.md").write_text(
                "---\nid: ADR-0.1.0\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n# ADR-0.1.0\n"
            )
            adr_one_dir.mkdir(parents=True, exist_ok=True)
            (adr_one_dir / "OBPI-0.1.0-01-demo.md").write_text(
                "---\n"
                "id: OBPI-0.1.0-01-demo\n"
                "parent: ADR-0.1.0\n"
                "item: 1\n"
                "lane: Lite\n"
                "status: Draft\n"
                "---\n\n"
                "# OBPI-0.1.0-01-demo\n"
            )

            adr_two_dir = adr_root / "ADR-0.2.0" / "obpis"
            adr_two_dir.parent.mkdir(parents=True, exist_ok=True)
            (adr_two_dir.parent / "ADR-0.2.0.md").write_text(
                "---\nid: ADR-0.2.0\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n# ADR-0.2.0\n"
            )
            adr_two_dir.mkdir(parents=True, exist_ok=True)
            (adr_two_dir / "OBPI-0.2.0-01-demo.md").write_text(
                "---\n"
                "id: OBPI-0.2.0-01-demo\n"
                "parent: ADR-0.2.0\n"
                "item: 1\n"
                "lane: Lite\n"
                "status: Draft\n"
                "---\n\n"
                "# OBPI-0.2.0-01-demo\n"
            )

            dry_run = runner.invoke(main, ["register-adrs", "ADR-0.1.0", "--all", "--dry-run"])
            self.assertEqual(dry_run.exit_code, 0)
            self.assertIn("Would append adr_created: ADR-0.1.0", dry_run.output)
            self.assertIn("Would append obpi_created: OBPI-0.1.0-01-demo", dry_run.output)
            self.assertNotIn("ADR-0.2.0", dry_run.output)
            self.assertNotIn("OBPI-0.2.0-01-demo", dry_run.output)

            result = runner.invoke(main, ["register-adrs", "ADR-0.1.0", "--all"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.1.0", result.output)
            self.assertIn("Registered OBPI: OBPI-0.1.0-01-demo", result.output)
            self.assertNotIn("OBPI-0.2.0-01-demo", result.output)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event":"adr_created","id":"ADR-0.1.0"', ledger_content)
            self.assertIn('"event":"obpi_created","id":"OBPI-0.1.0-01-demo"', ledger_content)
            self.assertNotIn('"event":"adr_created","id":"ADR-0.2.0"', ledger_content)
            self.assertNotIn('"event":"obpi_created","id":"OBPI-0.2.0-01-demo"', ledger_content)
