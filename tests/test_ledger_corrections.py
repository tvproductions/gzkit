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
from gzkit.ledger import Ledger, LedgerEvent, read_corrected_rows
from gzkit.ledger_corrections import (
    CORRECTION_EVENT,
    LEDGER_SCHEMA,
    correction_state,
    evidence_events,
    is_correction,
    is_well_formed,
    live_events,
    parse_ledger_ts,
    resolve_subject,
    subject_key,
)
from gzkit.ledger_events import ledger_event_corrected_event


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


def _ledger_file(case: unittest.TestCase, rows: list[dict]) -> Path:
    """Write ``rows`` to a real temp ledger and return its path.

    Shared so the validator and replay are handed the SAME bytes: the defect
    these tests cover is the two paths disagreeing about one row, which is only
    observable when neither gets its own fixture.
    """
    tmp = Path(case.enterContext(tempfile.TemporaryDirectory()))
    path = tmp / "ledger.jsonl"
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
    )
    return path


def _validate_rows(case: unittest.TestCase, rows: list[dict]) -> list:
    """Run the shipped ledger validator over ``rows`` in a temp file."""
    from gzkit.validate_pkg.ledger_check import validate_ledger

    return validate_ledger(_ledger_file(case, rows))


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

    #: A complete subject row. The correction fixtures below need the row they
    #: name to be PRESENT: `validate_ledger` refuses a dangling reference across
    #: rows, so a fixture carrying the correction alone asserts the validator
    #: accepts exactly the shape `gz ledger correct` refuses to write.
    SUBJECT = _row(
        "pipeline_launched",
        "OBPI-X",
        "2026-08-23T13:12:21.832251+00:00",
        nonce="0" * 32,
        marker_path=".gzkit/pipeline/OBPI-X.json",
        lane="heavy",
    )

    def test_gz_validate_ledger_accepts_a_well_formed_correction(self) -> None:
        """The OTHER contract must admit the row too, per GHI #877's ruling.

        Asserted through ``validate_ledger`` rather than by reading
        ``ledger.json``: what matters is that the shipped validator accepts the
        row, and a test that greps the schema file passes even if the validator
        never consults it.
        """
        errors = _validate_rows(
            self,
            [
                self.SUBJECT,
                _correction(self.SUBJECT, "void", ts="2026-09-06T20:00:00+00:00"),
            ],
        )
        self.assertEqual([e.message for e in errors], [])

    def test_gz_validate_ledger_rejects_a_correction_missing_its_subject(self) -> None:
        """The schema entry is load-bearing, so prove it fails closed too."""
        bad = _correction(self.SUBJECT, "void", ts="2026-09-06T20:00:00+00:00")
        del bad["subject_ts"]
        self.assertTrue(_validate_rows(self, [self.SUBJECT, bad]))


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

    def test_history_is_preserved_by_read_history(self) -> None:
        """Append-only: the corrected row stays readable, byte-for-byte, forever.

        ``read_all`` answers *what is currently true* and therefore nets; the raw
        append-only history is ``read_history``, and nothing may remove a row
        from it.
        """
        launched = _row("pipeline_launched", "OBPI-0.35.0-08", "2026-08-23T13:12:21.832251+00:00")
        rows = [
            _row(
                "obpi_created", "OBPI-0.35.0-08", "2026-07-21T23:36:03+00:00", parent="ADR-0.35.0"
            ),
            launched,
            _correction(launched, "void", ts="2026-09-06T20:00:00+00:00"),
        ]
        events = self._ledger(rows).read_history()
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


class TestProducerContractParity(unittest.TestCase):
    """A producer may not write a field neither contract declares (GHI #877 class).

    GHI #877 fenced this over *committed rows*, which is green while a producer
    that has never fired writes undeclared keys. ``_book_aborted_exit`` is that
    case: it fires only when an airlock exit raises, which has not happened in
    this repository, so zero rows exist and the committed-row fence saw nothing.
    """

    def test_no_producer_writes_an_undeclared_field(self) -> None:
        from gzkit.governance.trust_audits import audit_producer_fields

        errors = audit_producer_fields(Path(__file__).resolve().parents[1])
        self.assertEqual(
            [f"{e.artifact}: {e.message}" for e in errors],
            [],
            "A ledger producer writes a field that ledger.json or the typed union "
            "does not declare. Declare it in BOTH, per GHI #877's ruling.",
        )

    def test_the_aborted_airlock_exit_row_parses(self) -> None:
        """The exact shape ``_book_aborted_exit`` writes (GHI #877, reopened)."""
        parsed = parse_typed_event(
            {
                "schema": "gzkit.ledger.v1",
                "event": "airlock_out",
                "id": "OBPI-X",
                "ts": "2026-01-01T00:00:00+00:00",
                "verdict": "aborted",
                "aborted": True,
                "error": "RuntimeError",
            }
        )
        self.assertTrue(parsed.aborted)
        self.assertEqual(parsed.error, "RuntimeError")

    def test_gz_validate_ledger_accepts_the_aborted_exit_row(self) -> None:
        """The second contract, proven through the validator that enforces it."""
        errors = _validate_rows(
            self,
            [
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "airlock_out",
                    "id": "OBPI-X",
                    "ts": "2026-01-01T00:00:00+00:00",
                    "verdict": "aborted",
                    "aborted": True,
                    "error": "RuntimeError",
                }
            ],
        )
        self.assertEqual([e.message for e in errors], [])


class TestCorrectionsAreValidatedAtTheReplayBoundary(unittest.TestCase):
    """The CLI guard protects the write path; replay is what every reader uses.

    A correction reaching a reader has NOT necessarily passed the CLI — it may
    have been minted by the exported factory, hand-written, or merged in. The
    netting must therefore enforce the event's own declared contract itself, or
    the guard is decorative.
    """

    def _subject(self) -> dict:
        return _row("pipeline_launched", "OBPI-X", "2026-09-02T00:00:00+00:00")

    def _invalid(self, **overrides: str) -> list[dict]:
        subject = self._subject()
        correction = _correction(subject, "void", ts="2026-09-06T20:00:00+00:00")
        correction.update(overrides)
        return [subject, correction]

    def test_an_empty_attestor_makes_the_correction_inert(self) -> None:
        rows = self._invalid(attestor="")
        self.assertEqual(correction_state(rows), {})
        self.assertIn(rows[0], live_events(rows))

    def test_a_whitespace_attestor_makes_the_correction_inert(self) -> None:
        self.assertEqual(correction_state(self._invalid(attestor="   ")), {})

    def test_an_empty_reason_makes_the_correction_inert(self) -> None:
        rows = self._invalid(reason="")
        self.assertEqual(correction_state(rows), {})
        self.assertIn(rows[0], live_events(rows))

    def test_an_unknown_cause_makes_the_correction_inert(self) -> None:
        self.assertEqual(correction_state(self._invalid(cause="because")), {})

    def test_an_unknown_disposition_makes_the_correction_inert(self) -> None:
        self.assertEqual(correction_state(self._invalid(disposition="cancelled")), {})

    def test_the_factory_refuses_to_mint_an_invalid_correction(self) -> None:
        """A constructor that mints what both validators reject is a hole."""
        with self.assertRaises(ValidationError):
            ledger_event_corrected_event(
                subject_event="pipeline_launched",
                subject_id="OBPI-X",
                subject_ts="2026-09-02T00:00:00+00:00",
                disposition="void",
                cause="agent-error",
                attestor="",
                reason="",
            )

    def test_the_factory_still_mints_a_valid_correction(self) -> None:
        event = ledger_event_corrected_event(
            subject_event="pipeline_launched",
            subject_id="OBPI-X",
            subject_ts="2026-09-02T00:00:00+00:00",
            disposition="void",
            cause="agent-error",
            attestor="g0",
            reason="started in error",
        )
        self.assertEqual(event.extra["disposition"], "void")


class TestEveryGoverningConsumerReadsTheCorrectedStream(unittest.TestCase):
    """The netting must reach the readers that decide, not only the graph.

    The first pass wired ``get_artifact_graph`` and claimed every consumer
    followed. It did not: the sibling ``Ledger`` methods each run their own
    ``read_all()`` pass, and ``active_task_trailers`` reads the JSONL directly.
    """

    def _ledger(self, rows: list[dict]) -> Ledger:
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = tmp / "ledger.jsonl"
        path.write_text(
            "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
        )
        return Ledger(path)

    def test_a_voided_gate_pass_stops_counting_as_a_pass(self) -> None:
        """The readiness surface must not report a gate that never truly passed."""
        created = _row("adr_created", "ADR-9.9.9-demo", "2026-09-01T00:00:00+00:00", lane="heavy")
        gate = _row(
            "gate_checked", "ADR-9.9.9-demo", "2026-09-02T00:00:00+00:00", gate=2, status="pass"
        )
        ledger = self._ledger([created, gate])
        self.assertEqual(ledger.get_latest_gate_statuses("ADR-9.9.9-demo"), {2: "pass"})

        corrected = self._ledger(
            [
                created,
                gate,
                _correction(gate, "void", ts="2026-09-03T00:00:00+00:00", reason="gate never ran"),
            ]
        )
        self.assertEqual(corrected.get_latest_gate_statuses("ADR-9.9.9-demo"), {})
        self.assertEqual(corrected.get_effective_gate_statuses("ADR-9.9.9-demo"), {})

    def test_an_earlier_gate_result_resurfaces_when_the_later_one_is_voided(self) -> None:
        """Voiding is not truncation: the prior legitimate result is still there."""
        created = _row("adr_created", "ADR-9.9.9-demo", "2026-09-01T00:00:00+00:00", lane="heavy")
        first = _row(
            "gate_checked", "ADR-9.9.9-demo", "2026-09-02T00:00:00+00:00", gate=2, status="fail"
        )
        second = _row(
            "gate_checked", "ADR-9.9.9-demo", "2026-09-03T00:00:00+00:00", gate=2, status="pass"
        )
        ledger = self._ledger(
            [
                created,
                first,
                second,
                _correction(second, "void", ts="2026-09-04T00:00:00+00:00", reason="never ran"),
            ]
        )
        self.assertEqual(ledger.get_latest_gate_statuses("ADR-9.9.9-demo"), {2: "fail"})

    def test_a_correction_is_never_an_artifacts_latest_event(self) -> None:
        """A correction is bookkeeping about a row, not an event in the artifact's life."""
        created = _row("obpi_created", "OBPI-X", "2026-09-01T00:00:00+00:00", parent="ADR-9.9.9")
        launched = _row("pipeline_launched", "OBPI-X", "2026-09-02T00:00:00+00:00")
        ledger = self._ledger(
            [created, launched, _correction(launched, "void", ts="2026-09-03T00:00:00+00:00")]
        )
        latest = ledger.latest_event("OBPI-X")
        assert latest is not None
        self.assertEqual(latest.event, "obpi_created")

    def test_a_discharged_blocker_reopens_the_trailer_channel(self) -> None:
        """`gz task list` and the trailer stamper must not disagree about one TASK."""
        from gzkit.tasks import active_task_trailers

        started = _row(
            "task_started",
            "TASK-9.9.9-01-01-01",
            "2026-09-02T01:00:00+00:00",
            obpi_id="OBPI-X",
            task_id="TASK-9.9.9-01-01-01",
        )
        blocked = _row(
            "task_blocked",
            "TASK-9.9.9-01-01-01",
            "2026-09-02T02:00:00+00:00",
            obpi_id="OBPI-X",
            task_id="TASK-9.9.9-01-01-01",
            reason="awaiting an operator ruling",
        )
        blocked_ledger = self._ledger([started, blocked])
        self.assertEqual(active_task_trailers(blocked_ledger.path, ["src/gzkit/x.py"]), [])

        discharged = self._ledger(
            [
                started,
                blocked,
                _correction(
                    blocked,
                    "discharged",
                    ts="2026-09-06T20:00:00+00:00",
                    cause="condition-resolved",
                    reason="operator ruled",
                ),
            ]
        )
        self.assertEqual(
            active_task_trailers(discharged.path, ["src/gzkit/x.py"]),
            ["Task: TASK-9.9.9-01-01-01"],
        )

    def test_raw_history_stays_reachable_for_the_readers_that_need_it(self) -> None:
        """Replay, the census, and subject resolution must still see every row."""
        launched = _row("pipeline_launched", "OBPI-X", "2026-09-02T00:00:00+00:00")
        rows = [
            _row("obpi_created", "OBPI-X", "2026-09-01T00:00:00+00:00", parent="ADR-9.9.9"),
            launched,
            _correction(launched, "void", ts="2026-09-03T00:00:00+00:00"),
        ]
        ledger = self._ledger(rows)
        self.assertEqual([e.event for e in ledger.read_history()], [r["event"] for r in rows])
        self.assertEqual(ledger.get_replay_manifest().event_count, 3)


class TestTheAirlockOverrideProducerIsDeclared(unittest.TestCase):
    """The REAL override path, run end-to-end, must survive both readers (GHI #877).

    ``TestProducerContractParity`` above hand-writes the payload it expects.
    That proves the contracts agree with the *test author's* idea of the row and
    is silent on what the producer actually emits — which is how this survived:
    ``_override_extra`` (``gzkit.airlock.enter``) contributes ``override_seam``,
    ``override_attestor`` and ``override_revoked`` to the ``airlock_in`` payload,
    neither contract declared any of the three, and the static producer audit
    could not see them because the payload is built in a HELPER and merged with
    ``payload.update(extra)`` — no literal key ever appears at the call site.

    So this class exercises ``airlock_enter`` itself and reads the row back off
    the ledger, which is the only way the producer's own output is the subject.
    """

    def _emit_override_row(self) -> LedgerEvent:
        """Run the real airlock override path and return the row it wrote."""
        from gzkit.airlock.enter import CaptainOverride, airlock_enter

        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        brief = tmp / "OBPI-X.md"
        brief.write_text(
            "# OBPI-X\n\n## Allowed Paths\n\n- `src/gzkit/declared.py`\n",
            encoding="utf-8",
        )
        ledger = Ledger(tmp / "ledger.jsonl")
        airlock_enter(
            "OBPI-X",
            brief,
            reach_fn=lambda _node: ["src/gzkit/unaccounted.py"],
            override=CaptainOverride(attestor="g0", seam="src/gzkit/unaccounted.py"),
            ledger=ledger,
        )
        rows = [e for e in ledger.read_history() if e.event == "airlock_in"]
        self.assertEqual(len(rows), 1, "the override path booked no airlock_in row")
        return rows[0]

    def test_the_producer_really_writes_the_three_override_fields(self) -> None:
        """Guards every assertion below against a probe that emits nothing.

        If the override payload stopped being written, the parity assertions
        would pass vacuously — a green that proves the opposite of its claim.
        """
        row = self._emit_override_row()
        self.assertEqual(
            sorted(k for k in row.extra if k.startswith("override_")),
            ["override_attestor", "override_revoked", "override_seam"],
        )

    def test_the_emitted_row_replays_through_the_typed_union(self) -> None:
        """``_EventBase`` is ``extra="forbid"``: an undeclared field refuses the row."""
        parsed = parse_typed_event(self._emit_override_row().model_dump(exclude_none=True))
        self.assertEqual(parsed.event, "airlock_in")

    def test_the_emitted_row_passes_the_ledger_validator(self) -> None:
        errors = _validate_rows(self, [self._emit_override_row().model_dump(exclude_none=True)])
        self.assertEqual([e.message for e in errors], [])

    def test_the_payload_survives_the_round_trip_intact(self) -> None:
        """Declaring a field is worthless if replay drops its value."""
        parsed = parse_typed_event(self._emit_override_row().model_dump(exclude_none=True))
        self.assertEqual(parsed.override_seam, "src/gzkit/unaccounted.py")
        self.assertEqual(parsed.override_attestor, "g0")
        self.assertIs(parsed.override_revoked, False)

    def test_a_revoked_override_round_trips_as_revoked(self) -> None:
        """``revoked`` is the field a boolean-coercing reader would silently flip."""
        from gzkit.airlock.enter import CaptainOverride, airlock_enter

        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        brief = tmp / "OBPI-Y.md"
        brief.write_text("# OBPI-Y\n\n## Allowed Paths\n\n- `src/gzkit/a.py`\n", encoding="utf-8")
        ledger = Ledger(tmp / "ledger.jsonl")
        airlock_enter(
            "OBPI-Y",
            brief,
            reach_fn=lambda _node: ["src/gzkit/b.py"],
            override=CaptainOverride(attestor="g0", seam="src/gzkit/b.py", revoked=True),
            ledger=ledger,
        )
        row = next(e for e in ledger.read_history() if e.event == "airlock_in")
        self.assertIs(parse_typed_event(row.model_dump(exclude_none=True)).override_revoked, True)


class TestProducerAuditReadsHelperBuiltPayloads(unittest.TestCase):
    """The static audit must see a payload a HELPER returns (GHI #877, second pass).

    The first pass read two shapes — an inline ``extra={...}`` literal and a
    named dict mutated by literal-key subscript. ``_override_extra`` is neither:
    it RETURNS a literal dict that the call site merges. The audit reported zero
    findings while three undeclared fields were in flight, and a zero-finding
    scan over a shape the scanner cannot see is not evidence of absence.
    """

    def _audit(self, producer_source: str) -> list[str]:
        from gzkit.governance.trust_audits import audit_producer_fields

        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        source = root / "src" / "gzkit" / "producer.py"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(producer_source, encoding="utf-8")
        schema = root / "src" / "gzkit" / "schemas" / "ledger.json"
        schema.parent.mkdir(parents=True, exist_ok=True)
        schema.write_text(
            json.dumps({"events": {"airlock_in": {"required": [], "properties": {}}}}),
            encoding="utf-8",
        )
        return [e.artifact for e in audit_producer_fields(root)]

    def test_a_helper_returned_payload_is_scanned(self) -> None:
        findings = self._audit(
            "from gzkit.ledger import LedgerEvent\n\n\n"
            "def _extra() -> dict:\n"
            '    return {"undeclared_helper_field": 1}\n\n\n'
            "def emit() -> LedgerEvent:\n"
            '    return LedgerEvent(event="airlock_in", id="X", extra=_extra())\n'
        )
        self.assertEqual(findings, ["src/gzkit/producer.py::airlock_in.undeclared_helper_field"])

    def test_a_helper_payload_merged_into_a_named_dict_is_scanned(self) -> None:
        """The exact ``payload.update(_helper(...))`` shape ``_book_transit`` uses."""
        findings = self._audit(
            "from gzkit.ledger import LedgerEvent\n\n\n"
            "def _extra(flag: bool) -> dict:\n"
            '    return {"undeclared_merged_field": flag}\n\n\n'
            "def book(flag: bool) -> LedgerEvent:\n"
            "    payload = {}\n"
            "    payload.update(_extra(flag))\n"
            '    return LedgerEvent(event="airlock_in", id="X", extra=payload)\n'
        )
        self.assertEqual(findings, ["src/gzkit/producer.py::airlock_in.undeclared_merged_field"])

    def test_a_declared_helper_field_is_not_reported(self) -> None:
        """The scan must not become a false-positive generator."""
        from gzkit.governance.trust_audits import audit_producer_fields

        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        source = root / "src" / "gzkit" / "producer.py"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(
            "from gzkit.ledger import LedgerEvent\n\n\n"
            "def _extra() -> dict:\n"
            '    return {"decision": "GO"}\n\n\n'
            "def emit() -> LedgerEvent:\n"
            '    return LedgerEvent(event="airlock_in", id="X", extra=_extra())\n',
            encoding="utf-8",
        )
        schema = root / "src" / "gzkit" / "schemas" / "ledger.json"
        schema.parent.mkdir(parents=True, exist_ok=True)
        schema.write_text(
            json.dumps(
                {"events": {"airlock_in": {"required": [], "properties": {"decision": {}}}}}
            ),
            encoding="utf-8",
        )
        self.assertEqual([e.artifact for e in audit_producer_fields(root)], [])

    def test_the_runtime_scan_over_this_repository_is_clean(self) -> None:
        """The class fix, applied to the real tree the audit guards."""
        from gzkit.governance.trust_audits import audit_producer_fields

        errors = audit_producer_fields(Path(__file__).resolve().parents[1])
        self.assertEqual([f"{e.artifact}: {e.message}" for e in errors], [])


class TestCorrectionAttributionIsTypeStrict(unittest.TestCase):
    """A correction's attribution must be a real string on every reader.

    ``_field`` returned ``str(value)``, so ``attestor: None`` became the string
    ``"None"``, ``attestor: 7`` became ``"7"``, ``False`` became ``"False"`` and
    ``{}`` became ``"{}"`` — each non-empty, each passing ``is_well_formed``, and
    each therefore voiding its subject at replay. Both declared validators refuse
    all four: ``LedgerEventCorrectedEvent.attestor`` is ``str`` and the ledger
    schema declares ``string``. Replay is what every consumer uses, so the
    stringifying reader was the one that decided.
    """

    SUBJECT = _row("gate_checked", "ADR-0.0.1", "2026-09-06T00:00:00+00:00")

    def _correction(self, field: str, value: object) -> dict:
        correction = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        correction[field] = value
        return correction

    def test_a_non_string_attribution_is_not_well_formed(self) -> None:
        from gzkit.ledger_corrections import is_well_formed

        for field in ("attestor", "reason"):
            for label, value in (("null", None), ("number", 7), ("bool", False), ("object", {})):
                with self.subTest(field=field, value=label):
                    self.assertFalse(is_well_formed(self._correction(field, value)))

    def test_a_non_string_attribution_leaves_the_subject_live(self) -> None:
        """The property that matters: an inert correction changes no state."""
        for field in ("attestor", "reason"):
            for label, value in (("null", None), ("number", 7), ("bool", False), ("object", {})):
                with self.subTest(field=field, value=label):
                    stream = [self.SUBJECT, self._correction(field, value)]
                    self.assertIn(self.SUBJECT, live_events(stream))
                    self.assertIn(self.SUBJECT, evidence_events(stream))

    def test_the_ledger_validator_refuses_the_same_rows(self) -> None:
        """All three readers must agree, which is the point of the repair."""
        for field in ("attestor", "reason"):
            for label, value in (("null", None), ("number", 7), ("bool", False), ("object", {})):
                with self.subTest(field=field, value=label):
                    errors = _validate_rows(self, [self.SUBJECT, self._correction(field, value)])
                    self.assertNotEqual(errors, [], "the ledger validator accepted it")

    def test_a_genuine_string_attribution_still_applies(self) -> None:
        """Guard: the strictness must not make every correction inert."""
        stream = [self.SUBJECT, _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")]
        self.assertNotIn(self.SUBJECT, live_events(stream))


class TestSubjectIdentityIsTypeStrict(unittest.TestCase):
    """``subject_id: 7`` must not name the artifact whose id is the string ``"7"``.

    Both sides were stringified before comparison, so an integer subject id
    matched a string artifact id and voided a row the correction never named.
    """

    SUBJECT = _row("artifact_created", "7", "2026-09-06T00:00:00+00:00")

    def test_a_numeric_subject_id_does_not_match_a_string_artifact_id(self) -> None:
        correction = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        correction["subject_id"] = 7
        stream = [self.SUBJECT, correction]
        self.assertIn(self.SUBJECT, live_events(stream), "an int subject_id voided a string id")

    def test_the_matching_string_subject_id_still_matches(self) -> None:
        """Guard: strictness must not break the ordinary case."""
        stream = [self.SUBJECT, _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")]
        self.assertNotIn(self.SUBJECT, live_events(stream))


class TestTheFactoryRefusesBlankAttribution(unittest.TestCase):
    """``min_length=1`` counts characters, so ``"   "`` satisfied it.

    ``gz ledger correct`` strips before checking and the ledger validator
    measures the STRIPPED length (GHI #882), so the factory — the one
    constructor callers actually reach — was the only surface that would mint a
    whitespace-attributed correction.
    """

    def _mint(self, **overrides: str) -> None:
        payload = {
            "subject_event": "gate_checked",
            "subject_id": "ADR-0.0.1",
            "subject_ts": "2026-09-06T00:00:00+00:00",
            "disposition": "void",
            "cause": "agent-error",
            "attestor": "g0",
            "reason": "recorded in error",
        }
        ledger_event_corrected_event(**{**payload, **overrides})

    def test_a_whitespace_attestor_is_refused(self) -> None:
        with self.assertRaises(ValidationError):
            self._mint(attestor="   ")

    def test_a_whitespace_reason_is_refused(self) -> None:
        with self.assertRaises(ValidationError):
            self._mint(reason="\t\n ")

    def test_a_whitespace_subject_reference_is_refused(self) -> None:
        for field in ("subject_event", "subject_id", "subject_ts"):
            with self.subTest(field=field), self.assertRaises(ValidationError):
                self._mint(**{field: "  "})

    def test_a_real_attribution_still_mints(self) -> None:
        self._mint()


class TestValidateLedgerEnforcesTheCommandsContract(unittest.TestCase):
    """``gz ledger correct`` refuses three shapes; the ledger accepted all three.

    The command holds the whole ledger and can therefore check what a
    single-row reader cannot. But a hand-written row, a merge, or a direct
    factory call never passes through the command, and ``gz validate --ledger``
    is the gate that reads what actually landed — so its silence meant a
    contract-violating correction sat in the file reading as valid.
    """

    SUBJECT = _row(
        "gate_checked",
        "ADR-0.0.1",
        "2026-09-06T00:00:00+00:00",
        gate=2,
        status="pass",
        command="uv run gz check",
        returncode=0,
    )

    def test_a_dangling_subject_reference_is_refused(self) -> None:
        correction = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        correction["subject_ts"] = "2999-01-01T00:00:00+00:00"
        errors = _validate_rows(self, [self.SUBJECT, correction])
        self.assertTrue(
            any("no ledger row" in e.message for e in errors),
            f"expected a dangling-reference finding, got {[e.message for e in errors]}",
        )

    def test_a_correction_naming_another_correction_is_refused(self) -> None:
        first = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        second = _correction(self.SUBJECT, "reinstated", ts="2026-09-06T02:00:00+00:00")
        second["subject_event"] = CORRECTION_EVENT
        second["subject_ts"] = first["ts"]
        errors = _validate_rows(self, [self.SUBJECT, first, second])
        self.assertTrue(
            any("another correction" in e.message for e in errors),
            f"expected a correction-of-correction finding, got {[e.message for e in errors]}",
        )

    def test_a_correction_preceding_its_subject_is_refused(self) -> None:
        """The ledger is ts-ordered, so a correction can never predate its subject."""
        correction = _correction(self.SUBJECT, "void", ts="2026-09-05T00:00:00+00:00")
        errors = _validate_rows(self, [correction, self.SUBJECT])
        self.assertTrue(
            any("precedes its subject" in e.message for e in errors),
            f"expected an ordering finding, got {[e.message for e in errors]}",
        )

    def test_a_well_formed_correction_is_still_accepted(self) -> None:
        """Guard: none of the three refusals may fire on the ordinary case."""
        correction = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        self.assertEqual([e.message for e in _validate_rows(self, [self.SUBJECT, correction])], [])

    def test_the_validator_shares_the_replay_contract(self) -> None:
        """It must not become a second, drifting implementation of `is_well_formed`.

        The netting rule already lives in `gzkit.ledger_corrections`. A validator
        that re-derived "is this correction well formed" would be the per-consumer
        re-implementation this primitive exists to end — and the two copies would
        disagree on the first amendment to either.
        """
        import inspect

        from gzkit.validate_pkg import ledger_check

        source = inspect.getsource(ledger_check)
        self.assertIn("is_well_formed", source)
        self.assertIn("corrected_subject", source)


class TestInvalidCorrectionsCannotChangeDerivedState(unittest.TestCase):
    """The end-to-end property: an invalid correction moves nothing.

    Asserted against the derived readings a consumer actually calls, not against
    `is_well_formed` alone — a predicate can be right while a caller ignores it.
    """

    SUBJECT = _row("obpi_completed", "OBPI-X", "2026-09-06T00:00:00+00:00")

    def _invalid_corrections(self) -> list[tuple[str, dict]]:
        def mutate(label: str, **fields: object) -> tuple[str, dict]:
            correction = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
            correction.update(fields)
            return label, correction

        return [
            mutate("empty attestor", attestor=""),
            mutate("whitespace attestor", attestor="   "),
            mutate("null attestor", attestor=None),
            mutate("numeric attestor", attestor=7),
            mutate("empty reason", reason=""),
            mutate("null reason", reason=None),
            mutate("object reason", reason={"why": "x"}),
            mutate("unknown disposition", disposition="deleted"),
            mutate("unknown cause", cause="because"),
            mutate("blank subject event", subject_event=""),
            mutate("numeric subject id", subject_id=7),
            mutate("correction as subject", subject_event=CORRECTION_EVENT),
        ]

    def test_no_invalid_void_removes_its_subject(self) -> None:
        for label, correction in self._invalid_corrections():
            with self.subTest(correction=label):
                stream = [self.SUBJECT, correction]
                self.assertIn(self.SUBJECT, live_events(stream))
                self.assertIn(self.SUBJECT, evidence_events(stream))
                self.assertEqual(correction_state(stream), {})

    def test_no_invalid_reinstatement_revives_a_voided_subject(self) -> None:
        """The reversal direction, which a `void`-only test would miss entirely."""
        void = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        for label, template in self._invalid_corrections():
            reinstate = dict(template)
            reinstate["ts"] = "2026-09-06T02:00:00+00:00"
            if reinstate.get("disposition") == "void":
                reinstate["disposition"] = "reinstated"
            with self.subTest(correction=label):
                stream = [self.SUBJECT, void, reinstate]
                self.assertNotIn(
                    self.SUBJECT, live_events(stream), "an invalid reinstatement revived the row"
                )

    def test_a_valid_reinstatement_still_revives_it(self) -> None:
        """Guard: the assertion above must not pass because nothing ever revives."""
        void = _correction(self.SUBJECT, "void", ts="2026-09-06T01:00:00+00:00")
        good = _correction(self.SUBJECT, "reinstated", ts="2026-09-06T02:00:00+00:00")
        self.assertIn(self.SUBJECT, live_events([self.SUBJECT, void, good]))


class TestMalformedContainersAreRejectedNotFatal(unittest.TestCase):
    """A value of the wrong CONTAINER type is refused, never fatal.

    Two closed vocabularies and one identity triple are the surfaces, and both
    failed the same way. ``DISPOSITIONS`` and ``CAUSES`` are frozensets, so
    ``[] in DISPOSITIONS`` RAISES rather than returning ``False``; the
    ``(event, id, ts)`` triple is hashed into every subject index, so an ordinary
    row carrying ``id: []`` raised on the way in — with no correction anywhere in
    the file.

    The distinction that matters is between a finding and a crash. Both readers
    below are documented as reporting malformed input:
    ``gz validate --ledger`` exists to say what is wrong with a row, and
    :func:`~gzkit.ledger.read_corrected_rows` is the TOLERANT reader whose whole
    reason to exist is that a pipeline gate or a commit hook must not raise. An
    exception from either does not report the defect — it disables the reader
    that would have.
    """

    _SUBJECT_TS = "2026-09-02T00:00:00+00:00"

    def _rows_with(self, **overrides: object) -> list[dict]:
        subject = _row("pipeline_launched", "OBPI-X", self._SUBJECT_TS)
        correction = _correction(subject, "void", ts="2026-09-06T20:00:00+00:00")
        correction.update(overrides)
        return [subject, correction]

    def test_an_unhashable_disposition_is_inert_rather_than_fatal(self) -> None:
        rows = self._rows_with(disposition={})
        self.assertEqual(correction_state(rows), {})
        self.assertIn(rows[0], live_events(rows))

    def test_an_unhashable_cause_is_inert_rather_than_fatal(self) -> None:
        rows = self._rows_with(cause=[])
        self.assertEqual(correction_state(rows), {})
        self.assertIn(rows[0], live_events(rows))

    def test_an_unhashable_correction_is_inert_through_a_real_ledger(self) -> None:
        """Replay through the shipped reader, not the primitive in isolation."""
        rows = self._rows_with(cause=[])
        ledger = Ledger(_ledger_file(self, rows))
        self.assertEqual([e.event for e in ledger.read_all()], ["pipeline_launched"])

    def test_an_unhashable_identity_validates_to_findings_not_an_exception(self) -> None:
        """No correction is present at all — an ordinary malformed row sufficed."""
        for field in ("id", "ts"):
            with self.subTest(field=field):
                row = _row("pipeline_launched", "OBPI-X", self._SUBJECT_TS)
                row[field] = []
                messages = [e.message for e in _validate_rows(self, [row])]
                self.assertTrue(
                    any(f"Field '{field}'" in message for message in messages),
                    f"the malformed {field} was not reported: {messages}",
                )

    def test_the_tolerant_reader_survives_an_unhashable_identity(self) -> None:
        """Its contract is to skip what it cannot read, never to raise (GHI #611)."""
        from gzkit.ledger import read_corrected_rows

        row = _row("pipeline_launched", "OBPI-X", self._SUBJECT_TS)
        row["id"] = []
        self.assertEqual(read_corrected_rows(_ledger_file(self, [row])), [row])

    def test_a_correction_naming_an_unhashable_subject_is_inert(self) -> None:
        rows = self._rows_with(subject_id=[])
        self.assertEqual(correction_state(rows), {})
        self.assertIn(rows[0], live_events(rows))


class TestValidationAndReplayRefuseTheSameCorrections(unittest.TestCase):
    """One contract, two paths — a row either reader rejects is inert in both.

    The checks were split: envelope validity and append order lived only in
    ``gz validate --ledger``, and replay read neither. So a correction stamped
    with a foreign ``schema`` tag, or an unparseable ``ts``, or standing ahead of
    the row it corrects, was REPORTED by the validator and then went on voiding
    its subject everywhere derived state is read — which is every consumer. A
    guard only the write path enforces is decorative (the module says so of the
    payload checks); a guard only the validator enforces is worse, because the
    operator has seen it fire and believes the row was refused.

    Every case runs through an actual temporary :class:`~gzkit.ledger.Ledger`
    file: the same bytes are handed to the validator and to replay, so the two
    answers are comparable rather than merely both asserted.
    """

    SUBJECT_TS = "2026-09-02T00:00:00+00:00"
    LATER_TS = "2026-09-06T20:00:00+00:00"

    #: A SCHEMA-COMPLETE subject. The positive cases below assert the validator
    #: reports nothing at all, which is only meaningful when the rows carry every
    #: field their event declares — otherwise the assertion passes or fails on
    #: fixture shape rather than on the correction under test.
    LAUNCH_FIELDS = {
        "nonce": "b8f1c2",
        "marker_path": ".gzkit/pipeline/OBPI-0.35.0-08.json",
        "lane": "lite",
    }

    def setUp(self) -> None:
        self.subject = _row(
            "pipeline_launched", "OBPI-0.35.0-08", self.SUBJECT_TS, **self.LAUNCH_FIELDS
        )

    def _correcting(self, disposition: str = "void", **overrides: object) -> dict:
        correction = _correction(
            self.subject,
            disposition,
            ts=self.LATER_TS,
            cause="agent-error" if disposition != "reinstated" else "operator-error",
        )
        correction.update(overrides)
        return correction

    def _both(self, rows: list[dict]) -> tuple[list[str], list[str]]:
        """Return ``(validator messages, replayed event names)`` for one file."""
        path = _ledger_file(self, rows)
        from gzkit.validate_pkg.ledger_check import validate_ledger

        return (
            [e.message for e in validate_ledger(path)],
            [e.event for e in Ledger(path).read_all()],
        )

    def _assert_refused_by_both(self, rows: list[dict], expected: str) -> None:
        messages, replayed = self._both(rows)
        self.assertTrue(
            any(expected in message for message in messages),
            f"the validator did not report it: {messages}",
        )
        self.assertEqual(
            replayed,
            ["pipeline_launched"],
            "the validator refused this correction and replay applied it anyway",
        )

    def test_a_foreign_schema_tag_is_reported_and_inert(self) -> None:
        self._assert_refused_by_both(
            [self.subject, self._correcting(schema="gzkit.ledger.v0")],
            "Invalid schema value",
        )

    def test_an_unparseable_timestamp_is_reported_and_inert(self) -> None:
        self._assert_refused_by_both(
            [self.subject, self._correcting(ts="not-a-date")],
            "not valid ISO8601",
        )

    def test_an_empty_row_id_is_reported_and_inert(self) -> None:
        self._assert_refused_by_both(
            [self.subject, self._correcting(id="   ")],
            "must be a non-empty string",
        )

    def test_a_correction_preceding_its_subject_is_reported_and_inert(self) -> None:
        correction = self._correcting(ts="2026-09-01T00:00:00+00:00")
        self._assert_refused_by_both([correction, self.subject], "precedes its subject")

    def test_an_equal_timestamp_inversion_is_reported_and_inert(self) -> None:
        """Timestamps alone do not establish append order — position does.

        The ledger already contains a byte-identical pair sharing a ``ts``, so
        two rows may legitimately carry the same instant. An ordering rule that
        compares timestamps therefore reads ``correction_ts < subject_ts`` as
        false here and reports NOTHING, while the correction sits ahead of the
        row it names.
        """
        correction = self._correcting(ts=self.SUBJECT_TS)
        self._assert_refused_by_both([correction, self.subject], "precedes its subject")

    def test_an_invalid_reinstatement_cannot_revive_a_voided_row(self) -> None:
        """The reversal arm fails the same way, in the direction that restores state.

        A void that must not apply and a reinstatement that must not apply are
        not symmetric defects: the first wrongly hides a row, the second wrongly
        RESURRECTS one that a valid correction voided. Both are the same missing
        check, so both are asserted.
        """
        rows = [
            self.subject,
            self._correcting("void"),
            self._correcting("reinstated", ts="not-a-date"),
        ]
        messages, replayed = self._both(rows)
        self.assertTrue(any("not valid ISO8601" in message for message in messages), messages)
        self.assertEqual(replayed, [], "an invalid reinstatement revived a voided row")

    def test_a_reinstatement_preceding_its_subject_cannot_revive_it(self) -> None:
        rows = [self.subject, self._correcting("void")]
        early = _correction(
            self.subject, "reinstated", ts="2026-09-01T00:00:00+00:00", cause="operator-error"
        )
        messages, replayed = self._both([early, *rows])
        self.assertTrue(any("precedes its subject" in message for message in messages), messages)
        self.assertEqual(replayed, [])

    # --- positive cases: the legitimate shapes must keep working -------------

    def test_a_legitimate_void_is_accepted_by_both_paths(self) -> None:
        messages, replayed = self._both([self.subject, self._correcting()])
        self.assertEqual(messages, [])
        self.assertEqual(replayed, [])

    def test_repeated_corrections_resolve_to_the_last(self) -> None:
        rows = [
            self.subject,
            self._correcting("void"),
            _correction(
                self.subject,
                "discharged",
                ts="2026-09-07T00:00:00+00:00",
                cause="condition-resolved",
            ),
        ]
        messages, replayed = self._both(rows)
        self.assertEqual(messages, [])
        self.assertEqual(replayed, [])
        path = _ledger_file(self, rows)
        self.assertEqual(
            [e.event for e in Ledger(path).read_evidence()],
            ["pipeline_launched"],
            "a discharged row is still evidence that it was once true",
        )

    def test_a_reinstatement_restores_its_subject(self) -> None:
        rows = [
            self.subject,
            self._correcting("void"),
            _correction(
                self.subject, "reinstated", ts="2026-09-07T00:00:00+00:00", cause="operator-error"
            ),
        ]
        messages, replayed = self._both(rows)
        self.assertEqual(messages, [])
        self.assertEqual(replayed, ["pipeline_launched"])

    def test_intervening_work_between_subject_and_correction_is_untouched(self) -> None:
        other = _row(
            "pipeline_launched",
            "OBPI-0.35.0-09",
            "2026-09-03T00:00:00+00:00",
            **self.LAUNCH_FIELDS,
        )
        messages, replayed = self._both([self.subject, other, self._correcting()])
        self.assertEqual(messages, [])
        self.assertEqual(replayed, ["pipeline_launched"])
        self.assertEqual(
            [
                e.id
                for e in Ledger(
                    _ledger_file(self, [self.subject, other, self._correcting()])
                ).read_all()
            ],
            ["OBPI-0.35.0-09"],
            "the correction voided a neighbour it did not name",
        )

    def test_equal_timestamps_in_valid_order_are_accepted(self) -> None:
        """Sharing an instant is legitimate; only the INVERSION is refused.

        The counterpart to the equal-timestamp inversion above. Position, not the
        timestamp, is what the rule reads — so a correction stamped identically to
        its subject but appended AFTER it is a normal correction.
        """
        messages, replayed = self._both([self.subject, self._correcting(ts=self.SUBJECT_TS)])
        self.assertEqual(messages, [])
        self.assertEqual(replayed, [])


class TestAStoredRowsEnvelopeIsNeverManufactured(unittest.TestCase):
    """A correction's validity must describe the STORED ROW, not the parsed object.

    The class above proves the two paths refuse the same correction when the
    envelope carries a WRONG value. It could not see the other half: an ABSENT
    one. ``LedgerEvent`` supplies ``schema_`` and ``ts`` from field defaults, and
    :meth:`~gzkit.ledger.Ledger.read_history` parsed every stored row through it
    — so a correction whose bytes carry neither arrived at replay wearing this
    ledger's tag and a timestamp of *this instant*. The envelope check then read
    those manufactured values and passed. ``gz validate --ledger`` reported the
    row, ``read_corrected_rows`` left it inert, and the graph applied its void:
    three readers, one set of bytes, three answers.

    The defaults themselves are legitimate — an event being AUTHORED has no
    timestamp until something stamps one. What is not legitimate is applying
    them to a row that already exists on disk, because there the envelope is a
    fact about the file and reading is not the moment to invent it.

    The second half is the guard's own gap: ``parent`` is the fifth envelope
    field, ``gz validate --ledger`` checks it and ``LedgerEvent`` refuses it, but
    :func:`~gzkit.ledger_corrections.is_well_formed` never read it — so
    ``parent: 7`` was refused by both of those and applied by the tolerant reader
    that exists precisely to stand in for them where raising is not allowed.

    Every case hands the SAME temporary file to all three readers. The assertion
    is the SUBJECT'S STATE — the graph's ``pipeline_launched`` flag and the row's
    presence in the tolerant stream — never a helper's return value, because a
    helper agreeing while derived state diverges is the defect being closed.
    """

    SUBJECT_TS = "2026-09-02T00:00:00+00:00"
    VOID_TS = "2026-09-06T20:00:00+00:00"
    REINSTATE_TS = "2026-09-06T21:00:00+00:00"
    OBPI = "OBPI-0.35.0-08"

    #: Schema-complete, so a positive case asserting the validator reports
    #: NOTHING is answering about the correction rather than about the fixture.
    LAUNCH_FIELDS = {
        "nonce": "b8f1c2",
        "marker_path": ".gzkit/pipeline/OBPI-0.35.0-08.json",
        "lane": "lite",
    }

    def setUp(self) -> None:
        self.created = _row(
            "obpi_created", self.OBPI, "2026-07-21T23:36:03+00:00", parent="ADR-0.35.0"
        )
        self.subject = _row("pipeline_launched", self.OBPI, self.SUBJECT_TS, **self.LAUNCH_FIELDS)

    # -- fixtures ---------------------------------------------------------

    def _void(self, **overrides: object) -> dict:
        row = _correction(self.subject, "void", ts=self.VOID_TS, reason="started in error")
        row.update(overrides)
        return row

    def _reinstate(self, **overrides: object) -> dict:
        row = _correction(
            self.subject,
            "reinstated",
            ts=self.REINSTATE_TS,
            cause="operator-error",
            reason="the void was itself wrong",
        )
        row.update(overrides)
        return row

    @staticmethod
    def _without(row: dict, field: str) -> dict:
        """Return ``row`` with ``field`` ABSENT — not empty, not null, gone.

        Absence is the shape the model repaired; an empty or null value is a
        different case that the parser and the validator both already refuse.
        """
        stripped = dict(row)
        del stripped[field]
        return stripped

    # -- the three readers, one file --------------------------------------

    def _readers(self, rows: list[dict]) -> tuple[list[str], bool, bool]:
        """Return ``(validator messages, tolerant subject live, graph flag)``.

        One temporary file, read three ways. The last two are SUBJECT STATE:
        whether the corrected row survives the tolerant live stream, and what
        the artifact graph says about the OBPI it launched.
        """
        from gzkit.validate_pkg.ledger_check import validate_ledger

        path = _ledger_file(self, rows)
        messages = [e.message for e in validate_ledger(path)]
        tolerant = read_corrected_rows(path, stream="live")
        live = any(row.get("event") == "pipeline_launched" for row in tolerant)
        graph = Ledger(path).get_artifact_graph()[self.OBPI]["pipeline_launched"]
        return messages, live, bool(graph)

    def _assert_inert_everywhere(self, correction: dict, expected: str) -> None:
        """A void the validator reports must leave the launch standing in BOTH readers."""
        messages, tolerant_live, graph_flag = self._readers(
            [self.created, self.subject, correction]
        )
        self.assertTrue(
            any(expected in message for message in messages),
            f"the validator did not report it: {messages}",
        )
        self.assertTrue(tolerant_live, "the tolerant reader applied a correction it must refuse")
        self.assertTrue(graph_flag, "the graph applied a correction the validator rejects")

    def _assert_cannot_revive(self, reinstatement: dict, expected: str) -> None:
        """A malformed reinstatement must leave a validly-voided launch voided."""
        messages, tolerant_live, graph_flag = self._readers(
            [self.created, self.subject, self._void(), reinstatement]
        )
        self.assertTrue(
            any(expected in message for message in messages),
            f"the validator did not report it: {messages}",
        )
        self.assertFalse(tolerant_live, "a rejected reinstatement revived a validly voided row")
        self.assertFalse(graph_flag, "a rejected reinstatement revived a validly voided row")

    # -- absent schema ----------------------------------------------------

    def test_a_void_with_no_schema_tag_is_inert_in_every_reader(self) -> None:
        self._assert_inert_everywhere(
            self._without(self._void(), "schema"), "Missing required field: schema"
        )

    def test_a_reinstatement_with_no_schema_tag_cannot_revive(self) -> None:
        self._assert_cannot_revive(
            self._without(self._reinstate(), "schema"), "Missing required field: schema"
        )

    # -- absent timestamp -------------------------------------------------

    def test_a_void_with_no_timestamp_is_inert_in_every_reader(self) -> None:
        self._assert_inert_everywhere(
            self._without(self._void(), "ts"), "Missing required field: ts"
        )

    def test_a_reinstatement_with_no_timestamp_cannot_revive(self) -> None:
        self._assert_cannot_revive(
            self._without(self._reinstate(), "ts"), "Missing required field: ts"
        )

    # -- non-string parent ------------------------------------------------

    def test_a_void_with_a_non_string_parent_is_inert_in_the_tolerant_reader(self) -> None:
        """The gap the guard itself had, on the one path that had to catch it.

        ``gz validate --ledger`` reports this row and ``LedgerEvent`` refuses to
        parse it, so the strict :class:`~gzkit.ledger.Ledger` never applies it —
        it raises instead, which is that reader's documented contract for a
        malformed row. The tolerant reader exists BECAUSE raising is forbidden
        inside a pipeline gate or a commit hook, which left it as the only path
        that could apply the correction, and it did.
        """
        rows = [self.created, self.subject, self._void(parent=7)]
        path = _ledger_file(self, rows)
        from gzkit.validate_pkg.ledger_check import validate_ledger

        self.assertTrue(
            any("Field 'parent' must be a string" in e.message for e in validate_ledger(path)),
            "the validator did not report the non-string parent",
        )
        with self.assertRaises(ValidationError):
            Ledger(path).read_history()
        self.assertTrue(
            any(
                row.get("event") == "pipeline_launched"
                for row in read_corrected_rows(path, stream="live")
            ),
            "the tolerant reader applied a correction both other readers refuse",
        )

    def test_a_reinstatement_with_a_non_string_parent_cannot_revive(self) -> None:
        rows = [self.created, self.subject, self._void(), self._reinstate(parent=7)]
        path = _ledger_file(self, rows)
        self.assertFalse(
            any(
                row.get("event") == "pipeline_launched"
                for row in read_corrected_rows(path, stream="live")
            ),
            "a rejected reinstatement revived a validly voided row",
        )

    def test_a_string_parent_is_still_accepted(self) -> None:
        """The repair refuses the wrong TYPE, never the field itself."""
        messages, tolerant_live, graph_flag = self._readers(
            [self.created, self.subject, self._void(parent="ADR-0.35.0")]
        )
        self.assertEqual(messages, [])
        self.assertFalse(tolerant_live)
        self.assertFalse(graph_flag)

    # -- the shared contract ----------------------------------------------

    def test_both_readers_reach_the_same_verdict_on_the_same_bytes(self) -> None:
        """``is_well_formed`` must answer identically however the row was read.

        The property underneath every case above, asserted directly: for one set
        of bytes, the raw dict a tolerant reader holds and the
        :class:`~gzkit.ledger.LedgerEvent` a strict reader parses are the same
        row, so they cannot be allowed to disagree about whether it is a valid
        correction. They did, in the two directions a default can fill.
        """
        for label, correction in (
            ("no schema", self._without(self._void(), "schema")),
            ("no ts", self._without(self._void(), "ts")),
            ("valid", self._void()),
        ):
            with self.subTest(label):
                path = _ledger_file(self, [self.created, self.subject, correction])
                raw = [
                    json.loads(line)
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                typed = Ledger(path).read_history()
                self.assertEqual(
                    [is_well_formed(row) for row in raw if is_correction(row)],
                    [is_well_formed(event) for event in typed if is_correction(event)],
                    "the raw and typed readings of one row disagree about its validity",
                )

    # -- positive cases, unchanged ----------------------------------------

    def test_a_valid_void_still_reaches_every_reader(self) -> None:
        messages, tolerant_live, graph_flag = self._readers(
            [self.created, self.subject, self._void()]
        )
        self.assertEqual(messages, [])
        self.assertFalse(tolerant_live, "a valid void left its subject live")
        self.assertFalse(graph_flag, "a valid void left the graph reading the launch")

    def test_a_valid_reinstatement_still_revives_its_subject(self) -> None:
        messages, tolerant_live, graph_flag = self._readers(
            [self.created, self.subject, self._void(), self._reinstate()]
        )
        self.assertEqual(messages, [])
        self.assertTrue(tolerant_live, "a valid reinstatement did not restore its subject")
        self.assertTrue(graph_flag, "a valid reinstatement did not restore the graph flag")

    def test_repeated_corrections_still_resolve_to_the_last(self) -> None:
        messages, tolerant_live, graph_flag = self._readers(
            [
                self.created,
                self.subject,
                self._void(),
                self._reinstate(),
                self._void(ts="2026-09-06T22:00:00+00:00"),
            ]
        )
        self.assertEqual(messages, [])
        self.assertFalse(tolerant_live)
        self.assertFalse(graph_flag)

    def test_equal_timestamps_in_valid_append_order_are_still_accepted(self) -> None:
        """Sharing an instant is legitimate; the repair reads absence, not order."""
        messages, tolerant_live, graph_flag = self._readers(
            [self.created, self.subject, self._void(ts=self.SUBJECT_TS)]
        )
        self.assertEqual(messages, [])
        self.assertFalse(tolerant_live)
        self.assertFalse(graph_flag)

    def test_an_authored_event_still_gets_its_defaults(self) -> None:
        """The constructor defaults are legitimate and stay.

        Repairing the READ path must not disturb the AUTHORING path: an event
        being minted has no timestamp until something stamps one, and every
        producer in the tree relies on that.
        """
        authored = LedgerEvent(event="prd_created", id="PRD-1")
        self.assertEqual(authored.schema_, LEDGER_SCHEMA)
        self.assertIsNotNone(parse_ledger_ts(authored.ts))


class TestProducerAuditReadsTheRealAirlockProducer(unittest.TestCase):
    """Coverage is proven against the SHIPPED producer, never a stand-in.

    Two passes of this audit reported zero findings on ``gzkit/airlock/enter.py``
    while its override fields were undeclared, and each was defended by a
    synthetic fixture written in a shape the scanner could already read — a
    plain ``payload = {}`` opened with :class:`ast.Assign`, and a helper CALLED
    at the merge. The real producer has neither: ``_book_transit`` opens with an
    ANNOTATED assignment and merges ``payload.update(extra)``, where ``extra`` is
    a parameter its caller binds to ``_override_extra(override)``. So the scan
    saw nothing at all on that file — not the override fields, and not
    ``decision`` or ``unaccounted`` either — and reported clean.

    The fixture therefore copies the real ``enter.py`` and drops one declaration
    at a time from a copy of the real schema. A test that removes a declaration
    and still sees zero findings is the exact false green this class exists to
    make impossible.
    """

    #: What ``_book_transit`` writes on ``airlock_in``: two literal keys and the
    #: three the override helper contributes. Hard-coded rather than read back
    #: through the scanner under test, which would be circular; pinned against
    #: the schema below so a sixth field cannot be added silently.
    WRITTEN_FIELDS = frozenset(
        {"decision", "unaccounted", "override_seam", "override_attestor", "override_revoked"}
    )

    def _audit(self, dropped: str | None = None) -> list[str]:
        """Run the shipped audit over a tree holding the REAL producer source."""
        import shutil

        from gzkit.governance.trust_audits import audit_producer_fields

        repo = Path(__file__).resolve().parents[1]
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        package = root / "src" / "gzkit"
        (package / "airlock").mkdir(parents=True)
        (package / "schemas").mkdir(parents=True)
        shutil.copy(repo / "src" / "gzkit" / "airlock" / "enter.py", package / "airlock")

        schema = json.loads(
            (repo / "src" / "gzkit" / "schemas" / "ledger.json").read_text(encoding="utf-8")
        )
        if dropped is not None:
            del schema["events"]["airlock_in"]["properties"][dropped]
        (package / "schemas" / "ledger.json").write_text(json.dumps(schema), encoding="utf-8")
        return [e.artifact for e in audit_producer_fields(root)]

    def test_the_declared_airlock_in_fields_are_the_ones_the_producer_writes(self) -> None:
        """Pins the roster below, so a new payload field cannot slip past it."""
        from gzkit.schemas import load_schema

        self.assertEqual(
            set(load_schema("ledger")["events"]["airlock_in"]["properties"]),
            set(self.WRITTEN_FIELDS),
            "airlock_in's declared fields changed; extend WRITTEN_FIELDS and confirm "
            "the audit still reports each one's removal",
        )

    def test_the_real_producer_is_clean_against_the_shipped_schema(self) -> None:
        self.assertEqual(self._audit(), [])

    def test_removing_any_declaration_the_real_producer_writes_is_reported(self) -> None:
        """The claim the previous two passes made and could not support.

        Each field is dropped from the schema in turn; the audit must name that
        exact field on that exact producer. ``override_seam`` is the operator's
        named counterexample — it yielded zero findings before this pass.
        """
        for field in sorted(self.WRITTEN_FIELDS):
            with self.subTest(field=field):
                self.assertEqual(
                    self._audit(field),
                    [f"src/gzkit/airlock/enter.py::airlock_in.{field}"],
                )
