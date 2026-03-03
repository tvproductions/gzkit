import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from tests.commands.common import CliRunner


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
