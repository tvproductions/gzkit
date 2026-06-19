"""Substance channel: shape can NEVER produce a substance grade (OBPI-0.0.73-07).

The defect ADR-0.0.73 exists to kill: `gz adr evaluate` faked decision SUBSTANCE
with keyword/word-count heuristics and presented the fake as an authoritative
quality verdict (GHI #624). The honest contract pinned here: a substance grade
exists ONLY when a disciplined judge verdict has been recorded; absent that, the
dimension is UNGRADED — regardless of how rigorous or hollow the ADR prose is.
No deterministic analysis of the prose can lift a dimension out of UNGRADED.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.adr_eval_substance import (
    SUBSTANCE_DIMENSIONS,
    SubstanceGrade,
    get_substance_verdict_for_adr,
    substance_channel_for_adr,
)
from gzkit.traceability import covers

_ADR = "ADR-9.9.9-example"
_DIM = "Problem Substance"


def _write_ledger(root: Path, events: list[dict[str, object]]) -> None:
    gzdir = root / ".gzkit"
    gzdir.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(e) for e in events]
    (gzdir / "ledger.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


class TestSubstanceUngradedByDefault(unittest.TestCase):
    """REQ-0.0.73-07-01: substance is never fabricated from shape."""

    @covers("REQ-0.0.73-07-01")
    def test_no_ledger_yields_ungraded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            verdict = get_substance_verdict_for_adr(Path(d), _ADR, _DIM)
        self.assertEqual(verdict.grade, SubstanceGrade.UNGRADED)
        self.assertFalse(verdict.is_graded)

    @covers("REQ-0.0.73-07-01")
    def test_ledger_without_substance_event_yields_ungraded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ledger(root, [{"event": "obpi_created", "id": "OBPI-x"}])
            verdict = get_substance_verdict_for_adr(root, _ADR, _DIM)
        self.assertEqual(verdict.grade, SubstanceGrade.UNGRADED)

    @covers("REQ-0.0.73-07-01")
    def test_full_channel_is_all_ungraded_absent_verdicts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            channel = substance_channel_for_adr(Path(d), _ADR)
        self.assertEqual([v.dimension for v in channel], list(SUBSTANCE_DIMENSIONS))
        self.assertTrue(all(v.grade == SubstanceGrade.UNGRADED for v in channel))


class TestSubstanceGradedOnlyByDisciplinedVerdict(unittest.TestCase):
    """REQ-0.0.73-07-02: a grade requires a disciplined, recorded judge verdict."""

    @covers("REQ-0.0.73-07-02")
    def test_disciplined_judge_verdict_is_read_back(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ledger(
                root,
                [
                    {
                        "event": "adr_substance_verdict",
                        "adr_id": _ADR,
                        "dimension": _DIM,
                        "grade": "STRONG",
                        "rationale": "The problem is grounded in a measured 9s graph walk "
                        "and a concrete cache miss path; the contrast is real.",
                        "receipt_id": "arb-step-judge-abc123",
                    }
                ],
            )
            verdict = get_substance_verdict_for_adr(root, _ADR, _DIM)
        self.assertEqual(verdict.grade, SubstanceGrade.STRONG)
        self.assertTrue(verdict.is_graded)
        self.assertTrue(verdict.receipt_id.startswith("arb-step-judge-"))

    @covers("REQ-0.0.73-07-02")
    def test_short_rationale_does_not_grade(self) -> None:
        # An undisciplined record (no explanation-first rationale) must NOT grade.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ledger(
                root,
                [
                    {
                        "event": "adr_substance_verdict",
                        "adr_id": _ADR,
                        "dimension": _DIM,
                        "grade": "STRONG",
                        "rationale": "good",
                        "receipt_id": "arb-step-judge-abc123",
                    }
                ],
            )
            verdict = get_substance_verdict_for_adr(root, _ADR, _DIM)
        self.assertEqual(verdict.grade, SubstanceGrade.UNGRADED)

    @covers("REQ-0.0.73-07-02")
    def test_missing_judge_receipt_does_not_grade(self) -> None:
        # A "verdict" with no judge receipt is not a judge verdict.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ledger(
                root,
                [
                    {
                        "event": "adr_substance_verdict",
                        "adr_id": _ADR,
                        "dimension": _DIM,
                        "grade": "STRONG",
                        "rationale": "A sufficiently long rationale that nonetheless "
                        "carries no judge receipt to anchor it as a real verdict.",
                        "receipt_id": "",
                    }
                ],
            )
            verdict = get_substance_verdict_for_adr(root, _ADR, _DIM)
        self.assertEqual(verdict.grade, SubstanceGrade.UNGRADED)

    @covers("REQ-0.0.73-07-02")
    def test_latest_disciplined_verdict_wins(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_ledger(
                root,
                [
                    {
                        "event": "adr_substance_verdict",
                        "adr_id": _ADR,
                        "dimension": _DIM,
                        "grade": "WEAK",
                        "rationale": "An earlier verdict graded the problem substance weak "
                        "because the contrast was not yet grounded in evidence.",
                        "receipt_id": "arb-step-judge-old",
                    },
                    {
                        "event": "adr_substance_verdict",
                        "adr_id": _ADR,
                        "dimension": _DIM,
                        "grade": "ADEQUATE",
                        "rationale": "A later re-judgement found the revised problem statement "
                        "adequately grounded after the evidence section was added.",
                        "receipt_id": "arb-step-judge-new",
                    },
                ],
            )
            verdict = get_substance_verdict_for_adr(root, _ADR, _DIM)
        self.assertEqual(verdict.grade, SubstanceGrade.ADEQUATE)
        self.assertEqual(verdict.receipt_id, "arb-step-judge-new")


if __name__ == "__main__":
    unittest.main()
