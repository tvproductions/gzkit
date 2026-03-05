import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    attested_event,
    audit_receipt_emitted_event,
    gate_checked_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)
from tests.commands.common import CliRunner, _write_obpi


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

    def test_status_show_gates_shows_gate2_pass_from_ledger(self) -> None:
        """status --show-gates shows Gate 2 PASS when latest gate check passed."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["status", "--show-gates"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):   PASS", result.output)

    def test_status_show_gates_shows_gate2_fail_from_ledger(self) -> None:
        """status --show-gates shows Gate 2 FAIL when latest gate check failed."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "fail", "test", 1))

            result = runner.invoke(main, ["status", "--show-gates"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):   FAIL", result.output)

    def test_status_default_hides_gate_breakdown(self) -> None:
        """status output is OBPI/QC centric by default without gate rows."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("QC Readiness:", result.output)
            self.assertNotIn("Gate 2 (TDD):", result.output)

    def test_status_table_shows_adr_status_columns(self) -> None:
        """status --table renders a stable ADR summary table."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            result = runner.invoke(main, ["status", "--table"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR Status", result.output)
            self.assertIn("Lifecycle", result.output)
            self.assertIn("Lane", result.output)
            self.assertIn("OBPI Unit", result.output)
            self.assertIn("Pending Checks", result.output)
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("0/0", result.output)
            self.assertIn("TDD", result.output)

    def test_status_table_blocks_ready_on_incomplete_obpis(self) -> None:
        """status --table marks QC pending when linked OBPIs are incomplete."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            obpi_path.write_text(
                "\n".join(
                    [
                        "---",
                        "id: OBPI-0.1.0-01-demo",
                        "parent: ADR-0.1.0",
                        "item: 1",
                        "lane: Lite",
                        "status: Draft",
                        "---",
                        "",
                        "# OBPI-0.1.0-01-demo: Demo",
                        "",
                        "**Brief Status:** Draft",
                        "",
                        "## Evidence",
                        "",
                        "### Implementation Summary",
                        "- Placeholder",
                        "",
                    ]
                )
                + "\n"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["status", "--table"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(
                "| ADR-0.1.0 | Pending | LITE | 0/1 | PENDING | PENDING | OBPI completion |",
                result.output,
            )

    def test_status_shows_obpi_completion_summary(self) -> None:
        """status renders OBPI completion as the primary unit."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            obpi_path.write_text(
                "\n".join(
                    [
                        "---",
                        "id: OBPI-0.1.0-01-demo",
                        "parent: ADR-0.1.0",
                        "item: 1",
                        "lane: Lite",
                        "status: Completed",
                        "---",
                        "",
                        "# OBPI-0.1.0-01-demo: Demo",
                        "",
                        "**Brief Status:** Completed",
                        "",
                        "## Evidence",
                        "",
                        "### Implementation Summary",
                        "- Files created/modified: src/module.py",
                        "",
                    ]
                )
                + "\n"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))
            ledger.append(
                obpi_receipt_emitted_event(
                    obpi_id="OBPI-0.1.0-01-demo",
                    parent_adr="ADR-0.1.0",
                    receipt_event="completed",
                    attestor="human:test",
                    obpi_completion="completed",
                )
            )

            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("OBPI Unit:       COMPLETED", result.output)
            self.assertIn("OBPI Completion: 1/1 complete", result.output)
            self.assertIn("all linked OBPIs completed with evidence", result.output)


class TestLifecycleStatusSemantics(unittest.TestCase):
    """Tests for derived lifecycle semantics on status/state surfaces."""

    def test_adr_status_default_hides_gate_breakdown(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("QC Readiness:", result.output)
            self.assertNotIn("Gate 2 (TDD):", result.output)

    def test_adr_status_accepts_semver_prefix_for_suffixed_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_path = Path(config.paths.adrs) / "ADR-0.5.0-skill-lifecycle-governance.md"
            adr_path.parent.mkdir(parents=True, exist_ok=True)
            adr_path.write_text(
                "---\n"
                "id: ADR-0.5.0-skill-lifecycle-governance\n"
                "---\n\n"
                "# ADR-0.5.0: skill-lifecycle-governance\n"
            )

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.5.0-skill-lifecycle-governance", "", "heavy"))

            result = runner.invoke(main, ["adr", "status", "0.5.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR-0.5.0-skill-lifecycle-governance", result.output)

    def test_adr_status_show_gates_includes_gate_breakdown(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--show-gates"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):", result.output)

    def test_adr_status_heavy_features_missing_reports_gate4_pending(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["gates"]["4"], "pending")
            self.assertNotIn("gate4_na_reason", payload)

    def test_adr_status_legacy_semver_id_still_resolves(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init", "--mode", "heavy"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_path = Path(config.paths.adrs) / "ADR-0.2.0-gate-verification.md"
            adr_path.parent.mkdir(parents=True, exist_ok=True)
            adr_path.write_text(
                "---\nid: ADR-0.2.0\nlane: heavy\n---\n\n# ADR-0.2.0: Gate Verification\n"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.2.0", "", "heavy"))

            result = runner.invoke(main, ["adr", "status", "ADR-0.2.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["adr"], "ADR-0.2.0")

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

    def test_adr_status_json_obpi_incomplete_overrides_completed_lifecycle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "human"))

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["lifecycle_status"], "Pending")
            self.assertEqual(payload["closeout_phase"], "attested")
            self.assertEqual(payload["attestation_term"], "Completed")
            self.assertEqual(payload["obpi_summary"]["unit_status"], "pending")

    def test_adr_status_qc_readiness_includes_obpi_completion_blocker(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("QC Readiness: PENDING (pending: OBPI completion)", result.output)

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

    def test_status_json_obpi_incomplete_overrides_completed_lifecycle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "completed", "human"))

            result = runner.invoke(main, ["status", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-0.1.0"]
            self.assertEqual(adr_payload["lifecycle_status"], "Pending")
            self.assertEqual(adr_payload["closeout_phase"], "attested")
            self.assertEqual(adr_payload["attestation_term"], "Completed")
            self.assertEqual(adr_payload["obpi_summary"]["unit_status"], "pending")

    def test_status_json_includes_obpi_summary_fields(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
            )

            result = runner.invoke(main, ["status", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-0.1.0"]
            self.assertIn("obpis", adr_payload)
            self.assertIn("obpi_summary", adr_payload)
            self.assertEqual(adr_payload["obpi_summary"]["total"], 1)
            self.assertEqual(adr_payload["obpi_summary"]["completed"], 0)
            self.assertEqual(adr_payload["obpi_summary"]["unit_status"], "pending")

    def test_status_json_completed_status_with_empty_summary_stays_incomplete(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            obpi_path.write_text(
                "\n".join(
                    [
                        "---",
                        "id: OBPI-0.1.0-01-demo",
                        "parent: ADR-0.1.0",
                        "item: 1",
                        "lane: Lite",
                        "status: Completed",
                        "---",
                        "",
                        "# OBPI-0.1.0-01-demo: Demo",
                        "",
                        "**Brief Status:** Completed",
                        "",
                        "## Evidence",
                        "",
                        "### Implementation Summary",
                        "- Files created/modified:",
                        "- Tests added:",
                        "- Date completed:",
                        "",
                    ]
                )
                + "\n"
            )

            result = runner.invoke(main, ["status", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-0.1.0"]
            self.assertEqual(adr_payload["obpi_summary"]["completed"], 0)
            self.assertEqual(adr_payload["obpi_summary"]["unit_status"], "pending")
            self.assertIn(
                "implementation evidence is missing or placeholder",
                adr_payload["obpis"][0]["issues"],
            )

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
            self.assertEqual(payload["obpis"], [])

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
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))
            ledger.append(
                obpi_receipt_emitted_event(
                    obpi_id="OBPI-0.1.0-01-demo",
                    parent_adr="ADR-0.1.0",
                    receipt_event="completed",
                    attestor="human:test",
                    obpi_completion="completed",
                )
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
