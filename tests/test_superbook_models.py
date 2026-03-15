"""Tests for superbook Pydantic models."""

import unittest

from pydantic import ValidationError

from gzkit.superbook_models import (
    ADRDraft,
    ChunkData,
    CommitData,
    LaneClassification,
    OBPIDraft,
    PlanData,
    REQData,
    SpecData,
    TaskData,
)


class TestSpecData(unittest.TestCase):
    def test_spec_data_round_trips(self) -> None:
        """SpecData can be constructed and serialized."""
        spec = SpecData(
            title="Test Spec",
            goal="Reduce bloat",
            architecture="Three-layer model",
            decisions=["Use rules mirroring", "Categorize skills"],
            file_scope=["src/gzkit/sync.py", "src/gzkit/templates/claude.md"],
        )
        self.assertEqual(spec.title, "Test Spec")
        data = spec.model_dump()
        self.assertEqual(data["goal"], "Reduce bloat")
        self.assertEqual(len(data["decisions"]), 2)

    def test_spec_data_is_frozen(self) -> None:
        """Frozen models reject mutation."""
        spec = SpecData(title="T", goal="G")
        with self.assertRaises(ValidationError):
            spec.title = "Modified"


class TestPlanData(unittest.TestCase):
    def test_plan_data_with_chunks_and_tasks(self) -> None:
        """PlanData nests ChunkData and TaskData correctly."""
        plan = PlanData(
            goal="Implement feature",
            tech_stack="Python 3.13",
            chunks=[
                ChunkData(
                    name="Core Logic",
                    tasks=[
                        TaskData(
                            name="Task 1",
                            file_paths=["src/foo.py"],
                            steps=["Write test"],
                        )
                    ],
                    file_paths=["src/foo.py"],
                    criteria=["foo() returns expected"],
                ),
            ],
        )
        self.assertEqual(len(plan.chunks), 1)
        self.assertEqual(plan.chunks[0].tasks[0].name, "Task 1")


class TestLaneClassification(unittest.TestCase):
    def test_lane_classification_defaults(self) -> None:
        """LaneClassification defaults confidence to auto."""
        lc = LaneClassification(lane="heavy", signals=["src/gzkit/cli.py"])
        self.assertEqual(lc.confidence, "auto")


class TestCommitData(unittest.TestCase):
    def test_commit_data_is_frozen(self) -> None:
        """CommitData is frozen."""
        commit = CommitData(sha="abc123", message="feat: test", date="2026-03-15")
        with self.assertRaises(ValidationError):
            commit.sha = "modified"


class TestADRDraft(unittest.TestCase):
    def test_adr_draft_with_obpis(self) -> None:
        """ADRDraft contains OBPIDraft list."""
        adr = ADRDraft(
            id="ADR-0.17.0",
            title="Test ADR",
            semver="0.17.0",
            lane="heavy",
            intent="Reduce bloat",
            decision="Use rules mirroring",
            checklist=["Categorized catalog", "Rules mirroring"],
            scorecard={"data_state": 1, "logic_engine": 2},
            obpis=[
                OBPIDraft(
                    id="OBPI-0.17.0-01-catalog",
                    objective="Categorized skill catalog",
                    parent="ADR-0.17.0",
                    item=1,
                    lane="heavy",
                    reqs=[
                        REQData(
                            id="REQ-0.17.0-01-01",
                            description="Category extraction",
                        )
                    ],
                ),
            ],
        )
        self.assertEqual(len(adr.obpis), 1)
        self.assertEqual(adr.obpis[0].reqs[0].id, "REQ-0.17.0-01-01")


if __name__ == "__main__":
    unittest.main()
