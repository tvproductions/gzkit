"""Append-only corrective-action primitive over any ledger event (GHI #611).

Operator intent, verbatim: *"we need the power to UNDO agent (or human)
error"*, *"not to erase the ledger, but to provide subsequent corrective
actions."* Corrective work under ADR-0.0.71, whose own § Intent declares
repudiation a **port** — "an erroneously- or fraudulently-attested completion
can be governed-reversed ... leaving an honest audit trail" — with the
``obpi_completion_repudiated`` event as its *first adapter*. This is the port
generalized past that one adapter.

The tests assert the semantics the primitive owes, not the shape of any one
call: an original row is never mutated, a correction names its subject
unambiguously, repeated and chained corrections resolve deterministically, and
the two derived readings (*what is true* vs *what condition is live*) differ
mechanically rather than only in prose.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.events import LedgerEventCorrectedEvent, parse_typed_event
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ledger_corrections import (
    CORRECTION_EVENT,
    correction_state,
    evidence_events,
    live_events,
    resolve_subject,
    subject_key,
)
from gzkit.ledger_events import ledger_event_corrected_event

_SCHEMA_PATH = Path(__file__).parent.parent / "src" / "gzkit" / "schemas" / "ledger.json"


def _row(event: str, ident: str, ts: str, **extra: object) -> dict:
    """Build a raw ledger row in the on-disk (flattened) shape."""
    return {"schema": "gzkit.ledger.v1", "event": event, "id": ident, "ts": ts, **extra}


def _correction(
    subject: dict,
    disposition: str,
    *,
    ts: str,
    cause: str = "agent-error",
    reason: str = "recorded in error",
    attestor: str = "g0",
) -> dict:
    return _row(
        CORRECTION_EVENT,
        subject["id"],
        ts,
        subject_event=subject["event"],
        subject_id=subject["id"],
        subject_ts=subject["ts"],
        disposition=disposition,
        cause=cause,
        attestor=attestor,
        reason=reason,
    )


class TestCorrectionEventFailsClosed(unittest.TestCase):
    """A correction with no accountable author is not a correction."""

    def _kwargs(self) -> dict:
        return {
            "id": "OBPI-0.35.0-08",
            "event": CORRECTION_EVENT,
            "subject_event": "pipeline_launched",
            "subject_id": "OBPI-0.35.0-08",
            "subject_ts": "2026-08-23T13:12:21.832251+00:00",
            "disposition": "void",
            "cause": "agent-error",
            "attestor": "g0",
            "reason": "started without operator initiation",
        }

    def test_empty_attestor_fails_closed(self) -> None:
        """Attribution is the whole point: an unattributed correction is refused."""
        kwargs = self._kwargs() | {"attestor": ""}
        with self.assertRaises(ValidationError):
            LedgerEventCorrectedEvent(**kwargs)

    def test_empty_reason_fails_closed(self) -> None:
        """A correction with no stated reason records that state changed, never why."""
        kwargs = self._kwargs() | {"reason": ""}
        with self.assertRaises(ValidationError):
            LedgerEventCorrectedEvent(**kwargs)

    def test_unknown_disposition_is_refused(self) -> None:
        """The disposition vocabulary is closed; a free-form verb is a new point-solution."""
        kwargs = self._kwargs() | {"disposition": "cancelled"}
        with self.assertRaises(ValidationError):
            LedgerEventCorrectedEvent(**kwargs)

    def test_unknown_cause_is_refused(self) -> None:
        """``cause`` is closed so the corrections can be censused, not merely read."""
        kwargs = self._kwargs() | {"cause": "because"}
        with self.assertRaises(ValidationError):
            LedgerEventCorrectedEvent(**kwargs)

    def test_empty_subject_reference_is_refused(self) -> None:
        """A correction that does not name its subject cannot be applied by any reader."""
        for field in ("subject_event", "subject_id", "subject_ts"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                LedgerEventCorrectedEvent(**(self._kwargs() | {field: ""}))

    def test_parses_through_the_typed_union(self) -> None:
        """Wired into ``TypedLedgerEvent`` — an authored-but-unwired model is GHI #877."""
        parsed = parse_typed_event(
            _correction(
                _row("pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21.832251+00:00"),
                "void",
                ts="2026-09-06T20:00:00+00:00",
            )
        )
        self.assertEqual(parsed.event, CORRECTION_EVENT)

    def test_declared_in_the_ledger_json_schema(self) -> None:
        """Both contracts must declare the event, per GHI #877's ruling."""
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        declared = schema["events"][CORRECTION_EVENT]
        self.assertEqual(
            sorted(declared["required"]),
            [
                "attestor",
                "cause",
                "disposition",
                "reason",
                "subject_event",
                "subject_id",
                "subject_ts",
            ],
        )


class TestSubjectResolution(unittest.TestCase):
    """A correction must name exactly the rows it means, and nothing adjacent."""

    def setUp(self) -> None:
        self.blocked_a = _row(
            "task_blocked", "TASK-0.35.0-08-05-01", "2026-08-23T14:27:39.933308+00:00", reason="a"
        )
        self.blocked_b = _row(
            "task_blocked", "TASK-0.35.0-08-06-01", "2026-08-23T14:27:40.190363+00:00", reason="b"
        )
        self.rows = [self.blocked_a, self.blocked_b]

    def test_resolves_the_named_row_only(self) -> None:
        """The (event, id, ts) triple selects one row out of same-typed siblings."""
        resolved = resolve_subject(self.rows, subject_key(self.blocked_a))
        self.assertEqual(resolved, [self.blocked_a])

    def test_an_unresolvable_reference_selects_nothing(self) -> None:
        """A reference to a row that does not exist resolves empty — never 'close enough'."""
        self.assertEqual(
            resolve_subject(self.rows, ("task_blocked", "TASK-0.35.0-08-05-01", "2026-01-01")),
            [],
        )

    def test_same_id_different_ts_is_a_different_subject(self) -> None:
        """A repeated event on one artifact is many rows; correcting one leaves the rest."""
        repeat = _row("task_blocked", "TASK-0.35.0-08-05-01", "2026-08-24T00:00:00+00:00")
        rows = [self.blocked_a, repeat]
        corrected = live_events(
            [*rows, _correction(repeat, "void", ts="2026-09-06T20:00:00+00:00")]
        )
        self.assertIn(self.blocked_a, corrected)
        self.assertNotIn(repeat, corrected)


class TestNettingSemantics(unittest.TestCase):
    """``void`` and ``discharged`` differ mechanically, not only in prose."""

    def setUp(self) -> None:
        self.launched = _row(
            "pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21.832251+00:00"
        )
        self.witness = _row(
            "red_receipt_emitted",
            "arb-red-REQ-1",
            "2026-08-21T01:10:26.119810+00:00",
            req_id="REQ-1",
            failure_class="none",
        )

    def test_void_is_dropped_from_both_readings(self) -> None:
        """A void row records something that was not true: no reader may count it."""
        rows = [self.launched, _correction(self.launched, "void", ts="2026-09-06T20:00:00+00:00")]
        self.assertNotIn(self.launched, live_events(rows))
        self.assertNotIn(self.launched, evidence_events(rows))

    def test_discharged_leaves_the_evidentiary_reading_intact(self) -> None:
        """A discharged row was TRUE when written; only its condition stopped being live."""
        rows = [
            self.witness,
            _correction(
                self.witness,
                "discharged",
                ts="2026-09-06T20:00:00+00:00",
                cause="condition-resolved",
            ),
        ]
        self.assertNotIn(self.witness, live_events(rows))
        self.assertIn(self.witness, evidence_events(rows))

    def test_reinstated_returns_the_row_to_both_readings(self) -> None:
        """A correction is itself reversible — the issue's own declared design surface."""
        rows = [
            self.launched,
            _correction(self.launched, "void", ts="2026-09-06T20:00:00+00:00"),
            _correction(
                self.launched,
                "reinstated",
                ts="2026-09-06T21:00:00+00:00",
                cause="operator-error",
                reason="the void was itself mistaken",
            ),
        ]
        self.assertIn(self.launched, live_events(rows))
        self.assertEqual(correction_state(rows), {})

    def test_a_chain_resolves_by_last_correction_wins(self) -> None:
        """void -> reinstate -> void nets to void, the same rule park/block already use."""
        rows = [
            self.launched,
            _correction(self.launched, "void", ts="2026-09-06T20:00:00+00:00"),
            _correction(
                self.launched,
                "reinstated",
                ts="2026-09-06T21:00:00+00:00",
                cause="operator-error",
            ),
            _correction(self.launched, "void", ts="2026-09-06T22:00:00+00:00"),
        ]
        self.assertEqual(correction_state(rows), {subject_key(self.launched): "void"})

    def test_repeated_identical_corrections_are_inert(self) -> None:
        """Re-running the same correction changes nothing — no double-counting, no error."""
        once = [self.launched, _correction(self.launched, "void", ts="2026-09-06T20:00:00+00:00")]
        twice = [*once, _correction(self.launched, "void", ts="2026-09-06T21:00:00+00:00")]
        self.assertEqual(correction_state(once), correction_state(twice))
        self.assertEqual(live_events(once), live_events(twice))

    def test_a_correction_naming_a_correction_is_inert(self) -> None:
        """``reinstated`` is the in-family reversal; correcting a correction is refused.

        Without this fence the netting would have to resolve itself recursively,
        and a cycle would make *what is live* depend on evaluation order.
        """
        first = _correction(self.launched, "void", ts="2026-09-06T20:00:00+00:00")
        second = _correction(first, "void", ts="2026-09-06T21:00:00+00:00")
        self.assertEqual(
            correction_state([self.launched, first, second]),
            {subject_key(self.launched): "void"},
        )

    def test_correction_rows_are_never_themselves_derived_state(self) -> None:
        """The correction row is bookkeeping; it must not leak into either reading."""
        rows = [
            self.launched,
            _correction(
                self.launched,
                "discharged",
                ts="2026-09-06T20:00:00+00:00",
                cause="condition-resolved",
            ),
        ]
        self.assertEqual([r["event"] for r in live_events(rows)], [])
        self.assertEqual([r["event"] for r in evidence_events(rows)], ["pipeline_launched"])

    def test_an_unresolvable_correction_nets_nothing(self) -> None:
        """A dangling reference must not silently void a same-typed neighbour."""
        orphan = _correction(
            _row("pipeline_launched", "OBPI-0.35.0-08", "1999-01-01T00:00:00+00:00"),
            "void",
            ts="2026-09-06T20:00:00+00:00",
        )
        self.assertIn(self.launched, live_events([self.launched, orphan]))


class TestTypedAndRawShapesAgree(unittest.TestCase):
    """The netting must read a ``LedgerEvent`` and a raw JSONL dict identically."""

    def test_both_serialization_shapes_net_the_same(self) -> None:
        raw = _row("pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21.832251+00:00")
        correction = _correction(raw, "void", ts="2026-09-06T20:00:00+00:00")
        typed = [LedgerEvent.model_validate(raw), LedgerEvent.model_validate(correction)]
        self.assertEqual(live_events(typed), [])
        self.assertEqual(
            correction_state(typed),
            correction_state([raw, correction]),
        )


class TestLedgerConsumers(unittest.TestCase):
    """The corrections must reach the real producers and consumers, not a fixture."""

    def _ledger(self, rows: list[dict]) -> Ledger:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = tmp / "ledger.jsonl"
        path.write_text(
            "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
        )
        return Ledger(path)

    def test_history_is_preserved_by_read_all(self) -> None:
        """Append-only: the corrected row stays readable, byte-for-byte, forever."""
        launched = _row("pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21.832251+00:00")
        rows = [
            _row(
                "obpi_created", "OBPI-0.35.0-08", "2026-07-21T23:36:03+00:00", parent="ADR-0.35.0"
            ),
            launched,
            _correction(launched, "void", ts="2026-09-06T20:00:00+00:00"),
        ]
        events = self._ledger(rows).read_all()
        self.assertEqual([e.event for e in events], [r["event"] for r in rows])

    def test_voiding_the_launch_returns_the_obpi_to_pending(self) -> None:
        """#930's wrongly-started OBPI: the graph must stop reading it as in-flight."""
        launched = _row("pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21.832251+00:00")
        created = _row(
            "obpi_created", "OBPI-0.35.0-08", "2026-07-21T23:36:03+00:00", parent="ADR-0.35.0"
        )
        before = self._ledger([created, launched]).get_artifact_graph()["OBPI-0.35.0-08"]
        self.assertTrue(before["pipeline_launched"])

        corrected = self._ledger(
            [
                created,
                launched,
                _correction(
                    launched,
                    "void",
                    ts="2026-09-06T20:00:00+00:00",
                    reason="started without operator initiation (IRON LAW)",
                ),
            ]
        ).get_artifact_graph()["OBPI-0.35.0-08"]
        self.assertFalse(corrected["pipeline_launched"])

    def test_a_later_legitimate_launch_still_counts(self) -> None:
        """Correcting one launch must not discard work done after it."""
        created = _row(
            "obpi_created", "OBPI-0.35.0-08", "2026-07-21T23:36:03+00:00", parent="ADR-0.35.0"
        )
        wrong = _row("pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21+00:00")
        right = _row("pipeline_launched", "OBPI-0.35.0-08", "2026-09-10T09:00:00+00:00")
        graph = self._ledger(
            [created, wrong, _correction(wrong, "void", ts="2026-09-06T20:00:00+00:00"), right]
        ).get_artifact_graph()
        self.assertTrue(graph["OBPI-0.35.0-08"]["pipeline_launched"])

    def test_discharging_a_task_block_returns_the_task_to_in_progress(self) -> None:
        """A blocker whose reason the operator resolved must stop reading as live."""
        from gzkit.commands.task import _load_tasks_for_obpi

        obpi = "OBPI-0.35.0-08"
        started = _row(
            "task_started",
            "TASK-0.35.0-08-05-01",
            "2026-08-23T13:12:21+00:00",
            obpi_id=obpi,
            task_id="TASK-0.35.0-08-05-01",
        )
        blocked = _row(
            "task_blocked",
            "TASK-0.35.0-08-05-01",
            "2026-08-23T14:27:39.933308+00:00",
            obpi_id=obpi,
            task_id="TASK-0.35.0-08-05-01",
            reason="two residuals await an operator ruling",
        )
        ledger = self._ledger([started, blocked])
        self.assertEqual(
            _load_tasks_for_obpi(ledger, obpi)["TASK-0.35.0-08-05-01"]["status"], "blocked"
        )

        discharged = self._ledger(
            [
                started,
                blocked,
                _correction(
                    blocked,
                    "discharged",
                    ts="2026-09-06T20:00:00+00:00",
                    cause="condition-resolved",
                    reason="operator ruled 2026-08-24; REQ reworded",
                ),
            ]
        )
        self.assertEqual(
            _load_tasks_for_obpi(discharged, obpi)["TASK-0.35.0-08-05-01"]["status"],
            "in_progress",
        )

    def test_a_sibling_blocker_is_untouched(self) -> None:
        """Discharging one TASK's blocker must leave every other blocker live."""
        from gzkit.commands.task import _load_tasks_for_obpi

        obpi = "OBPI-0.35.0-08"
        rows = []
        for seq in ("05", "06"):
            rows.append(
                _row(
                    "task_blocked",
                    f"TASK-0.35.0-08-{seq}-01",
                    f"2026-08-23T14:27:{seq}+00:00",
                    obpi_id=obpi,
                    task_id=f"TASK-0.35.0-08-{seq}-01",
                    reason="awaiting a ruling",
                )
            )
        rows.append(
            _correction(
                rows[0], "discharged", ts="2026-09-06T20:00:00+00:00", cause="condition-resolved"
            )
        )
        states = _load_tasks_for_obpi(self._ledger(rows), obpi)
        self.assertEqual(states["TASK-0.35.0-08-06-01"]["status"], "blocked")


class TestRedParityConsumesCorrections(unittest.TestCase):
    """A trust audit reading raw rows must honour a write-side void (GHI #611)."""

    def test_a_voided_witness_is_not_selected(self) -> None:
        from gzkit.governance.trust_audits.red_parity import _collect

        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (tmp / ".gzkit").mkdir()
        genuine = _row(
            "red_receipt_emitted",
            "arb-red-REQ-1-a",
            "2026-08-20T00:00:00+00:00",
            req_id="REQ-1",
            failure_class="assertion",
        )
        false_none = _row(
            "red_receipt_emitted",
            "arb-red-REQ-1-b",
            "2026-08-21T00:00:00+00:00",
            req_id="REQ-1",
            failure_class="none",
        )
        rows = [
            genuine,
            false_none,
            _correction(
                false_none,
                "void",
                ts="2026-09-06T20:00:00+00:00",
                cause="runtime-error",
                reason="banked from a mid-fix code path; the finding is false",
            ),
        ]
        (tmp / ".gzkit" / "ledger.jsonl").write_text(
            "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
        )
        witnesses, _ = _collect(tmp)
        self.assertEqual(witnesses["REQ-1"]["failure_class"], "assertion")

    def test_a_discharged_witness_is_still_evidence(self) -> None:
        """Only ``void`` unmakes a witness; ``discharged`` never touches evidence."""
        from gzkit.governance.trust_audits.red_parity import _collect

        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (tmp / ".gzkit").mkdir()
        witness = _row(
            "red_receipt_emitted",
            "arb-red-REQ-1-b",
            "2026-08-21T00:00:00+00:00",
            req_id="REQ-1",
            failure_class="none",
        )
        rows = [
            witness,
            _correction(
                witness, "discharged", ts="2026-09-06T20:00:00+00:00", cause="condition-resolved"
            ),
        ]
        (tmp / ".gzkit" / "ledger.jsonl").write_text(
            "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
        )
        witnesses, _ = _collect(tmp)
        self.assertEqual(witnesses["REQ-1"]["failure_class"], "none")


class TestFactoryProducesAValidRow(unittest.TestCase):
    """The producer and the typed contract must agree, per GHI #877."""

    def test_factory_round_trips_through_the_typed_union(self) -> None:
        event = ledger_event_corrected_event(
            subject_event="pipeline_launched",
            subject_id="OBPI-0.35.0-08",
            subject_ts="2026-08-23T13:12:21.832251+00:00",
            disposition="void",
            cause="agent-error",
            attestor="g0",
            reason="started without operator initiation",
        )
        parsed = parse_typed_event(event.model_dump())
        self.assertEqual(parsed.subject_id, "OBPI-0.35.0-08")
        self.assertEqual(parsed.id, "OBPI-0.35.0-08")


if __name__ == "__main__":
    unittest.main()
