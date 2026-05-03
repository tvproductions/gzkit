"""Tests for ``adr-evaluation`` ledger event emission from ``adr_eval_cmd`` (OBPI-0.0.26-01).

@covers ADR-0.0.26-evaluation-feedback-loop-doctrine
@covers OBPI-0.0.26-01-persist-evaluation-events

Verifies that every successful ``gz adr eval`` invocation writes exactly one
``adr-evaluation`` event to a tempfile-backed ledger, and that a failed
invocation (exception from evaluate_adr) writes none.

All tests use tempfile-backed ledgers; the live ``.gzkit/ledger.jsonl`` is
never touched (REQ-0.0.26-01-06). Emission goes through the production code
path — not seeded directly (REQ-0.0.26-01-09).
"""

from __future__ import annotations

import contextlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.adr_eval import AdrEvalResult, DimensionScore, EvalVerdict
from gzkit.commands.adr_promote import adr_eval_cmd
from gzkit.traceability import covers


def _make_eval_result(
    adr_id: str = "ADR-0.0.26",
    verdict: EvalVerdict = EvalVerdict.GO,
    *,
    score: int = 3,
) -> AdrEvalResult:
    dim = DimensionScore(
        dimension="clarity",
        weight=0.25,
        score=score,
        weighted=round(score * 0.25, 3),
        findings=[],
    )
    return AdrEvalResult(
        adr_id=adr_id,
        adr_dimensions=[dim],
        adr_weighted_total=round(score * 0.25, 3),
        obpi_scores=[],
        red_team_results=None,
        verdict=verdict,
        action_items=[],
        timestamp="2026-05-03T10:00:00Z",
    )


class TestAdrEvalCmdEmission(unittest.TestCase):
    """Verify ``adr_eval_cmd`` emits exactly one ``adr-evaluation`` event on success."""

    def _run_cmd_with_temp_ledger(
        self,
        result: AdrEvalResult,
        *,
        evaluate_raises: BaseException | None = None,
    ) -> tuple[Path, list[dict]]:
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            mock_config = MagicMock()
            mock_config.paths.ledger = ".gzkit/ledger.jsonl"

            def _fake_evaluate(project_root: Path, adr_id: str) -> AdrEvalResult:
                if evaluate_raises is not None:
                    raise evaluate_raises
                return result

            with (
                patch("gzkit.commands.adr_promote.ensure_initialized", return_value=mock_config),
                patch("gzkit.commands.adr_promote.get_project_root", return_value=Path(tmp)),
                patch("gzkit.adr_eval.evaluate_adr", side_effect=_fake_evaluate),
                contextlib.suppress(SystemExit, Exception),
            ):
                adr_eval_cmd("0.0.26", as_json=False, write_scorecard=False)

            if ledger_path.exists():
                lines = ledger_path.read_text(encoding="utf-8").strip().split("\n")
                events = [json.loads(line) for line in lines if line.strip()]
            else:
                events = []

            return ledger_path, events

    @covers("REQ-0.0.26-01-01")
    def test_successful_eval_emits_exactly_one_adr_evaluation_event(self) -> None:
        result = _make_eval_result(verdict=EvalVerdict.GO)
        _, events = self._run_cmd_with_temp_ledger(result)
        eval_events = [e for e in events if e.get("event") == "adr-evaluation"]
        self.assertEqual(
            len(eval_events), 1, f"Expected 1 adr-evaluation event, got {len(eval_events)}"
        )

    @covers("REQ-0.0.26-01-01")
    def test_emitted_event_has_artifact_id(self) -> None:
        result = _make_eval_result(adr_id="ADR-0.0.26", verdict=EvalVerdict.GO)
        _, events = self._run_cmd_with_temp_ledger(result)
        eval_events = [e for e in events if e.get("event") == "adr-evaluation"]
        self.assertEqual(len(eval_events), 1)
        self.assertEqual(eval_events[0]["artifact_id"], "ADR-0.0.26")

    @covers("REQ-0.0.26-01-01")
    def test_emitted_event_dimensions_maps_dimension_name_to_score(self) -> None:
        result = _make_eval_result(verdict=EvalVerdict.GO, score=3)
        _, events = self._run_cmd_with_temp_ledger(result)
        eval_events = [e for e in events if e.get("event") == "adr-evaluation"]
        self.assertEqual(len(eval_events), 1)
        dims = eval_events[0]["dimensions"]
        self.assertIn("clarity", dims)
        self.assertEqual(dims["clarity"], 3.0)

    @covers("REQ-0.0.26-01-01")
    def test_emitted_event_has_evaluator_persona(self) -> None:
        result = _make_eval_result(verdict=EvalVerdict.GO)
        _, events = self._run_cmd_with_temp_ledger(result)
        eval_events = [e for e in events if e.get("event") == "adr-evaluation"]
        self.assertEqual(len(eval_events), 1)
        self.assertEqual(eval_events[0]["evaluator_persona"], "gz-adr-evaluate")

    @covers("REQ-0.0.26-01-02")
    def test_evaluate_adr_exception_does_not_emit_adr_evaluation_event(self) -> None:
        result = _make_eval_result()
        _, events = self._run_cmd_with_temp_ledger(
            result, evaluate_raises=RuntimeError("validator error: malformed input")
        )
        eval_events = [e for e in events if e.get("event") == "adr-evaluation"]
        self.assertEqual(
            len(eval_events), 0, "No adr-evaluation event expected when evaluate_adr raises"
        )

    @covers("REQ-0.0.26-01-01")
    def test_no_go_verdict_still_emits_adr_evaluation_event(self) -> None:
        result = _make_eval_result(verdict=EvalVerdict.NO_GO)
        _, events = self._run_cmd_with_temp_ledger(result)
        eval_events = [e for e in events if e.get("event") == "adr-evaluation"]
        self.assertEqual(
            len(eval_events),
            1,
            "adr-evaluation should be emitted even on NO_GO — evaluation completed successfully",
        )
