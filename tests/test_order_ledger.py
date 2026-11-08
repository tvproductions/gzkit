"""The order's Layer-2 writer: RP-12 O2 task 3, act 1.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: an order's lifecycle
lives only in the ledger (ruling 44), `opened` booked on the operator's words when
the order is written (ruling 52), then `frozen`, `commenced` and `accepted` one
step at a time; `closed` is Gate 5 at the order, O2 task 4. A freeze carries the
risk note, the reviewer's receipt and a baseline of repair REQs held on the
order's package (rulings 2, 45), each in one live order's baseline at a time
(ruling 53), and approves the package's alterations no earlier freeze approved
(ruling 63). A refusal writes nothing.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.events import BaselinedReq, OrderTransitionedEvent, parse_typed_event
from gzkit.ledger import Ledger
from gzkit.models.catalog import Alteration, Catalog, Criterion, Order, RepairReq, WorkPackage
from gzkit.ontology.corpus import project_corpus
from gzkit.order_ledger import (
    OrderLedgerError,
    OrderMove,
    booked_order_ids,
    order_holds,
    order_state,
    record_order_transition,
)
from gzkit.work_package_ledger import (
    TransitionRequest,
    declared_modules,
    footprint_sealed,
    record_work_package_transition,
)


def _package(wp_id: str, kind: str = "repair") -> WorkPackage:
    repair = kind == "repair"
    return WorkPackage(
        id=wp_id,
        kind=kind,  # ty: ignore[invalid-argument-type]
        outcome=None if repair else "H1",
        issues=(1301,) if wp_id == "WP-01-stamp" else (1302,) if repair else (),
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


def _repair_req(req_id: str, held_on: str) -> RepairReq:
    return RepairReq(
        id=req_id,
        specialization="repair",
        held_on=held_on,
        problem_report=1301 if held_on == "WP-01-stamp" else 1302,
        statement="The stamp generator imports again.",
        criteria=(Criterion(state_or_input="an import", required_outcome="ok", evidence="t"),),
        kind="BEHAVIOR",
        revision=1,
    )


def _order(order_id: str, package: str = "WP-01-stamp") -> Order:
    return Order(id=order_id, work_package=package, aliases=(), purpose="Fix.", procedure="NA")


def _catalog() -> Catalog:
    return Catalog(
        families=(),
        outcomes=(),
        reqs=(
            _repair_req("REQ-1", "WP-01-stamp"),
            _repair_req("REQ-2", "WP-01-stamp"),
            _repair_req("REQ-3", "WP-03-other"),
        ),
        work_packages=(_package("WP-01-stamp"), _package("WP-03-other")),
        orders=(
            _order("ORD-01-import"),
            _order("ORD-02-matcher"),
            _order("ORD-03-other", "WP-03-other"),
        ),
    )


def _rows(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


_FREEZE = {
    "baseline": (BaselinedReq(req="REQ-1", revision=1),),
    "risk_note": "The import touches the hook.",
    "review_receipt": "review-01",
}
_CLOSE: dict[str, object] = {
    "decision": "proceed",
    "attestor": "g0",
    "attestation_text": "the import holds",
    "residual_risk": "none",
}
_PAYLOADS: dict[str, dict[str, object]] = {
    "opened": {"operator_text": "open the import order"},
    "frozen": _FREEZE,
    "commenced": {},
    "accepted": {},
}


class _OrderCase(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = Path(self._dir.name) / "ledger.jsonl"
        self.ledger = Ledger(self.path)
        self.catalog = _catalog()
        for package in ("WP-01-stamp", "WP-03-other"):
            self.initiate(package)

    def initiate(self, package: str) -> None:
        request = TransitionRequest(
            work_package=package, to_state="initiated", evidence="e", operator_text="go"
        )
        record_work_package_transition(self.catalog, self.ledger, request)

    def move(self, to_state: str, **fields: object) -> OrderTransitionedEvent:
        request = OrderMove.model_validate(
            {"order": "ORD-01-import", "to_state": to_state, "evidence": "evt-1", **fields}
        )
        return record_order_transition(self.catalog, self.ledger, request)

    def walk_to(self, state: str, order: str = "ORD-01-import", **fields: object) -> None:
        states = tuple(_PAYLOADS)
        for step in states[: states.index(state) + 1]:
            extra = fields if step == "frozen" else {}
            self.move(step, order=order, **{**_PAYLOADS[step], **extra})

    def assert_refused(self, to_state: str, **fields: object) -> str:
        before = _rows(self.path)
        with self.assertRaises(OrderLedgerError) as caught:
            self.move(to_state, **fields)
        self.assertEqual(_rows(self.path), before)
        return str(caught.exception)


class LifecycleTests(_OrderCase):
    def test_an_order_with_no_event_is_not_opened(self) -> None:
        self.assertIsNone(order_state(self.ledger, "ORD-01-import"))

    def test_opening_is_booked_on_the_operators_words(self) -> None:
        """Ruling 52: the order is born on the ledger, as a package is initiated."""
        event = self.move("opened", operator_text="open the import order")
        self.assertEqual(
            (event.id, event.order, event.work_package, event.from_state, event.to_state),
            ("ORD-01-import", "ORD-01-import", "WP-01-stamp", None, "opened"),
        )
        self.assertEqual(event.operator_text, "open the import order")
        persisted = parse_typed_event(_rows(self.path)[-1])
        self.assertIsInstance(persisted, OrderTransitionedEvent)
        unstamped = [
            {key: value for key, value in held.model_dump().items() if key != "ts"}
            for held in (persisted, event)
        ]
        self.assertEqual(unstamped[0], unstamped[1])
        self.assertEqual(order_state(self.ledger, "ORD-01-import"), "opened")

    def test_opening_without_the_operators_words_is_refused(self) -> None:
        self.assert_refused("opened")
        self.assert_refused("opened", operator_text="  ")

    def test_the_lifecycle_walks_one_step_at_a_time_to_accepted(self) -> None:
        self.walk_to("accepted")
        moves = [r["to_state"] for r in _rows(self.path) if r["event"] == "order_transitioned"]
        self.assertEqual(moves, ["opened", "frozen", "commenced", "accepted"])

    def test_a_skipped_or_backward_step_is_refused(self) -> None:
        self.assert_refused("frozen", **_FREEZE)
        self.move("opened", **_PAYLOADS["opened"])
        self.assert_refused("commenced")
        self.assert_refused("opened", **_PAYLOADS["opened"])

    def test_an_accepted_order_closes_through_gate_5(self) -> None:
        """Rulings 44 and 74: the lifecycle ends accepted -> closed."""
        self.walk_to("accepted")
        self.assertEqual(self.move("closed", **_CLOSE).from_state, "accepted")

    def test_an_accepted_order_moves_no_further(self) -> None:
        self.walk_to("accepted")
        for state in ("opened", "frozen", "commenced", "accepted"):
            with self.subTest(state=state):
                self.assert_refused(state, **_PAYLOADS[state])

    def test_an_order_the_store_lacks_is_refused(self) -> None:
        self.assert_refused("opened", order="ORD-09-ghost", **_PAYLOADS["opened"])

    def test_a_field_the_target_state_does_not_carry_is_refused(self) -> None:
        self.assert_refused("opened", operator_text="go", risk_note="Too early.")
        self.move("opened", **_PAYLOADS["opened"])
        self.assert_refused("frozen", **_FREEZE, operator_text="again")

    def test_empty_evidence_is_refused(self) -> None:
        self.assert_refused("opened", evidence=" ", **_PAYLOADS["opened"])

    def test_each_order_keeps_its_own_state(self) -> None:
        self.walk_to("commenced")
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        self.assertEqual(order_state(self.ledger, "ORD-01-import"), "commenced")
        self.assertEqual(order_state(self.ledger, "ORD-02-matcher"), "opened")

    def test_an_order_moves_only_while_its_package_is_open(self) -> None:
        """Rulings 2 and 44: the package stays initiated while its orders run."""
        catalog = self.catalog.model_copy(
            update={"work_packages": (*self.catalog.work_packages, _package("WP-04-idle"))}
        )
        self.catalog = catalog.model_copy(
            update={"orders": (*catalog.orders, _order("ORD-04-idle", "WP-04-idle"))}
        )
        output = self.assert_refused("opened", order="ORD-04-idle", **_PAYLOADS["opened"])
        self.assertIn("not initiated", output)

    def test_booked_order_ids_reads_every_order_the_ledger_names(self) -> None:
        self.move("opened", **_PAYLOADS["opened"])
        self.move("opened", order="ORD-03-other", **_PAYLOADS["opened"])
        self.assertEqual(booked_order_ids(self.ledger), {"ORD-01-import", "ORD-03-other"})


class FreezeTests(_OrderCase):
    def setUp(self) -> None:
        super().setUp()
        self.move("opened", **_PAYLOADS["opened"])

    def test_a_freeze_lacking_its_risk_note_or_receipt_is_refused(self) -> None:
        for missing in ("risk_note", "review_receipt"):
            with self.subTest(missing=missing):
                self.assert_refused("frozen", **{**_FREEZE, missing: " "})

    def test_an_empty_baseline_is_refused(self) -> None:
        """Ruling 61: an order freezes at least one requirement."""
        self.assertIn("ruling 61", self.assert_refused("frozen", **{**_FREEZE, "baseline": ()}))

    def test_the_freeze_records_its_baseline_note_and_receipt(self) -> None:
        event = self.move("frozen", **_FREEZE)
        self.assertEqual(event.baseline, (BaselinedReq(req="REQ-1", revision=1),))
        self.assertEqual(
            (event.risk_note, event.review_receipt), ("The import touches the hook.", "review-01")
        )

    def test_the_baseline_holds_repair_reqs_held_on_the_orders_package(self) -> None:
        """Rulings 2 and 45: a repair order freezes its own package's repair REQs."""
        for req, revision in (("REQ-3", 1), ("REQ-1", 2), ("REQ-9", 1)):
            with self.subTest(req=req):
                baseline = (BaselinedReq(req=req, revision=revision),)
                self.assert_refused("frozen", **{**_FREEZE, "baseline": baseline})

    def test_a_req_sits_in_one_live_orders_baseline_at_a_time(self) -> None:
        """Ruling 53: a second live order cannot freeze a REQ the first holds."""
        self.move("frozen", **_FREEZE)
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        output = self.assert_refused("frozen", order="ORD-02-matcher", **_FREEZE)
        self.assertIn("ORD-01-import", output)
        both = (BaselinedReq(req="REQ-2", revision=1),)
        self.assertEqual(
            self.move("frozen", order="ORD-02-matcher", **{**_FREEZE, "baseline": both}).baseline,
            both,
        )

    def test_an_order_opened_and_not_frozen_holds_no_baseline(self) -> None:
        """Ruling 53 reads only frozen baselines: an open order beside holds nothing."""
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        self.assertEqual(self.move("frozen", **_FREEZE).to_state, "frozen")

    def test_an_unknown_state_is_refused(self) -> None:
        self.assert_refused("inspected")

    def test_a_terminated_orders_req_may_be_frozen_again(self) -> None:
        """Ruling 53: once the holder is accepted, a later order may freeze the REQ."""
        self.move("frozen", **_FREEZE)
        self.move("commenced")
        self.move("accepted")
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        self.assertEqual(self.move("frozen", order="ORD-02-matcher", **_FREEZE).to_state, "frozen")


class GateFiveTests(_OrderCase):
    """Rulings 30, 73, 74 and 75: Gate 5 at the order."""

    def close(self, **fields: object) -> OrderTransitionedEvent:
        return self.move("closed", **fields)

    def refused(self, **fields: object) -> str:
        return self.assert_refused("closed", **fields)

    def test_proceed_books_the_decision_the_words_and_the_residual_risk(self) -> None:
        self.walk_to("accepted")
        event = self.close(**_CLOSE)
        self.assertEqual(
            (event.decision, event.attestor, event.attestation_text, event.residual_risk),
            ("proceed", "g0", "the import holds", "none"),
        )
        self.assertEqual(order_state(self.ledger, "ORD-01-import"), "closed")

    def test_a_frozen_or_commenced_order_does_not_close(self) -> None:
        """Ruling 74: a frozen or commenced order closes only after it is accepted."""
        for state in ("frozen", "commenced"):
            with self.subTest(state=state):
                self.walk_to(state)
                self.assertIn("ruling 74", self.refused(**_CLOSE))
                self.setUp()

    def test_an_order_never_frozen_closes_only_as_terminate(self) -> None:
        """Ruling 74: an opened order holds no REQ, so it is only withdrawn."""
        self.move("opened", **_PAYLOADS["opened"])
        self.assertIn("ruling 74", self.refused(**_CLOSE))
        words = {"attestor": "g0", "attestation_text": "withdraw it"}
        event = self.close(decision="terminate", **words)
        self.assertEqual((event.from_state, event.decision), ("opened", "terminate"))

    def test_the_attestor_the_words_and_the_decision_are_required(self) -> None:
        self.walk_to("accepted")
        for missing in ("attestor", "attestation_text", "decision"):
            with self.subTest(missing=missing):
                fields = {k: v for k, v in _CLOSE.items() if k != missing}
                self.refused(**fields)
        self.refused(**{**_CLOSE, "attestation_text": "  "})

    def test_each_decision_carries_its_own_field_and_refuses_the_others(self) -> None:
        """Ruling 73: proceed the residual risk, redirect its successor, pause the revisit."""
        self.walk_to("accepted")
        words = {"attestor": "g0", "attestation_text": "ruled"}
        for decision, fields in (
            ("proceed", {}),
            ("proceed", {"residual_risk": "none", "revisit_condition": "later"}),
            ("pause", {}),
            ("pause", {"revisit_condition": "later", "residual_risk": "none"}),
            ("redirect", {}),
            ("terminate", {"residual_risk": "none"}),
        ):
            with self.subTest(decision=decision, fields=sorted(fields)):
                self.refused(decision=decision, **words, **fields)
        paused = self.close(decision="pause", revisit_condition="after RP-14", **words)
        self.assertEqual(paused.revisit_condition, "after RP-14")

    def test_a_blank_field_of_another_decision_is_refused_too(self) -> None:
        """Ruling 73: a decision refuses the others' fields, given blank or not."""
        self.walk_to("accepted")
        for foreign in ({"revisit_condition": "  "}, {"superseded_by": " "}):
            with self.subTest(foreign=foreign):
                self.assertIn("ruling 73", self.refused(**_CLOSE, **foreign))
        own_blank = self.refused(**{**_CLOSE, "residual_risk": "  "})
        self.assertIn("carries residual-risk", own_blank)  # its own field, given blank

    def test_the_attestor_is_booked_stripped_and_the_words_verbatim(self) -> None:
        self.walk_to("accepted")
        event = self.close(**{**_CLOSE, "attestor": " g0 ", "attestation_text": " my words "})
        self.assertEqual((event.attestor, event.attestation_text), ("g0", " my words "))

    def test_a_redirect_names_an_opened_order_of_the_same_package(self) -> None:
        """Ruling 75: the successor is opened, not frozen, and sits in the same package."""
        self.walk_to("accepted")
        words = {"decision": "redirect", "attestor": "g0", "attestation_text": "rework"}
        for successor in ("ORD-02-matcher", "ORD-03-other", "ORD-01-import", "ORD-09-ghost"):
            with self.subTest(successor=successor):
                self.refused(superseded_by=successor, **words)
        self.move("opened", order="ORD-03-other", **_PAYLOADS["opened"])
        other = self.refused(superseded_by="ORD-03-other", **words)
        self.assertIn("not another order of WP-01-stamp", other)  # opened, but elsewhere
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        event = self.close(superseded_by="ORD-02-matcher", **words)
        self.assertEqual(event.superseded_by, "ORD-02-matcher")

    def test_a_redirects_successor_that_has_frozen_is_refused(self) -> None:
        self.walk_to("accepted")
        second = {**_FREEZE, "baseline": (BaselinedReq(req="REQ-2", revision=1),)}
        self.walk_to("frozen", order="ORD-02-matcher", **second)
        words = {"decision": "redirect", "attestor": "g0", "attestation_text": "rework"}
        self.assertIn("ruling 75", self.refused(superseded_by="ORD-02-matcher", **words))

    def test_a_proceed_holds_the_reqs_the_order_froze(self) -> None:
        """Ruling 78: a repair REQ holds at the revision a proceed-closed order froze it."""
        self.walk_to("accepted")
        self.assertEqual(order_holds(self.ledger, "ORD-01-import"), {})
        self.close(**_CLOSE)
        self.assertEqual(order_holds(self.ledger, "ORD-01-import"), {"REQ-1": 1})

    def test_no_other_decision_holds_a_req(self) -> None:
        self.walk_to("accepted")
        self.close(decision="terminate", attestor="g0", attestation_text="stop")
        self.assertEqual(order_holds(self.ledger, "ORD-01-import"), {})

    def test_a_held_req_is_never_frozen_again_at_that_revision(self) -> None:
        """Ruling 81: a REQ a proceed holds is delivered there, so no later order freezes it."""
        self.walk_to("accepted")
        self.close(**_CLOSE)
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        output = self.assert_refused("frozen", order="ORD-02-matcher", **_FREEZE)
        self.assertIn("ruling 81", output)

    def test_a_closed_order_moves_no_further_and_releases_its_reqs(self) -> None:
        """Ruling 53: a terminated order holds no REQ, so a later order freezes it again."""
        self.walk_to("accepted")
        self.close(decision="terminate", attestor="g0", attestation_text="stop")
        for state in ("opened", "frozen", "commenced", "accepted", "closed"):
            with self.subTest(state=state):
                self.assert_refused(state, **_PAYLOADS.get(state, _CLOSE))
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        self.assertEqual(self.move("frozen", order="ORD-02-matcher", **_FREEZE).to_state, "frozen")


class FootprintSealTests(_OrderCase):
    """Ruling 56: each order's freeze seals its repair package's footprint."""

    def setUp(self) -> None:
        super().setUp()
        self.move("opened", **_PAYLOADS["opened"])

    def package(self, *modules: str) -> WorkPackage:
        return _package("WP-01-stamp").model_copy(update={"modules": modules})

    def test_the_freeze_records_the_packages_footprint(self) -> None:
        self.assertEqual(self.move("frozen", **_FREEZE).modules, ("src/stamp.py",))

    def test_before_any_order_freezes_the_store_is_the_footprint(self) -> None:
        self.assertFalse(footprint_sealed(self.ledger, "WP-01-stamp"))
        edited = self.package("src/stamp.py", "src/extra.py")
        self.assertEqual(declared_modules(self.ledger, edited), edited.modules)

    def test_a_store_edited_after_the_freeze_moves_nothing(self) -> None:
        self.move("frozen", **_FREEZE)
        self.assertTrue(footprint_sealed(self.ledger, "WP-01-stamp"))
        edited = self.package("src/other.py")
        self.assertEqual(declared_modules(self.ledger, edited), ("src/stamp.py",))

    def test_a_later_orders_freeze_seals_the_store_as_it_then_reads(self) -> None:
        """The limit ruling 56 states: a later freeze can widen what the first sealed."""
        self.move("frozen", **_FREEZE)
        widened = self.package("src/stamp.py", "src/extra.py")
        self.catalog = self.catalog.model_copy(
            update={"work_packages": (widened, _package("WP-03-other"))}
        )
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        second = {**_FREEZE, "baseline": (BaselinedReq(req="REQ-2", revision=1),)}
        self.move("frozen", order="ORD-02-matcher", **second)
        self.assertEqual(
            declared_modules(self.ledger, self.package()), ("src/stamp.py", "src/extra.py")
        )

    def test_a_later_freeze_refuses_a_store_that_dropped_a_sealed_path(self) -> None:
        """Ruling 71: a sealed footprint only grows, so a narrowed store is refused."""
        self.move("frozen", **_FREEZE)
        narrowed = self.package("src/extra.py")
        self.catalog = self.catalog.model_copy(
            update={"work_packages": (narrowed, _package("WP-03-other"))}
        )
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])
        second = {**_FREEZE, "baseline": (BaselinedReq(req="REQ-2", revision=1),)}
        output = self.assert_refused("frozen", order="ORD-02-matcher", **second)
        self.assertIn("src/stamp.py", output)
        self.assertIn("rulings 56 and 71", output)

    def test_another_packages_order_does_not_seal_this_one(self) -> None:
        self.move("opened", order="ORD-03-other", **_PAYLOADS["opened"])
        other = {**_FREEZE, "baseline": (BaselinedReq(req="REQ-3", revision=1),)}
        self.move("frozen", order="ORD-03-other", **other)
        self.assertFalse(footprint_sealed(self.ledger, "WP-01-stamp"))


def _alteration(alteration_id: str) -> Alteration:
    return Alteration(id=alteration_id, description="A remodel.", configuration_change="replaced")


class AlterationApprovalTests(_OrderCase):
    """Ruling 63: each order's freeze approves the alterations no earlier freeze approved."""

    def setUp(self) -> None:
        super().setUp()
        self.plan("ALT-1", "ALT-2")
        self.move("opened", **_PAYLOADS["opened"])
        self.move("opened", order="ORD-02-matcher", **_PAYLOADS["opened"])

    def plan(self, *alterations: str, package: str = "WP-01-stamp") -> None:
        held = [
            wp.model_copy(update={"alterations": tuple(map(_alteration, alterations))})
            if wp.id == package
            else wp
            for wp in self.catalog.work_packages
        ]
        self.catalog = self.catalog.model_copy(update={"work_packages": tuple(held)})

    def freeze(self, *approved: str, order: str = "ORD-01-import", req: str = "REQ-1"):
        baseline = (BaselinedReq(req=req, revision=1),)
        return self.move(
            "frozen", order=order, **{**_FREEZE, "baseline": baseline},
            approved_alterations=approved,
        )  # fmt: skip

    def test_the_first_freeze_approves_every_planned_alteration(self) -> None:
        for approved in ((), ("ALT-1",), ("ALT-1", "ALT-2", "ALT-9")):
            with self.subTest(approved=approved):
                output = self.assert_refused(
                    "frozen", **_FREEZE, approved_alterations=approved
                )  # fmt: skip
                self.assertIn("ruling 63", output)
        event = self.freeze("ALT-2", "ALT-1")
        self.assertEqual(set(event.approved_alterations), {"ALT-1", "ALT-2"})
        persisted = parse_typed_event(_rows(self.path)[-1])
        self.assertIsInstance(persisted, OrderTransitionedEvent)

    def test_a_later_freeze_approves_only_what_was_planned_since(self) -> None:
        self.freeze("ALT-1", "ALT-2")
        self.plan("ALT-1", "ALT-2", "ALT-3")
        output = self.assert_refused(
            "frozen", order="ORD-02-matcher",
            **{**_FREEZE, "baseline": (BaselinedReq(req="REQ-2", revision=1),)},
            approved_alterations=("ALT-1", "ALT-2", "ALT-3"),
        )  # fmt: skip
        self.assertIn("['ALT-3'] are due", output)
        event = self.freeze("ALT-3", order="ORD-02-matcher", req="REQ-2")
        self.assertEqual(event.approved_alterations, ("ALT-3",))

    def test_nothing_due_is_an_empty_approval(self) -> None:
        self.freeze("ALT-1", "ALT-2")
        event = self.freeze(order="ORD-02-matcher", req="REQ-2")
        self.assertEqual(event.approved_alterations, ())

    def test_another_packages_approvals_do_not_count(self) -> None:
        self.plan("ALT-1", package="WP-03-other")
        self.move("opened", order="ORD-03-other", **_PAYLOADS["opened"])
        self.freeze("ALT-1", order="ORD-03-other", req="REQ-3")
        self.assert_refused("frozen", **_FREEZE, approved_alterations=("ALT-2",))
        self.assertEqual(
            set(self.freeze("ALT-1", "ALT-2").approved_alterations), {"ALT-1", "ALT-2"}
        )


class CorpusTests(_OrderCase):
    def test_the_corpus_projection_accounts_for_the_event(self) -> None:
        self.move("opened", **_PAYLOADS["opened"])
        project_corpus(self.ledger)


if __name__ == "__main__":
    unittest.main()
