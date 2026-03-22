import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    gate_checked_event,
)
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


class TestAttestSemantics(unittest.TestCase):
    """Tests for strict attestation prerequisites and canonical term mapping."""

    def test_attest_lite_requires_gate2(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Gate 2 must pass", result.output)

    def test_attest_heavy_requires_gate3(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Gate 3 must pass", result.output)

    def test_attest_heavy_requires_gate4(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 3, "pass", "docs", 0))

            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Gate 4 must pass", result.output)

    def test_attest_force_bypass_requires_reason(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
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
            _init_git_repo(Path.cwd())
            _quick_init()
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
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("attested", ledger_content)
            self.assertIn("manual override for reconciliation", ledger_content)

    def test_attest_updates_adr_attestation_block_and_closeout_form(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 3, "pass", "docs", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 4, "pass", "bdd", 0))

            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertEqual(result.exit_code, 0)

            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file = next(Path(config.paths.adrs).rglob("ADR-0.1.0.md"))
            adr_content = adr_file.read_text(encoding="utf-8")
            self.assertIn("| 0.1.0 | Completed | Test User |", adr_content)
            self.assertNotIn("| 0.1.0 | Pending | | | |", adr_content)

            closeout_form = adr_file.parent / "ADR-CLOSEOUT-FORM.md"
            self.assertTrue(closeout_form.exists())
            closeout_content = closeout_form.read_text(encoding="utf-8")
            self.assertIn("**Status**: Phase 2 — Completed", closeout_content)
            self.assertIn("- `completed`", closeout_content)
            self.assertIn("**Attested by**: Test User", closeout_content)

    def test_attest_rejects_pool_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
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

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn('"event":"attested","id":"ADR-pool.sample"', ledger_content)

    def test_attest_completed_blocks_on_incomplete_obpis(self) -> None:
        """Attestation as completed is blocked when OBPIs are not done."""
        from gzkit.ledger import obpi_created_event  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])

            # Register an OBPI so the ADR has incomplete work
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-test", "ADR-0.1.0"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            # Create the OBPI file in Draft status
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file = next(Path(config.paths.adrs).rglob("ADR-0.1.0*.md"))
            obpis_dir = adr_file.parent / "obpis"
            obpis_dir.mkdir(parents=True, exist_ok=True)
            obpi_file = obpis_dir / "OBPI-0.1.0-01-test.md"
            obpi_file.write_text(
                "---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
                "item: 1\nlane: lite\nstatus: Draft\n---\n\n# OBPI-0.1.0-01-test\n"
            )

            result = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("OBPI(s) are not completed", result.output)

    def test_attest_completed_force_bypasses_obpi_check(self) -> None:
        """Force flag allows attestation despite incomplete OBPIs."""
        from gzkit.ledger import obpi_created_event  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-test", "ADR-0.1.0"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file = next(Path(config.paths.adrs).rglob("ADR-0.1.0*.md"))
            obpis_dir = adr_file.parent / "obpis"
            obpis_dir.mkdir(parents=True, exist_ok=True)
            obpi_file = obpis_dir / "OBPI-0.1.0-01-test.md"
            obpi_file.write_text(
                "---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
                "item: 1\nlane: lite\nstatus: Draft\n---\n\n# OBPI-0.1.0-01-test\n"
            )

            result = runner.invoke(
                main,
                [
                    "attest",
                    "ADR-0.1.0",
                    "--status",
                    "completed",
                    "--force",
                    "--reason",
                    "retroactive booking",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Attestation recorded", result.output)
