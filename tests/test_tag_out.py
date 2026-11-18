"""The tag-out log's issue and hang writers and reducer: RP-12 O3 tasks 2 and 3.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the tag-out log is
ledger events (ruling 4); the coordinator issues a tag (ruling 6) whose
`tag_issued` event carries the whole line item (rulings 5 and 120), held by the
open MX session (rulings 3, 113 and 114), under check level C or D (113), on a
surface written `<kind>:<name>` and resolved against today's registries (112,
123), from one of ruling 124's four sources, on an opened or frozen order of an
initiated repair package (121), one open tag per surface (122). Its id is
`TAG-<NN>-<slug>` (111). The repair dispatch hangs it (ruling 6), a stamped call
of a live `Repair` dispatch on the tag's frozen, unblocked order (rulings 109, 130,
131 and 133), copying the issue's line item (120); a hung tag reads open whatever
its order's state (129). Every refusal is proved here against the writers, which
import no `gzkit.cli` (ruling 125). A refusal writes nothing.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from gzkit.events import (
    BaselinedReq,
    OrderTransitionedEvent,
    TagHungEvent,
    TagIssuedEvent,
    WorkPackageDispatchedEvent,
    parse_typed_event,
)
from gzkit.ledger import Ledger, ledger_row
from gzkit.models.catalog import Catalog, Criterion, Order, RepairReq, WorkPackage
from gzkit.mx.tag_out import (
    TagIssue,
    TagOutError,
    next_tag_id,
    open_tags,
    record_tag_hang,
    record_tag_issue,
    tag_log,
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

_SESSION = "mx-20261117-probe"
_REPAIR = "WP-01-stamp"
_SPARE = "WP-03-spare"
_DELIVERY = "WP-02-build"
_ORDER = "ORD-01-import"
#: A hang's call stamped with the dispatch it names, as the stamp hook would (ruling 133).
_AS_NAMED = "as-named"


class _Registry:
    """A hand-written fake of the `SurfaceRegistry` port: it resolves what it holds.

    It records every call, so a test can see that a refusal raised before the
    registry was asked, and it holds a registry's own spelling beside the name a
    surface is written with (ruling 123).
    """

    def __init__(self, held: dict[tuple[str, str], str]) -> None:
        self.held = held
        self.calls: list[tuple[str, str]] = []

    def resolve(self, kind: str, name: str) -> str | None:
        self.calls.append((kind, name))
        return self.held.get((kind, name))


def _registry() -> _Registry:
    return _Registry(
        {
            ("validator", "hexagon-tests"): "hexagon_tests",
            ("check", "module-size"): "Module size",
            ("hook", "stamp-dispatch"): ".claude/hooks/stamp-dispatch.py",
            ("hook", "stamp-dispatch.py"): ".claude/hooks/stamp-dispatch.py",
            ("path", "src/stamp.py"): "src/stamp.py",
        }
    )


def _package(wp_id: str, kind: str = "repair") -> WorkPackage:
    repair = kind == "repair"
    return WorkPackage(
        id=wp_id,
        kind=kind,  # ty: ignore[invalid-argument-type]
        outcome=None if repair else "H1",
        issues=(1301,) if repair else (),
        lane="lite" if repair else None,
        aliases=(),
        modules=("src/stamp.py",) if repair else (),
        initial_conditions="NA",
        procedure="NA",
        test_and_inspection="NA",
        system_restoration="NA",
        oqe=(),
        alterations=(),
        departures=(),
    )


def _order(order_id: str, package: str) -> Order:
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
        work_packages=(_package(_REPAIR), _package(_DELIVERY, "delivery"), _package(_SPARE)),
        orders=(
            _order(_ORDER, _REPAIR),
            _order("ORD-02-build", _DELIVERY),
            _order("ORD-03-spare", _SPARE),
        ),
    )


def _request(**fields: object) -> TagIssue:
    return TagIssue.model_validate(
        {
            "slug": "stamp-hook",
            "order": _ORDER,
            "tag_class": "Danger",
            "surface": "hook:stamp-dispatch",
            "position": "off",
            "hazard": "The stamp hook books claims while its generator is rewritten.",
            "removal_procedure": "Re-register the hook in .claude/settings.json and run it once.",
            "source": "order-work",
            "check_level": "C",
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


class _TagCase(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = Path(self._dir.name) / "ledger.jsonl"
        self.ledger = Ledger(self.path)
        self.catalog = _catalog()
        self.registry = _registry()
        self.initiate(_REPAIR)
        self.move("opened", operator_text="open the import order")

    def initiate(self, package: str) -> None:
        request = TransitionRequest(
            work_package=package, to_state="initiated", evidence="e", operator_text="go"
        )
        record_work_package_transition(self.catalog, self.ledger, request)

    def move(self, to_state: str, order: str = _ORDER, **fields: object) -> None:
        request = OrderMove.model_validate(
            {"order": order, "to_state": to_state, "evidence": "evt-1", **fields}
        )
        record_order_transition(self.catalog, self.ledger, request)

    def freeze(self) -> None:
        self.move(
            "frozen",
            baseline=(BaselinedReq(req="REQ-1", revision=1),),
            risk_note="The import touches the hook.",
            review_receipt="review-01",
        )

    def issue(self, session: str | None = _SESSION, **fields: object) -> TagIssuedEvent:
        return record_tag_issue(
            self.catalog,
            self.ledger,
            _request(**fields),
            mx_session_id=session,
            registry=self.registry,
        )

    def assert_refused(self, session: str | None = _SESSION, **fields: object) -> str:
        before = _rows(self.path)
        raised = _raised(lambda: self.issue(session, **fields))
        self.assertIsInstance(raised, TagOutError)
        self.assertEqual(_rows(self.path), before)
        return str(raised)


class IssueTests(_TagCase):
    def test_an_issue_books_the_whole_line_item_held_by_the_mx_session(self) -> None:
        """Rulings 5, 113, 114 and 120: the issue carries the item, the session its mark."""
        returned = self.issue()
        rows = _rows(self.path)
        event = parse_typed_event(rows[-1])
        # The ledger row is the record; the writer's return names the same tag.
        self.assertIsInstance(event, TagIssuedEvent)
        assert isinstance(event, TagIssuedEvent)
        self.assertEqual(returned.tag_id, event.tag_id)
        self.assertEqual(
            (event.id, event.tag_id, event.order, event.work_package),
            ("TAG-01-stamp-hook", "TAG-01-stamp-hook", _ORDER, _REPAIR),
        )
        self.assertEqual(
            (event.tag_class, event.position, event.source, event.check_level),
            ("Danger", "off", "order-work", "C"),
        )
        self.assertEqual(
            (event.surface, event.surface_kind, event.surface_name),
            ("hook:stamp-dispatch", "hook", ".claude/hooks/stamp-dispatch.py"),
        )
        self.assertEqual(event.hazard, _request().hazard)
        self.assertEqual(event.removal_procedure, _request().removal_procedure)
        self.assertEqual(event.mx_session_id, _SESSION)
        self.assertEqual(self.registry.calls, [("hook", "stamp-dispatch")])


class IssueRefusalTests(_TagCase):
    def test_an_issue_with_no_mx_session_open_is_refused(self) -> None:
        """Rulings 3 and 113: the open MX session holds the tag; with none, no holder."""
        self.assert_refused(session=None)

    def test_an_issue_under_a_level_that_does_not_disconnect_is_refused(self) -> None:
        """Ruling 113: only levels C and D disconnect, so A, B or none is refused."""
        for level in ("A", "B", "", "c"):
            with self.subTest(level=level):
                self.assert_refused(check_level=level)

    def test_a_slug_that_is_not_lowercase_words_joined_by_hyphens_is_refused(self) -> None:
        """Ruling 111: the slug ends the id TAG-<NN>-<slug>, as an order's ends ORD-<NN>-<slug>."""
        for slug in ("Stamp", "stamp_hook", "", "-stamp", "stamp--hook", "stamp hook"):
            with self.subTest(slug=slug):
                self.assert_refused(slug=slug)

    def test_a_blank_hazard_or_removal_procedure_is_refused(self) -> None:
        """Ruling 5: the item names its hazard and a procedure legible to anyone."""
        for field in ("hazard", "removal_procedure"):
            for blank in ("", "   \n"):
                with self.subTest(field=field, blank=blank):
                    self.assert_refused(**{field: blank})

    def test_a_surface_not_written_as_a_known_kind_and_a_name_is_refused(self) -> None:
        """Ruling 112: a surface is <kind>:<name>, its kind validator, check, hook or path."""
        for surface in ("stamp-dispatch", "guard:stamp", "Hook:stamp-dispatch", ""):
            with self.subTest(surface=surface):
                self.assert_refused(surface=surface)
                # A surface of no known kind is refused before any registry is asked.
                self.assertEqual(self.registry.calls, [])

    def test_a_surface_the_registry_does_not_resolve_is_refused(self) -> None:
        """Rulings 112 and 123: an unresolved name would tag nothing, so it is refused."""
        for surface in ("hook:stamp-dispach", "validator:hexagon_tests", "path:", "check:Lint"):
            with self.subTest(surface=surface):
                self.assert_refused(surface=surface)

    def test_an_order_the_catalog_does_not_hold_is_refused(self) -> None:
        """A tag is issued on an order of the store (RP-12 rulings 47 and 121)."""
        self.assert_refused(order="ORD-09-absent")

    def test_an_order_of_a_delivery_package_is_refused(self) -> None:
        """Rulings 2 and 44: a tag isolates a surface for a repair, on a repair order."""
        self.initiate(_DELIVERY)
        self.move("opened", order="ORD-02-build", operator_text="open the build order")
        self.assert_refused(order="ORD-02-build")

    def test_an_order_whose_repair_package_is_not_initiated_is_refused(self) -> None:
        """Rulings 2 and 44: an order acts only while its repair package is initiated.

        The real writers never open an order in a package not initiated, so the row is
        seated by hand: the gate is the writer's own, fail-closed on a ledger that holds it.
        """
        seated = OrderTransitionedEvent(
            event="order_transitioned",
            id="ORD-03-spare",
            order="ORD-03-spare",
            work_package=_SPARE,
            to_state="opened",
            evidence="seated",
            operator_text="seated",
        )
        self.ledger.append(ledger_row(seated))
        self.assert_refused(order="ORD-03-spare")

    def test_an_order_not_opened_or_frozen_is_refused(self) -> None:
        """Ruling 121: a tag is issued on an opened or frozen order, never after."""
        self.initiate(_SPARE)
        with self.subTest(state="not opened"):
            self.assert_refused(order="ORD-03-spare")
        self.move("opened", order="ORD-03-spare", operator_text="open the spare order")
        self.move(
            "closed",
            order="ORD-03-spare",
            decision="terminate",
            attestor="g0",
            attestation_text="terminate it",
        )
        with self.subTest(state="closed"):
            self.assert_refused(order="ORD-03-spare")
        self.freeze()
        self.move("commenced")
        with self.subTest(state="commenced"):
            self.assert_refused()

    def test_a_surface_already_carrying_an_open_tag_is_refused(self) -> None:
        """Ruling 122: one open tag per surface, compared on the registry's own name."""
        self.issue()
        for surface in ("hook:stamp-dispatch", "hook:stamp-dispatch.py"):
            with self.subTest(surface=surface):
                self.assert_refused(slug="second", surface=surface)


class TagLogTests(_TagCase):
    def test_a_tag_reads_closed_once_its_order_has_closed(self) -> None:
        """Ruling 122: a closed order's unhung tag leaves the open log and frees its surface."""
        self.initiate(_SPARE)
        self.move("opened", order="ORD-03-spare", operator_text="open the spare order")
        first = self.issue(order="ORD-03-spare")
        self.assertEqual([tag.issue.tag_id for tag in open_tags(self.ledger)], [first.tag_id])
        self.move(
            "closed",
            order="ORD-03-spare",
            decision="terminate",
            attestor="g0",
            attestation_text="terminate it",
        )
        self.assertEqual(open_tags(self.ledger), [])
        self.freeze()
        second = self.issue(slug="again")
        log = {tag.issue.tag_id: tag.is_open for tag in tag_log(self.ledger)}
        self.assertEqual(log, {first.tag_id: False, second.tag_id: True})
        self.assertEqual(second.tag_id, "TAG-02-again")

    def test_the_next_id_is_numbered_past_every_tag_the_ledger_books(self) -> None:
        """Ruling 111: one series read from the ledger, by number, never reused past a gap.

        TAG-99 against TAG-100 is the case a lexicographic maximum gets wrong
        (`AGENTS.md`: versioned identifiers are ordered semantically).
        """
        self.issue()
        far = self.issue(slug="far", surface="path:src/stamp.py")
        for number in ("99", "100"):
            tag_id = f"TAG-{number}-far"
            self.ledger.append(ledger_row(far.model_copy(update={"id": tag_id, "tag_id": tag_id})))
        self.assertEqual(next_tag_id(self.ledger, "next"), "TAG-101-next")

    def test_a_malformed_issue_row_is_refused_with_its_void_not_a_crash(self) -> None:
        """Ruling 4: the log is ledger events; a row it cannot read stops it, named."""
        self.issue()
        row = {"schema": "gzkit.ledger.v1", "event": "tag_issued", "id": "TAG-7-bad"}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**row, "ts": "2026-11-17T00:00:00+00:00"}) + "\n")
        raised = _raised(lambda: tag_log(self.ledger))
        self.assertIsInstance(raised, TagOutError)
        self.assertIn("TAG-7-bad", str(raised))
        self.assertIn("uv run gz ledger correct", str(raised))


class RefusalProseOutputContract(_TagCase):
    """Every refusal names what failed, the ruling it breaks and a next step."""

    def test_the_no_session_refusal_cites_its_rulings_and_the_way_to_open_one(self) -> None:
        # output-contract: guardrail-feedback-prose's three parts are the refusal's contract
        text = self.assert_refused(session=None)
        self.assertIn("No MX session is open", text)
        self.assertIn("RP-12 rulings 3, 113 and 114", text)
        self.assertIn("`uv run gz mx enter`", text)

    def test_the_unknown_order_refusal_cites_the_store_and_the_issuable_states(self) -> None:
        # output-contract: the refusal's cited rulings are its contract (guardrail-feedback-prose)
        text = self.assert_refused(order="ORD-09-absent")
        self.assertIn("not in data/catalog/orders.json", text)
        self.assertIn("RP-12 rulings 47 and 121", text)
        self.assertIn("`uv run gz wp order new`", text)

    def test_an_unresolved_hook_refusal_names_the_qualified_forms(self) -> None:
        # output-contract: the refusal's next step is its contract (guardrail-feedback-prose)
        text = self.assert_refused(surface="hook:nothing-registered")
        self.assertIn("RP-12 rulings 112 and 123", text)
        self.assertIn("`hook:settings:<script>` or `hook:pre-commit:<id>` (ruling 127)", text)

    def test_the_one_open_tag_refusal_names_the_log_to_read(self) -> None:
        # output-contract: the refusal's next step is its contract (guardrail-feedback-prose)
        self.issue()
        text = self.assert_refused(slug="second")
        self.assertIn("already carries open tag TAG-01-stamp-hook", text)
        self.assertIn("RP-12 ruling 122", text)
        self.assertIn("`uv run gz wp tag show`", text)


class _HangCase(_TagCase):
    """A tag issued on the opened order, the order frozen, a Repair dispatch booked on it."""

    def setUp(self) -> None:
        super().setUp()
        self.tag = self.issue()
        self.freeze()
        self.dispatch = self.book("Repair")

    def book(self, role: str, order: str = _ORDER, package: str = _REPAIR) -> str:
        request = DispatchRequest(
            work_package=package,
            role=role,
            model="opus",
            root=Path(self._dir.name).resolve().as_posix(),
            order=order,
        )
        return str(record_work_package_dispatch(self.catalog, self.ledger, request).dispatch_id)

    def seat_dispatch(self, role: str, order: str, package: str = _REPAIR) -> str:
        """Seat a dispatch row by hand, the gate under test the hang writer's own.

        The dispatch writer books no Repair dispatch off a frozen order and no other
        role on one, so a row the hang must refuse is seated directly.

        Returns:
            The seated dispatch's id.

        """
        dispatch_id = f"D-{len(_rows(self.path)):016x}"
        seated = WorkPackageDispatchedEvent.model_validate(
            {
                "event": "work_package_dispatched",
                "id": package,
                "work_package": package,
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

    def hang(
        self,
        tag_id: str | None = None,
        dispatch_id: str | None = None,
        *,
        stamped: str | None = _AS_NAMED,
        session: str | None = _SESSION,
    ) -> TagHungEvent:
        dispatch_id = dispatch_id or self.dispatch
        return record_tag_hang(
            self.ledger,
            tag_id or self.tag.tag_id,
            dispatch_id,
            stamped_id=dispatch_id if stamped == _AS_NAMED else stamped,
            mx_session_id=session,
        )

    def assert_hang_refused(self, failed: str, act: Callable[[], object] | None = None) -> str:
        """Assert the hang is refused by the check named, and nothing is written.

        ``failed`` is a fragment of the refusal's what-failed part, so a test cannot pass
        on an earlier check's refusal.

        Returns:
            The refusal's text.

        """
        # output-contract: the refusal's what-failed part names the check that refused
        before = _rows(self.path)
        raised = _raised(act or self.hang)
        self.assertIsInstance(raised, TagOutError)
        self.assertIn(failed, str(raised))
        self.assertEqual(_rows(self.path), before)
        return str(raised)


class HangTests(_HangCase):
    def test_a_hang_copies_the_issue_and_records_its_dispatch_and_holder(self) -> None:
        """Rulings 5, 120 and 133: the hang adds its dispatch, copies the item, names its holder."""
        holder = "mx-20261118-relief"
        returned = self.hang(session=holder)
        event = parse_typed_event(_rows(self.path)[-1])
        self.assertIsInstance(event, TagHungEvent)
        assert isinstance(event, TagHungEvent)
        # The ledger stamps the row's time; every other field is the writer's return.
        written, read = returned.model_dump(), event.model_dump()
        written.pop("ts")
        read.pop("ts")
        self.assertEqual(written, read)
        self.assertEqual(
            (event.id, event.tag_id, event.dispatch_id),
            (self.tag.tag_id, self.tag.tag_id, self.dispatch),
        )
        copied = (
            "order",
            "work_package",
            "tag_class",
            "surface",
            "surface_kind",
            "surface_name",
            "position",
            "hazard",
            "removal_procedure",
            "source",
            "check_level",
        )
        for field in copied:
            with self.subTest(field=field):
                self.assertEqual(getattr(event, field), getattr(self.tag, field))
        # The issue's mark is carried; the open session at the hang is the holder.
        self.assertEqual(event.issued_by_session, _SESSION)
        self.assertEqual(event.mx_session_id, holder)


class HangRefusalTests(_HangCase):
    def test_a_hang_with_no_mx_session_open_is_refused(self) -> None:
        """Rulings 3 and 133: the open MX session holds the hung tag; with none, no holder."""
        for session in (None, "", "  "):
            with self.subTest(session=session):
                self.assert_hang_refused(
                    "No MX session is open", lambda session=session: self.hang(session=session)
                )

    def test_a_hang_not_stamped_with_the_dispatch_it_names_is_refused(self) -> None:
        """Ruling 133: a hang is the stamped call of the Repair dispatch it names."""
        other = self.book("Repair")
        for stamped in (None, other):
            with self.subTest(stamped=stamped):
                self.assert_hang_refused(
                    "a hang is the stamped call", lambda stamped=stamped: self.hang(stamped=stamped)
                )

    def test_the_stamp_refusal_names_a_step_other_than_the_failed_call(self) -> None:
        """Ruling 133: the refusal's next step is one that can succeed, never the same call."""
        failed = f"--dispatch {self.dispatch}`"
        with self.subTest(stamped="none"):
            refusal = self.assert_hang_refused(
                "a hang is the stamped call", lambda: self.hang(stamped=None)
            )
            self.assertNotIn(failed, refusal)
            self.assertIn("--role Repair", refusal)
        other = self.book("Repair")
        with self.subTest(stamped="another dispatch"):
            refusal = self.assert_hang_refused(
                "a hang is the stamped call", lambda: self.hang(stamped=other)
            )
            self.assertNotIn(failed, refusal)
            self.assertIn(f"--dispatch {other}`", refusal)

    def test_a_tag_the_ledger_does_not_hold_is_refused(self) -> None:
        """Rulings 6 and 120: a hang cites an issue; with none there is nothing to copy."""
        self.assert_hang_refused(
            "is not issued in the ledger", lambda: self.hang(tag_id="TAG-09-absent")
        )

    def test_a_tag_already_hung_is_refused(self) -> None:
        """Ruling 6: a tag is hung once, by the repair dispatch citing its issue."""
        self.hang()
        with self.subTest(by="the same dispatch"):
            self.assert_hang_refused("is already hung")
        other = self.book("Repair")
        with self.subTest(by="another Repair dispatch"):
            self.assert_hang_refused("is already hung", lambda: self.hang(dispatch_id=other))

    def test_a_tag_not_open_is_refused(self) -> None:
        """Ruling 122: an unhung tag on a closed order reads closed; it is hung no more.

        An order closes from opened only as a terminate, where no Repair dispatch is
        booked, so the spare order's dispatch is seated by hand.
        """
        self.initiate(_SPARE)
        self.move("opened", order="ORD-03-spare", operator_text="open the spare order")
        spare = self.issue(slug="spare", order="ORD-03-spare", surface="path:src/stamp.py")
        self.move(
            "closed",
            order="ORD-03-spare",
            decision="terminate",
            attestor="g0",
            attestation_text="terminate it",
        )
        seated = self.seat_dispatch("Repair", "ORD-03-spare", package=_SPARE)
        self.assert_hang_refused(
            "is not open", lambda: self.hang(tag_id=spare.tag_id, dispatch_id=seated)
        )

    def test_a_dispatch_the_ledger_does_not_hold_live_is_refused(self) -> None:
        """Rulings 1 and 42: a hang names a booked dispatch, never a voided one."""
        with self.subTest(dispatch="none booked"):
            self.assert_hang_refused(
                "is not a live dispatch", lambda: self.hang(dispatch_id="D-00000000000000ff")
            )
        record_dispatch_void(self.ledger, _REPAIR, self.dispatch, "abandoned")
        with self.subTest(dispatch="voided"):
            self.assert_hang_refused("is not a live dispatch")

    def test_a_dispatch_whose_role_is_not_repair_is_refused(self) -> None:
        """Rulings 6 and 109: a hang requires a Repair dispatch, the craftsman's position."""
        seated = {role: self.seat_dispatch(role, _ORDER) for role in ("Restoration", "Implementer")}
        for role, dispatch_id in seated.items():
            with self.subTest(role=role):
                self.assert_hang_refused(
                    "a tag is hung by a Repair dispatch",
                    lambda d=dispatch_id: self.hang(dispatch_id=d),
                )

    def test_a_repair_dispatch_on_another_order_is_refused(self) -> None:
        """Ruling 130: a Repair dispatch is bound to its order and hangs that order's tags."""
        seated = self.seat_dispatch("Repair", "ORD-03-spare")
        self.assert_hang_refused("is bound to", lambda: self.hang(dispatch_id=seated))

    def test_a_tag_whose_order_is_not_frozen_is_refused(self) -> None:
        """Ruling 131: the hang belongs to a frozen order; after commencement it is refused."""
        self.move("commenced")
        self.assert_hang_refused("a tag is hung on a frozen order")

    def test_a_tag_whose_order_was_never_frozen_is_refused(self) -> None:
        """Rulings 108 and 131: a tag issued on an opened order waits for the freeze.

        The dispatch writer books no Repair dispatch off a frozen order, so the spare
        order's dispatch is seated by hand.
        """
        self.initiate(_SPARE)
        self.move("opened", order="ORD-03-spare", operator_text="open the spare order")
        spare = self.issue(slug="spare", order="ORD-03-spare", surface="path:src/stamp.py")
        seated = self.seat_dispatch("Repair", "ORD-03-spare", package=_SPARE)
        refusal = self.assert_hang_refused(
            "a tag is hung on a frozen order",
            lambda: self.hang(tag_id=spare.tag_id, dispatch_id=seated),
        )
        self.assertIn("Order ORD-03-spare is opened", refusal)

    def test_a_tag_whose_order_is_blocked_is_refused(self) -> None:
        """Rulings 59 and 131: a blocked order's acts are held, the hang among them."""
        request = BlockRequest(
            work_package=_REPAIR, reason="stuck", next_action="rule on it", order=_ORDER
        )
        record_work_package_block(self.catalog, self.ledger, request, refutations={})
        self.assert_hang_refused("is blocked on the operator")


class HungTagLogTests(_HangCase):
    def close_the_order(self) -> None:
        self.move("commenced")
        self.move("accepted", acceptance_ready=True)
        self.move("closed", decision="terminate", attestor="g0", attestation_text="terminate it")

    def test_a_hung_tag_reads_open_after_its_order_closes(self) -> None:
        """Ruling 129: a hung tag stays open until cleared, whatever its order's state."""
        hung = self.hang()
        self.close_the_order()
        (tag,) = tag_log(self.ledger)
        self.assertTrue(tag.is_open)
        assert tag.hang is not None
        self.assertEqual((tag.hang.tag_id, tag.hang.dispatch_id), (hung.tag_id, hung.dispatch_id))
        self.assertEqual([t.issue.tag_id for t in open_tags(self.ledger)], [self.tag.tag_id])

    def test_an_unhung_tag_keeps_ruling_122s_reading(self) -> None:
        """Rulings 122 and 129: an unhung tag reads open until its order closes, hang None."""
        (tag,) = tag_log(self.ledger)
        self.assertEqual((tag.is_open, tag.hang), (True, None))

    def test_a_closed_orders_hung_tag_still_holds_its_surface(self) -> None:
        """Rulings 122 and 129: until cleared, a hung tag refuses a new issue on its surface."""
        self.hang()
        self.close_the_order()
        self.initiate(_SPARE)
        self.move("opened", order="ORD-03-spare", operator_text="open the spare order")
        text = self.assert_refused(slug="second", order="ORD-03-spare")
        # output-contract: the refusal says why the surface is still held (ruling 129)
        self.assertIn(f"It is hung, by dispatch {self.dispatch}", text)
        self.assertIn("until it is cleared", text)

    def test_a_malformed_hang_row_is_refused_with_its_void_not_a_crash(self) -> None:
        """Ruling 4: the log is ledger events; a hang row it cannot read stops it, named."""
        row = {"schema": "gzkit.ledger.v1", "event": "tag_hung", "id": "TAG-7-bad"}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**row, "ts": "2026-11-17T00:00:00+00:00"}) + "\n")
        raised = _raised(lambda: tag_log(self.ledger))
        # output-contract: the refusal names the row's event and the void that recovers it
        self.assertIsInstance(raised, TagOutError)
        self.assertIn("ledger's tag_hung row 'TAG-7-bad'", str(raised))
        self.assertIn("--subject-event tag_hung --subject-id TAG-7-bad", str(raised))
