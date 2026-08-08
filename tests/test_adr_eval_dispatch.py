"""Persona-dispatch channel: an undispatched ceremony must say so (GHI #770).

`gz-adr-evaluate` SKILL.md carries a mandatory `## Persona Dispatch` section —
`spec-reviewer`, `quality-reviewer` and `narrator` produce independent dimension
scores the driver synthesizes, because "a single driver scoring its own scoring
is the precise optimistic-bias defect `spec-reviewer`'s anti-traits name".

On 2026-08-07 an evaluation ran against ADR-0.35.0 with **no dispatch at all**
(a standing session instruction forbade subagents). It produced 8 dimension
scores and a GO verdict, and nothing in the ledger, the scorecard, the validator
or `gz check` recorded that the mandated dispatch had not happened: a
single-driver evaluation and a properly dispatched one were **byte-identical in
every artifact the system produces**.

This module pins the honest contract, mirroring the substance channel's shape
(GHI #624): a dispatch is credited ONLY from a recorded dispatch receipt, and is
reported NOT DISPATCHED absent one. It is never inferred from the presence of
scores — the same reason substance is never inferred from shape.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.adr_eval import AdrEvalResult, EvalVerdict, render_scorecard_markdown
from gzkit.adr_eval_dispatch import (
    MANDATED_EVALUATION_PERSONAS,
    DispatchState,
    PersonaDispatchRecord,
    dispatch_channel_for_adr,
    get_dispatch_record_for_adr,
    is_single_driver,
    not_dispatched,
)
from gzkit.traceability import covers

_ADR = "ADR-0.35.0-canon-entry-corpus-landing"
_PERSONA = "spec-reviewer"


def _ledger(root: Path, *events: dict) -> None:
    gz = root / ".gzkit"
    gz.mkdir(parents=True, exist_ok=True)
    (gz / "ledger.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events), encoding="utf-8"
    )


def _dispatch_event(**overrides: object) -> dict:
    event = {
        "event": "persona_dispatched",
        "adr_id": _ADR,
        "persona_id": _PERSONA,
        "ceremony": "gz-adr-evaluate",
        "receipt_id": "arb-step-dispatch-1a2b3c",
    }
    event.update(overrides)
    return event


class TestDispatchIsNeverInferred(unittest.TestCase):
    """A dispatch is credited only from a receipt, never from surrounding output."""

    @covers("REQ-0.0.73-07-01")
    def test_absent_ledger_yields_not_dispatched(self) -> None:
        """No ledger at all is the commonest real case and must not crash."""
        with tempfile.TemporaryDirectory() as d:
            record = get_dispatch_record_for_adr(Path(d), _ADR, _PERSONA)

        self.assertIs(record.state, DispatchState.NOT_DISPATCHED)
        self.assertEqual(record.receipt_id, "")

    @covers("REQ-0.0.73-07-01")
    def test_ledger_without_dispatch_event_yields_not_dispatched(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, {"event": "artifact_edited", "id": "x", "path": "x"})
            record = get_dispatch_record_for_adr(root, _ADR, _PERSONA)

        self.assertIs(record.state, DispatchState.NOT_DISPATCHED)

    @covers("REQ-0.0.73-07-01")
    def test_recorded_dispatch_is_credited(self) -> None:
        """The channel is not permanently constant — a real receipt populates it.

        Without this the whole channel could be a stub that always reports
        NOT DISPATCHED, which is the tautology GHI #730 names: green (or in this
        case honest-looking) because it structurally cannot see its field.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, _dispatch_event())
            record = get_dispatch_record_for_adr(root, _ADR, _PERSONA)

        self.assertIs(record.state, DispatchState.DISPATCHED)
        self.assertEqual(record.receipt_id, "arb-step-dispatch-1a2b3c")

    @covers("REQ-0.0.73-07-01")
    def test_dispatch_without_a_receipt_id_does_not_credit(self) -> None:
        """Discipline gate, mirroring the substance channel's rationale floor.

        An event asserting a dispatch happened, with nothing citable behind it,
        is narrative recall — the exact failure the pool ADR names as
        "agent narrative recall instead of receipts".
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, _dispatch_event(receipt_id=""))
            record = get_dispatch_record_for_adr(root, _ADR, _PERSONA)

        self.assertIs(record.state, DispatchState.NOT_DISPATCHED)

    @covers("REQ-0.0.73-07-01")
    def test_dispatch_for_a_different_adr_does_not_credit(self) -> None:
        """The hollow-gate lesson from GHI #647: an event of the right TYPE that
        does not cite THIS subject proves nothing about it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, _dispatch_event(adr_id="ADR-0.0.1-some-other-adr"))
            record = get_dispatch_record_for_adr(root, _ADR, _PERSONA)

        self.assertIs(record.state, DispatchState.NOT_DISPATCHED)

    @covers("REQ-0.0.73-07-01")
    def test_dispatch_for_a_different_persona_does_not_credit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, _dispatch_event(persona_id="narrator"))
            record = get_dispatch_record_for_adr(root, _ADR, _PERSONA)

        self.assertIs(record.state, DispatchState.NOT_DISPATCHED)


class TestDispatchChannel(unittest.TestCase):
    """The channel covers every mandated persona, always."""

    @covers("REQ-0.0.73-07-01")
    def test_channel_covers_every_mandated_persona(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            channel = dispatch_channel_for_adr(Path(d), _ADR)

        self.assertEqual(
            [r.persona_id for r in channel],
            list(MANDATED_EVALUATION_PERSONAS),
            "the channel must report on every persona the ceremony mandates — a "
            "persona omitted from the report is a dispatch nobody can miss",
        )

    @covers("REQ-0.0.73-07-01")
    def test_no_dispatch_is_single_driver(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            channel = dispatch_channel_for_adr(Path(d), _ADR)

        self.assertTrue(is_single_driver(channel))

    @covers("REQ-0.0.73-07-01")
    def test_partial_dispatch_is_still_single_driver(self) -> None:
        """One persona of three is not an independent review.

        The ceremony mandates all three because they score different dimension
        families; crediting a partial run as "dispatched" would let one cheap
        dispatch launder the other two.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(root, _dispatch_event())
            channel = dispatch_channel_for_adr(root, _ADR)

        self.assertTrue(is_single_driver(channel))

    @covers("REQ-0.0.73-07-01")
    def test_full_dispatch_is_not_single_driver(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ledger(
                root,
                *(
                    _dispatch_event(persona_id=p, receipt_id=f"arb-step-dispatch-{i}")
                    for i, p in enumerate(MANDATED_EVALUATION_PERSONAS)
                ),
            )
            channel = dispatch_channel_for_adr(root, _ADR)

        self.assertFalse(is_single_driver(channel))


class TestScorecardCannotBeSilentAboutDispatch(unittest.TestCase):
    """The rendered artifact must differ between a dispatched and undispatched run.

    This is the assertion GHI #770 turns on. Its reproduction was that the two
    were byte-identical, so no reader — human, validator, or `gz check` — could
    tell which had happened.
    """

    def _result(self, dispatch: list[PersonaDispatchRecord]) -> AdrEvalResult:
        return AdrEvalResult(
            adr_id=_ADR,
            adr_dimensions=[],
            adr_weighted_total=3.6,
            obpi_scores=[],
            verdict=EvalVerdict.GO,
            action_items=[],
            timestamp="2026-08-08T00:00:00+00:00",
            dispatch=dispatch,
        )

    @covers("REQ-0.0.73-07-01")
    def test_undispatched_run_is_marked_single_driver(self) -> None:
        rendered = render_scorecard_markdown(
            self._result([not_dispatched(p) for p in MANDATED_EVALUATION_PERSONAS])
        )

        self.assertIn("SINGLE-DRIVER", rendered)
        self.assertIn("0 of 3 mandated", rendered)

    @covers("REQ-0.0.73-07-01")
    def test_an_empty_channel_still_reports_not_dispatched(self) -> None:
        """A caller that supplies no channel must not produce a silent scorecard.

        Silence is the defect. The renderer defaults to the mandated roster so
        the honest statement survives a caller that forgot the channel entirely.
        """
        rendered = render_scorecard_markdown(self._result([]))

        self.assertIn("SINGLE-DRIVER", rendered)
        for persona in MANDATED_EVALUATION_PERSONAS:
            self.assertIn(persona, rendered)

    @covers("REQ-0.0.73-07-01")
    def test_dispatched_and_undispatched_scorecards_differ(self) -> None:
        """The byte-identity GHI #770 reproduced must be impossible."""
        undispatched = render_scorecard_markdown(
            self._result([not_dispatched(p) for p in MANDATED_EVALUATION_PERSONAS])
        )
        dispatched = render_scorecard_markdown(
            self._result(
                [
                    PersonaDispatchRecord(
                        persona_id=p,
                        state=DispatchState.DISPATCHED,
                        receipt_id=f"arb-step-dispatch-{i}",
                    )
                    for i, p in enumerate(MANDATED_EVALUATION_PERSONAS)
                ]
            )
        )

        self.assertNotEqual(undispatched, dispatched)
        self.assertIn("SINGLE-DRIVER", undispatched)
        self.assertNotIn("SINGLE-DRIVER", dispatched)


if __name__ == "__main__":
    unittest.main()
