import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import (
    Ledger,
    adr_created_event,
)
from tests.commands.common import CliRunner, _quick_init


class TestMigrateSemverCommand(unittest.TestCase):
    """Tests for gz migrate-semver command."""

    def test_migrate_semver_renames_status_output(self) -> None:
        """migrate-semver records rename events used by status."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
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
            _quick_init()
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
            _quick_init()
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
