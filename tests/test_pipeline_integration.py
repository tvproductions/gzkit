"""Tests for OBPI-0.18.0-05 dispatch tracking, aggregation, and agent validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.pipeline_runtime import (
    ModelRoutingConfig,
    SubagentDispatchRecord,
    aggregate_dispatch_results,
    complete_subagent_dispatch_record,
    create_subagent_dispatch_record,
    get_agent_file_for_role,
    load_dispatch_state,
    load_dispatch_summary,
    load_model_routing_config,
    persist_dispatch_state,
    persist_dispatch_summary,
    validate_agent_files,
)


class TestSubagentDispatchRecord(unittest.TestCase):
    """Test creation and completion of dispatch records."""

    def test_create_record_sets_timestamp_and_status(self) -> None:
        record = create_subagent_dispatch_record(1, "Implementer", "sonnet")
        self.assertEqual(record.task_id, 1)
        self.assertEqual(record.role, "Implementer")
        self.assertEqual(record.agent_file, ".claude/agents/implementer.md")
        self.assertEqual(record.model, "sonnet")
        self.assertEqual(record.status, "in_progress")
        self.assertIsNotNone(record.dispatched_at)
        self.assertIsNone(record.completed_at)

    def test_create_record_with_isolation(self) -> None:
        record = create_subagent_dispatch_record(
            2, "Reviewer", "opus", isolation="worktree", background=True
        )
        self.assertEqual(record.isolation, "worktree")
        self.assertTrue(record.background)

    def test_complete_record_sets_completed_at(self) -> None:
        record = create_subagent_dispatch_record(1, "Implementer", "sonnet")
        completed = complete_subagent_dispatch_record(record, "done", {"files_changed": ["a.py"]})
        self.assertEqual(completed.status, "done")
        self.assertIsNotNone(completed.completed_at)
        self.assertEqual(completed.result, {"files_changed": ["a.py"]})
        # Original is unchanged (frozen)
        self.assertEqual(record.status, "in_progress")

    def test_serialization_round_trip(self) -> None:
        record = create_subagent_dispatch_record(3, "Narrator", "sonnet")
        data = record.model_dump()
        restored = SubagentDispatchRecord(**data)
        self.assertEqual(restored, record)


class TestDispatchAggregation(unittest.TestCase):
    """Table-driven tests for aggregate_dispatch_results."""

    def test_empty_records(self) -> None:
        agg = aggregate_dispatch_results([])
        self.assertEqual(agg.total_tasks, 0)
        self.assertEqual(agg.completed, 0)
        self.assertEqual(agg.blocked, 0)
        self.assertEqual(agg.fix_cycles, 0)

    def test_all_done(self) -> None:
        records = [
            _make_completed_record(1, "Implementer", "done"),
            _make_completed_record(2, "Implementer", "done"),
        ]
        agg = aggregate_dispatch_results(records)
        self.assertEqual(agg.total_tasks, 2)
        self.assertEqual(agg.completed, 2)
        self.assertEqual(agg.blocked, 0)

    def test_mixed_statuses(self) -> None:
        records = [
            _make_completed_record(1, "Implementer", "done"),
            _make_completed_record(2, "Implementer", "blocked"),
            _make_completed_record(3, "Implementer", "done_with_concerns"),
        ]
        agg = aggregate_dispatch_results(records)
        self.assertEqual(agg.completed, 2)
        self.assertEqual(agg.blocked, 1)

    def test_fix_cycles_from_duplicate_task_ids(self) -> None:
        records = [
            _make_completed_record(1, "Implementer", "done"),
            _make_completed_record(1, "Implementer", "done"),  # re-dispatch
            _make_completed_record(2, "Implementer", "done"),
        ]
        agg = aggregate_dispatch_results(records)
        self.assertEqual(agg.fix_cycles, 1)

    def test_severity_counts_from_findings(self) -> None:
        records = [
            _make_completed_record(
                1,
                "Reviewer",
                "done",
                result={
                    "findings": [
                        {"severity": "critical", "message": "bad"},
                        {"severity": "minor", "message": "ok"},
                    ]
                },
            ),
        ]
        agg = aggregate_dispatch_results(records)
        self.assertEqual(agg.review_findings_by_severity, {"critical": 1, "minor": 1})

    def test_model_usage_per_role(self) -> None:
        records = [
            _make_completed_record(1, "Implementer", "done", model="sonnet"),
            _make_completed_record(2, "Implementer", "done", model="opus"),
            _make_completed_record(1, "Reviewer", "done", model="sonnet"),
        ]
        agg = aggregate_dispatch_results(records)
        self.assertEqual(agg.model_usage_per_role["Implementer"], {"sonnet": 1, "opus": 1})
        self.assertEqual(agg.model_usage_per_role["Reviewer"], {"sonnet": 1})


class TestModelRoutingConfig(unittest.TestCase):
    """Test declarative model routing configuration."""

    def test_defaults(self) -> None:
        config = ModelRoutingConfig()
        self.assertEqual(config.implementer["simple"], "haiku")
        self.assertEqual(config.reviewer["complex"], "opus")
        self.assertEqual(config.verifier["standard"], "sonnet")

    def test_load_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / ".gzkit"
            config_dir.mkdir()
            config_path = config_dir / "pipeline-config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "model_routing": {
                            "implementer": {
                                "simple": "sonnet",
                                "standard": "opus",
                                "complex": "opus",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            config = load_model_routing_config(root)
            self.assertEqual(config.implementer["simple"], "sonnet")
            # Others get defaults
            self.assertEqual(config.reviewer["simple"], "sonnet")

    def test_load_missing_file_returns_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = load_model_routing_config(Path(tmp))
            self.assertEqual(config.implementer["simple"], "haiku")


class TestDispatchStatePersistence(unittest.TestCase):
    """Test persist/load round-trip for dispatch state in pipeline markers."""

    def test_persist_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            obpi_id = "OBPI-0.18.0-05"
            marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
            marker_path.write_text(
                json.dumps({"obpi_id": obpi_id, "current_stage": "stage-2"}),
                encoding="utf-8",
            )
            records = [
                create_subagent_dispatch_record(1, "Implementer", "sonnet"),
                create_subagent_dispatch_record(2, "Reviewer", "opus"),
            ]
            persist_dispatch_state(plans_dir, obpi_id, records)
            loaded = load_dispatch_state(plans_dir, obpi_id)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].task_id, 1)
            self.assertEqual(loaded[1].role, "Reviewer")

    def test_load_no_marker_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load_dispatch_state(Path(tmp), "OBPI-NONE")
            self.assertEqual(loaded, [])

    def test_persist_no_marker_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            persist_dispatch_state(Path(tmp), "OBPI-NONE", [])
            # No crash, no file created
            self.assertFalse((Path(tmp) / ".pipeline-active-OBPI-NONE.json").exists())


class TestDispatchSummary(unittest.TestCase):
    """Test persist/load of dispatch summary for historical queries."""

    def test_persist_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            obpi_id = "OBPI-0.18.0-05"
            records = [_make_completed_record(1, "Implementer", "done")]
            agg = aggregate_dispatch_results(records)
            path = persist_dispatch_summary(plans_dir, obpi_id, agg, records)
            self.assertTrue(path.is_file())

            loaded = load_dispatch_summary(plans_dir, obpi_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["obpi_id"], obpi_id)
            self.assertEqual(loaded["aggregation"]["total_tasks"], 1)

    def test_load_missing_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_dispatch_summary(Path(tmp), "OBPI-NONE"))


class TestValidateAgentFiles(unittest.TestCase):
    """Test agent file validation."""

    def test_all_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)
            for fname in [
                "implementer.md",
                "spec-reviewer.md",
                "quality-reviewer.md",
                "narrator.md",
            ]:
                (agents_dir / fname).write_text(
                    "---\nname: test\ntools: Read, Glob\n---\nContent\n",
                    encoding="utf-8",
                )
            errors = validate_agent_files(root)
            self.assertEqual(errors, [])

    def test_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            errors = validate_agent_files(Path(tmp))
            self.assertEqual(len(errors), 4)
            self.assertTrue(any("implementer.md" in e for e in errors))

    def test_missing_frontmatter_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_dir = root / ".claude" / "agents"
            agents_dir.mkdir(parents=True)
            (agents_dir / "implementer.md").write_text(
                "---\nname: impl\n---\nContent\n", encoding="utf-8"
            )
            for fname in ["spec-reviewer.md", "quality-reviewer.md", "narrator.md"]:
                (agents_dir / fname).write_text(
                    "---\nname: test\ntools: Read\n---\nContent\n", encoding="utf-8"
                )
            errors = validate_agent_files(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("tools", errors[0])


class TestGetAgentFileForRole(unittest.TestCase):
    """Test role-to-agent-file mapping."""

    def test_known_roles(self) -> None:
        cases = [
            ("Implementer", ".claude/agents/implementer.md"),
            ("Reviewer", ".claude/agents/spec-reviewer.md"),
            ("QualityReviewer", ".claude/agents/quality-reviewer.md"),
            ("Narrator", ".claude/agents/narrator.md"),
        ]
        for role, expected in cases:
            with self.subTest(role=role):
                self.assertEqual(get_agent_file_for_role(role), expected)

    def test_unknown_role_returns_empty(self) -> None:
        self.assertEqual(get_agent_file_for_role("Unknown"), "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_completed_record(
    task_id: int,
    role: str,
    status: str,
    *,
    model: str = "sonnet",
    result: dict | None = None,
) -> SubagentDispatchRecord:
    """Create a completed dispatch record for test purposes."""
    record = create_subagent_dispatch_record(task_id, role, model)
    return complete_subagent_dispatch_record(record, status, result)


if __name__ == "__main__":
    unittest.main()
