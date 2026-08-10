"""Tests for the end-to-end closeout pipeline (OBPI-0.19.0-01).

Verifies that ``gz closeout ADR-X.Y.Z`` runs quality gates inline,
prompts for human attestation, bumps version, and marks the ADR Completed.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands.closeout_ceremony import (
    CeremonyState,
    CeremonyStep,
    save_ceremony_state,
)
from gzkit.ledger import Ledger, attested_event
from gzkit.quality import QualityResult
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _make_qr(success: bool = True, command: str = "test", returncode: int = 0) -> QualityResult:
    """Build a synthetic QualityResult for mocking."""
    return QualityResult(
        success=success,
        command=command,
        stdout="OK" if success else "",
        stderr="" if success else "FAIL",
        returncode=returncode,
    )


def _count_attested(adr_id: str) -> int:
    """Count ``attested`` ledger events recorded for one ADR id."""
    lines = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
    count = 0
    for line in lines:
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("event") == "attested" and event.get("id") == adr_id:
            count += 1
    return count


def _seed_consumed_ceremony(
    project_root: Path,
    adr_id: str,
    attestation: str = "Completed",
    status: str = "completed",
) -> None:
    """Mirror ``gz closeout <adr> --ceremony --attest``: record the verdict in
    ceremony state AND emit the ceremony's Step-6 ``attested`` event
    (closeout_ceremony.py:549) — the BI-3 gate's single-source receipt that
    OBPI-0.0.63-05 keeps while suppressing the pipeline's duplicate.
    """
    state = CeremonyState(
        adr_id=adr_id,
        current_step=int(CeremonyStep.CLOSEOUT),
        is_foundation=False,
        started_at="2026-04-28T00:00:00Z",
        updated_at="2026-04-28T00:00:00Z",
        attestation=attestation,
    )
    save_ceremony_state(project_root, state)
    ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
    ledger.append(attested_event(adr_id, status, "Tester", None))


class TestCloseoutPipelineGates(unittest.TestCase):
    """Closeout executes verification steps inline via run_command (REQ-01)."""

    @covers("REQ-0.19.0-01-01")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_gates_run_inline_and_pass(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(mock_run.called, "run_command must be called for gate execution")
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("gate_checked", ledger_text)
            self.assertIn('"pass"', ledger_text)

    @covers("REQ-0.19.0-01-02")
    @patch("gzkit.cli.main.run_command")
    def test_gate_failure_halts_pipeline(self, mock_run):
        """Pipeline halts on first gate failure with exit 1 (REQ-02)."""
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("gate_checked", ledger_text)
            self.assertIn('"fail"', ledger_text)

    @patch("gzkit.cli.main.run_command")
    def test_partial_gate_results_recorded_on_failure(self, mock_run):
        """Partial gate results are recorded when a later gate fails (REQ-02)."""
        call_count = 0

        def side_effect(command, cwd=None):
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return _make_qr(success=True, command=command)
            return _make_qr(success=False, command=command, returncode=1)

        mock_run.side_effect = side_effect
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 1)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            gate_lines = [ln for ln in ledger_text.splitlines() if "gate_checked" in ln]
            self.assertGreaterEqual(len(gate_lines), 2, "Both pass and fail gate events recorded")


class TestCloseoutPipelineAttestation(unittest.TestCase):
    """Closeout prompts for attestation after gates pass (REQ-03)."""

    @covers("REQ-0.19.0-01-03")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_attestation_recorded_in_ledger(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("attested", ledger_text)
            self.assertIn("completed", ledger_text)

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_attestation_never_skipped(self, mock_input, mock_run):
        """Attestation prompt must always execute — never skipped (REQ-08)."""
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            mock_input.assert_called_once()


class TestCloseoutPipelineVersionBump(unittest.TestCase):
    """Closeout bumps version when ADR semver exceeds project (REQ-04)."""

    @covers("REQ-0.19.0-01-04")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_version_bump_when_needed(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            # Create pyproject.toml with lower version
            Path("pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.0.1"\n', encoding="utf-8"
            )
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            content = Path("pyproject.toml").read_text(encoding="utf-8")
            self.assertIn('version = "0.1.0"', content)


class TestCloseoutPipelineCompletion(unittest.TestCase):
    """Closeout marks ADR Completed after attestation (REQ-05)."""

    @covers("REQ-0.19.0-01-05")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_adr_marked_completed(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("lifecycle_transition", ledger_text)
            self.assertIn("Completed", ledger_text)

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_adr_frontmatter_status_reconciled_to_ledger(self, _mock_input, mock_run):
        """Closeout reconciles the ADR's own status: frontmatter to the ledger.

        The pipeline writes the lifecycle_transition (Completed) to the ledger
        (Layer 2) and regenerates the adr-status index (Layer 3). It must also
        reconcile the ADR's own ``status:`` frontmatter (Layer 1) in the same
        run — otherwise the ADR is left Proposed-vs-Completed drifted, the next
        ``gz validate --frontmatter`` fails (exit 3), and the index it just
        regenerated was built from stale frontmatter. Regression for the
        closeout-leaves-drift gap surfaced at ADR-0.0.69 closeout.
        """
        import re

        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            matches = [
                p for p in Path.cwd().rglob("ADR-0.1.0-f.md") if p.parent.name == "ADR-0.1.0-f"
            ]
            self.assertTrue(matches, "ADR-0.1.0-f canonical file not found")
            adr_file = matches[0]
            fm_status = re.search(r"(?m)^status:\s*(.+)$", adr_file.read_text(encoding="utf-8"))
            self.assertIsNotNone(fm_status, "ADR frontmatter has no status: field")
            self.assertEqual(
                "Completed",
                fm_status.group(1).strip(),
                msg="closeout left ADR frontmatter status drifted from the ledger",
            )


class TestCloseoutDryRun(unittest.TestCase):
    """--dry-run shows pipeline plan without executing (REQ-06)."""

    @covers("REQ-0.19.0-01-06")
    def test_dry_run_shows_plan_no_execution(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--dry-run"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn("Dry run", result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("gate_checked", ledger_text)
            self.assertNotIn("attested", ledger_text)

    def test_dry_run_json_includes_version_sync(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            Path("pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.0.1"\n', encoding="utf-8"
            )
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--dry-run", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("version_sync", data)
            self.assertTrue(data["version_sync"]["needs_bump"])


class TestCloseoutJsonOutput(unittest.TestCase):
    """--json emits structured JSON with all pipeline results (REQ-07)."""

    @covers("REQ-0.19.0-01-07")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_json_output_contains_all_stages(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("gate_results", data)
            self.assertIn("attestation", data)
            self.assertIn("version_sync", data)
            self.assertIn("status_transition", data)

    @patch("gzkit.cli.main.run_command")
    def test_json_output_on_gate_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--json"])
            self.assertEqual(result.exit_code, 1)
            data = json.loads(result.output)
            self.assertIn("gate_results", data)
            self.assertTrue(data["halted"])


class TestCloseoutAdrStatusRegen(unittest.TestCase):
    """Closeout regenerates adr-status.md after completing (GHI #322)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_adr_status_index_regenerated_on_closeout(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            status_path = Path("docs/governance/GovZero/adr-status.md")
            status_path.parent.mkdir(parents=True, exist_ok=True)
            status_path.write_text("stale content\n", encoding="utf-8")
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            content = status_path.read_text(encoding="utf-8")
            self.assertNotEqual(content, "stale content\n")
            self.assertIn("ADR Status Table", content)

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_json_output_includes_adr_status_regen(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f", "--json"])
            self.assertEqual(result.exit_code, 0, result.output)
            data = json.loads(result.output)
            self.assertIn("adr_status_regen", data)


class TestCloseoutExitCodes(unittest.TestCase):
    """Exit code 0 = full success, exit code 1 = failure (REQ-10)."""

    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_exit_0_on_success(self, _mock_input, mock_run):
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0)

    @patch("gzkit.cli.main.run_command")
    def test_exit_1_on_gate_failure(self, mock_run):
        mock_run.return_value = _make_qr(success=False, returncode=1)
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 1)


class TestDualRuntimeCollapseBI2(unittest.TestCase):
    """OBPI-0.0.63-05: collapse the ceremony/pipeline ``attested`` double-emit.

    BI-2 (single-runtime-engine ledger parity): one logical closeout emits one
    ``attested`` event regardless of path. The ceremony's Step-6 emission is the
    single source (BI-3); the Step-7 pipeline must not re-emit when it consumed a
    ceremony attestation, but remains the sole emitter on the direct path.
    """

    @covers("REQ-0.0.63-05-01")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input")
    def test_ceremony_driven_closeout_emits_single_attested(self, mock_input, mock_run):
        """REQ-01: a ceremony-driven closeout leaves exactly one ``attested``
        event (the ceremony's); the pipeline does not append a duplicate."""
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_consumed_ceremony(Path.cwd(), "ADR-0.1.0-f", "Completed")
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_input.assert_not_called()
            self.assertEqual(
                _count_attested("ADR-0.1.0-f"),
                1,
                "ceremony-driven closeout must leave exactly one attested event "
                "(no ceremony/pipeline double-emit)",
            )

    @covers("REQ-0.0.63-05-02")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_ceremony_and_direct_paths_emit_equal_attested_surface(self, _mock_input, mock_run):
        """REQ-02: the same logical closeout run ceremony-driven vs direct leaves
        an equal ``attested`` surface — exactly one event on each path."""
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            _seed_consumed_ceremony(Path.cwd(), "ADR-0.1.0-f", "Completed")
            runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            count_ceremony = _count_attested("ADR-0.1.0-f")
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            count_direct = _count_attested("ADR-0.1.0-f")
        self.assertEqual(
            count_ceremony,
            count_direct,
            "ceremony-driven and direct closeouts must leave equal attested surfaces",
        )
        self.assertEqual(
            count_ceremony, 1, "each logical closeout emits exactly one attested event"
        )

    @covers("REQ-0.0.63-05-03")
    @patch("gzkit.cli.main.run_command")
    @patch("builtins.input", return_value="1")
    def test_direct_closeout_remains_sole_emitter(self, _mock_input, mock_run):
        """REQ-03: a direct closeout with no ceremony to consume still emits
        exactly one ``attested`` event — the guard does not over-correct."""
        mock_run.return_value = _make_qr()
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(
                _count_attested("ADR-0.1.0-f"),
                1,
                "direct closeout pipeline must remain the sole attested emitter",
            )
