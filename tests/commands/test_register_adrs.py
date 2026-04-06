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
            self.assertNotIn("Would append adr_created: ADR-0.2.0", dry_run.output)
            self.assertNotIn("Would append obpi_created: OBPI-0.2.0-01-demo", dry_run.output)

            result = runner.invoke(main, ["register-adrs", "ADR-0.1.0", "--all"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.1.0", result.output)
            self.assertIn("Registered OBPI: OBPI-0.1.0-01-demo", result.output)
            self.assertNotIn("Registered OBPI: OBPI-0.2.0-01-demo", result.output)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event":"adr_created","id":"ADR-0.1.0"', ledger_content)
            self.assertIn('"event":"obpi_created","id":"OBPI-0.1.0-01-demo"', ledger_content)
            self.assertNotIn('"event":"adr_created","id":"ADR-0.2.0"', ledger_content)
            self.assertNotIn('"event":"obpi_created","id":"OBPI-0.2.0-01-demo"', ledger_content)

    def test_register_adrs_default_includes_versioned(self) -> None:
        """register-adrs without flags registers versioned (non-pool) ADRs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.5.0-sample"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.5.0-sample.md").write_text(
                "---\nid: ADR-0.5.0-sample\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n"
                "# ADR-0.5.0: Sample\n",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.5.0-sample", result.output)

    def test_register_adrs_pool_only_skips_versioned(self) -> None:
        """register-adrs --pool-only skips versioned ADRs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.6.0-sample"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.6.0-sample.md").write_text(
                "---\nid: ADR-0.6.0-sample\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n"
                "# ADR-0.6.0: Sample\n",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["register-adrs", "--pool-only"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No unregistered ADRs or OBPIs found.", result.output)

    def test_register_adrs_resolves_short_form_obpi_parent(self) -> None:
        """register-adrs resolves short-form parent (ADR-0.7.0) to full slug."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            # Create ADR with full slug
            adr_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.7.0-my-feature"
            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.7.0-my-feature.md").write_text(
                "---\nid: ADR-0.7.0-my-feature\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n"
                "# ADR-0.7.0: My Feature\n",
                encoding="utf-8",
            )
            # OBPI with short-form parent (the bug scenario)
            (obpi_dir / "OBPI-0.7.0-01-first-item.md").write_text(
                "---\n"
                "id: OBPI-0.7.0-01-first-item\n"
                "parent: ADR-0.7.0\n"
                "item: 1\n"
                "lane: lite\n"
                "status: Draft\n"
                "---\n\n"
                "# OBPI-0.7.0-01: First Item\n",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.7.0-my-feature", result.output)
            self.assertIn("Registered OBPI: OBPI-0.7.0-01-first-item", result.output)
            self.assertIn("short-form parent", result.output)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event":"obpi_created","id":"OBPI-0.7.0-01-first-item"', ledger_content)
            self.assertIn('"parent":"ADR-0.7.0-my-feature"', ledger_content)

    def test_register_adrs_warns_on_orphan_obpis(self) -> None:
        """register-adrs warns when ledger OBPIs have no file on disk (GHI #67)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            # Create ADR with one OBPI on disk
            adr_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.1.0-sample"
            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.1.0-sample.md").write_text(
                "---\nid: ADR-0.1.0-sample\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n"
                "# ADR-0.1.0: Sample\n",
                encoding="utf-8",
            )
            (obpi_dir / "OBPI-0.1.0-01-real.md").write_text(
                "---\n"
                "id: OBPI-0.1.0-01-real\n"
                "parent: ADR-0.1.0-sample\n"
                "item: 1\n"
                "lane: lite\n"
                "status: Draft\n"
                "---\n\n"
                "# OBPI-0.1.0-01: Real\n",
                encoding="utf-8",
            )

            # Register the ADR and its OBPI
            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered OBPI: OBPI-0.1.0-01-real", result.output)

            # Manually inject a phantom OBPI into the ledger (simulates rename
            # without artifact_renamed event)
            from gzkit.ledger import Ledger, obpi_created_event

            ledger = Ledger(Path(config.paths.ledger))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-old-slug", "ADR-0.1.0-sample"))

            # Re-run register — should warn about orphan
            result2 = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result2.exit_code, 0)
            self.assertIn("orphan", result2.output)
            self.assertIn("OBPI-0.1.0-01-old-slug", result2.output)

    def test_register_adrs_no_orphan_warning_for_withdrawn(self) -> None:
        """register-adrs does not warn about withdrawn OBPIs with no file (GHI #67)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.2.0-sample"
            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.2.0-sample.md").write_text(
                "---\nid: ADR-0.2.0-sample\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n"
                "# ADR-0.2.0: Sample\n",
                encoding="utf-8",
            )

            # Register ADR, then inject and withdraw a phantom OBPI
            runner.invoke(main, ["register-adrs"])

            from gzkit.ledger import Ledger, obpi_created_event
            from gzkit.ledger_events import obpi_withdrawn_event

            ledger = Ledger(Path(config.paths.ledger))
            ledger.append(obpi_created_event("OBPI-0.2.0-01-phantom", "ADR-0.2.0-sample"))
            ledger.append(
                obpi_withdrawn_event("OBPI-0.2.0-01-phantom", "ADR-0.2.0-sample", "superseded")
            )

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("orphan", result.output)

    def test_register_adrs_warns_on_stale_promoted_pool_file(self) -> None:
        """register-adrs warns when a pool file on disk maps to a promoted versioned ADR."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            # Create and register a pool ADR
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "ADR-pool.my-feature.md"
            pool_file.write_text(
                "---\nid: ADR-pool.my-feature\nstatus: Pool\nlane: lite\n---\n\n"
                "# ADR-pool.my-feature\n",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-pool.my-feature", result.output)

            # Simulate promotion: create versioned ADR and record rename event
            versioned_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.5.0-my-feature"
            versioned_dir.mkdir(parents=True, exist_ok=True)
            (versioned_dir / "ADR-0.5.0-my-feature.md").write_text(
                "---\nid: ADR-0.5.0-my-feature\nparent: PRD-GZKIT-1.0.0\nlane: heavy\n---\n\n"
                "# ADR-0.5.0: My Feature\n",
                encoding="utf-8",
            )

            from gzkit.ledger import Ledger, adr_created_event, artifact_renamed_event

            ledger = Ledger(Path(config.paths.ledger))
            ledger.append(adr_created_event("ADR-0.5.0-my-feature", "PRD-GZKIT-1.0.0", "heavy"))
            ledger.append(
                artifact_renamed_event(
                    old_id="ADR-pool.my-feature",
                    new_id="ADR-0.5.0-my-feature",
                    reason="pool_promotion",
                )
            )

            # Pool file still on disk (stale leftover)
            # Re-run register — should warn about stale pool file
            result2 = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result2.exit_code, 0)
            self.assertIn("stale", result2.output)
            self.assertIn("ADR-pool.my-feature", result2.output)
            self.assertIn("ADR-0.5.0-my-feature", result2.output)

    def test_register_adrs_warns_on_unresolvable_parent(self) -> None:
        """register-adrs warns when OBPI parent cannot be resolved."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            # Create ADR dir with an orphaned OBPI (no matching ADR)
            adr_dir = Path(config.paths.adrs) / "pre-release" / "ADR-0.8.0-orphan"
            obpi_dir = adr_dir / "obpis"
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.8.0-orphan.md").write_text(
                "---\nid: ADR-0.8.0-orphan\nparent: PRD-GZKIT-1.0.0\nlane: lite\n---\n\n"
                "# ADR-0.8.0: Orphan\n",
                encoding="utf-8",
            )
            # OBPI pointing to a non-existent parent
            (obpi_dir / "OBPI-0.9.0-01-wrong-parent.md").write_text(
                "---\n"
                "id: OBPI-0.9.0-01-wrong-parent\n"
                "parent: ADR-0.9.0\n"
                "item: 1\n"
                "lane: lite\n"
                "status: Draft\n"
                "---\n\n"
                "# OBPI-0.9.0-01: Wrong Parent\n",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["register-adrs"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Registered ADR: ADR-0.8.0-orphan", result.output)
            self.assertIn("Skipping OBPI-0.9.0-01-wrong-parent.md", result.output)
            self.assertNotIn("Registered OBPI: OBPI-0.9.0-01-wrong-parent", result.output)
