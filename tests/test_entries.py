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

from gzkit.events import BaselinedReq, EntryBookedEvent, WorkPackageDispatchedEvent
from gzkit.ledger import Ledger, ledger_row
from gzkit.models.catalog import Catalog, Criterion, Order, RepairReq, WorkPackage
from gzkit.mx.entries import EntryBook, EntryError, maintenance_record, record_entry_book
from gzkit.order_ledger import OrderMove, record_order_transition
from gzkit.work_package_ledger import TransitionRequest, record_work_package_transition
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    record_dispatch_end,
    record_dispatch_void,
    record_work_package_block,
    record_work_package_dispatch,
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

    def seat_dispatch(self, role: str, order: str = _ORDER) -> str:
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
                "subject": order,
                "dispatch_id": dispatch_id,
                "intended_root": Path(self._dir.name).resolve().as_posix(),
                "order": order,
            }
        )
        self.ledger.append(ledger_row(seated))
        return dispatch_id

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
        self.assert_refused("not stamped", lambda: self.entry(stamped=None))
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


if __name__ == "__main__":
    unittest.main()
