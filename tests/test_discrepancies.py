"""The list of discrepancies' writer and reducer: RP-12 O4 task 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the list of discrepancies
is ledger events, rendered as a view (ruling 9). A line is graded *blocks return to
service* or *due by a named event*, the event named in text (ruling 179), and is
always on an order (ruling 178). The coordinator's unstamped call records any source
but an inspector's rejection, and a live `Implementer`, `SingleDriver` or
`Restoration` dispatch's stamped call records a find in the work on its own order
(rulings 172 and 175). The coordinator alone clears a line, on evidence the ledger
resolves, an entry, a cleared tag, or an open GitHub issue confirmed through `gh`
(rulings 172 and 180), with root cause and corrective action on a blocking or
recurring line (ruling 181). Each id is `DSC-<NN>-<slug>` (rulings 169 and 176). A
refusal writes nothing.
"""

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from gzkit.events import (
    BaselinedReq,
    DiscrepancyClearedEvent,
    DiscrepancyRecordedEvent,
    EntryBookedEvent,
    TagClearedEvent,
    TagHungEvent,
    TagIssuedEvent,
    WorkPackageDispatchedEvent,
)
from gzkit.ledger import Ledger, ledger_row
from gzkit.models.catalog import Catalog, Criterion, Order, RepairReq, WorkPackage
from gzkit.mx.discrepancies import (
    DiscrepancyClear,
    DiscrepancyError,
    DiscrepancyRecord,
    DiscrepancyUnavailableError,
    discrepancy_list,
    open_discrepancies,
    record_discrepancy,
    record_discrepancy_clear,
)
from gzkit.order_ledger import OrderMove, record_order_transition
from gzkit.work_package_ledger import TransitionRequest, record_work_package_transition
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    record_dispatch_void,
    record_work_package_block,
    record_work_package_dispatch,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_SESSION = "mx-20261120-probe"
_REPAIR = "WP-01-stamp"
_IDLE = "WP-02-idle"
_ORDER = "ORD-01-import"
_OTHER = "ORD-02-other"
_IDLE_ORDER = "ORD-03-idle"
_DELIVERY = "WP-03-deliver"
_DELIVERY_ORDER = "ORD-04-deliver"
_NOW = datetime(2026, 11, 20, tzinfo=UTC)


def _package(wp_id: str) -> WorkPackage:
    return WorkPackage(
        id=wp_id,
        kind="repair",
        outcome=None,
        issues=(1301,) if wp_id == _REPAIR else (1302,),
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


def _order(order_id: str, package: str = _REPAIR) -> Order:
    return Order(id=order_id, work_package=package, aliases=(), purpose="Fix.", procedure="NA")


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
        work_packages=(_package(_REPAIR), _package(_IDLE)),
        orders=(_order(_ORDER), _order(_OTHER), _order(_IDLE_ORDER, _IDLE)),
    )


class _Witnesses:
    """A fake of the clear's two readers: an issue's state and a citation's time."""

    def __init__(
        self,
        issues: dict[int, str | None] | None = None,
        times: dict[str, datetime] | None = None,
    ) -> None:
        self.issues = issues or {}
        self.times = times or {}
        self.asked: list[int] = []
        self.min_occurrences = 3
        self.separation_hours = 24.0

    def issue_state(self, number: int) -> str | None:
        self.asked.append(number)
        return self.issues.get(number)

    def resolve_cite(self, cite: str) -> tuple[str, datetime] | None:
        """Label a GHI ``#<n>`` however it is spelled, as `gz insights recurrence` does."""
        number = cite.removeprefix("#")
        label = f"#{number}" if number.isdigit() else cite
        stamp = self.times.get(label)
        return (label, stamp) if stamp is not None else None


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


class _DiscrepancyCase(unittest.TestCase):
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
        self.move(_ORDER, "opened", operator_text="open it")
        self.move(
            _ORDER,
            "frozen",
            baseline=(BaselinedReq(req="REQ-1", revision=1),),
            risk_note="The import touches the hook.",
            review_receipt="review-01",
        )
        self.move(_ORDER, "commenced", no_isolation="The fix isolates no surface.")
        self.dispatch = self.book("Implementer")
        self.witnesses = _Witnesses()

    def move(self, order: str, to_state: str, **fields: object) -> None:
        request = OrderMove.model_validate(
            {"order": order, "to_state": to_state, "evidence": "evt-1", **fields}
        )
        record_order_transition(self.catalog, self.ledger, request)

    def book(self, role: str) -> str:
        request = DispatchRequest(
            work_package=_REPAIR,
            role=role,
            model="opus",
            req=None if role == "Restoration" else "REQ-1",
            root=Path(self._dir.name).resolve().as_posix(),
            order=_ORDER,
        )
        return str(record_work_package_dispatch(self.catalog, self.ledger, request).dispatch_id)

    def seat_dispatch(self, role: str) -> str:
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
                "subject": _ORDER,
                "dispatch_id": dispatch_id,
                "intended_root": Path(self._dir.name).resolve().as_posix(),
                "order": _ORDER,
            }
        )
        self.ledger.append(ledger_row(seated))
        return dispatch_id

    def seat(self, row: dict[str, object]) -> None:
        """Append a raw row and re-read the ledger, as a later call would (a void, a move)."""
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"schema": "gzkit.ledger.v1", **row}) + "\n")
        self.ledger = Ledger(self.path)

    def seat_state(self, order: str, state: str, package: str = _REPAIR) -> None:
        self.seat(
            {
                "event": "order_transitioned",
                "id": order,
                "ts": "2026-11-20T00:00:00+00:00",
                "order": order,
                "work_package": package,
                "to_state": state,
                "evidence": "e",
            }
        )

    def seat_tag(self, tag_id: str, *, order: str = _ORDER, cleared: bool = False) -> None:
        """Seat a tag issued and hung on *order*, and its clear when *cleared*."""
        line = {
            "tag_id": tag_id,
            "order": order,
            "work_package": _REPAIR,
            "tag_class": "Caution",
            "surface": "check:module-size",
            "surface_kind": "check",
            "surface_name": "module-size",
            "position": "advisory",
            "hazard": "The size gate is lowered.",
            "removal_procedure": "Raise it.",
            "source": "order-work",
            "check_level": "C",
        }
        issue = {"event": "tag_issued", "id": tag_id, **line, "mx_session_id": _SESSION}
        self.ledger.append(ledger_row(TagIssuedEvent.model_validate(issue)))
        hung = {
            "event": "tag_hung",
            "id": tag_id,
            **line,
            "dispatch_id": "D-00000000000000aa",
            "issued_by_session": _SESSION,
            "mx_session_id": _SESSION,
        }
        self.ledger.append(ledger_row(TagHungEvent.model_validate(hung)))
        if cleared:
            clear = {
                "event": "tag_cleared",
                "id": tag_id,
                "tag_id": tag_id,
                "order": order,
                "work_package": _REPAIR,
                "dispatch_id": "D-00000000000000bb",
                "hanging_dispatch_id": "D-00000000000000aa",
                "position_found": "advisory",
                "authorized_by_session": _SESSION,
                "mx_session_id": _SESSION,
            }
            self.ledger.append(ledger_row(TagClearedEvent.model_validate(clear)))

    def seat_entry(self, entry_id: str, package: str = _REPAIR) -> None:
        entry = {
            "event": "entry_booked",
            "id": entry_id,
            "entry_id": entry_id,
            "order": _ORDER if package == _REPAIR else _IDLE_ORDER,
            "work_package": package,
            "dispatch_id": self.dispatch,
            "description": "Fixed.",
            "before": "red",
            "after": "green",
            "witness": "uv run -m unittest tests.test_stamp",
            "mx_session_id": _SESSION,
        }
        self.ledger.append(ledger_row(EntryBookedEvent.model_validate(entry)))

    def record(
        self, *, stamped: str | None = None, session: str | None = _SESSION, **fields: object
    ) -> DiscrepancyRecordedEvent:
        request = DiscrepancyRecord.model_validate(
            {
                "slug": "hook-left-off",
                "grade": "blocks-return-to-service",
                "source": "left-broken",
                "description": "The stamp hook is left off.",
                "order": None if stamped else _ORDER,
                **fields,
            }
        )
        return record_discrepancy(
            self.catalog, self.ledger, request, stamped_id=stamped, mx_session_id=session
        )

    def recorded(self, *, stamped: str | None = None, **fields: object) -> DiscrepancyRecordedEvent:
        """Record a line, asserting it is not refused.

        Returns:
            The line recorded.

        """
        held: list[DiscrepancyRecordedEvent] = []
        self.assertIsNone(
            _raised(lambda: held.append(self.record(stamped=stamped, session=_SESSION, **fields)))
        )
        return held[0]

    def clear(
        self,
        discrepancy: str,
        *,
        stamped: str | None = None,
        session: str | None = _SESSION,
        **fields: object,
    ) -> DiscrepancyClearedEvent:
        request = DiscrepancyClear.model_validate({"discrepancy": discrepancy, **fields})
        return record_discrepancy_clear(
            self.ledger,
            request,
            stamped_id=stamped,
            mx_session_id=session,
            witnesses=self.witnesses,
        )

    def cleared(
        self, discrepancy: str, *, stamped: str | None = None, **fields: object
    ) -> DiscrepancyClearedEvent:
        """Clear a line, asserting it is not refused.

        Returns:
            The clear booked.

        """
        held: list[DiscrepancyClearedEvent] = []
        self.assertIsNone(
            _raised(
                lambda: held.append(
                    self.clear(discrepancy, stamped=stamped, session=_SESSION, **fields)
                )
            )
        )
        return held[0]

    def assert_refused(self, failed: str, act: Callable[[], object]) -> str:
        """Assert the act is refused by the check named, and nothing is written.

        Returns:
            The refusal's text.

        """
        # output-contract: the refusal's what-failed part names the check that refused
        before = _rows(self.path)
        raised = _raised(act)
        self.assertIsInstance(raised, DiscrepancyError)
        self.assertIn(failed, str(raised))
        self.assertEqual(_rows(self.path), before)
        return str(raised)


class RecordTests(_DiscrepancyCase):
    def test_the_coordinator_records_a_blocking_line_on_its_order(self) -> None:
        """Rulings 9, 114, 169 and 178: one event, the order typed, no dispatch."""
        before = len(_rows(self.path))
        line = self.recorded()
        rows = _rows(self.path)
        self.assertEqual(len(rows), before + 1)
        self.assertEqual(rows[-1]["event"], "discrepancy_recorded")
        self.assertEqual(line.discrepancy_id, "DSC-01-hook-left-off")
        self.assertEqual(line.id, line.discrepancy_id)
        self.assertEqual((line.order, line.work_package), (_ORDER, _REPAIR))
        self.assertEqual(line.grade, "blocks-return-to-service")
        self.assertIsNone(line.due_by)
        self.assertIsNone(line.dispatch_id)
        self.assertEqual(line.mx_session_id, _SESSION)

    def test_a_due_by_line_names_its_event_in_text(self) -> None:
        """Ruling 179: the event a due-by line is due by is text."""
        line = self.recorded(grade="due-by-event", due_by="O9's carry")
        self.assertEqual((line.grade, line.due_by), ("due-by-event", "O9's carry"))

    def test_lines_number_in_one_series_and_a_voided_number_never_returns(self) -> None:
        """Rulings 169 and 176: DSC-01, DSC-02, then past a voided number."""
        first = self.recorded()
        second = self.recorded(slug="second")
        self.assertEqual(second.discrepancy_id, "DSC-02-second")
        self.seat(
            {
                "event": "ledger_event_corrected",
                "id": second.id,
                "ts": "2099-01-01T00:00:00+00:00",
                "subject_event": "discrepancy_recorded",
                "subject_id": second.id,
                "subject_ts": _rows(self.path)[-1]["ts"],
                "disposition": "void",
                "cause": "agent-error",
                "attestor": "g0",
                "reason": "recorded in error",
            }
        )
        self.assertEqual([d.record.id for d in discrepancy_list(self.ledger)], [first.id])
        self.assertEqual(self.recorded(slug="third").discrepancy_id, "DSC-03-third")

    def test_a_performer_records_a_find_in_the_work_on_its_own_order(self) -> None:
        """Rulings 172, 175 and 178: the order read from the dispatch, never typed."""
        performers = {
            "Implementer": self.dispatch,
            "SingleDriver": self.seat_dispatch("SingleDriver"),
            "Restoration": self.book("Restoration"),
        }
        for role, dispatch_id in performers.items():
            with self.subTest(role=role):
                line = self.recorded(
                    stamped=dispatch_id,
                    dispatch=dispatch_id,
                    source="found-in-work",
                    slug=f"found-{role.lower()}",
                )
                self.assertEqual((line.order, line.dispatch_id), (_ORDER, dispatch_id))

    def test_the_coordinator_records_on_any_order_state_but_closed(self) -> None:
        """Ruling 178: opened, frozen, commenced and accepted orders take lines."""
        for state in ("opened", "frozen", "accepted"):
            with self.subTest(state=state):
                self.seat_state(_OTHER, state)
                self.assertEqual(self.recorded(order=_OTHER, slug=state).order, _OTHER)

    def test_a_blocked_order_still_takes_a_line(self) -> None:
        """Ruling 178: a discrepancy is often what holds an order."""
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
        self.assertEqual(self.recorded().order, _ORDER)
        self.assertEqual(
            self.recorded(
                stamped=self.dispatch, dispatch=self.dispatch, source="found-in-work", slug="b"
            ).order,
            _ORDER,
        )

    def test_the_coordinator_cites_a_tag_issued_on_the_order(self) -> None:
        """Ruling 171: a carry's line cites the tag and its order."""
        self.seat_tag("TAG-01-size")
        line = self.recorded(grade="due-by-event", due_by="O9's carry", tag="TAG-01-size")
        self.assertEqual(line.tag_id, "TAG-01-size")


class RecordRefusalTests(_DiscrepancyCase):
    def test_no_open_mx_session_is_refused(self) -> None:
        """Ruling 9: a line records the MX session it was found under."""
        self.assert_refused("No MX session is open", lambda: self.record(session=None))

    def test_a_slug_outside_the_grammar_or_a_blank_description_is_refused(self) -> None:
        """Ruling 169 and ruling 9's what is wrong."""
        self.assert_refused("--slug 'Bad Slug'", lambda: self.record(slug="Bad Slug"))
        self.assert_refused("--description is blank", lambda: self.record(description="  "))

    def test_a_grade_and_its_due_by_disagreeing_are_refused(self) -> None:
        """Ruling 179: required on a due-by line, refused on a blocking one, never blank."""
        self.assert_refused(
            "--due-by is required", lambda: self.record(grade="due-by-event", due_by=None)
        )
        self.assert_refused(
            "--due-by is required", lambda: self.record(grade="due-by-event", due_by=" ")
        )
        self.assert_refused("blocks return to service", lambda: self.record(due_by="O9's carry"))

    def test_an_inspectors_rejection_waits_on_o6(self) -> None:
        """Ruling 172: an inspector's rejection waits on O6's QAI dispatch."""
        self.assert_refused(
            "inspector's rejection", lambda: self.record(source="inspector-rejection")
        )

    def test_the_coordinators_line_names_its_order(self) -> None:
        """Ruling 178: every line is on an order."""
        self.assert_refused("--order is required", lambda: self.record(order=None))

    def test_a_call_not_stamped_as_the_named_dispatch_is_refused(self) -> None:
        """Rulings 133's form and 172: a performer's line is its own stamped call."""
        self.assert_refused(
            "not stamped with a dispatch id",
            lambda: self.record(dispatch=self.dispatch, source="found-in-work"),
        )
        other = self.seat_dispatch("SingleDriver")
        self.assert_refused(
            f"stamped with {other}",
            lambda: self.record(stamped=other, dispatch=self.dispatch, source="found-in-work"),
        )

    def test_a_performers_line_is_a_find_in_the_work_alone(self) -> None:
        """Ruling 172: a stamped call records only a find in the work."""
        self.assert_refused(
            "records a find in the work",
            lambda: self.record(stamped=self.dispatch, dispatch=self.dispatch),
        )

    def test_a_performer_types_no_order_and_cites_no_tag(self) -> None:
        """Rulings 1, 130, 171 and 178: the order is read from the dispatch; a carry is the
        coordinator's."""
        found = {"stamped": self.dispatch, "dispatch": self.dispatch, "source": "found-in-work"}
        self.assert_refused("--order is read from", lambda: self.record(order=_ORDER, **found))
        self.seat_tag("TAG-01-size")
        self.assert_refused(
            "--tag is the coordinator's", lambda: self.record(tag="TAG-01-size", **found)
        )

    def test_a_dispatch_not_live_or_not_a_performer_is_refused(self) -> None:
        """Rulings 1, 118 and 175: only a live performer records a find."""
        for role in ("Repair", "SpecReviewer"):
            with self.subTest(role=role):
                seated = self.seat_dispatch(role)
                self.assert_refused(
                    f"a {role} dispatch",
                    lambda seated=seated: self.record(
                        stamped=seated, dispatch=seated, source="found-in-work"
                    ),
                )
        record_dispatch_void(self.ledger, _REPAIR, self.dispatch, "killed by TaskStop")
        self.assert_refused(
            "voided",
            lambda: self.record(
                stamped=self.dispatch, dispatch=self.dispatch, source="found-in-work"
            ),
        )

    def test_an_order_the_store_does_not_hold_is_refused(self) -> None:
        """Ruling 178: the line's order is one the catalog holds."""
        self.assert_refused("ORD-09-none", lambda: self.record(order="ORD-09-none"))

    def test_an_order_not_opened_or_closed_is_refused(self) -> None:
        """Ruling 178: any state but closed, and an order never opened has none."""
        self.assert_refused(f"Order {_OTHER} is not opened", lambda: self.record(order=_OTHER))
        self.seat_state(_OTHER, "closed")
        self.assert_refused(f"Order {_OTHER} is closed", lambda: self.record(order=_OTHER))

    def test_an_order_of_a_package_not_initiated_is_refused(self) -> None:
        """Rulings 2, 44 and 178: an order of a repair package initiated and not closed."""
        self.seat_state(_IDLE_ORDER, "opened", _IDLE)
        self.assert_refused(
            f"Work package {_IDLE} is not initiated", lambda: self.record(order=_IDLE_ORDER)
        )

    def test_an_order_of_a_delivery_package_is_refused(self) -> None:
        """Rulings 2, 44 and 178: a line is recorded on an order of a repair package; a
        delivery package's order, its package initiated and the order opened, takes none."""
        delivery = _package(_DELIVERY).model_copy(
            update={"kind": "delivery", "outcome": "A1", "issues": (), "lane": None}
        )
        self.catalog = self.catalog.model_copy(
            update={
                "work_packages": (*self.catalog.work_packages, delivery),
                "orders": (*self.catalog.orders, _order(_DELIVERY_ORDER, _DELIVERY)),
            }
        )
        record_work_package_transition(
            self.catalog,
            self.ledger,
            TransitionRequest(
                work_package=_DELIVERY, to_state="initiated", evidence="e", operator_text="go"
            ),
        )
        self.seat_state(_DELIVERY_ORDER, "opened", _DELIVERY)
        self.assert_refused(
            f"sits in {_DELIVERY}, a delivery package",
            lambda: self.record(order=_DELIVERY_ORDER),
        )

    def test_a_tag_not_issued_on_the_order_is_refused(self) -> None:
        """Ruling 171: the line cites a tag on its own order."""
        self.assert_refused("TAG-07-none", lambda: self.record(tag="TAG-07-none"))
        self.seat_state(_OTHER, "frozen")
        self.seat_tag("TAG-01-size", order=_OTHER)
        self.assert_refused(f"issued on {_OTHER}", lambda: self.record(tag="TAG-01-size"))


class ClearTests(_DiscrepancyCase):
    def test_a_line_cleared_on_an_entry_reads_closed(self) -> None:
        """Rulings 9 and 172: the clear cites an entry of the line's package."""
        line = self.recorded(grade="due-by-event", due_by="the fix")
        self.seat_entry("ENT-01-fixed")
        self.assertEqual([d.record.id for d in open_discrepancies(self.ledger)], [line.id])
        clear = self.cleared(line.id, entry="ENT-01-fixed")
        self.assertEqual(
            (clear.entry_id, clear.order, clear.mx_session_id), ("ENT-01-fixed", _ORDER, _SESSION)
        )
        self.assertEqual(open_discrepancies(self.ledger), [])
        (listed,) = discrepancy_list(self.ledger)
        self.assertFalse(listed.is_open)
        self.assertIsNotNone(listed.clear)
        self.assertEqual(listed.clear.entry_id if listed.clear else None, "ENT-01-fixed")

    def test_a_line_cleared_on_a_cleared_tag(self) -> None:
        """Ruling 172: a cleared tag is evidence."""
        line = self.recorded(grade="due-by-event", due_by="the restoration")
        self.seat_tag("TAG-01-size", cleared=True)
        self.assertEqual(self.cleared(line.id, tag="TAG-01-size").tag_id, "TAG-01-size")

    def test_a_line_filed_as_an_open_issue_is_cleared_citing_it(self) -> None:
        """Ruling 180: the issue confirmed open through gh, the clear citing it."""
        line = self.recorded(grade="due-by-event", due_by="the next package")
        self.witnesses.issues[1400] = "open"
        self.assertEqual(self.cleared(line.id, ghi=1400).ghi, 1400)
        self.assertEqual(self.witnesses.asked, [1400])

    def test_a_blocking_line_carries_root_cause_and_corrective_action(self) -> None:
        """Rulings 9 and 181: required on a blocking line's clear."""
        line = self.recorded()
        self.seat_entry("ENT-01-fixed")
        self.assert_refused(
            "--root-cause and --corrective-action",
            lambda: self.clear(line.id, entry="ENT-01-fixed"),
        )
        self.assert_refused(
            "--corrective-action",
            lambda: self.clear(
                line.id, entry="ENT-01-fixed", root_cause="a typo", corrective_action=" "
            ),
        )
        clear = self.cleared(
            line.id, entry="ENT-01-fixed", root_cause="a typo", corrective_action="a test"
        )
        self.assertEqual((clear.root_cause, clear.corrective_action), ("a typo", "a test"))

    def test_a_recurring_due_by_line_carries_both_fields(self) -> None:
        """Ruling 181: --recurs read by the threshold, both fields then required."""
        line = self.recorded(grade="due-by-event", due_by="the fix")
        self.seat_entry("ENT-01-fixed")
        cites = ["#1", "#2", "#3"]
        self.witnesses.times = {c: _NOW + timedelta(days=i) for i, c in enumerate(cites)}
        self.assert_refused(
            "recurs", lambda: self.clear(line.id, entry="ENT-01-fixed", recurs=cites)
        )
        clear = self.cleared(
            line.id,
            entry="ENT-01-fixed",
            recurs=cites,
            root_cause="a typo",
            corrective_action="a test",
        )
        self.assertEqual(clear.recurs, cites)

    def test_one_record_cited_twice_is_read_once(self) -> None:
        """Ruling 181: the clear reads `gz insights recurrence`'s check, which keys a GHI by
        its label, so `1412` and `#1412` are one record, counted and stored once."""
        line = self.recorded(grade="due-by-event", due_by="the fix")
        self.seat_entry("ENT-01-fixed")
        self.witnesses.times = {c: _NOW + timedelta(days=i) for i, c in enumerate(["#1", "#2"])}
        self.assert_refused(
            "2 cited of 3 required",
            lambda: self.clear(line.id, entry="ENT-01-fixed", recurs=["1", "#1", "#2"]),
        )
        self.witnesses.times["#3"] = _NOW + timedelta(days=2)
        clear = self.cleared(
            line.id,
            entry="ENT-01-fixed",
            recurs=["1", "#1", "#2", "3"],
            root_cause="a typo",
            corrective_action="a test",
        )
        self.assertEqual(clear.recurs, ["#1", "#2", "#3"])

    def test_a_due_by_line_takes_the_fields_optionally_without_recurrence(self) -> None:
        """Ruling 181: otherwise the two fields are optional."""
        line = self.recorded(grade="due-by-event", due_by="the fix")
        self.seat_entry("ENT-01-fixed")
        self.assertIsNone(self.cleared(line.id, entry="ENT-01-fixed").root_cause)


class ClearRefusalTests(_DiscrepancyCase):
    def setUp(self) -> None:
        super().setUp()
        self.line = self.recorded(grade="due-by-event", due_by="the fix")
        self.seat_entry("ENT-01-fixed")

    def test_a_stamped_call_is_refused(self) -> None:
        """Ruling 172: the coordinator's unstamped call alone clears a line."""
        self.assert_refused(
            "stamped", lambda: self.clear(self.line.id, stamped=self.dispatch, entry="ENT-01-fixed")
        )

    def test_no_open_mx_session_is_refused(self) -> None:
        """Ruling 114: the coordinator's mark is the open MX session."""
        self.assert_refused(
            "No MX session is open",
            lambda: self.clear(self.line.id, session=None, entry="ENT-01-fixed"),
        )

    def test_a_line_unknown_or_already_cleared_is_refused(self) -> None:
        """Ruling 9: a later event clears the line, once."""
        self.assert_refused("DSC-09-none", lambda: self.clear("DSC-09-none", entry="ENT-01-fixed"))
        self.cleared(self.line.id, entry="ENT-01-fixed")
        self.assert_refused(
            "already cleared", lambda: self.clear(self.line.id, entry="ENT-01-fixed")
        )

    def test_a_clear_with_no_evidence_is_refused(self) -> None:
        """Rulings 9 and 172: a line is cleared with its evidence."""
        self.assert_refused("no evidence", lambda: self.clear(self.line.id))

    def test_an_entry_not_in_the_record_or_of_another_package_is_refused(self) -> None:
        """Ruling 172: the evidence resolves in the ledger, within the line's package."""
        self.assert_refused("ENT-07-none", lambda: self.clear(self.line.id, entry="ENT-07-none"))
        self.seat_entry("ENT-02-elsewhere", _IDLE)
        self.assert_refused(
            f"entry of {_IDLE}", lambda: self.clear(self.line.id, entry="ENT-02-elsewhere")
        )

    def test_a_tag_not_cleared_is_refused(self) -> None:
        """Ruling 172: the evidence is a cleared tag."""
        self.assert_refused("TAG-07-none", lambda: self.clear(self.line.id, tag="TAG-07-none"))
        self.seat_tag("TAG-01-size")
        self.assert_refused("not cleared", lambda: self.clear(self.line.id, tag="TAG-01-size"))

    def test_a_closed_issue_is_refused(self) -> None:
        """Ruling 180: the line leaves the list as an open problem report."""
        self.witnesses.issues[1400] = "closed"
        self.assert_refused("#1400 is closed", lambda: self.clear(self.line.id, ghi=1400))

    def test_an_issue_gh_cannot_read_is_unavailable_and_writes_nothing(self) -> None:
        """Ruling 180: a failed gh call exits 2 and writes nothing."""
        before = _rows(self.path)
        raised = _raised(lambda: self.clear(self.line.id, ghi=1400))
        self.assertIsInstance(raised, DiscrepancyUnavailableError)
        self.assertEqual(_rows(self.path), before)

    def test_an_issue_number_below_one_is_refused_before_gh_is_asked(self) -> None:
        """Ruling 180: the clear cites an issue, numbered from 1 as its event requires; a
        number no issue can carry is the caller's error, never a `gh` outage to retry."""
        for number in (0, -5):
            with self.subTest(number=number):
                self.assert_refused(
                    f"--ghi {number} is not an issue number",
                    lambda number=number: self.clear(self.line.id, ghi=number),
                )
        self.assertEqual(self.witnesses.asked, [])

    def test_an_offline_refusal_never_asks_gh(self) -> None:
        """Ruling 180: the ledger's checks run first, so a refused clear calls no network."""
        self.assert_refused(
            "ENT-07-none", lambda: self.clear(self.line.id, entry="ENT-07-none", ghi=1400)
        )
        self.assertEqual(self.witnesses.asked, [])

    def test_recurrence_below_the_threshold_is_refused_naming_its_shortfall(self) -> None:
        """Ruling 181: a citation that does not meet the threshold is refused."""
        self.witnesses.times = {"#1": _NOW, "#2": _NOW + timedelta(days=1)}
        refusal = self.assert_refused(
            "2 cited of 3 required",
            lambda: self.clear(self.line.id, entry="ENT-01-fixed", recurs=["#1", "#2"]),
        )
        self.assertIn("recurrence", refusal)
        self.witnesses.times = {
            c: _NOW + timedelta(hours=i) for i, c in enumerate(["#1", "#2", "#3"])
        }
        self.assert_refused(
            "closer than",
            lambda: self.clear(self.line.id, entry="ENT-01-fixed", recurs=["#1", "#2", "#3"]),
        )

    def test_a_citation_that_names_nothing_is_refused(self) -> None:
        """Ruling 181: each citation resolves to an insight record or a GHI."""
        self.assert_refused(
            "#9 names no", lambda: self.clear(self.line.id, entry="ENT-01-fixed", recurs=["#9"])
        )

    def test_recurs_on_a_blocking_line_is_refused(self) -> None:
        """Ruling 181: --recurs is taken on a due-by line; a blocking line carries both anyway."""
        blocking = self.recorded(slug="blocking")
        self.assert_refused(
            "--recurs is read on a line graded due by",
            lambda: self.clear(
                blocking.id,
                entry="ENT-01-fixed",
                recurs=["#1"],
                root_cause="a",
                corrective_action="b",
            ),
        )

    def test_a_blank_optional_field_is_refused(self) -> None:
        """Ruling 181: a field given is written out."""
        self.assert_refused(
            "--root-cause is blank",
            lambda: self.clear(self.line.id, entry="ENT-01-fixed", root_cause=" "),
        )


class ListTests(_DiscrepancyCase):
    def test_the_list_reads_every_line_oldest_first_with_its_clear(self) -> None:
        """Ruling 9: the list is a view over the events."""
        first = self.recorded(grade="due-by-event", due_by="the fix")
        second = self.recorded(slug="second")
        self.seat_entry("ENT-01-fixed")
        self.cleared(first.id, entry="ENT-01-fixed")
        listed = discrepancy_list(self.ledger)
        self.assertEqual([d.record.id for d in listed], [first.id, second.id])
        self.assertEqual([d.is_open for d in listed], [False, True])
        self.assertEqual([d.record.id for d in open_discrepancies(self.ledger)], [second.id])

    def test_a_malformed_row_is_refused_with_its_void(self) -> None:
        """Ruling 9: the ledger is append-only, so a malformed row is voided."""
        self.seat(
            {"event": "discrepancy_recorded", "id": "DSC-01-bad", "ts": "2026-11-20T00:00:00+00:00"}
        )
        raised = _raised(lambda: discrepancy_list(self.ledger))
        self.assertIsInstance(raised, DiscrepancyError)
        self.assertIn("gz ledger correct", str(raised))
        self.assertIn("RP-12 ruling 9)", str(raised))


if __name__ == "__main__":
    unittest.main()
