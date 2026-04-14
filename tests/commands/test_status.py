import json
import subprocess
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.status_render import TABLE_TITLE_FEATURE  # noqa: F401
from gzkit.config import GzkitConfig
from gzkit.events import EventAnchor
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    attested_event,
    audit_receipt_emitted_event,
    gate_checked_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)
from gzkit.traceability import covers  # noqa: F401
from tests.commands.common import CliRunner, _init_git_repo, _quick_init, _write_obpi


class TestStatusCommand(unittest.TestCase):
    """Tests for gz status command."""

    def test_status_shows_no_adrs(self) -> None:
        """status shows message when no ADRs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No ADRs found", result.output)

    def test_status_shows_adr(self) -> None:
        """status shows ADR when present."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR-0.1.0", result.output)

    def test_status_show_gates_shows_gate2_pass_from_ledger(self) -> None:
        """status --show-gates shows Gate 2 PASS when latest gate check passed."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["status", "--show-gates"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):   PASS", result.output)

    def test_status_show_gates_shows_gate2_fail_from_ledger(self) -> None:
        """status --show-gates shows Gate 2 FAIL when latest gate check failed."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("QC Readiness:", result.output)
            self.assertNotIn("Gate 2 (TDD):", result.output)

    def test_status_table_shows_adr_status_columns(self) -> None:
        """status --table renders a stable ADR summary table."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["status", "--table"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(TABLE_TITLE_FEATURE, result.output)
            self.assertIn("Life", result.output)
            self.assertIn("Lane", result.output)
            self.assertIn("Status", result.output)
            self.assertIn("Checks", result.output)
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("0/0", result.output)
            self.assertIn("TDD", result.output)

    def test_status_table_wraps_long_adr_ids_instead_of_truncating(self) -> None:
        """status --table preserves long ADR ids instead of ellipsizing them."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))

            adr_id = "ADR-0.10.0-obpi-runtime-surface"
            adr_path = adr_dir / f"{adr_id}.md"
            adr_path.parent.mkdir(parents=True, exist_ok=True)
            adr_path.write_text(f"---\nid: {adr_id}\n---\n\n# {adr_id}\n")
            ledger.append(adr_created_event(adr_id, "", "heavy"))

            result = runner.invoke(main, ["status", "--table"])

            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("…", result.output)
            self.assertIn("ADR-0.10.0-obpi-runtime-surface", result.output)

    def test_status_table_blocks_ready_on_incomplete_obpis(self) -> None:
        """status --table marks QC pending when linked OBPIs are incomplete."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("0/1", result.output)
            self.assertIn("PENDING", result.output)
            self.assertIn("OBPI completion", result.output)

    def test_status_json_orders_semver_ids_numerically(self) -> None:
        """status --json sorts SemVer ADR ids numerically, not lexicographically."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            adr_dir = Path(config.paths.adrs)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))

            for adr_id in ("ADR-0.10.0", "ADR-0.2.0", "ADR-0.9.0"):
                adr_path = adr_dir / f"{adr_id}.md"
                adr_path.parent.mkdir(parents=True, exist_ok=True)
                adr_path.write_text(f"---\nid: {adr_id}\n---\n\n# {adr_id}\n")
                ledger.append(adr_created_event(adr_id, "", "lite"))

            result = runner.invoke(main, ["status", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(
                list(payload["adrs"].keys()),
                ["ADR-0.2.0", "ADR-0.9.0", "ADR-0.10.0"],
            )

    def test_status_shows_obpi_completion_summary(self) -> None:
        """status renders OBPI completion as the primary unit."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "## Key Proof",
                        "uv run gz adr status ADR-0.1.0 --json",
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
                    evidence={
                        "value_narrative": (
                            "The demo OBPI completed with canonical receipt evidence."
                        ),
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                    },
                )
            )

            result = runner.invoke(main, ["status"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("OBPI Unit:       COMPLETED", result.output)
            self.assertIn("OBPI Completion: 1/1 complete", result.output)
            self.assertIn("all linked OBPIs completed with evidence", result.output)

    def test_obpi_status_json_includes_runtime_fields(self) -> None:
        """obpi status --json reports the focused OBPI runtime payload."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                    evidence={
                        "value_narrative": "The focused OBPI status is backed by receipt evidence.",
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                    },
                )
            )

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["obpi"], "OBPI-0.1.0-01-demo")
            self.assertEqual(payload["parent_adr"], "ADR-0.1.0")
            self.assertTrue(payload["found_file"])
            self.assertTrue(payload["completed"])
            self.assertEqual(payload["runtime_state"], "completed")
            self.assertEqual(payload["proof_state"], "recorded")
            self.assertEqual(payload["attestation_requirement"], "optional")
            self.assertEqual(payload["issues"], [])

    def test_obpi_status_json_reports_missing_file(self) -> None:
        """obpi status reports missing brief files explicitly."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertFalse(payload["found_file"])
            self.assertIsNone(payload["file"])
            self.assertIn("linked in ledger but no OBPI file found", payload["issues"])

    def test_obpi_status_json_supports_file_backed_obpi_without_ledger_link(self) -> None:
        """obpi status still inspects standalone OBPI briefs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="src/module.py",
            )

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertFalse(payload["linked_in_ledger"])
            self.assertTrue(payload["found_file"])
            self.assertEqual(payload["parent_adr"], "ADR-0.1.0")
            self.assertEqual(payload["attestation_requirement"], "optional")

    def test_obpi_reconcile_json_passes_for_completed_obpi(self) -> None:
        """obpi reconcile passes when ledger, file, and proof are coherent."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                    evidence={
                        "value_narrative": "The reconcile path has canonical completion evidence.",
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                    },
                )
            )

            result = runner.invoke(main, ["obpi", "reconcile", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["blockers"], [])
            self.assertEqual(payload["runtime_state"], "completed")

    def test_obpi_reconcile_json_reports_reflection_drift_without_blocking(self) -> None:
        """obpi reconcile stays green when only the markdown reflection is stale."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="",
                key_proof="",
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
                        "value_narrative": (
                            "The runtime engine is now the canonical execution path."
                        ),
                        "key_proof": "uv run gz obpi pipeline OBPI-0.1.0-01-demo --json",
                    },
                )
            )

            result = runner.invoke(main, ["obpi", "reconcile", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["blockers"], [])
            self.assertEqual(payload["runtime_state"], "completed")
            self.assertIn("brief reflection is not marked Completed", payload["reflection_issues"])

    @covers("REQ-0.11.0-04-02")
    def test_obpi_reconcile_fails_closed_when_proof_missing(self) -> None:
        """obpi reconcile emits BLOCKERS and exits non-zero when proof is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="src/module.py",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))

            result = runner.invoke(main, ["obpi", "reconcile", "OBPI-0.1.0-01-demo"])

            self.assertEqual(result.exit_code, 1)
            self.assertIn("BLOCKERS:", result.output)
            self.assertIn("ledger proof of completion is missing", result.output)

    @covers("REQ-0.11.0-04-03")
    def test_obpi_reconcile_reports_anchor_drift_for_scope_changes(self) -> None:
        """Anchor-aware reconcile fails when tracked files changed since completion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
            )
            module_path = Path("src/module.py")
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("value = 1\n", encoding="utf-8")
            anchor_commit = _init_git_repo(Path.cwd())

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
                        "value_narrative": "Anchor-aware reconciliation remains canonical.",
                        "key_proof": "uv run gz obpi reconcile OBPI-0.1.0-01-demo --json",
                        "scope_audit": {
                            "allowlist": ["src/module.py"],
                            "changed_files": ["src/module.py"],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "blockers": [],
                        },
                    },
                    anchor=EventAnchor(commit=anchor_commit, semver="0.1.0"),
                )
            )

            module_path.write_text("value = 2\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "src/module.py"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "change module"],
                check=True,
                capture_output=True,
                text=True,
            )

            result = runner.invoke(main, ["obpi", "reconcile", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["runtime_state"], "completed")
            self.assertEqual(payload["anchor_state"], "superseded")
            self.assertEqual(payload["anchor_commit"], anchor_commit)
            self.assertEqual(payload["anchor_drift_files"], ["src/module.py"])

    def test_obpi_status_json_surfaces_tracked_defects_for_anchor_drift(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
                tracked_defects=[
                    "GHI-11 (open): Ignore transient anchor drift noise",
                    "GHI-12 (closed): Preserve completion state when only anchor freshness drifts",
                ],
            )
            module_path = Path("src/module.py")
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("value = 1\n", encoding="utf-8")
            anchor_commit = _init_git_repo(Path.cwd())

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
                        "value_narrative": "Anchor drift is tracked with linked defects.",
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                        "scope_audit": {
                            "allowlist": ["src/module.py"],
                            "changed_files": ["src/module.py"],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "blockers": [],
                        },
                    },
                    anchor=EventAnchor(commit=anchor_commit, semver="0.1.0"),
                )
            )

            module_path.write_text("value = 2\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "src/module.py"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "change module"],
                check=True,
                capture_output=True,
                text=True,
            )

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["tracked_defects"][0]["id"], "GHI-11")
            self.assertEqual(payload["tracked_defects"][0]["state"], "open")
            self.assertEqual(payload["tracked_defects"][1]["id"], "GHI-12")
            self.assertEqual(payload["tracked_defects"][1]["state"], "closed")
            # Anchor is superseded (later commits on top), not stale
            self.assertEqual(payload["anchor_state"], "superseded")

    def test_obpi_reconcile_ignores_shared_file_changes_absorbed_by_later_sibling_completion(
        self,
    ) -> None:
        """Later completed sibling OBPIs should absorb shared-file drift for earlier siblings."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_dir = Path(config.paths.adrs) / "obpis"
            obpi_dir.mkdir(parents=True, exist_ok=True)
            obpi_one_path = obpi_dir / "OBPI-0.1.0-01-demo.md"
            _write_obpi(
                path=obpi_one_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
            )
            obpi_two_path = obpi_dir / "OBPI-0.1.0-02-demo.md"
            obpi_two_path.write_text(
                "\n".join(
                    [
                        "---",
                        "id: OBPI-0.1.0-02-demo",
                        "parent: ADR-0.1.0",
                        "item: 2",
                        "lane: Lite",
                        "status: Completed",
                        "---",
                        "",
                        "# OBPI-0.1.0-02-demo: Demo",
                        "",
                        "**Brief Status:** Completed",
                        "",
                        "## Evidence",
                        "",
                        "### Implementation Summary",
                        "- Files created/modified: src/module.py",
                        "- Validation commands run: uv run -m unittest discover tests",
                        "- Date completed: 2026-02-14",
                        "",
                        "## Key Proof",
                        "uv run gz adr status ADR-0.1.0 --json",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            module_path = Path("src/module.py")
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("value = 1\n", encoding="utf-8")
            first_anchor = _init_git_repo(Path.cwd())

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))
            ledger.append(obpi_created_event("OBPI-0.1.0-02-demo", "ADR-0.1.0"))
            ledger.append(
                obpi_receipt_emitted_event(
                    obpi_id="OBPI-0.1.0-01-demo",
                    parent_adr="ADR-0.1.0",
                    receipt_event="completed",
                    attestor="human:test",
                    obpi_completion="completed",
                    evidence={
                        "value_narrative": (
                            "Earlier sibling receipts stay complete after later shared changes."
                        ),
                        "key_proof": "uv run gz obpi reconcile OBPI-0.1.0-01-demo --json",
                        "scope_audit": {
                            "allowlist": ["src/module.py"],
                            "changed_files": ["src/module.py"],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "blockers": [],
                        },
                    },
                    anchor=EventAnchor(commit=first_anchor, semver="0.1.0"),
                )
            )

            module_path.write_text("value = 2\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "src/module.py"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "later sibling change"],
                check=True,
                capture_output=True,
                text=True,
            )
            second_anchor = subprocess.run(
                ["git", "rev-parse", "--short=7", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            ledger.append(
                obpi_receipt_emitted_event(
                    obpi_id="OBPI-0.1.0-02-demo",
                    parent_adr="ADR-0.1.0",
                    receipt_event="completed",
                    attestor="human:test",
                    obpi_completion="completed",
                    evidence={
                        "value_narrative": (
                            "Later sibling completion absorbs the shared-file change."
                        ),
                        "key_proof": "uv run gz obpi status OBPI-0.1.0-02-demo --json",
                        "scope_audit": {
                            "allowlist": ["src/module.py"],
                            "changed_files": ["src/module.py"],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "blockers": [],
                        },
                    },
                    anchor=EventAnchor(commit=second_anchor, semver="0.1.0"),
                )
            )

            result = runner.invoke(main, ["obpi", "reconcile", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["passed"])
            self.assertEqual(payload["runtime_state"], "completed")
            # Earlier OBPI's anchor is superseded by later sibling commit
            self.assertEqual(payload["anchor_state"], "superseded")
            self.assertEqual(payload["anchor_drift_files"], ["src/module.py"])

    def test_obpi_status_json_exposes_anchor_fields(self) -> None:
        """Focused OBPI status includes anchor reconciliation fields."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
            )
            module_path = Path("src/module.py")
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("value = 1\n", encoding="utf-8")
            anchor_commit = _init_git_repo(Path.cwd())

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
                        "value_narrative": (
                            "Anchor fields come from the canonical completion receipt."
                        ),
                        "key_proof": "uv run gz obpi status OBPI-0.1.0-01-demo --json",
                        "scope_audit": {
                            "allowlist": ["src/module.py"],
                            "changed_files": ["src/module.py"],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "blockers": [],
                        },
                    },
                    anchor=EventAnchor(commit=anchor_commit, semver="0.1.0"),
                )
            )

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["runtime_state"], "completed")
            self.assertEqual(payload["anchor_state"], "current")
            self.assertEqual(payload["anchor_commit"], anchor_commit)
            self.assertEqual(payload["current_head"], anchor_commit)
            self.assertEqual(payload["anchor_issues"], [])

    def test_obpi_status_uses_only_key_proof_section_for_file_reflection(self) -> None:
        """Key proof extraction still parses the file section without promoting canonical proof."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "## Key Proof",
                        "uv run gz obpi status OBPI-0.1.0-01-demo --json",
                        "",
                        "### Implementation Summary",
                        "- Files created/modified: src/module.py",
                    ]
                )
                + "\n"
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["key_proof_ok"])
            self.assertEqual(payload["req_proof_inputs"], [])

    def test_obpi_status_accepts_legacy_verification_section_as_file_reflection(self) -> None:
        """Legacy Verification sections still parse as file proof without redefining lifecycle."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "lane: Heavy",
                        "status: Completed",
                        "---",
                        "",
                        "# OBPI-0.1.0-01-demo: Demo",
                        "",
                        "**Brief Status:** Completed",
                        "",
                        "## Verification",
                        "```bash",
                        "uv run gz status --table",
                        "uv run -m unittest discover tests",
                        "```",
                        "",
                        "## Evidence",
                        "",
                        "### Implementation Summary",
                        "- Files created/modified: src/module.py",
                        "- Date completed: 2026-03-10",
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

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["key_proof_ok"])
            self.assertEqual(payload["runtime_state"], "drift")
            self.assertEqual(payload["req_proof_state"], "missing")

    def test_status_json_accepts_legacy_gate_evidence_section_as_file_reflection(self) -> None:
        """Gate Evidence parses as file proof; ledger receipt is authoritative for completion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "## Gate Evidence",
                        "",
                        "| Gate | Evidence | Command/Path |",
                        "|------|----------|--------------|",
                        "| Gate 2 (TDD) | Tests pass | `uv run -m unittest discover tests` |",
                        "",
                        "## Evidence",
                        "",
                        "### Implementation Summary",
                        "- Files created/modified: src/module.py",
                        "- Date completed: 2026-03-10",
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
            ledger.append(attested_event("ADR-0.1.0", "completed", "human"))

            result = runner.invoke(main, ["status", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-0.1.0"]
            self.assertEqual(adr_payload["obpi_summary"]["completed"], 1)
            self.assertEqual(adr_payload["obpi_summary"]["unit_status"], "completed")
            self.assertEqual(adr_payload["lifecycle_status"], "Completed")
            self.assertTrue(adr_payload["obpis"][0]["key_proof_ok"])

    def test_obpi_status_accepts_verification_heading_prefix_as_file_reflection(self) -> None:
        """Verification headings with legacy suffixes still parse as file proof only."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "lane: Heavy",
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
                        "- Date completed: 2026-03-10",
                        "",
                        "### Verification Commands Run (2026-03-10)",
                        "",
                        "```text",
                        "uv run gz lint",
                        "uv run gz test",
                        "```",
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

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["key_proof_ok"])
            self.assertEqual(payload["req_proof_state"], "missing")

    def test_obpi_status_accepts_validation_commands_bullet_as_file_reflection(self) -> None:
        """Legacy validation-command bullets still parse as file proof only."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "lane: Heavy",
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
                        "- Validation commands run:",
                        "  - uv run gz lint",
                        "  - uv run gz check",
                        "- Validation outcome: PASS",
                        "- Date completed: 2026-03-10",
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

            result = runner.invoke(main, ["obpi", "status", "OBPI-0.1.0-01-demo", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertTrue(payload["key_proof_ok"])
            self.assertEqual(payload["req_proof_inputs"], [])


class TestLifecycleStatusSemantics(unittest.TestCase):
    """Tests for derived lifecycle semantics on status/state surfaces."""

    def test_adr_status_default_hides_gate_breakdown(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR Overview", result.output)
            self.assertNotIn("Gate 2 (TDD):", result.output)

    def test_adr_status_renders_shared_table_via_deterministic_renderer(self) -> None:
        """gz adr status renders the same deterministic tables as gz adr report.

        Locks the skill Output Contract that says "consistent table format" and
        "do not replace the table with prose" for both modes. Before GHI #141's
        follow-up repair, this command produced ad-hoc indented prose and
        violated the skill design.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            status_result = runner.invoke(main, ["adr", "status", "ADR-0.1.0"])
            report_result = runner.invoke(main, ["adr", "report", "ADR-0.1.0"])

            self.assertEqual(status_result.exit_code, 0)
            self.assertEqual(report_result.exit_code, 0)
            self.assertIn("ADR Overview", status_result.output)
            self.assertIn("OBPIs", status_result.output)
            self.assertIn("ADR-0.1.0", status_result.output)
            self.assertIn("ADR Overview", report_result.output)

    def test_adr_status_accepts_semver_prefix_for_suffixed_adr(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
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
            self.assertIn("ADR-0.5.0", result.output)

    def test_adr_status_show_gates_includes_gate_breakdown(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--show-gates"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Gate 2 (TDD):", result.output)

    def test_adr_status_heavy_features_missing_reports_gate4_pending(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
            runner.invoke(main, ["plan", "create", "0.1.0", "--lane", "heavy"])

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertEqual(payload["gates"]["4"], "pending")
            self.assertNotIn("gate4_na_reason", payload)

    def test_adr_status_legacy_semver_id_still_resolves(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("heavy")
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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

    def test_adr_status_surfaces_closeout_blockers(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Draft",
                brief_status="Draft",
                implementation_line="src/module.py",
            )

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0"])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Closeout Readiness: BLOCKED", result.output)
            self.assertIn("Closeout Blockers:", result.output)
            self.assertIn(
                "OBPI-0.1.0-01-demo: ledger proof of completion is missing", result.output
            )

    def test_adr_status_closeout_blockers_include_tracked_defect_refs(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(
                path=obpi_path,
                status="Completed",
                brief_status="Completed",
                implementation_line="src/module.py",
                tracked_defects=[
                    "GHI-11 (open): Ignore transient anchor drift noise",
                    "GHI-12 (open): Reconcile shared-scope sibling completions correctly",
                ],
            )
            module_path = Path("src/module.py")
            module_path.parent.mkdir(parents=True, exist_ok=True)
            module_path.write_text("value = 1\n", encoding="utf-8")
            anchor_commit = _init_git_repo(Path.cwd())

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
                        "value_narrative": "Anchor drift is tracked with linked defects.",
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                        "scope_audit": {
                            "allowlist": ["src/module.py"],
                            "changed_files": ["src/module.py"],
                            "out_of_scope_files": [],
                        },
                        "git_sync_state": {
                            "dirty": False,
                            "ahead": 0,
                            "behind": 0,
                            "diverged": False,
                            "blockers": [],
                        },
                    },
                    anchor=EventAnchor(commit=anchor_commit, semver="0.1.0"),
                )
            )

            module_path.write_text("value = 2\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "src/module.py"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "change module"],
                check=True,
                capture_output=True,
                text=True,
            )

            result = runner.invoke(main, ["adr", "status", "ADR-0.1.0", "--json"])

            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            # Anchor superseded by later commits — not a closeout blocker
            self.assertEqual(payload["closeout_blockers"], [])
            self.assertEqual(payload["obpis"][0]["anchor_state"], "superseded")
            self.assertEqual(payload["obpis"][0]["tracked_defects"][0]["id"], "GHI-11")

    def test_adr_status_json_validated(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(attested_event("ADR-0.1.0", "partial", "human", "staged rollout"))

            result = runner.invoke(main, ["status", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            adr_payload = payload["adrs"]["ADR-0.1.0"]
            self.assertEqual(adr_payload["lifecycle_status"], "Completed")
            self.assertEqual(adr_payload["attestation_term"], "Completed - Partial")

    def test_status_json_obpi_incomplete_overrides_completed_lifecycle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
            self.assertIn("closeout_ready", adr_payload)
            self.assertIn("closeout_blockers", adr_payload)
            self.assertEqual(adr_payload["obpi_summary"]["total"], 1)
            self.assertEqual(adr_payload["obpi_summary"]["completed"], 0)
            self.assertEqual(adr_payload["obpi_summary"]["unit_status"], "pending")
            self.assertFalse(adr_payload["closeout_ready"])
            self.assertIn("OBPI-0.1.0-01-demo", adr_payload["closeout_blockers"][0])

    def test_status_json_completed_status_with_empty_summary_stays_incomplete(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                        "## Key Proof",
                        "uv run gz adr status ADR-0.1.0 --json",
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
                "ledger proof of completion is missing",
                adr_payload["obpis"][0]["issues"],
            )

    def test_adr_status_json_pool_adr_ignores_attestation_for_lifecycle(self) -> None:
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
            _quick_init()
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
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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
                    evidence={
                        "value_narrative": "ADR status rows reflect canonical receipt evidence.",
                        "key_proof": "uv run gz adr status ADR-0.1.0 --json",
                    },
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
            self.assertEqual(row["runtime_state"], "completed")
            self.assertEqual(row["proof_state"], "recorded")
            self.assertEqual(row["attestation_requirement"], "optional")
            self.assertEqual(row["req_proof_state"], "recorded")
            self.assertEqual(row["req_proof_summary"]["present"], 1)
            self.assertEqual(row["issues"], [])

    def test_adr_status_json_reports_missing_linked_obpi_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
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

    def test_adr_report_renders_overview_and_obpi_tables(self) -> None:
        """gz adr report renders deterministic ASCII tables."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["adr", "report", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR Overview", result.output)
            self.assertIn("OBPIs", result.output)
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("Pending", result.output)

    def test_adr_report_shows_obpi_rows(self) -> None:
        """gz adr report includes OBPI rows when OBPIs are linked."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            config = GzkitConfig.load(Path(".gzkit.json"))
            obpi_path = Path(config.paths.adrs) / "OBPI-0.1.0-01-demo.md"
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            _write_obpi(obpi_path, "Draft", "draft", "Not started")
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))

            result = runner.invoke(main, ["adr", "report", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("OBPI-0.1.0-01-demo", result.output)
            self.assertIn("draft", result.output)

    def test_adr_report_shows_issues_section(self) -> None:
        """gz adr report prints issues when OBPIs have problems."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-core-feature", "ADR-0.1.0"))

            result = runner.invoke(main, ["adr", "report", "ADR-0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Issues", result.output)
            self.assertIn("ledger proof of completion is missing", result.output)

    def test_adr_report_accepts_semver_prefix(self) -> None:
        """gz adr report resolves short semver prefixes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["adr", "report", "0.1.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("ADR-0.1.0", result.output)

    def test_adr_report_no_arg_renders_summary_table(self) -> None:
        """gz adr report (no argument) renders the ADR summary table."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])

            result = runner.invoke(main, ["adr", "report"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(TABLE_TITLE_FEATURE, result.output)
            self.assertIn("ADR-0.1.0", result.output)
            self.assertIn("Checks legend", result.output)

    def test_state_ready_json_only_includes_gate_ready_unattested_adrs(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            runner.invoke(main, ["plan", "create", "0.2.0"])
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))

            result = runner.invoke(main, ["state", "--ready", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertIn("ADR-0.1.0", payload)
            self.assertNotIn("ADR-0.2.0", payload)
