"""Tests for the end-to-end audit pipeline.

Covers OBPI-0.19.0-02, OBPI-0.19.0-04, OBPI-0.19.0-05, and OBPI-0.19.0-06.

Verifies that ``gz audit ADR-X.Y.Z`` emits a validation receipt,
transitions the ADR to Validated when all checks pass, preserves
the attestation guard, enriches AUDIT.md with attestation record,
gate results, and evidence links, and renders from templates with
evidence aggregated from the ledger.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import _write_audit_artifacts, main
from gzkit.commands.common import aggregate_audit_evidence
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    attested_event,
    closeout_initiated_event,
    gate_checked_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)
from gzkit.quality import QualityResult
from gzkit.templates import load_template
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _make_qr(success: bool = True, command: str = "test", returncode: int = 0) -> QualityResult:
    return QualityResult(
        success=success,
        command=command,
        stdout="OK" if success else "",
        stderr="" if success else "FAIL",
        returncode=returncode,
    )


def _setup_attested_adr(runner: CliRunner) -> None:
    """Create an ADR that has been attested (ready for audit)."""
    _init_git_repo(Path.cwd())
    _quick_init()
    runner.invoke(main, ["plan", "0.1.0"])
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
    ledger.append(attested_event("ADR-0.1.0", "completed", "Test User"))


class TestAuditAttestationGuard(unittest.TestCase):
    """Audit blocks when ADR is not attested (REQ-01, REQ-09)."""

    def test_audit_blocks_without_attestation(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("attestation", result.output.lower())


class TestAuditArtifacts(unittest.TestCase):
    """Audit creates artifacts and runs commands (REQ-02)."""

    @patch("gzkit.cli.run_command")
    def test_audit_creates_artifacts(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            adr_dir = next(Path("design/adr").rglob("ADR-0.1.0*.md")).parent
            audit_dir = adr_dir / "audit"
            self.assertTrue(audit_dir.exists())
            self.assertTrue((audit_dir / "AUDIT_PLAN.md").exists())
            self.assertTrue((audit_dir / "AUDIT.md").exists())
            self.assertTrue((audit_dir / "proofs").exists())


class TestAuditReceiptEmission(unittest.TestCase):
    """Audit emits a validation receipt to the ledger (REQ-03)."""

    @patch("gzkit.cli.run_command")
    def test_validation_receipt_in_ledger(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("audit_receipt_emitted", ledger_text)
            self.assertIn("validated", ledger_text)


class TestAuditStatusTransition(unittest.TestCase):
    """Audit transitions ADR to Validated when all pass (REQ-04)."""

    @patch("gzkit.cli.run_command")
    def test_adr_transitions_to_validated(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("lifecycle_transition", ledger_text)
            self.assertIn("Validated", ledger_text)


class TestAuditFailureNoTransition(unittest.TestCase):
    """Audit does NOT transition ADR on failure (REQ-05, REQ-08)."""

    @patch("gzkit.cli.run_command")
    def test_no_transition_on_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            # Receipt should still be emitted (with failure recorded)
            self.assertIn("audit_receipt_emitted", ledger_text)
            # But no lifecycle transition
            self.assertNotIn("lifecycle_transition", ledger_text)

    @patch("gzkit.cli.run_command")
    def test_artifacts_still_written_on_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            runner.invoke(main, ["audit", "ADR-0.1.0"])
            adr_dir = next(Path("design/adr").rglob("ADR-0.1.0*.md")).parent
            self.assertTrue((adr_dir / "audit" / "AUDIT.md").exists())


class TestAuditDryRun(unittest.TestCase):
    """--dry-run shows full plan without executing (REQ-06)."""

    def test_dry_run_shows_receipt_and_transition_plan(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Dry run", result.output)
            self.assertIn("receipt", result.output.lower())
            self.assertIn("Validated", result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("audit_receipt_emitted", ledger_text)

    def test_dry_run_json_includes_receipt_and_transition(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("validation_receipt", data)
            self.assertIn("status_transition", data)


class TestAuditJsonOutput(unittest.TestCase):
    """--json emits structured output with all stages (REQ-07)."""

    @patch("gzkit.cli.run_command")
    def test_json_contains_all_fields(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("results", data)
            self.assertIn("validation_receipt", data)
            self.assertIn("status_transition", data)
            self.assertTrue(data["passed"])


# ---------------------------------------------------------------------------
# OBPI-0.19.0-04: Enrichment tests (attestation record, gate results, evidence links)
# ---------------------------------------------------------------------------


def _make_ledger_with_events(ledger_path: Path, adr_id: str) -> Ledger:
    """Create a ledger populated with attested and gate_checked events."""
    ledger = Ledger(ledger_path)
    ledger.append(gate_checked_event(adr_id, 2, "pass", "uv run gz test", 0))
    ledger.append(gate_checked_event(adr_id, 5, "pass", "uv run gz lint", 0))
    ledger.append(attested_event(adr_id, "completed", "human:Jeff"))
    return ledger


def _call_write_audit_artifacts(
    tmp: Path,
    adr_id: str = "ADR-0.19.0",
    ledger: Ledger | None = None,
    result_rows: list | None = None,
    create_obpi_files: bool = False,
    create_closeout_form: bool = False,
) -> tuple[Path, Path, dict]:
    """Set up directory structure and call _write_audit_artifacts."""
    project_root = tmp
    adr_dir = tmp / "docs" / "design" / "adr" / "ADR-0.19.0-test"
    adr_file = adr_dir / f"{adr_id}-some-title.md"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file.write_text("# ADR\n", encoding="utf-8")

    if create_obpi_files:
        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        (obpi_dir / "OBPI-0.19.0-01-first.md").write_text("# OBPI\n", encoding="utf-8")
        (obpi_dir / "OBPI-0.19.0-02-second.md").write_text("# OBPI\n", encoding="utf-8")

    if create_closeout_form:
        closeout_dir = adr_dir / "closeout"
        closeout_dir.mkdir(parents=True, exist_ok=True)
        (closeout_dir / "CLOSEOUT.md").write_text("# Closeout\n", encoding="utf-8")

    audit_dir = adr_dir / "audit"
    proofs_dir = audit_dir / "proofs"
    proofs_dir.mkdir(parents=True, exist_ok=True)

    if result_rows is None:
        result_rows = [
            {
                "label": "Lint",
                "command": "uv run gz lint",
                "success": True,
                "returncode": 0,
                "proof_file": "design/adr/ADR-0.19.0-test/audit/proofs/lint.txt",
            }
        ]

    plan_file, audit_file, enrichment = _write_audit_artifacts(
        adr_id=adr_id,
        adr_file=adr_file,
        audit_dir=audit_dir,
        proofs_dir=proofs_dir,
        result_rows=result_rows,
        project_root=project_root,
        ledger=ledger,
    )
    return plan_file, audit_file, enrichment


class TestAuditMdAttestationRecord(unittest.TestCase):
    """REQ-01: AUDIT.md must contain an Attestation Record section."""

    def test_attestation_section_rendered_with_event(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_events(ledger_path, "ADR-0.19.0")
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Attestation Record", content)
            self.assertIn("human:Jeff", content)
            self.assertIn("completed", content)

    def test_attestation_section_fallback_when_no_event(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)  # empty ledger
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Attestation Record", content)
            self.assertIn("No attestation record found", content)


class TestAuditMdGateResults(unittest.TestCase):
    """REQ-02: AUDIT.md must contain a Gate Results section."""

    def test_gate_results_table_rendered(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_events(ledger_path, "ADR-0.19.0")
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Gate Results", content)
            self.assertIn("| Gate |", content)
            self.assertIn("uv run gz test", content)
            self.assertIn("uv run gz lint", content)

    def test_gate_results_note_when_no_events(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)  # no gate events
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Gate Results", content)
            self.assertIn("No prior gate results recorded", content)


class TestAuditMdEvidenceLinks(unittest.TestCase):
    """REQ-03: AUDIT.md must contain an Evidence Links section."""

    def test_obpi_files_listed(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)
            _, audit_file, _ = _call_write_audit_artifacts(
                tmp, ledger=ledger, create_obpi_files=True
            )
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Evidence Links", content)
            self.assertIn("OBPI-0.19.0-01-first.md", content)
            self.assertIn("OBPI-0.19.0-02-second.md", content)

    def test_closeout_form_listed_when_present(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)
            _, audit_file, _ = _call_write_audit_artifacts(
                tmp, ledger=ledger, create_obpi_files=True, create_closeout_form=True
            )
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Evidence Links", content)
            self.assertIn("Closeout:", content)
            self.assertIn("CLOSEOUT.md", content)

    def test_evidence_links_use_forward_slashes(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)
            _, audit_file, _ = _call_write_audit_artifacts(
                tmp, ledger=ledger, create_obpi_files=True
            )
            content = audit_file.read_text(encoding="utf-8")
            # Paths in the Evidence Links section must use forward slashes
            self.assertNotIn("\\", content)

    def test_no_evidence_links_note_when_empty(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Evidence Links", content)
            self.assertIn("No evidence links found", content)


class TestAuditEnrichmentJsonKeys(unittest.TestCase):
    """REQ-04: JSON output must contain enrichment keys alongside existing keys."""

    @patch("gzkit.cli.run_command")
    def test_json_output_contains_enrichment_keys(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("attestation_record", data)
            self.assertIn("gate_results", data)
            self.assertIn("evidence_links", data)

    @patch("gzkit.cli.run_command")
    def test_json_output_preserves_existing_keys(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            # Existing keys must be preserved unchanged
            self.assertIn("adr", data)
            self.assertIn("audit_file", data)
            self.assertIn("audit_plan_file", data)
            self.assertIn("results", data)
            self.assertIn("passed", data)

    @patch("gzkit.cli.run_command")
    def test_attestation_record_has_correct_fields(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            rec = data["attestation_record"]
            self.assertIn("attestor", rec)
            self.assertIn("status", rec)
            self.assertIn("timestamp", rec)
            self.assertEqual(rec["attestor"], "Test User")
            self.assertEqual(rec["status"], "completed")

    @patch("gzkit.cli.run_command")
    def test_gate_results_list_has_correct_structure(self, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            gate_results = data["gate_results"]
            self.assertIsInstance(gate_results, list)
            self.assertGreaterEqual(len(gate_results), 1)
            first = gate_results[0]
            self.assertIn("gate", first)
            self.assertIn("status", first)
            self.assertIn("command", first)
            self.assertIn("returncode", first)


class TestAuditGeneratedLedgerEvent(unittest.TestCase):
    """audit_cmd() appends audit_generated event to ledger (OBPI-0.19.0-05)."""

    @patch("gzkit.cli.run_command")
    def test_audit_generated_event_in_ledger(self, mock_run):
        """Successful audit appends audit_generated with correct fields."""
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"audit_generated"', ledger_text)
            # Parse the specific event
            events = [json.loads(line) for line in ledger_text.strip().splitlines()]
            audit_events = [e for e in events if e["event"] == "audit_generated"]
            self.assertEqual(len(audit_events), 1)
            evt = audit_events[0]
            self.assertEqual(evt["id"], "ADR-0.1.0")
            self.assertIn("AUDIT.md", evt["audit_file"])
            self.assertIn("AUDIT_PLAN.md", evt["audit_plan_file"])
            self.assertTrue(evt["passed"])

    @patch("gzkit.cli.run_command")
    def test_audit_generated_passed_false_on_failure(self, mock_run):
        """Failed verification records passed=False in audit_generated event."""
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            runner.invoke(main, ["audit", "ADR-0.1.0"])
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            events = [json.loads(line) for line in ledger_text.strip().splitlines()]
            audit_events = [e for e in events if e["event"] == "audit_generated"]
            self.assertEqual(len(audit_events), 1)
            self.assertFalse(audit_events[0]["passed"])

    def test_dry_run_no_audit_generated_event(self):
        """--dry-run does NOT append audit_generated event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _setup_attested_adr(runner)
            result = runner.invoke(main, ["audit", "ADR-0.1.0", "--dry-run"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("audit_generated", ledger_text)

    def test_attestation_blocker_no_audit_generated_event(self):
        """Attestation blocker (exit 1) does NOT append audit_generated event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])
            # No attestation — should block
            result = runner.invoke(main, ["audit", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("audit_generated", ledger_text)


# ---------------------------------------------------------------------------
# OBPI-0.19.0-06: Audit templates and evidence aggregation from ledger
# ---------------------------------------------------------------------------


class TestAuditTemplatesExist(unittest.TestCase):
    """REQ-0.19.0-06-01: audit.md and audit_plan.md templates exist with .format() placeholders."""

    def test_audit_template_exists_and_has_placeholders(self):
        content = load_template("audit")
        for placeholder in (
            "{adr_id}",
            "{adr_path}",
            "{attestation_section}",
            "{gate_results_section}",
            "{obpi_summary_section}",
            "{verification_results_section}",
            "{evidence_links_section}",
        ):
            self.assertIn(placeholder, content, f"Missing placeholder: {placeholder}")

    def test_audit_plan_template_exists_and_has_placeholders(self):
        content = load_template("audit_plan")
        for placeholder in (
            "{adr_id}",
            "{adr_path}",
            "{verification_commands_section}",
            "{proofs_dir}",
        ):
            self.assertIn(placeholder, content, f"Missing placeholder: {placeholder}")

    def test_templates_use_format_not_jinja(self):
        """Templates must NOT use Jinja2 syntax (REQ-06: NEVER)."""
        for name in ("audit", "audit_plan"):
            content = load_template(name)
            self.assertNotIn("{%", content, f"{name} template contains Jinja2 block tag")
            self.assertNotIn("{{", content, f"{name} template contains Jinja2 variable tag")


def _make_ledger_with_obpis(ledger_path: Path, adr_id: str) -> Ledger:
    """Create a ledger with ADR, child OBPIs, gate checks, attestation, and closeout."""
    ledger = Ledger(ledger_path)
    ledger.append(adr_created_event(adr_id, "lite", "test-slug"))
    for i in range(1, 4):
        obpi_id = f"OBPI-0.19.0-{i:02d}"
        ledger.append(obpi_created_event(obpi_id, adr_id))
        if i <= 2:
            ledger.append(
                obpi_receipt_emitted_event(
                    obpi_id,
                    receipt_event="completed",
                    attestor="agent",
                    parent_adr=adr_id,
                    obpi_completion="completed",
                )
            )
    ledger.append(gate_checked_event(adr_id, 2, "pass", "uv run gz test", 0))
    ledger.append(gate_checked_event(adr_id, 5, "pass", "uv run gz lint", 0))
    ledger.append(attested_event(adr_id, "completed", "human:Jeff"))
    ledger.append(closeout_initiated_event(adr_id, by="agent", mode="standard"))
    return ledger


class TestAggregateAuditEvidence(unittest.TestCase):
    """REQ-0.19.0-06-02 / REQ-0.19.0-06-04 / REQ-0.19.0-06-05:
    aggregate_audit_evidence returns correct keys, includes OBPI completions,
    and is deterministic.
    """

    def test_returns_all_required_keys(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            graph = ledger.get_artifact_graph()
            result = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            self.assertIn("obpi_completions", result)
            self.assertIn("gate_results", result)
            self.assertIn("attestation", result)
            self.assertIn("closeout", result)

    def test_obpi_completions_lists_all_children(self):
        """REQ-04: Three OBPIs, two completed."""
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            graph = ledger.get_artifact_graph()
            result = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            completions = result["obpi_completions"]
            self.assertEqual(len(completions), 3)
            completed_ids = [c["obpi_id"] for c in completions if c["ledger_completed"]]
            self.assertEqual(len(completed_ids), 2)
            # Each entry has required fields
            for c in completions:
                self.assertIn("obpi_id", c)
                self.assertIn("receipt_event", c)
                self.assertIn("ledger_completed", c)

    def test_gate_results_structure(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            graph = ledger.get_artifact_graph()
            result = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            self.assertEqual(len(result["gate_results"]), 2)
            for gr in result["gate_results"]:
                self.assertIn("gate", gr)
                self.assertIn("status", gr)
                self.assertIn("command", gr)
                self.assertIn("returncode", gr)

    def test_attestation_populated(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            graph = ledger.get_artifact_graph()
            result = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            att = result["attestation"]
            self.assertIsNotNone(att)
            self.assertEqual(att["by"], "human:Jeff")
            self.assertEqual(att["status"], "completed")
            self.assertIn("ts", att)

    def test_closeout_populated(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            graph = ledger.get_artifact_graph()
            result = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            co = result["closeout"]
            self.assertIsNotNone(co)
            self.assertEqual(co["by"], "agent")
            self.assertEqual(co["mode"], "standard")

    def test_deterministic_ordering(self):
        """REQ-05: Same ledger state produces identical results."""
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            graph = ledger.get_artifact_graph()
            result1 = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            result2 = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            self.assertEqual(result1, result2)

    def test_empty_ledger_returns_defaults(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            ledger_path = Path(tmp_str) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)
            graph = ledger.get_artifact_graph()
            result = aggregate_audit_evidence(ledger, "ADR-0.19.0", graph)
            self.assertEqual(result["obpi_completions"], [])
            self.assertEqual(result["gate_results"], [])
            self.assertIsNone(result["attestation"])
            self.assertIsNone(result["closeout"])


class TestAuditMdRenderedFromTemplate(unittest.TestCase):
    """REQ-0.19.0-06-03: AUDIT.md is rendered from template, not inline assembly."""

    def test_audit_md_contains_obpi_summary_section(self):
        """Rendered AUDIT.md includes the OBPI Completion Summary section."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_obpis(ledger_path, "ADR-0.19.0")
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## OBPI Completion Summary", content)
            self.assertIn("OBPI-0.19.0-01", content)
            self.assertIn("OBPI-0.19.0-02", content)

    def test_audit_md_contains_generated_timestamp(self):
        """Rendered AUDIT.md includes a Generated timestamp from template."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_events(ledger_path, "ADR-0.19.0")
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("Generated:", content)

    def test_audit_plan_md_rendered_from_template(self):
        """AUDIT_PLAN.md is rendered from audit_plan template."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = Ledger(ledger_path)
            plan_file, _, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = plan_file.read_text(encoding="utf-8")
            self.assertIn("# Audit Plan: ADR-0.19.0", content)
            self.assertIn("Generated:", content)
            self.assertIn("uv run gz lint", content)

    def test_audit_md_verification_results_section(self):
        """Rendered AUDIT.md has Verification Results section (not old Results)."""
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            ledger_path = tmp / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            ledger = _make_ledger_with_events(ledger_path, "ADR-0.19.0")
            _, audit_file, _ = _call_write_audit_artifacts(tmp, ledger=ledger)
            content = audit_file.read_text(encoding="utf-8")
            self.assertIn("## Verification Results", content)
            self.assertIn("PASS", content)
