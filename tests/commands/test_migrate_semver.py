import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    obpi_created_event,
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


class TestMigrateSemverDiskDrift(unittest.TestCase):
    """GHI #345: migrate-semver auto-detects bare→slug drift from on-disk canon.

    Layer-1 canon (filename stems under `design/adr/**/ADR-*.md`) is compared
    against Layer-2 ledger touched ids; bare-semver events whose on-disk form
    is the slug are reconciled without hand-curating SEMVER_ID_RENAMES.
    """

    def _write_adr_file(self, stem: str, kind: str = "foundation") -> Path:
        adr_dir = Path("design/adr") / stem
        adr_dir.mkdir(parents=True, exist_ok=True)
        adr_file = adr_dir / f"{stem}.md"
        adr_file.write_text(
            f"---\nid: {stem}\nkind: {kind}\nlane: lite\n---\n\n# {stem}: Test\n",
            encoding="utf-8",
        )
        return adr_file

    def _write_obpi_file(self, parent_stem: str, stem: str) -> Path:
        obpi_dir = Path("design/adr") / parent_stem / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        obpi_file = obpi_dir / f"{stem}.md"
        obpi_file.write_text(
            f"---\nid: {stem}\nparent: {parent_stem}\nlane: lite\n---\n\n# {stem}\n",
            encoding="utf-8",
        )
        return obpi_file

    def test_disk_drift_emits_rename_for_bare_adr_when_only_slug_form_exists_on_disk(
        self,
    ) -> None:
        """Ledger has bare ADR-X.Y.Z; on-disk has slug form → rename auto-emitted."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.99.0", "PRD-GZKIT-1.0.0", "lite"))
            self._write_adr_file("ADR-0.99.0-test-doctrine")

            result = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(result.exit_code, 0)

            fresh = Ledger(Path(".gzkit/ledger.jsonl"))
            renames = fresh.query(event_type="artifact_renamed", artifact_id="ADR-0.99.0")
            self.assertEqual(len(renames), 1)
            self.assertEqual(renames[0].extra.get("new_id"), "ADR-0.99.0-test-doctrine")

    def test_disk_drift_emits_rename_for_bare_obpi_when_only_slug_form_exists_on_disk(
        self,
    ) -> None:
        """Ledger has bare OBPI-X.Y.Z-NN; on-disk has slug form → rename auto-emitted."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.99.0-test-doctrine", "", "lite"))
            ledger.append(obpi_created_event("OBPI-0.99.0-01", "ADR-0.99.0-test-doctrine"))
            self._write_adr_file("ADR-0.99.0-test-doctrine")
            self._write_obpi_file("ADR-0.99.0-test-doctrine", "OBPI-0.99.0-01-first-step")

            result = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(result.exit_code, 0)

            fresh = Ledger(Path(".gzkit/ledger.jsonl"))
            renames = fresh.query(event_type="artifact_renamed", artifact_id="OBPI-0.99.0-01")
            self.assertEqual(len(renames), 1)
            self.assertEqual(renames[0].extra.get("new_id"), "OBPI-0.99.0-01-first-step")

    def test_disk_drift_does_not_emit_rename_when_ledger_already_has_slug_form(self) -> None:
        """No drift when ledger's adr_created already targets the slug form on disk."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.99.0-test-doctrine", "PRD-GZKIT-1.0.0", "lite"))
            self._write_adr_file("ADR-0.99.0-test-doctrine")

            result = runner.invoke(main, ["migrate-semver"])
            self.assertEqual(result.exit_code, 0)

            fresh = Ledger(Path(".gzkit/ledger.jsonl"))
            renames = fresh.query(event_type="artifact_renamed")
            self.assertEqual(renames, [])

    def test_disk_drift_dry_run_reports_without_writing_ledger(self) -> None:
        """Dry-run mode reports the auto-detected drift without appending to the ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.99.0", "PRD-GZKIT-1.0.0", "lite"))
            self._write_adr_file("ADR-0.99.0-test-doctrine")

            result = runner.invoke(main, ["migrate-semver", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR-0.99.0 -> ADR-0.99.0-test-doctrine", result.output)

            fresh = Ledger(Path(".gzkit/ledger.jsonl"))
            renames = fresh.query(event_type="artifact_renamed")
            self.assertEqual(renames, [])
