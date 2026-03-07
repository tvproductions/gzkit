import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    gate_checked_event,
)
from tests.commands.common import CliRunner


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

    def test_attest_heavy_requires_gate4(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
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
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
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

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn('"event":"attested","id":"ADR-pool.sample"', ledger_content)
