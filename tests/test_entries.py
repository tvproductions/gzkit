"""The maintenance record's writer and reducer: RP-12 O4 task 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the maintenance record
is ledger events, rendered as a view (ruling 8). The performer books its own entry
(ruling 167, 14 CFR § 43.9(a)): a call stamped as the live `Implementer`,
`SingleDriver` or `Restoration` dispatch it names, on that dispatch's order
(rulings 133's form, 160 and 175), the order commenced and not blocked. The entry
carries what was done, the measurement before and after and the witness that
measured it, none blank (ruling 173), with the open MX session (ruling 8); its id
is `ENT-<NN>-<slug>` (ruling 169). The order and the package are read from the
dispatch record, never typed (rulings 1 and 130). A refusal writes nothing.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from gzkit.events import (
    BaselinedReq,
    EntryBookedEvent,
    OrderTransitionedEvent,
    WorkPackageDispatchedEvent,
)
from gzkit.ledger import Ledger, ledger_row
from gzkit.models.catalog import Catalog, Criterion, Order, RepairReq, WorkPackage
from gzkit.mx.entries import (
    EntryBook,
    EntryError,
    LandingCommit,
    RecordedEntry,
    entries_cited,
    entry_block,
    landings,
    maintenance_record,
    record_entry_book,
    record_view,
)
from gzkit.order_ledger import OrderMove, order_took_stopping_exit, record_order_transition
from gzkit.work_package_ledger import TransitionRequest, record_work_package_transition
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    UnblockRequest,
    record_dispatch_end,
    record_dispatch_void,
    record_work_package_block,
    record_work_package_dispatch,
    record_work_package_unblock,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_SESSION = "mx-20261120-probe"
_REPAIR = "WP-01-stamp"
_ORDER = "ORD-01-import"
_OTHER = "ORD-02-other"
#: A call stamped with the dispatch it names, as the stamp hook would (ruling 133's form).
_AS_NAMED = "as-named"


def _package(wp_id: str) -> WorkPackage:
    return WorkPackage(
        id=wp_id,
        kind="repair",
        outcome=None,
        issues=(1301,),
        lane="lite",
        aliases=(),
        modules=("src/stamp.py",),
        initial_conditions="NA",
        procedure="NA",
        test_and_inspection="NA",
        system_restoration="NA",
        oqe=(),
        alterations=(),
        departures=(),
    )


def _order(order_id: str) -> Order:
    return Order(id=order_id, work_package=_REPAIR, aliases=(), purpose="Fix.", procedure="NA")


def _catalog() -> Catalog:
    req = RepairReq(
        id="REQ-1",
        specialization="repair",
        held_on=_REPAIR,
        problem_report=1301,
        statement="The stamp generator imports again.",
        criteria=(Criterion(state_or_input="an import", required_outcome="ok", evidence="t"),),
        kind="BEHAVIOR",
        revision=1,
    )
    return Catalog(
        families=(),
        outcomes=(),
        reqs=(req,),
        work_packages=(_package(_REPAIR),),
        orders=(_order(_ORDER), _order(_OTHER)),
    )


def _request(**fields: object) -> EntryBook:
    return EntryBook.model_validate(
        {
            "slug": "stamp-import",
            "dispatch": "D-0000000000000000",
            "description": "The stamp generator imports its template again.",
            "before": "tests.test_stamp fails: ImportError on the template",
            "after": "tests.test_stamp passes, 12 tests",
            "witness": "uv run -m unittest tests.test_stamp",
            **fields,
        }
    )


def _raised(act: Callable[[], object]) -> Exception | None:
    """Run *act* and return what it raised, so a crash fails an assertion rather than erroring."""
    try:
        act()
    except Exception as exc:  # a crash in place of the behaviour must fail, not error
        return exc
    return None


def _rows(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class _EntryCase(unittest.TestCase):
    """The repair package initiated, its order commenced with no isolation, an Implementer
    dispatched on it against the order's frozen REQ."""

    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = Path(self._dir.name) / "ledger.jsonl"
        self.ledger = Ledger(self.path)
        self.catalog = _catalog()
        record_work_package_transition(
            self.catalog,
            self.ledger,
            TransitionRequest(
                work_package=_REPAIR, to_state="initiated", evidence="e", operator_text="go"
            ),
        )
        self.commence(_ORDER)
        self.dispatch = self.book("Implementer")

    def move(self, order: str, to_state: str, **fields: object) -> None:
        request = OrderMove.model_validate(
            {"order": order, "to_state": to_state, "evidence": "evt-1", **fields}
        )
        record_order_transition(self.catalog, self.ledger, request)

    def commence(self, order: str) -> None:
        self.move(order, "opened", operator_text="open it")
        self.move(
            order,
            "frozen",
            baseline=(BaselinedReq(req="REQ-1", revision=1),),
            risk_note="The import touches the hook.",
            review_receipt="review-01",
        )
        self.move(order, "commenced", no_isolation="The fix isolates no surface.")

    def book(self, role: str, order: str = _ORDER) -> str:
        request = DispatchRequest(
            work_package=_REPAIR,
            role=role,
            model="opus",
            req=None if role == "Restoration" else "REQ-1",
            root=Path(self._dir.name).resolve().as_posix(),
            order=order,
        )
        return str(record_work_package_dispatch(self.catalog, self.ledger, request).dispatch_id)

    def seat_dispatch(self, role: str, order: str | None = _ORDER) -> str:
        """Seat a dispatch row by hand, a role the dispatch writer books on no commenced order.

        Returns:
            The seated dispatch's id.

        """
        dispatch_id = f"D-{len(_rows(self.path)):016x}"
        seated = WorkPackageDispatchedEvent.model_validate(
            {
                "event": "work_package_dispatched",
                "id": _REPAIR,
                "work_package": _REPAIR,
                "role": role,
                "model": "opus",
                "subject": order or _REPAIR,
                "dispatch_id": dispatch_id,
                "intended_root": Path(self._dir.name).resolve().as_posix(),
                "order": order,
            }
        )
        self.ledger.append(ledger_row(seated))
        return dispatch_id

    def seat(self, row: dict[str, object]) -> None:
        """Append a raw row and re-read the ledger, as a later call would (a void, a move)."""
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"schema": "gzkit.ledger.v1", **row}) + "\n")
        self.ledger = Ledger(self.path)

    def entry(
        self,
        dispatch_id: str | None = None,
        *,
        stamped: str | None = _AS_NAMED,
        session: str | None = _SESSION,
        **fields: str,
    ) -> EntryBookedEvent:
        dispatch_id = dispatch_id or self.dispatch
        return record_entry_book(
            self.ledger,
            _request(dispatch=dispatch_id, **fields),
            stamped_id=dispatch_id if stamped == _AS_NAMED else stamped,
            mx_session_id=session,
        )

    def booked(self, dispatch_id: str | None = None, **fields: str) -> EntryBookedEvent:
        """Book an entry, asserting it is not refused (RP-12 ruling 156).

        Returns:
            The entry booked.

        """
        held: list[EntryBookedEvent] = []
        self.assertIsNone(_raised(lambda: held.append(self.entry(dispatch_id, **fields))))
        return held[0]

    def assert_refused(self, failed: str, act: Callable[[], object] | None = None) -> str:
        """Assert the entry is refused by the check named, and nothing is written.

        ``failed`` is a fragment of the refusal's what-failed part, so a test cannot pass
        on an earlier check's refusal.

        Returns:
            The refusal's text.

        """
        # output-contract: the refusal's what-failed part names the check that refused
        before = _rows(self.path)
        raised = _raised(act or self.entry)
        self.assertIsInstance(raised, EntryError)
        self.assertIn(failed, str(raised))
        self.assertEqual(_rows(self.path), before)
        return str(raised)


class EntryTests(_EntryCase):
    def test_an_entry_records_the_work_its_measurement_and_its_performer(self) -> None:
        """Rulings 8, 167, 169 and 173: one event, the order read from the dispatch."""
        before = len(_rows(self.path))
        returned = self.booked()
        rows = _rows(self.path)
        self.assertEqual(len(rows), before + 1)
        self.assertEqual(returned.entry_id, "ENT-01-stamp-import")
        self.assertEqual((returned.order, returned.work_package), (_ORDER, _REPAIR))
        self.assertEqual(returned.dispatch_id, self.dispatch)
        self.assertEqual(returned.mx_session_id, _SESSION)
        self.assertEqual(
            (returned.before, returned.after, returned.witness),
            (
                "tests.test_stamp fails: ImportError on the template",
                "tests.test_stamp passes, 12 tests",
                "uv run -m unittest tests.test_stamp",
            ),
        )
        self.assertEqual(rows[-1]["event"], "entry_booked")
        self.assertEqual(rows[-1]["id"], "ENT-01-stamp-import")

    def test_entries_number_in_one_series_past_every_entry(self) -> None:
        """Ruling 169: the next id is the highest number the ledger names plus one."""
        self.booked()
        second = self.booked(slug="stamp-docs")
        self.assertEqual(second.entry_id, "ENT-02-stamp-docs")

    def test_the_series_is_numbered_not_spelled_past_99(self) -> None:
        """Ruling 169: past ENT-100 comes ENT-101, a number compared, never a string.

        A string maximum reads ENT-99 above ENT-100 and would mint ENT-100 twice.
        """
        self.booked()
        for number in ("99", "100"):
            row = {
                **_rows(self.path)[-1],
                "id": f"ENT-{number}-far",
                "entry_id": f"ENT-{number}-far",
            }
            row.pop("schema")
            self.seat(row)
        self.assertEqual(self.booked(slug="late").entry_id, "ENT-101-late")

    def test_a_row_the_event_no_longer_admits_still_holds_its_number(self) -> None:
        """Ruling 176: the series reads each row's id by its shape, a malformed row included."""
        self.booked()
        self.seat({"event": "entry_booked", "id": "ENT-05-bad", "ts": "2026-11-20T00:00:00+00:00"})
        self.assertEqual(self.booked(slug="after").entry_id, "ENT-06-after")

    def test_a_voided_entrys_number_is_never_reissued(self) -> None:
        """Ruling 176: the series reads past every number the history names, a void included."""
        voided = _rows(self.path)
        self.booked()
        (subject,) = [row for row in _rows(self.path) if row not in voided]
        self.seat(
            {
                "event": "ledger_event_corrected",
                "id": subject["id"],
                "ts": "2099-01-01T00:00:00+00:00",
                "subject_event": "entry_booked",
                "subject_id": subject["id"],
                "subject_ts": subject["ts"],
                "disposition": "void",
                "cause": "agent-error",
                "attestor": "g0",
                "reason": "booked in error",
            }
        )
        self.assertEqual(maintenance_record(self.ledger), [])
        self.assertEqual(self.booked(slug="again").entry_id, "ENT-02-again")

    def test_each_performing_role_books_its_entry(self) -> None:
        """Ruling 175: Implementer, SingleDriver and Restoration each perform maintenance."""
        for role in ("SingleDriver", "Restoration"):
            with self.subTest(role=role):
                dispatch_id = self.seat_dispatch(role)
                self.assertEqual(self.booked(dispatch_id).dispatch_id, dispatch_id)


class EntryRefusalTests(_EntryCase):
    def test_no_open_mx_session_is_refused(self) -> None:
        """Ruling 8: the entry carries its MX session; with none open it has none."""
        self.assert_refused("No MX session is open", lambda: self.entry(session=None))
        self.assert_refused("No MX session is open", lambda: self.entry(session="  "))

    def test_a_call_not_stamped_as_the_named_dispatch_is_refused(self) -> None:
        """Ruling 167: the performer books its own entry, stamped (ruling 133's form)."""
        self.assert_refused("not stamped with a dispatch id", lambda: self.entry(stamped=None))
        other = self.book("Implementer")
        refusal = self.assert_refused(f"stamped with {other}", lambda: self.entry(stamped=other))
        self.assertIn(f"--dispatch {other}", refusal)

    def test_a_slug_outside_the_grammar_is_refused(self) -> None:
        """Ruling 169: ENT-<NN>-<slug>, lowercase words joined by hyphens."""
        self.assert_refused("is not lowercase words", lambda: self.entry(slug="Stamp Import"))

    def test_a_blank_description_or_measurement_or_witness_is_refused(self) -> None:
        """Rulings 8 and 173: what was done, before, after and the witness are each required."""
        for field in ("description", "before", "after", "witness"):
            with self.subTest(field=field):
                refusal = self.assert_refused(
                    "is blank", lambda field=field: self.entry(**{field: "   "})
                )
                self.assertIn(f"--{field}", refusal)

    def test_a_dispatch_not_booked_voided_or_ended_is_refused(self) -> None:
        """Rulings 1, 42, 115 and 160: only a live dispatch performs."""
        self.assert_refused("not booked", lambda: self.entry(dispatch_id="D-ffffffffffffffff"))
        voided = self.book("Implementer")
        record_dispatch_void(self.ledger, _REPAIR, voided, "killed by TaskStop")
        self.assert_refused("voided", lambda: self.entry(dispatch_id=voided))
        record_dispatch_end(self.ledger, self.dispatch, "a-implementer")
        self.assert_refused("ended", self.entry)

    def test_a_role_that_performs_no_maintenance_is_refused(self) -> None:
        """Ruling 175: Repair only hangs tags, and the reviewers perform no maintenance."""
        for role in ("Repair", "SpecReviewer", "QualityReviewer"):
            with self.subTest(role=role):
                dispatch_id = self.seat_dispatch(role)
                refusal = self.assert_refused(
                    f"a {role} dispatch", lambda dispatch_id=dispatch_id: self.entry(dispatch_id)
                )
                self.assertIn("Implementer, SingleDriver or Restoration", refusal)

    def test_a_dispatch_on_no_order_is_refused(self) -> None:
        """Ruling 175: an entry is booked by a dispatch that performs maintenance on an order."""
        dispatch_id = self.seat_dispatch("Implementer", None)
        refusal = self.assert_refused("on no order", lambda: self.entry(dispatch_id))
        self.assertIn("Implementer, SingleDriver or Restoration", refusal)

    def test_a_frozen_or_accepted_order_is_refused(self) -> None:
        """Refusal 2, rulings 57 and 132: only a commenced order takes its maintenance."""
        dispatch_id = self.seat_dispatch("Implementer", _OTHER)
        for state in ("frozen", "accepted"):
            with self.subTest(state=state):
                self.seat(
                    {
                        "event": "order_transitioned",
                        "id": _OTHER,
                        "ts": "2026-11-20T00:00:00+00:00",
                        "order": _OTHER,
                        "work_package": _REPAIR,
                        "to_state": state,
                        "evidence": "e",
                    }
                )
                self.assert_refused(f"Order {_OTHER} is {state}", lambda: self.entry(dispatch_id))

    def test_an_order_not_commenced_is_refused(self) -> None:
        """Refusal 2, rulings 57 and 132: maintenance is done on a commenced order."""
        self.move(_OTHER, "opened", operator_text="open it")
        dispatch_id = self.seat_dispatch("Implementer", _OTHER)
        self.assert_refused(f"Order {_OTHER} is opened", lambda: self.entry(dispatch_id))

    def test_a_blocked_order_is_refused(self) -> None:
        """Rulings 59 and 137: a blocked order's acts are held."""
        record_work_package_block(
            self.catalog,
            self.ledger,
            BlockRequest(
                work_package=_REPAIR,
                reason="the operator holds it",
                next_action="rule on the order",
                order=_ORDER,
            ),
            refutations={},
        )
        self.assert_refused("is blocked", self.entry)

    def test_an_order_stopped_by_an_exit_still_takes_entries(self) -> None:
        """Ruling 177: a stop ends new work, not the record of the work done."""
        record_work_package_block(
            self.catalog,
            self.ledger,
            BlockRequest(
                work_package=_REPAIR,
                reason="the operator holds it",
                next_action="rule on the order",
                order=_ORDER,
            ),
            refutations={},
        )
        record_work_package_unblock(
            self.catalog,
            self.ledger,
            UnblockRequest(
                work_package=_REPAIR,
                ruling="terminate it",
                operator="g0",
                exit_taken="terminate",
                order=_ORDER,
            ),
        )
        self.assertTrue(order_took_stopping_exit(self.ledger, _ORDER))
        self.assertEqual(self.booked().order, _ORDER)
        restorer = self.book("Restoration")
        self.assertEqual(self.booked(restorer, slug="restored").dispatch_id, restorer)


class MaintenanceRecordTests(_EntryCase):
    def test_the_record_reads_every_entry_oldest_first(self) -> None:
        """Ruling 8: the record is a view over the entry events, never edited."""
        first = self.booked()
        second = self.booked(slug="stamp-docs")
        self.assertEqual(
            [entry.entry_id for entry in maintenance_record(self.ledger)],
            [first.entry_id, second.entry_id],
        )

    def test_a_malformed_row_is_refused_with_its_recovery(self) -> None:
        """A row the event's shape does not admit is refused, never read past."""
        self.booked()
        rows = _rows(self.path)
        rows[-1].pop("witness")
        self.path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        raised = _raised(lambda: maintenance_record(self.ledger))
        self.assertIsInstance(raised, EntryError)
        self.assertIn("gz ledger correct", str(raised))


class RecordViewTests(_EntryCase):
    """Ruling 8: each entry is read with its order's Gate 5, the approver's signature."""

    def close(self, order: str) -> OrderTransitionedEvent:
        """Seat the order's Gate 5 row, the close a terminate or a proceed books.

        Returns:
            The closing event seated.

        """
        closed = OrderTransitionedEvent.model_validate(
            {
                "event": "order_transitioned",
                "id": order,
                "order": order,
                "work_package": _REPAIR,
                "from_state": "accepted",
                "to_state": "closed",
                "evidence": "inspected",
                "decision": "proceed",
                "attestor": "g0",
                "attestation_text": "proceed",
                "residual_risk": "none",
            }
        )
        self.ledger.append(ledger_row(closed))
        return closed

    def test_an_entry_on_an_order_not_closed_reads_no_gate_5(self) -> None:
        entry = self.booked()
        views = record_view(self.ledger)
        self.assertEqual([(v.entry.entry_id, v.gate5) for v in views], [(entry.entry_id, None)])

    def test_an_entry_reads_its_own_orders_gate_5_and_no_other(self) -> None:
        entry = self.booked()
        self.close(_OTHER)
        unsigned = [view.gate5 for view in record_view(self.ledger)]
        self.close(_ORDER)
        signed = [
            (v.entry.entry_id, v.gate5.order, v.gate5.attestor, v.gate5.decision)
            for v in record_view(self.ledger)
            if v.gate5 is not None
        ]
        self.assertEqual(unsigned, [None])
        self.assertEqual(signed, [(entry.entry_id, _ORDER, "g0", "proceed")])

    def test_a_malformed_closing_row_is_refused_with_its_void(self) -> None:
        """A closing row the event's shape does not admit is refused, never a crash."""
        self.booked()
        self.seat(
            {
                "event": "order_transitioned",
                "id": _ORDER,
                "ts": "2026-11-20T00:00:00+00:00",
                "order": _ORDER,
                "to_state": "closed",
            }
        )
        raised = _raised(lambda: record_view(self.ledger))
        self.assertIsInstance(raised, EntryError)
        self.assertIn("gz ledger correct", str(raised))


def _entry(entry_id: str = "ENT-01-stamp-import") -> EntryBookedEvent:
    """An entry as the writer books it, for the reads that take the record as given."""
    return EntryBookedEvent.model_validate(
        {
            "event": "entry_booked",
            "id": entry_id,
            "ts": "2026-11-21T09:00:00+00:00",
            "entry_id": entry_id,
            "order": _ORDER,
            "work_package": _REPAIR,
            "dispatch_id": "D-0000000000000000",
            "description": "The stamp generator imports its template again.",
            "before": "tests.test_stamp fails: ImportError on the template",
            "after": "tests.test_stamp passes, 12 tests",
            "witness": "uv run -m unittest tests.test_stamp",
            "mx_session_id": _SESSION,
        }
    )


def _commit(sha: str, subject: str) -> LandingCommit:
    return LandingCommit(commit_sha=sha * 40, subject=subject)


class EntryCitationTests(unittest.TestCase):
    """A landing commit names its entry in its subject (RP-12 ruling 170)."""

    def test_a_subject_cites_each_whole_entry_id_it_names_once(self) -> None:
        cases = {
            "fix(stamp): imports again (ENT-01-stamp-import)": ["ENT-01-stamp-import"],
            "fix(x): two acts (ENT-01-a, ENT-12-b-c)": ["ENT-01-a", "ENT-12-b-c"],
            "fix(x): (ENT-01-a) and again ENT-01-a": ["ENT-01-a"],
            "fix(x): one digit ENT-1-a": [],
            "fix(x): glued XENT-01-a": [],
            "fix(x): a dangling hyphen ENT-01-a-": [],
            "fix(x): no entry (GHI #1301)": [],
        }
        for subject, cited in cases.items():
            with self.subTest(subject=subject):
                self.assertEqual(entries_cited(subject), cited)

    def test_each_entry_is_joined_to_the_commits_naming_it_and_no_other(self) -> None:
        first, other, stray = (
            _commit("a", "fix(stamp): imports again (ENT-01-stamp-import)"),
            _commit("b", "fix(stamp): the second act (ENT-02-second)"),
            _commit("c", "fix(x): an entry no one booked (ENT-09-ghost)"),
        )
        joined = landings(["ENT-01-stamp-import", "ENT-03-unlanded"], [first, other, stray])
        self.assertEqual(joined, {"ENT-01-stamp-import": [first], "ENT-03-unlanded": []})


class EntryBlockRendering(unittest.TestCase):
    """One block per entry, read by `gz wp entry show` and the MX log (RP-12 rulings 191, 192)."""

    def test_a_landed_entry_names_each_commit_that_landed_it(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, the Landed line
        landed = [
            _commit("a", "fix(stamp): imports again (ENT-01-stamp-import)"),
            _commit("b", "test(stamp): the import is witnessed (ENT-01-stamp-import)"),
        ]
        lines = entry_block(RecordedEntry(entry=_entry()), landed).splitlines()
        at = lines.index(
            "  Landed:      aaaaaaaaaaaa fix(stamp): imports again (ENT-01-stamp-import)"
        )
        continued = "bbbbbbbbbbbb test(stamp): the import is witnessed (ENT-01-stamp-import)"
        self.assertEqual(lines[at + 1], f"{'':15}{continued}")
        self.assertEqual(lines[at + 2], "  Gate 5:      not signed")

    def test_a_signed_entry_names_its_orders_gate_5(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, the Gate 5 line (ruling 8)
        closed = OrderTransitionedEvent.model_validate(
            {
                "event": "order_transitioned",
                "id": _ORDER,
                "ts": "2026-11-21T10:00:00+00:00",
                "order": _ORDER,
                "work_package": _REPAIR,
                "from_state": "accepted",
                "to_state": "closed",
                "evidence": "inspected",
                "decision": "pause",
                "attestor": "g0",
                "attestation_text": "pause",
                "residual_risk": "none",
            }
        )
        lines = entry_block(RecordedEntry(entry=_entry(), gate5=closed), []).splitlines()
        self.assertEqual(lines[-1], "  Gate 5:      g0, pause, 2026-11-21T10:00:00+00:00")

    def test_an_entry_no_commit_names_reads_not_landed(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, ruling 167's reading
        lines = entry_block(RecordedEntry(entry=_entry()), []).splitlines()
        self.assertEqual(lines[0], "ENT-01-stamp-import on ORD-01-import (WP-01-stamp)")
        self.assertIn("  Landed:      not landed", lines)


if __name__ == "__main__":
    unittest.main()
