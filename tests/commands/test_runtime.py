import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    gate_checked_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


class TestAdrRuntimeCommands(unittest.TestCase):
    """Behavioral tests for closeout/audit-check/emit-receipt runtime surfaces."""

    @staticmethod
    def _write_obpi(
        path: Path,
        status: str,
        brief_status: str,
        implementation_line: str,
        *,
        lane: str = "Lite",
        key_proof: str = "uv run gz adr status ADR-0.1.0 --json",
        human_attestation: tuple[str, str, str] | None = None,
        allowed_paths: list[str] | None = None,
    ) -> None:
        allowlist = allowed_paths or [path.as_posix()]
        lines = [
            "---",
            "id: OBPI-0.1.0-01-demo",
            "parent: ADR-0.1.0",
            "item: 1",
            f"lane: {lane}",
            f"status: {status}",
            "---",
            "",
            "# OBPI-0.1.0-01-demo: Demo",
            "",
            f"**Brief Status:** {brief_status}",
            "",
            "## Allowed Paths",
            *(f"- `{allowed_path}` - in scope" for allowed_path in allowlist),
            "",
            "## Evidence",
            "",
            "### Implementation Summary",
            f"- Files created/modified: {implementation_line}",
            "- Validation commands run: uv run -m unittest discover tests",
            "- Date completed: 2026-02-14",
            "",
            "## Key Proof",
            key_proof,
            "",
        ]
        if human_attestation is not None:
            attestor, attestation, attestation_date = human_attestation
            lines.extend(
                [
                    "## Human Attestation",
                    f"- Attestor: {attestor}",
                    f"- Attestation: {attestation}",
                    f"- Date: {attestation_date}",
                    "",
                ]
            )
        path.write_text("\n".join(lines) + "\n")

    @staticmethod
    def _set_manifest_verification_noop() -> None:
        manifest_path = Path(".gzkit/manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["verification"] = {
            "test": "python -c \"print('ok')\"",
            "lint": "python -c \"print('ok')\"",
            "typecheck": "python -c \"print('ok')\"",
            "docs": "python -c \"print('ok')\"",
            "bdd": "python -c \"print('ok')\"",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))

    @staticmethod
    def _create_pool_adr(adr_id: str = "ADR-pool.sample") -> None:
        config = GzkitConfig.load(Path(".gzkit.json"))
        pool_dir = Path(config.paths.adrs) / "pool"
        pool_dir.mkdir(parents=True, exist_ok=True)
        pool_adr = pool_dir / f"{adr_id}.md"
        pool_adr.write_text(f"---\nid: {adr_id}\n---\n\n# {adr_id}\n")
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(adr_created_event(adr_id, "", "heavy"))

    def test_closeout_missing_adr_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["closeout", "ADR-9.9.9"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("ADR not found", result.output)

    def test_closeout_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _init_git_repo(Path.cwd())
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("closeout_initiated", ledger_content)
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_file = next(Path(config.paths.adrs).rglob("ADR-0.1.0.md"))
            closeout_form = adr_file.parent / "ADR-CLOSEOUT-FORM.md"
            self.assertTrue(closeout_form.exists())
            closeout_content = closeout_form.read_text(encoding="utf-8")
            self.assertIn("# ADR Closeout Form: ADR-0.1.0", closeout_content)
            self.assertIn("Awaiting explicit human attestation.", closeout_content)

    def test_closeout_dry_run_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("closeout_initiated", ledger_content)

    def test_closeout_includes_canonical_attestation_choices(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Completed - Partial: [reason]", result.output)
            self.assertIn("Dropped - [reason]", result.output)

    def test_closeout_heavy_includes_bdd_command_when_features_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 4 (BDD):", result.output)
            self.assertIn("uv run -m behave features/", result.output)
            self.assertNotIn("Gate 4 (BDD): N/A", result.output)

    def test_closeout_heavy_includes_bdd_command_when_features_exist(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            Path("features").mkdir(exist_ok=True)
            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 4 (BDD):", result.output)
            self.assertIn("uv run -m behave features/", result.output)

    def test_closeout_rejects_pool_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            self._create_pool_adr()
            result = runner.invoke(main, ["closeout", "ADR-pool.sample"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot be closed out", result.output)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn('"event":"closeout_initiated","id":"ADR-pool.sample"', ledger_content)

    def test_closeout_blocks_when_obpi_proof_is_incomplete(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="src/module.py",
            )

            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])

            self.assertEqual(result.exit_code, 1)
            self.assertIn("Closeout blocked:", result.output)
            self.assertIn("BLOCKERS:", result.output)
            self.assertIn(
                "OBPI-0.1.0-01-demo: ledger proof of completion is missing", result.output
            )
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("closeout_initiated", ledger_content)

    def test_closeout_json_includes_obpi_blockers(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="src/module.py",
            )

            result = runner.invoke(main, ["closeout", "ADR-0.1.0", "--json"])

            self.assertEqual(result.exit_code, 1)
            payload = json.loads(result.output)
            self.assertFalse(payload["allowed"])
            self.assertIn("OBPI-0.1.0-01-demo", payload["blockers"][0])
            self.assertEqual(payload["obpi_summary"]["total"], 1)
            self.assertEqual(payload["obpi_rows"][0]["id"], "OBPI-0.1.0-01-demo")
            self.assertIn(
                "uv run gz obpi reconcile OBPI-0.1.0-01-demo",
                payload["next_steps"],
            )
            self.assertIsNone(payload["event"])

    def test_closeout_blocks_heavy_obpi_missing_required_human_attestation(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
                lane="Heavy",
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
                    evidence={"attestation_requirement": "required"},
                )
            )

            result = runner.invoke(main, ["closeout", "ADR-0.1.0"])

            self.assertEqual(result.exit_code, 1)
            self.assertIn(
                "OBPI-0.1.0-01-demo: required human attestation evidence is missing",
                result.output,
            )

    def test_audit_pre_attestation_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Audit blocked", result.output)

    def test_audit_after_attestation_writes_artifacts(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            self._set_manifest_verification_noop()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            attestation = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertEqual(attestation.exit_code, 0)

            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/adr/audit/AUDIT.md").exists())
            self.assertTrue(Path("design/adr/audit/AUDIT_PLAN.md").exists())
            self.assertTrue(Path("design/adr/audit/proofs/test.txt").exists())

    def test_audit_dry_run_after_attestation_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            self._set_manifest_verification_noop()
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
            attestation = runner.invoke(main, ["attest", "ADR-0.1.0", "--status", "completed"])
            self.assertEqual(attestation.exit_code, 0)

            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path("design/adr/audit").exists())

    def test_audit_rejects_pool_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            self._create_pool_adr()
            result = runner.invoke(main, ["audit", "ADR-pool.sample"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot be audited", result.output)

    def test_adr_audit_check_passes_for_completed_obpi_with_evidence(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
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
                    evidence={
                        "value_narrative": "The OBPI completed with canonical receipt evidence.",
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                    },
                )
            )
            result = runner.invoke(main, ["adr", "audit-check", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("PASS", result.output)

    def test_adr_audit_check_fails_for_incomplete_obpi(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
            )
            result = runner.invoke(main, ["adr", "audit-check", "ADR-0.1.0"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("FAIL", result.output)

    def test_adr_audit_check_rejects_pool_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            self._create_pool_adr()
            result = runner.invoke(main, ["adr", "audit-check", "ADR-pool.sample"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot be audit-checked", result.output)

    def test_adr_covers_check_passes_for_adr_and_linked_obpi(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])

            tests_dir = Path("tests")
            tests_dir.mkdir(parents=True, exist_ok=True)
            (tests_dir / "test_traceability.py").write_text(
                "\n".join(
                    [
                        '@covers("ADR-0.1.0")',
                        '@covers("OBPI-0.1.0-01-demo")',
                        '@covers("REQ-0.1.0-01-01")',
                        '@covers("REQ-0.1.0-01-02")',
                        '@covers("REQ-0.1.0-01-03")',
                        "def test_traceability():",
                        "    pass",
                        "",
                    ]
                )
            )

            result = runner.invoke(main, ["adr", "covers-check", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("PASS", result.output)

    def test_adr_covers_check_fails_when_obpi_cover_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])

            tests_dir = Path("tests")
            tests_dir.mkdir(parents=True, exist_ok=True)
            (tests_dir / "test_traceability.py").write_text(
                "\n".join(
                    [
                        '@covers("ADR-0.1.0")',
                        "def test_traceability():",
                        "    pass",
                        "",
                    ]
                )
            )

            result = runner.invoke(main, ["adr", "covers-check", "ADR-0.1.0", "--json"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('"passed": false', result.output)
            self.assertIn("OBPI-0.1.0-01-demo", result.output)

    def test_adr_covers_check_fails_when_criterion_missing_req_id(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])

            obpi_file = next(Path(".").rglob("OBPI-0.1.0-01-demo.md"))
            content = obpi_file.read_text(encoding="utf-8")
            content = content.replace(
                "REQ-0.1.0-01-01: Given/When/Then behavior criterion 1",
                "Given/When/Then behavior criterion 1",
            )
            obpi_file.write_text(content)

            tests_dir = Path("tests")
            tests_dir.mkdir(parents=True, exist_ok=True)
            (tests_dir / "test_traceability.py").write_text(
                "\n".join(
                    [
                        '@covers("ADR-0.1.0")',
                        '@covers("OBPI-0.1.0-01-demo")',
                        '@covers("REQ-0.1.0-01-02")',
                        '@covers("REQ-0.1.0-01-03")',
                        "def test_traceability():",
                        "    pass",
                        "",
                    ]
                )
            )

            result = runner.invoke(main, ["adr", "covers-check", "ADR-0.1.0", "--json"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('"criteria_without_req_ids"', result.output)

    def test_adr_emit_receipt_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-0.1.0",
                    "--event",
                    "validated",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    '{"gate":5}',
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("audit_receipt_emitted", ledger_content)

    def test_adr_emit_receipt_invalid_json_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-0.1.0",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    "{bad json}",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid --evidence-json", result.output)

    def test_adr_emit_receipt_dry_run_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-0.1.0",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("audit_receipt_emitted", ledger_content)

    def test_adr_emit_receipt_rejects_pool_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            self._create_pool_adr()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "emit-receipt",
                    "ADR-pool.sample",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot be issued receipts", result.output)

    def test_obpi_emit_receipt_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "validated",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    '{"acceptance":"observed"}',
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("obpi_receipt_emitted", ledger_content)
            self.assertIn('"id":"OBPI-0.1.0-01-demo"', ledger_content)

    def test_obpi_emit_receipt_invalid_json_fails(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    "{bad json}",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid --evidence-json", result.output)

    def test_obpi_emit_receipt_dry_run_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    (
                        '{"value_narrative":"before/after capability",'
                        '"key_proof":"uv run gz status --table"}'
                    ),
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("obpi_receipt_emitted", ledger_content)

    def test_obpi_emit_receipt_completed_requires_evidence(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("require --evidence-json", result.output)

    def test_obpi_emit_receipt_completed_heavy_requires_human_attestation_evidence(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0", "--lane", "heavy"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    (
                        '{"value_narrative":"capability now exists",'
                        '"key_proof":"uv run gz adr status ADR-0.1.0 --json"}'
                    ),
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("human_attestation=true", result.output)

    def test_obpi_emit_receipt_completed_heavy_records_attested_completion(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            runner.invoke(main, ["specify", "demo", "--parent", "ADR-0.1.0", "--lane", "heavy"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    (
                        '{"value_narrative":"manual completion now auditable",'
                        '"key_proof":"uv run gz status --table",'
                        '"human_attestation":true,'
                        '"attestation_text":"attest completed",'
                        '"attestation_date":"2026-03-01"}'
                    ),
                ],
            )
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"obpi_completion":"attested_completed"', ledger_content)
            self.assertIn('"req_proof_inputs"', ledger_content)

    def test_obpi_emit_receipt_lite_obpi_under_heavy_parent_requires_human_attestation(
        self,
    ) -> None:
        """Lite-lane OBPI under Heavy parent inherits parent attestation rigor."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path("."))
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="src/demo.py",
                lane="Lite",
                human_attestation=("human:jeff", "attest completed", "2026-03-21"),
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    (
                        '{"value_narrative":"vendor manifest schema implemented",'
                        '"key_proof":"config.vendors.claude.enabled returns True",'
                        '"human_attestation":true,'
                        '"attestation_text":"attest completed",'
                        '"attestation_date":"2026-03-21"}'
                    ),
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"obpi_completion":"attested_completed"', ledger_content)

    def test_obpi_emit_receipt_completed_enriches_structured_receipt_context(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "0.1.0", "--lane", "heavy"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line=(
                    "docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-0.1.0-01-demo.md"
                ),
                lane="Heavy",
                human_attestation=("human:jeff", "attest completed", "2026-03-11"),
                allowed_paths=[obpi_path.as_posix()],
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))
            evidence_json = json.dumps(
                {
                    "value_narrative": ("manual completion now captures structured scope evidence"),
                    "key_proof": "uv run gz obpi status OBPI-0.1.0-01-demo --json",
                    "human_attestation": True,
                    "attestation_text": "attest completed",
                    "attestation_date": "2026-03-11",
                }
            )

            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-0.1.0-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                    "--evidence-json",
                    evidence_json,
                ],
            )

            self.assertEqual(result.exit_code, 0)
            entries = [
                json.loads(line)
                for line in Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
                if line
            ]
            receipt = [entry for entry in entries if entry["event"] == "obpi_receipt_emitted"][-1]
            evidence = receipt["evidence"]
            self.assertEqual(evidence["recorder_source"], "cli:obpi_emit_receipt")
            self.assertEqual(evidence["scope_audit"]["allowlist"], [obpi_path.as_posix()])
            self.assertIsInstance(evidence["scope_audit"]["changed_files"], list)
            self.assertIsInstance(evidence["scope_audit"]["out_of_scope_files"], list)
            self.assertIn("git_sync_state", evidence)
            self.assertIn("recorder_warnings", evidence)
            self.assertTrue(evidence["recorder_warnings"])
            self.assertTrue(
                any("Not a git repository." in warning for warning in evidence["recorder_warnings"])
            )
            self.assertNotIn("anchor", receipt)

    def test_obpi_emit_receipt_rejects_pool_linked_obpi(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            self._create_pool_adr()
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "pool" / "OBPI-pool.sample-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            obpi_path.write_text(
                "---\n"
                "id: OBPI-pool.sample-01-demo\n"
                "parent: ADR-pool.sample\n"
                "item: 1\n"
                "lane: Heavy\n"
                "status: Completed\n"
                "---\n\n"
                "# OBPI-pool.sample-01-demo\n"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-pool.sample-01-demo", "ADR-pool.sample"))

            result = runner.invoke(
                main,
                [
                    "obpi",
                    "emit-receipt",
                    "OBPI-pool.sample-01-demo",
                    "--event",
                    "completed",
                    "--attestor",
                    "human:jeff",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool-linked OBPIs cannot be issued receipts", result.output)
