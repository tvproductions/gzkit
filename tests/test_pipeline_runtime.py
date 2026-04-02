import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.pipeline_runtime import (
    clear_stale_pipeline_markers,
    extract_brief_status,
    find_active_pipeline_marker,
    find_stale_pipeline_markers,
    load_plan_audit_receipt,
    pipeline_command,
    pipeline_completion_reminder_message,
    pipeline_gate_message,
    pipeline_receipt_path,
    pipeline_resume_command,
    pipeline_router_message,
)
from gzkit.traceability import covers


class TestPipelineRuntime(unittest.TestCase):
    @covers("REQ-0.13.0-01-01")
    def test_load_plan_audit_receipt_without_target_obpi_accepts_pass_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            (plans_dir / ".plan-audit-receipt.json").write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-0.13.0-05-runtime-engine-integration",
                        "verdict": "PASS",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            state, warnings, receipt = load_plan_audit_receipt(plans_dir, "")

            self.assertEqual(state, "pass")
            self.assertEqual(warnings, [])
            assert receipt is not None
            self.assertEqual(receipt["obpi_id"], "OBPI-0.13.0-05-runtime-engine-integration")

    @covers("REQ-0.13.0-02-01")
    def test_find_active_pipeline_marker_prefers_per_obpi_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            (plans_dir / ".pipeline-active-OBPI-0.13.0-05.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-05", "current_stage": "implement"}) + "\n",
                encoding="utf-8",
            )
            (plans_dir / ".pipeline-active.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-04", "current_stage": "verify"}) + "\n",
                encoding="utf-8",
            )

            marker = find_active_pipeline_marker(plans_dir)

            assert marker is not None
            self.assertEqual(marker["obpi_id"], "OBPI-0.13.0-05")

    @covers("REQ-0.13.0-02-03")
    def test_find_active_pipeline_marker_skips_corrupted_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            # First per-OBPI marker is corrupted JSON
            (plans_dir / ".pipeline-active-OBPI-0.13.0-01.json").write_text(
                "NOT VALID JSON{{{",
                encoding="utf-8",
            )
            # Second per-OBPI marker is valid
            (plans_dir / ".pipeline-active-OBPI-0.13.0-05.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-05", "current_stage": "implement"}) + "\n",
                encoding="utf-8",
            )

            marker = find_active_pipeline_marker(plans_dir)

            assert marker is not None
            self.assertEqual(marker["obpi_id"], "OBPI-0.13.0-05")

    def test_find_active_pipeline_marker_falls_through_to_legacy_after_corrupted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            # Per-OBPI marker is corrupted
            (plans_dir / ".pipeline-active-OBPI-0.13.0-01.json").write_text(
                "CORRUPT",
                encoding="utf-8",
            )
            # Legacy marker is valid
            (plans_dir / ".pipeline-active.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-04", "current_stage": "verify"}) + "\n",
                encoding="utf-8",
            )

            marker = find_active_pipeline_marker(plans_dir)

            assert marker is not None
            self.assertEqual(marker["obpi_id"], "OBPI-0.13.0-04")

    @covers("REQ-0.13.0-01-04")
    def test_extract_brief_status_reads_frontmatter_and_body_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            brief_path = Path(tmpdir) / "OBPI-0.13.0-05.md"
            brief_path.write_text(
                "\n".join(
                    [
                        "---",
                        "status: Draft",
                        "---",
                        "",
                        "**Brief Status:** Accepted",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            self.assertEqual(extract_brief_status(brief_path), "Draft")

    @covers("REQ-0.13.0-03-01")
    def test_pipeline_resume_command_uses_resume_point_when_next_command_missing(self) -> None:
        marker = {
            "obpi_id": "OBPI-0.13.0-05-runtime-engine-integration",
            "current_stage": "verify",
            "resume_point": "verify",
            "next_command": None,
        }

        self.assertEqual(
            pipeline_resume_command(marker),
            pipeline_command("OBPI-0.13.0-05-runtime-engine-integration", "verify"),
        )

    @covers("REQ-0.13.0-05-02")
    def test_pipeline_completion_reminder_uses_runtime_managed_guidance(self) -> None:
        marker = {
            "obpi_id": "OBPI-0.13.0-05-runtime-engine-integration",
            "current_stage": "verify",
            "receipt_state": "missing",
            "resume_point": "verify",
            "next_command": None,
            "blockers": ["uv run gz lint: lint failed"],
            "required_human_action": None,
        }

        message = pipeline_completion_reminder_message(marker, brief_status="Accepted")

        assert message is not None
        self.assertIn("PIPELINE COMPLETION REMINDER", message)
        self.assertIn("Active blockers:", message)
        self.assertIn("uv run gz lint: lint failed", message)
        self.assertIn(
            "uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration --from=verify",
            message,
        )
        self.assertIn("Do not clear the pipeline marker by hand", message)

    @covers("REQ-0.13.0-05-01")
    def test_pipeline_router_and_gate_messages_use_runtime_command(self) -> None:
        self.assertIn(
            "uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration",
            pipeline_router_message("OBPI-0.13.0-05-runtime-engine-integration"),
        )
        self.assertIn(
            "uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration --from=verify",
            pipeline_gate_message("OBPI-0.13.0-05-runtime-engine-integration"),
        )

    # --- Issue #20: Per-OBPI receipts ---

    @covers("REQ-0.13.0-02-02")
    def test_load_receipt_prefers_per_obpi_receipt_over_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            obpi_id = "OBPI-0.13.0-05"
            # Legacy receipt targets a different OBPI
            (plans_dir / ".plan-audit-receipt.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-01", "verdict": "PASS"}) + "\n",
                encoding="utf-8",
            )
            # Per-OBPI receipt targets the correct OBPI
            pipeline_receipt_path(plans_dir, obpi_id).write_text(
                json.dumps({"obpi_id": obpi_id, "verdict": "PASS"}) + "\n",
                encoding="utf-8",
            )

            state, warnings, receipt = load_plan_audit_receipt(plans_dir, obpi_id)

            self.assertEqual(state, "pass")
            self.assertEqual(warnings, [])
            assert receipt is not None
            self.assertEqual(receipt["obpi_id"], obpi_id)

    def test_load_receipt_falls_back_to_legacy_when_no_per_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            obpi_id = "OBPI-0.13.0-05"
            (plans_dir / ".plan-audit-receipt.json").write_text(
                json.dumps({"obpi_id": obpi_id, "verdict": "PASS"}) + "\n",
                encoding="utf-8",
            )

            state, warnings, receipt = load_plan_audit_receipt(plans_dir, obpi_id)

            self.assertEqual(state, "pass")
            assert receipt is not None
            self.assertEqual(receipt["obpi_id"], obpi_id)

    def test_load_receipt_discovery_finds_per_obpi_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            # No legacy receipt, only per-OBPI
            pipeline_receipt_path(plans_dir, "OBPI-0.13.0-05").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-05", "verdict": "PASS"}) + "\n",
                encoding="utf-8",
            )

            state, warnings, receipt = load_plan_audit_receipt(plans_dir, "")

            self.assertEqual(state, "pass")
            assert receipt is not None
            self.assertEqual(receipt["obpi_id"], "OBPI-0.13.0-05")

    # --- Issue #20: Stale marker detection ---

    @covers("REQ-0.13.0-03-03")
    def test_find_stale_markers_detects_old_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            old_time = (
                (datetime.now(UTC) - timedelta(hours=5))
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
            (plans_dir / ".pipeline-active-OBPI-0.13.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-01", "updated_at": old_time}) + "\n",
                encoding="utf-8",
            )

            stale = find_stale_pipeline_markers(plans_dir)

            self.assertEqual(len(stale), 1)
            self.assertEqual(stale[0][1]["obpi_id"], "OBPI-0.13.0-01")

    def test_find_stale_markers_ignores_fresh_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            fresh_time = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            (plans_dir / ".pipeline-active-OBPI-0.13.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-01", "updated_at": fresh_time}) + "\n",
                encoding="utf-8",
            )

            stale = find_stale_pipeline_markers(plans_dir)

            self.assertEqual(len(stale), 0)

    @covers("REQ-0.13.0-01-02")
    def test_clear_stale_markers_removes_old_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            old_time = (
                (datetime.now(UTC) - timedelta(hours=5))
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z")
            )
            marker_path = plans_dir / ".pipeline-active-OBPI-0.13.0-01.json"
            marker_path.write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-01", "updated_at": old_time}) + "\n",
                encoding="utf-8",
            )

            removed = clear_stale_pipeline_markers(plans_dir)

            self.assertEqual(len(removed), 1)
            self.assertEqual(removed[0][1], "OBPI-0.13.0-01")
            self.assertFalse(marker_path.exists())

    def test_find_stale_markers_flags_corrupted_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            (plans_dir / ".pipeline-active-OBPI-0.13.0-01.json").write_text(
                "CORRUPT",
                encoding="utf-8",
            )

            stale = find_stale_pipeline_markers(plans_dir)

            self.assertEqual(len(stale), 1)

    def test_find_stale_markers_flags_missing_updated_at(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plans_dir = Path(tmpdir)
            (plans_dir / ".pipeline-active-OBPI-0.13.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.13.0-01"}) + "\n",
                encoding="utf-8",
            )

            stale = find_stale_pipeline_markers(plans_dir)

            self.assertEqual(len(stale), 1)


class TestValidateBriefForPipeline(unittest.TestCase):
    """Tests for validate_brief_for_pipeline (#29)."""

    def test_scaffold_brief_returns_errors(self) -> None:
        from gzkit.pipeline_runtime import validate_brief_for_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "paths": {"ledger": ".gzkit/ledger.jsonl", "design_root": "docs/design"},
                    }
                ),
                encoding="utf-8",
            )
            (root / ".gzkit").mkdir(exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")

            brief = root / "brief.md"
            brief.write_text(
                "---\nid: OBPI-0.1.0-01-demo\nparent: ADR-0.1.0\n"
                "item: 1\nlane: Lite\nstatus: Draft\n---\n\n"
                "## Allowed Paths\n- `src/module/` - Reason\n\n"
                "## Requirements (FAIL-CLOSED)\n1. REQUIREMENT: First constraint\n",
                encoding="utf-8",
            )

            errors = validate_brief_for_pipeline(root, brief)
            self.assertTrue(len(errors) > 0)
            self.assertTrue(any("template placeholder" in e for e in errors))

    def test_authored_brief_returns_no_errors(self) -> None:
        from gzkit.pipeline_runtime import validate_brief_for_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "paths": {"ledger": ".gzkit/ledger.jsonl", "design_root": "docs/design"},
                    }
                ),
                encoding="utf-8",
            )
            (root / ".gzkit").mkdir(exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")

            brief = root / "brief.md"
            brief.write_text(
                "---\nid: OBPI-0.1.0-01-demo\nparent: ADR-0.1.0\n"
                "item: 1\nlane: Lite\nstatus: Draft\n---\n\n"
                "## Objective\nDefine typed port interfaces.\n\n"
                "## Lane\n**Lite** - Internal contract only.\n\n"
                "## Allowed Paths\n- `src/gzkit/ports/` - Port definitions\n\n"
                "## Denied Paths\n- `docs/user/commands/` - No operator docs drift\n\n"
                "## Requirements (FAIL-CLOSED)\n"
                "1. REQUIREMENT: Ports use typing.Protocol\n\n"
                "## Discovery Checklist\n"
                "**Prerequisites (check existence, STOP if missing):**\n"
                "- [ ] `src/gzkit/runtime.py` - Runtime entry point\n\n"
                "**Existing Code (understand current state):**\n"
                "- [ ] `src/gzkit/ports.py` - Existing port patterns\n\n"
                "## Verification\n```bash\n"
                "uv run gz validate --documents\n"
                "uv run gz lint\n"
                "uv run gz typecheck\n"
                "uv run gz test\n"
                "uv run -m unittest tests.test_ports\n"
                "```\n\n"
                "## Acceptance Criteria\n"
                "- [ ] REQ-0.1.0-01-01: Port interfaces are defined in one module.\n",
                encoding="utf-8",
            )

            errors = validate_brief_for_pipeline(root, brief)
            self.assertEqual(errors, [])

    def test_thin_non_scaffold_brief_still_returns_authored_errors(self) -> None:
        from gzkit.pipeline_runtime import validate_brief_for_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "paths": {"ledger": ".gzkit/ledger.jsonl", "design_root": "docs/design"},
                    }
                ),
                encoding="utf-8",
            )
            (root / ".gzkit").mkdir(exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")

            brief = root / "brief.md"
            brief.write_text(
                "---\nid: OBPI-0.1.0-01-demo\nparent: ADR-0.1.0\n"
                "item: 1\nlane: Lite\nstatus: Draft\n---\n\n"
                "## Allowed Paths\n- `src/gzkit/ports/` - Port definitions\n\n"
                "## Requirements (FAIL-CLOSED)\n"
                "1. REQUIREMENT: Ports use typing.Protocol\n\n"
                "## Acceptance Criteria\n"
                "- [ ] REQ-0.1.0-01-01: Port interfaces are defined.\n",
                encoding="utf-8",
            )

            errors = validate_brief_for_pipeline(root, brief)
            self.assertTrue(any("'Objective'" in error for error in errors))


class TestCheckAdrEvaluationVerdict(unittest.TestCase):
    """Tests for check_adr_evaluation_verdict (#32)."""

    def test_no_scorecard_returns_empty(self) -> None:
        from gzkit.pipeline_runtime import check_adr_evaluation_verdict

        with tempfile.TemporaryDirectory() as tmpdir:
            errors = check_adr_evaluation_verdict(Path(tmpdir))
            self.assertEqual(errors, [])

    def test_go_verdict_returns_empty(self) -> None:
        from gzkit.pipeline_runtime import check_adr_evaluation_verdict

        with tempfile.TemporaryDirectory() as tmpdir:
            adr_dir = Path(tmpdir)
            (adr_dir / "EVALUATION_SCORECARD.md").write_text(
                "# Scorecard\n\n**Overall Verdict:** GO\n",
                encoding="utf-8",
            )
            errors = check_adr_evaluation_verdict(adr_dir)
            self.assertEqual(errors, [])

    def test_conditional_go_returns_empty(self) -> None:
        from gzkit.pipeline_runtime import check_adr_evaluation_verdict

        with tempfile.TemporaryDirectory() as tmpdir:
            adr_dir = Path(tmpdir)
            (adr_dir / "EVALUATION_SCORECARD.md").write_text(
                "# Scorecard\n\n**Overall Verdict:** CONDITIONAL GO\n",
                encoding="utf-8",
            )
            errors = check_adr_evaluation_verdict(adr_dir)
            self.assertEqual(errors, [])

    def test_no_go_returns_blocker(self) -> None:
        from gzkit.pipeline_runtime import check_adr_evaluation_verdict

        with tempfile.TemporaryDirectory() as tmpdir:
            adr_dir = Path(tmpdir)
            (adr_dir / "EVALUATION_SCORECARD.md").write_text(
                "# Scorecard\n\n**Overall Verdict:** NO GO\n",
                encoding="utf-8",
            )
            errors = check_adr_evaluation_verdict(adr_dir)
            self.assertEqual(len(errors), 1)
            self.assertIn("NO GO", errors[0])


class TestPersonaPipelineIntegration(unittest.TestCase):
    """Verify persona material flows through compose_implementer_prompt."""

    @covers("REQ-0.0.11-02-03")
    def test_compose_implementer_prompt_with_persona_context(self) -> None:
        from gzkit.pipeline_dispatch import DispatchTask, compose_implementer_prompt

        task = DispatchTask(
            task_id=1,
            description="Implement persona loading",
            allowed_paths=["src/gzkit/models/persona.py"],
            test_expectations=[],
            complexity="simple",
            model="haiku",
        )
        persona_body = (
            "# Implementer Persona\n\n## Behavioral Anchors\n\n- **Methodical**: Follow the plan."
        )
        prompt = compose_implementer_prompt(task, brief_requirements=[], extra_context=persona_body)
        self.assertIn("### Additional Context", prompt)
        self.assertIn("Implementer Persona", prompt)
        self.assertIn("Methodical", prompt)

    @covers("REQ-0.0.11-02-03")
    def test_load_persona_integrates_with_dispatch(self) -> None:
        from gzkit.models.persona import load_persona

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            (pdir / "implementer.md").write_text(
                "---\nname: implementer\ntraits:\n  - methodical\n"
                "anti-traits:\n  - shortcuts\ngrounding: Craft.\n---\n\n"
                "# Implementer Persona\n\nBody text.\n",
                encoding="utf-8",
            )
            body = load_persona(root, "implementer")
            self.assertIsNotNone(body)
            self.assertIn("Implementer Persona", body)


if __name__ == "__main__":
    unittest.main()
