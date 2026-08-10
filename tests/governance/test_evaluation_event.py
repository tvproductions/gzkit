"""Tests for the ``adr-evaluation`` ledger event factory (OBPI-0.0.26-01).

@covers ADR-0.0.26-evaluation-feedback-loop-doctrine
@covers OBPI-0.0.26-01-persist-evaluation-events

Tests derive from the OBPI brief's REQ list per ``.claude/rules/tests.md``
Red-Green-Refactor discipline. Each test is REQ-pinned via the ``covers``
decorator and asserts behavior, not strings.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.ledger import Ledger
from gzkit.ledger_events import adr_evaluation_event
from gzkit.traceability import covers


class TestAdrEvaluationEventFactory(unittest.TestCase):
    """Verify the ``adr_evaluation_event`` factory produces the canonical shape."""

    def _make_event(self, **overrides):
        defaults: dict = {
            "artifact_id": "ADR-0.0.26",
            "artifact_type": "ADR",
            "dimensions": {"clarity": 3.0, "structure": 2.0},
            "scores": {"clarity": 0.6, "structure": 0.4},
            "weighted_total": 1.0,
            "red_team_challenges_fired": ["challenge-2"],
            "evaluator_persona": "gz-adr-evaluate",
            "timestamp": "2026-05-03T10:00:00Z",
        }
        defaults.update(overrides)
        return adr_evaluation_event(**defaults)

    @covers("REQ-0.0.26-01-01")
    def test_event_name_is_adr_evaluation(self) -> None:
        event = self._make_event()
        self.assertEqual(event.event, "adr-evaluation")

    @covers("REQ-0.0.26-01-01")
    def test_payload_contains_artifact_id(self) -> None:
        event = self._make_event(artifact_id="ADR-0.0.99")
        self.assertEqual(event.extra["artifact_id"], "ADR-0.0.99")

    @covers("REQ-0.0.26-01-01")
    def test_payload_contains_all_required_fields(self) -> None:
        event = self._make_event()
        required = {
            "artifact_id",
            "artifact_type",
            "dimensions",
            "scores",
            "weighted_total",
            "red_team_challenges_fired",
            "evaluator_persona",
            "timestamp",
        }
        self.assertTrue(required.issubset(event.extra.keys()))

    @covers("REQ-0.0.26-01-01")
    def test_dimensions_is_name_to_score_map(self) -> None:
        dims = {"clarity": 3.0, "structure": 2.0}
        event = self._make_event(dimensions=dims)
        self.assertIsInstance(event.extra["dimensions"], dict)
        self.assertEqual(event.extra["dimensions"], dims)

    @covers("REQ-0.0.26-01-01")
    def test_red_team_challenges_fired_is_list_of_strings(self) -> None:
        challenges = ["challenge-1", "challenge-3"]
        event = self._make_event(red_team_challenges_fired=challenges)
        self.assertIsInstance(event.extra["red_team_challenges_fired"], list)
        self.assertEqual(event.extra["red_team_challenges_fired"], challenges)

    @covers("REQ-0.0.26-01-01")
    def test_empty_red_team_when_all_challenges_pass(self) -> None:
        event = self._make_event(red_team_challenges_fired=[])
        self.assertEqual(event.extra["red_team_challenges_fired"], [])

    @covers("REQ-0.0.26-01-01")
    def test_event_id_matches_artifact_id(self) -> None:
        event = self._make_event(artifact_id="ADR-0.0.26")
        self.assertEqual(event.id, "ADR-0.0.26")


_SCHEMA_PATH = Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"


class TestAdrEvaluationEventSchema(unittest.TestCase):
    """Verify the ``adr-evaluation`` event type has a schema entry in ledger.json."""

    @covers("REQ-0.0.26-01-03")
    def test_schema_entry_exists(self) -> None:
        self.assertTrue(_SCHEMA_PATH.exists(), "ledger.json schema file not found")
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIn(
            "adr-evaluation", schema.get("events", {}), "adr-evaluation not in schema events"
        )

    @covers("REQ-0.0.26-01-03")
    def test_schema_has_required_fields(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        event_schema = schema["events"]["adr-evaluation"]
        required_fields = {
            "artifact_id",
            "artifact_type",
            "dimensions",
            "scores",
            "weighted_total",
            "red_team_challenges_fired",
            "evaluator_persona",
            "timestamp",
        }
        declared = set(event_schema.get("required", []))
        missing = required_fields - declared
        self.assertFalse(missing, f"Schema missing required fields: {missing}")


class TestAdrEvaluationMultipleAppend(unittest.TestCase):
    """Verify multiple evaluations append distinct events (no upsert/dedup)."""

    @covers("REQ-0.0.26-01-04")
    def test_two_evaluations_produce_two_distinct_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            event1 = adr_evaluation_event(
                artifact_id="ADR-0.0.26",
                artifact_type="ADR",
                dimensions={"clarity": 3.0},
                scores={"clarity": 0.6},
                weighted_total=0.6,
                red_team_challenges_fired=[],
                evaluator_persona="gz-adr-evaluate",
                timestamp="2026-05-03T10:00:00Z",
            )
            event2 = adr_evaluation_event(
                artifact_id="ADR-0.0.26",
                artifact_type="ADR",
                dimensions={"clarity": 4.0},
                scores={"clarity": 0.8},
                weighted_total=0.8,
                red_team_challenges_fired=[],
                evaluator_persona="gz-adr-evaluate",
                timestamp="2026-05-03T11:00:00Z",
            )
            ledger.append(event1)
            ledger.append(event2)

            lines = ledger_path.read_text(encoding="utf-8").strip().split("\n")
            all_events = [json.loads(line) for line in lines]
            eval_events = [e for e in all_events if e.get("event") == "adr-evaluation"]

            self.assertEqual(len(eval_events), 2, "Expected exactly two adr-evaluation events")
            timestamps = {e["timestamp"] for e in eval_events}
            self.assertEqual(len(timestamps), 2, "Events must have distinct timestamps")

    @covers("REQ-0.0.26-01-04")
    def test_ledger_replay_reproduces_score_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "ledger.jsonl"
            ledger = Ledger(ledger_path)

            for i, score in enumerate([3.0, 4.0, 2.0]):
                ledger.append(
                    adr_evaluation_event(
                        artifact_id="ADR-0.0.26",
                        artifact_type="ADR",
                        dimensions={"clarity": score},
                        scores={"clarity": score * 0.2},
                        weighted_total=round(score * 0.2, 3),
                        red_team_challenges_fired=[],
                        evaluator_persona="gz-adr-evaluate",
                        timestamp=f"2026-05-03T{10 + i:02d}:00:00Z",
                    )
                )

            events = ledger.read_all()
            eval_events = [e for e in events if e.event == "adr-evaluation"]
            self.assertEqual(len(eval_events), 3)
            recorded_scores = [e.extra["dimensions"]["clarity"] for e in eval_events]
            self.assertEqual(recorded_scores, [3.0, 4.0, 2.0])
