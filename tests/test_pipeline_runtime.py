import json
import tempfile
import unittest
from pathlib import Path

from gzkit.pipeline_runtime import (
    extract_brief_status,
    find_active_pipeline_marker,
    load_plan_audit_receipt,
    pipeline_command,
    pipeline_completion_reminder_message,
    pipeline_gate_message,
    pipeline_resume_command,
    pipeline_router_message,
)


class TestPipelineRuntime(unittest.TestCase):
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

    def test_pipeline_router_and_gate_messages_use_runtime_command(self) -> None:
        self.assertIn(
            "uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration",
            pipeline_router_message("OBPI-0.13.0-05-runtime-engine-integration"),
        )
        self.assertIn(
            "uv run gz obpi pipeline OBPI-0.13.0-05-runtime-engine-integration --from=verify",
            pipeline_gate_message("OBPI-0.13.0-05-runtime-engine-integration"),
        )


if __name__ == "__main__":
    unittest.main()
