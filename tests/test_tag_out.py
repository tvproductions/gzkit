"""The tag-out log's issue writer and reducer: RP-12 O3 task 2, act 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the tag-out log is
ledger events (ruling 4); the coordinator issues a tag (ruling 6) whose
`tag_issued` event carries the whole line item (rulings 5 and 120), held by the
open MX session (rulings 3, 113 and 114), under check level C or D (113), on a
surface written `<kind>:<name>` and resolved against today's registries (112,
123), from one of ruling 124's four sources, on an opened or frozen order of an
initiated repair package (121), one open tag per surface (122). Its id is
`TAG-<NN>-<slug>` (111). Every refusal is proved here against the writer, which
imports no `gzkit.cli` (ruling 125). A refusal writes nothing.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from gzkit.events import BaselinedReq, OrderTransitionedEvent, TagIssuedEvent, parse_typed_event
from gzkit.ledger import Ledger, ledger_row
from gzkit.models.catalog import Catalog, Criterion, Order, RepairReq, WorkPackage
from gzkit.mx.tag_out import (
    TagIssue,
    TagOutError,
    next_tag_id,
    open_tags,
    record_tag_issue,
    tag_log,
)
from gzkit.order_ledger import OrderMove, record_order_transition
from gzkit.work_package_ledger import TransitionRequest, record_work_package_transition

if TYPE_CHECKING:
    from collections.abc import Callable

_SESSION = "mx-20261117-probe"
_REPAIR = "WP-01-stamp"
_SPARE = "WP-03-spare"
_DELIVERY = "WP-02-build"
_ORDER = "ORD-01-import"


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
