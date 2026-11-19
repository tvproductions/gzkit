"""The run of an order: dispatch, block and unblock (RP-12 O2 task 3, act 3).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: with `--order`,
`gz wp dispatch` takes only a REQ the order's freeze holds, at its frozen
revision, while the order is commenced (ruling 57); `gz wp block --order` holds
that order alone, its dispatches and lifecycle moves refused until
`gz wp unblock --order` records the operator's ruling (ruling 59). Every reader of
a run in flight reads the order's state, so the guard of ruling 40 does not go
silent on repair work, whose package stays initiated (ruling 44). A refusal
writes nothing.
"""

import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, cast

from gzkit.events import BaselinedReq, OrderTransitionedEvent
from gzkit.ledger import ledger_row
from gzkit.order_ledger import (
    OrderLedgerError,
    is_order_blocked,
    order_state,
    order_took_stopping_exit,
)
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.pipeline_stage_fence import frozen_order_write_refusal, work_package_write_refusal
from gzkit.work_package_fence import (
    FencedPackage,
    fenced_packages,
    work_package_commit_message,
    work_package_write_message,
)
from gzkit.work_package_ledger import (
    ChangeRequest,
    TransitionRequest,
    WorkPackageLedgerError,
    is_blocked,
    record_work_package_change,
    record_work_package_transition,
)
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    RunPosition,
    UnblockRequest,
    find_dispatch,
    open_unclaimed_dispatches,
    record_dispatch_void,
    record_work_package_block,
    record_work_package_dispatch,
    record_work_package_unblock,
    run_positions,
    took_stopping_exit,
)
from tests.test_order_ledger import (
    _CLOSE,
    _FREEZE,
    _PAYLOADS,
    _OrderCase,
    _package,
    _raised,
    _rows,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_PACKAGE = "WP-01-stamp"
_ORDER = "ORD-01-import"
_SECOND = "ORD-02-matcher"
_ROOT = "/elsewhere/project"


class _OrderRun(_OrderCase):
    """Two orders on one repair package, the first commenced on REQ-1."""

    def setUp(self) -> None:
        super().setUp()
        self.walk_to("commenced")

    def commence_second(self) -> None:
        self.walk_to("commenced", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))

    def dispatch(
        self,
        role: str = "Implementer",
        *,
        order: str | None = _ORDER,
        req: str | None = "REQ-1",
        root: str = _ROOT,
        reason: str | None = None,
    ):
        request = DispatchRequest(
            work_package=_PACKAGE, order=order, role=role, model="m", req=req, root=root,
            reason=reason,
        )  # fmt: skip
        return record_work_package_dispatch(self.catalog, self.ledger, request)

    def block(self, order: str | None = _ORDER):
        request = BlockRequest(
            work_package=_PACKAGE, order=order, reason="refuted", next_action="rule on it"
        )
        return record_work_package_block(self.catalog, self.ledger, request, refutations={})

    def unblock(self, order: str | None = _ORDER, exit_taken: str | None = None, req=None):
        request = UnblockRequest(
            work_package=_PACKAGE, order=order, ruling="a", operator="g0",
            exit_taken=exit_taken, req=req,
        )  # fmt: skip
        return record_work_package_unblock(self.catalog, self.ledger, request)

    def refused(self, pattern: str, act) -> str:
        before = _rows(self.path)
        raised = _raised(act)
        self.assertIsInstance(raised, (WorkPackageLedgerError, OrderLedgerError))
        self.assertRegex(str(raised), pattern)
        self.assertEqual(_rows(self.path), before)
        return str(raised)

    def reach_the_bound(self) -> None:
        for _ in range(MAX_REVIEW_FIX_CYCLES):
            self.dispatch()
            self.dispatch("SpecReviewer")
        self.dispatch()
        self.dispatch("SpecReviewer")


class DispatchOnAnOrder(_OrderRun):
    """Ruling 57: an order's dispatch targets only a REQ its freeze holds."""

    def test_a_frozen_req_is_dispatched_at_its_frozen_revision(self) -> None:
        event = self.dispatch()
        self.assertEqual(
            (event.work_package, event.order, event.subject), (_PACKAGE, _ORDER, "REQ-1@1")
        )

    def test_a_req_held_on_the_package_but_not_frozen_by_the_order_is_refused(self) -> None:
        self.refused("frozen baseline", lambda: self.dispatch(req="REQ-2"))

    def test_another_orders_req_is_refused(self) -> None:
        self.commence_second()
        self.refused("frozen baseline", lambda: self.dispatch(req="REQ-2"))

    def test_an_order_dispatch_names_a_req(self) -> None:
        self.refused("names a REQ its freeze holds", lambda: self.dispatch(req=None))

    def test_an_order_of_a_repair_package_cannot_be_single_driver(self) -> None:
        self.refused(
            "nobody inspects their own work",
            lambda: self.dispatch("SingleDriver", reason="none"),
        )

    def test_an_order_not_commenced_takes_no_dispatch(self) -> None:
        self.walk_to("opened", order=_SECOND)
        self.refused("not commenced", lambda: self.dispatch(order=_SECOND))

    def test_an_accepted_order_takes_no_dispatch(self) -> None:
        self.move("accepted", **_PAYLOADS["accepted"])
        self.refused("not commenced", self.dispatch)

    def test_an_order_of_another_package_is_refused(self) -> None:
        self.refused("ORD-03-other", lambda: self.dispatch(order="ORD-03-other"))

    def test_an_order_the_store_lacks_is_refused(self) -> None:
        self.refused("ORD-09-ghost", lambda: self.dispatch(order="ORD-09-ghost"))

    def test_a_package_the_catalog_lacks_is_refused_not_crashed_on(self) -> None:
        """A dispatch naming no catalogued package is a refusal, never a crash on its absence."""
        request = DispatchRequest(
            work_package="WP-99-ghost", order=_ORDER, role="Implementer", model="m",
            req="REQ-1", root=_ROOT,
        )  # fmt: skip
        before = _rows(self.path)
        try:
            record_work_package_dispatch(self.catalog, self.ledger, request)
        except Exception as exc:  # a crash must fail this test, not error it
            raised: Exception | None = exc
        else:
            raised = None
        self.assertIsInstance(raised, WorkPackageLedgerError)
        self.assertIn("WP-99-ghost", str(raised))
        self.assertEqual(_rows(self.path), before)

    def test_another_packages_commenced_order_takes_no_dispatch(self) -> None:
        """Ruling 44: an order dispatches only as an order of the package the call names."""
        self.walk_to(
            "commenced", order="ORD-03-other", baseline=(BaselinedReq(req="REQ-3", revision=1),)
        )
        self.refused(
            "not one of WP-01-stamp's orders",
            lambda: self.dispatch(order="ORD-03-other", req="REQ-3"),
        )

    def test_the_fix_cycle_bound_counts_against_the_orders_subject(self) -> None:
        self.reach_the_bound()
        self.refused("bound", self.dispatch)

    def test_an_order_whose_package_closed_takes_no_dispatch(self) -> None:
        """Rulings 44 and 76: the package closes once its orders have, and none works on."""
        self.move("accepted", **_PAYLOADS["accepted"])
        self.move("closed", decision="terminate", attestor="g0", attestation_text="stop")
        close = TransitionRequest(
            work_package=_PACKAGE, to_state="closed", evidence="e", attestor="g0",
            residual_risk="none",
        )  # fmt: skip
        record_work_package_transition(self.catalog, self.ledger, close)
        self.refused("initiated", self.dispatch)

    def test_a_dispatch_on_the_repair_package_names_its_order(self) -> None:
        self.refused("--order", lambda: self.dispatch(order=None))


class RepairOnAnOrder(_OrderRun):
    """Rulings 108, 130 and 131: a Repair dispatch takes a frozen order and no REQ."""

    def freeze_second(self) -> None:
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))

    def test_a_frozen_order_takes_it_with_the_order_as_its_subject(self) -> None:
        self.freeze_second()
        event = self.dispatch("Repair", order=_SECOND, req=None)
        self.assertEqual((event.role, event.order, event.subject), ("Repair", _SECOND, _SECOND))

    def test_its_record_carries_its_order(self) -> None:
        """Task 3's hang reads a dispatch's order from its record."""
        self.freeze_second()
        event = self.dispatch("Repair", order=_SECOND, req=None)
        found = find_dispatch(self.ledger, str(event.dispatch_id))
        assert found is not None
        self.assertEqual((found.role, found.order, found.subject), ("Repair", _SECOND, _SECOND))

    def test_a_commenced_order_refuses_it(self) -> None:
        refusal = self.refused("frozen order", lambda: self.dispatch("Repair", req=None))
        self.assertIn("131", refusal)
        self.assertIn("uv run gz wp order show", refusal)

    def test_it_names_no_req(self) -> None:
        self.freeze_second()
        refusal = self.refused(
            "names no REQ", lambda: self.dispatch("Repair", order=_SECOND, req="REQ-2")
        )
        self.assertIn("without --req", refusal)

    def test_a_blocked_frozen_order_refuses_it(self) -> None:
        self.freeze_second()
        self.block(order=_SECOND)
        self.refused(
            f"Order {_SECOND} is blocked on the operator; it takes no dispatch",
            lambda: self.dispatch("Repair", order=_SECOND, req=None),
        )


class RestorationOnAnOrder(_OrderRun):
    """Ruling 132: a Restoration dispatch takes a commenced order and no REQ."""

    def test_a_commenced_order_takes_it_with_the_order_as_its_subject(self) -> None:
        event = self.dispatch("Restoration", req=None)
        self.assertEqual((event.role, event.order, event.subject), ("Restoration", _ORDER, _ORDER))

    def test_a_frozen_order_refuses_it(self) -> None:
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        refusal = self.refused(
            "commenced order", lambda: self.dispatch("Restoration", order=_SECOND, req=None)
        )
        self.assertIn("132", refusal)

    def test_it_names_no_req(self) -> None:
        refusal = self.refused("names no REQ", lambda: self.dispatch("Restoration"))
        self.assertIn("without --req", refusal)

    def test_a_blocked_commenced_order_refuses_it(self) -> None:
        """Ruling 59: a blocked order takes no dispatch, the craftsman's among them."""
        self.block()
        self.refused(
            f"Order {_ORDER} is blocked on the operator; it takes no dispatch",
            lambda: self.dispatch("Restoration", req=None),
        )

    def test_an_accepted_order_refuses_it(self) -> None:
        """Ruling 132: Restoration takes a commenced order alone, not an accepted one."""
        self.move("accepted", **_PAYLOADS["accepted"])
        refusal = self.refused(
            "is accepted; a Restoration dispatch takes a commenced order",
            lambda: self.dispatch("Restoration", req=None),
        )
        self.assertIn("132", refusal)


class BlockOnAnOrder(_OrderRun):
    """Ruling 59: `gz wp block --order` holds that order alone."""

    def test_the_block_holds_the_order_and_not_its_package(self) -> None:
        event = self.block()
        self.assertEqual((event.id, event.work_package, event.order), (_ORDER, _PACKAGE, _ORDER))
        self.assertTrue(is_order_blocked(self.ledger, _ORDER))
        self.assertFalse(is_blocked(self.ledger, _PACKAGE))

    def test_a_blocked_order_takes_no_dispatch(self) -> None:
        self.block()
        self.refused(
            f"Order {_ORDER} is blocked on the operator; it takes no dispatch", self.dispatch
        )

    def test_a_blocked_order_does_not_move(self) -> None:
        self.block()
        self.refused(
            f"Order {_ORDER} is blocked on the operator; it does not move",
            lambda: self.move("accepted", **_PAYLOADS["accepted"]),
        )

    def test_the_packages_other_orders_are_still_dispatched_and_moved(self) -> None:
        self.commence_second()
        self.block()
        self.assertEqual(self.dispatch(order=_SECOND, req="REQ-2").order, _SECOND)
        self.move("accepted", order=_SECOND, **_PAYLOADS["accepted"])
        self.assertEqual(order_state(self.ledger, _SECOND), "accepted")

    def test_a_block_on_the_repair_package_names_its_order(self) -> None:
        self.refused("--order", lambda: self.block(order=None))

    def test_the_facts_are_the_orders_own(self) -> None:
        self.dispatch()
        event = self.block()
        self.assertEqual(event.fix_cycles, {"REQ-1@1": 0})
        self.assertEqual((event.at_bound, event.held, event.exits_used), ((), (), ()))

    def test_a_later_block_carries_the_orders_exits_and_reopenings(self) -> None:
        self.reach_the_bound()
        self.block()
        self.unblock(exit_taken="hold")
        event = self.block()
        self.assertEqual((event.exits_used, event.held), (("hold",), ("REQ-1@1",)))
        self.assertIsNone(_raised(lambda: self.unblock(exit_taken="reopen", req="REQ-1")))
        self.assertEqual(self.block().reopened, ("REQ-1",))

    def test_a_second_block_while_the_order_is_blocked_is_refused(self) -> None:
        self.block()
        self.refused("already blocked", self.block)

    def test_an_accepted_order_takes_no_block(self) -> None:
        """RP-12 ruling 69: final inspection is done; Gate 5's outcomes remain."""
        self.move("accepted", **_PAYLOADS["accepted"])
        refusal = self.refused("accepted", self.block)
        # output-contract: the recovery step is the refusal's contract
        self.assertIn("closes through Gate 5", refusal)

    def test_an_order_not_opened_or_closed_is_not_sent_to_gate_5_by_the_refusal(self) -> None:
        """Ruling 69's next step is an accepted order's alone: no other refusal names it."""
        self.move("accepted", **_PAYLOADS["accepted"])
        self.move("closed", decision="terminate", attestor="g0", attestation_text="stop")
        for order, state in ((_SECOND, "not opened"), (_ORDER, "closed")):
            with self.subTest(order=order):
                refusal = self.refused(state, lambda order=order: self.block(order=order))
                # output-contract: the recovery step is the refusal's contract
                self.assertNotIn("closes through Gate 5", refusal)

    def test_a_block_names_its_reason_and_the_decision_owed(self) -> None:
        """Ruling 59: a block carries why the order cannot proceed and what the operator owes."""
        for reason, next_action in (("  ", "rule on it"), ("refuted", "  ")):
            request = BlockRequest(
                work_package=_PACKAGE, order=_ORDER, reason=reason, next_action=next_action
            )
            with self.subTest(reason=reason, next_action=next_action):
                self.refused(
                    "names its reason",
                    lambda request=request: record_work_package_block(
                        self.catalog, self.ledger, request, refutations={}
                    ),
                )

    def test_another_packages_commenced_order_takes_no_block(self) -> None:
        """Ruling 59: a block on an order holds only an order of the package the call names."""
        self.walk_to(
            "commenced", order="ORD-03-other", baseline=(BaselinedReq(req="REQ-3", revision=1),)
        )
        self.refused("not one of WP-01-stamp's orders", lambda: self.block(order="ORD-03-other"))

    def test_an_order_not_opened_or_of_another_package_takes_no_block(self) -> None:
        for order in ("ORD-02-matcher", "ORD-03-other", "ORD-09-ghost"):
            with self.subTest(order=order):
                self.refused(order, lambda order=order: self.block(order=order))

    def test_an_unblock_with_no_exit_spends_none_for_the_next_block(self) -> None:
        """Ruling 69's exits are counted from the exits taken; an unblock without one takes none."""
        self.dispatch()
        self.block()
        self.unblock()
        events = []
        self.assertIsNone(_raised(lambda: events.append(self.block())))
        self.assertEqual(events[0].exits_used, ())


class OrderOnADeliveryPackage(_OrderRun):
    """A delivery package holds no orders, so a run verb refuses its --order (ruling 44)."""

    def test_each_run_verb_refuses_an_order_on_a_delivery_package_in_three_parts(self) -> None:
        # output-contract: guardrail-feedback-prose's three parts, RP-12 rulings 44 and 103
        delivery = _package("WP-05-feat", "delivery")
        self.catalog = self.catalog.model_copy(
            update={"work_packages": (*self.catalog.work_packages, delivery)}
        )
        record_work_package_transition(
            self.catalog,
            self.ledger,
            TransitionRequest(
                work_package="WP-05-feat", to_state="initiated", evidence="e", operator_text="go"
            ),
        )
        dispatch = DispatchRequest(
            work_package="WP-05-feat", order=_ORDER, role="Implementer", model="m",
            req="REQ-1", root=_ROOT,
        )  # fmt: skip
        block = BlockRequest(work_package="WP-05-feat", order=_ORDER, reason="r", next_action="n")
        unblock = UnblockRequest(work_package="WP-05-feat", order=_ORDER, ruling="a", operator="g0")
        calls = {
            "dispatch": lambda: record_work_package_dispatch(self.catalog, self.ledger, dispatch),
            "block": lambda: record_work_package_block(
                self.catalog, self.ledger, block, refutations={}
            ),
            "unblock": lambda: record_work_package_unblock(self.catalog, self.ledger, unblock),
        }
        for verb, call in calls.items():
            with self.subTest(verb=verb):
                self.assertEqual(
                    self.refused("holds no orders", call),
                    "Work package WP-05-feat is a delivery package and holds no orders; a "
                    "delivery package keeps its five states until RP-14 moves construction onto "
                    f"the order (RP-12 ruling 44). Re-run the call without --order {_ORDER}.",
                )


class UnblockOnAnOrder(_OrderRun):
    """Only `gz wp unblock --order` lifts an order's block (ruling 59)."""

    def test_the_operators_ruling_clears_the_orders_block(self) -> None:
        self.block()
        event = self.unblock()
        self.assertEqual((event.id, event.order), (_ORDER, _ORDER))
        self.assertFalse(is_order_blocked(self.ledger, _ORDER))
        self.assertEqual(self.dispatch().order, _ORDER)

    def test_another_packages_blocked_order_is_refused(self) -> None:
        self.walk_to(
            "commenced", order="ORD-03-other", baseline=(BaselinedReq(req="REQ-3", revision=1),)
        )
        record_work_package_block(
            self.catalog,
            self.ledger,
            BlockRequest(
                work_package="WP-03-other", order="ORD-03-other", reason="r", next_action="n"
            ),
            refutations={},
        )
        self.refused("not one of WP-01-stamp's orders", lambda: self.unblock(order="ORD-03-other"))

    def test_an_order_not_blocked_is_refused(self) -> None:
        self.refused("not blocked", self.unblock)

    def test_an_unblock_of_an_unblocked_order_reads_in_three_parts(self) -> None:
        # output-contract: guardrail-feedback-prose's three parts, RP-12 ruling 101
        self.assertEqual(
            self.refused("not blocked", self.unblock),
            f"Order {_ORDER} is not blocked; an unblock records the operator's ruling on an open "
            "block (RP-12 ruling 59). Read the run's position with `uv run gz wp runs`.",
        )

    def test_an_order_outside_the_package_reads_in_three_parts(self) -> None:
        # output-contract: guardrail-feedback-prose's three parts, RP-12 ruling 101
        for order, where, step in (
            (
                "ORD-03-other",
                "an order of WP-03-other",
                (
                    "Read its package with `uv run gz wp order show ORD-03-other`, and re-run "
                    f"with an order of {_PACKAGE}."
                ),
            ),
            (
                "ORD-09-ghost",
                "not in data/catalog/orders.json",
                (
                    f"Check the id; an order is written with `uv run gz wp order new {_PACKAGE} "
                    "--slug <slug> --purpose <text> --operator-text <words>`."
                ),
            ),
        ):
            with self.subTest(order=order):
                self.assertEqual(
                    self.refused("not one of", lambda order=order: self.unblock(order=order)),
                    f"Order {order!r} is {where}; it is not one of {_PACKAGE}'s orders; a "
                    "run verb's --order takes an order of the package it names (RP-12 rulings 57 "
                    f"and 59). {step}",
                )

    def test_a_package_unblock_does_not_lift_an_orders_block(self) -> None:
        self.block()
        self.refused("--order", lambda: self.unblock(order=None))
        self.assertTrue(is_order_blocked(self.ledger, _ORDER))

    def test_at_the_bound_the_unblock_names_an_exit(self) -> None:
        self.reach_the_bound()
        self.block()
        self.refused("name an exit", self.unblock)

    def test_terminate_stops_the_order_and_not_its_package(self) -> None:
        self.commence_second()
        self.reach_the_bound()
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertTrue(order_took_stopping_exit(self.ledger, _ORDER))
        self.assertFalse(order_took_stopping_exit(self.ledger, _SECOND))
        self.assertFalse(took_stopping_exit(self.ledger, _PACKAGE))
        self.refused("terminate exit", self.dispatch)
        held = []
        self.assertIsNone(_raised(lambda: held.append(self.dispatch(order=_SECOND, req="REQ-2"))))
        self.assertEqual(held[0].order, _SECOND)

    def test_a_stopped_orders_refusal_names_the_order(self) -> None:
        # output-contract: the refusal's what-failed part, RP-12 ruling 101
        self.reach_the_bound()
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertEqual(
            self.refused("terminate exit", self.dispatch),
            f"Order {_ORDER} took the terminate exit; it takes no further repair and closes "
            "through Gate 5.",
        )

    def test_a_stopped_order_never_ready_does_not_close_as_proceed(self) -> None:
        """Rulings 80 and 84: the writer reads the readiness booked at acceptance."""
        self.block()
        self.unblock(exit_taken="terminate")
        self.move("accepted", acceptance_ready=False)
        self.refused("rulings 78, 80 and 84", lambda: self.move("closed", **_CLOSE))
        self.setUp()
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertTrue(self.move("accepted", acceptance_ready=True).acceptance_ready)
        self.assertEqual(self.move("closed", **_CLOSE).decision, "proceed")

    def test_readiness_is_booked_at_acceptance_alone(self) -> None:
        """Ruling 84: `acceptance_ready` is a field of the accepted move only."""
        self.move("accepted", **_PAYLOADS["accepted"])
        self.refused(
            "does not carry acceptance_ready",
            lambda: self.move("closed", acceptance_ready=True, **_CLOSE),
        )

    def test_a_proceed_on_a_req_another_proceed_holds_is_refused(self) -> None:
        """Ruling 82: a stopped order's REQ refrozen and proceeded is not held twice."""
        self.block()
        self.unblock(exit_taken="terminate")
        self.walk_to("accepted", order=_SECOND)
        self.move("closed", order=_SECOND, **_CLOSE)
        self.move("accepted", acceptance_ready=True)
        self.refused("ruling 82", lambda: self.move("closed", **_CLOSE))
        stop = {"decision": "terminate", "attestor": "g0", "attestation_text": "stop"}
        self.assertEqual(self.move("closed", **stop).decision, "terminate")

    def test_a_stopped_orders_req_may_be_frozen_again(self) -> None:
        """Ruling 53: a stopped order's REQ is not stranded; a later order may freeze it."""
        self.move("opened", order=_SECOND, **_PAYLOADS["opened"])
        self.refused("ORD-01-import", lambda: self.move("frozen", order=_SECOND, **_FREEZE))
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertEqual(
            self.move("frozen", order=_SECOND, **_FREEZE).baseline, _FREEZE["baseline"]
        )


class OrderFence(_OrderRun):
    """Ruling 58: an accepted, blocked or stopped order holds the production-write fence."""

    def fences(self) -> list[tuple[str, str | None, str]]:
        root = Path(self._dir.name)
        (root / ".gzkit.json").write_text('{"paths": {"ledger": "ledger.jsonl"}}', encoding="utf-8")
        return [(f.work_package, f.order, f.reason) for f in fenced_packages(root)]

    def test_a_commenced_order_does_not_fence(self) -> None:
        self.assertEqual(self.fences(), [])

    def test_a_blocked_order_fences_until_the_operator_rules(self) -> None:
        self.block()
        self.assertEqual(self.fences(), [(_PACKAGE, _ORDER, "blocked")])
        self.unblock()
        self.assertEqual(self.fences(), [])

    def test_an_accepted_order_fences(self) -> None:
        self.move("accepted", **_PAYLOADS["accepted"])
        self.assertEqual(self.fences(), [(_PACKAGE, _ORDER, "accepted")])

    def test_an_order_stopped_by_an_exit_fences(self) -> None:
        self.reach_the_bound()
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertEqual(self.fences(), [(_PACKAGE, _ORDER, "stopped")])

    def test_a_blocked_frozen_order_fences_its_footprint_not_the_tree(self) -> None:
        """Rulings 58 and 116: before commencement an order holds its footprint alone."""
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        self.block(order=_SECOND)
        self.assertEqual(self.fences(), [(_PACKAGE, _SECOND, "frozen")])

    def test_one_fenced_order_fences_beside_a_working_one(self) -> None:
        self.commence_second()
        self.block(order=_SECOND)
        self.assertEqual(self.fences(), [(_PACKAGE, _SECOND, "blocked")])


class FrozenOrderFence(_OrderRun):
    """Rulings 116, 145 and 147: a frozen order fences its sealed footprint until it commences."""

    def setUp(self) -> None:
        super().setUp()
        self.root = Path(self._dir.name)
        (self.root / ".gzkit.json").write_text(
            '{"paths": {"ledger": "ledger.jsonl"}}', encoding="utf-8"
        )

    def freeze_second(self) -> None:
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))

    def _read(self, read: Callable[[], object]) -> object:
        """Run one fence read, asserting it answers and never crashes (RP-12 ruling 156).

        Returns:
            What the read returned.

        """
        held: list[object] = []
        self.assertIsNone(_raised(lambda: held.append(read())))
        return held[0]

    def _fences(self) -> tuple[FencedPackage, ...]:
        return cast("tuple[FencedPackage, ...]", self._read(lambda: fenced_packages(self.root)))

    def _frozen(self, path: str) -> str | None:
        return cast("str | None", self._read(lambda: frozen_order_write_refusal(self.root, path)))

    def _write(self, path: str) -> str | None:
        return cast("str | None", self._read(lambda: work_package_write_refusal(self.root, path)))

    def test_a_frozen_order_fences_its_sealed_footprint(self) -> None:
        """Ruling 116: the footprint sealed at the order's freeze (ruling 56)."""
        self.freeze_second()
        (fence,) = self._fences()
        self.assertEqual(
            (fence.work_package, fence.order, fence.reason, fence.footprint),
            (_PACKAGE, _SECOND, "frozen", ("src/stamp.py",)),
        )

    def test_a_footprint_write_is_refused_and_one_outside_passes(self) -> None:
        """Ruling 116: a write outside the footprint passes; one inside is held."""
        self.freeze_second()
        self.assertIsNotNone(self._write("src/stamp.py"))
        self.assertIsNone(self._write("src/other.py"))

    def test_the_frozen_check_runs_alone_above_the_demotion(self) -> None:
        """Ruling 146: the hook's pre-demotion check reads only a frozen order's footprint."""
        self.freeze_second()
        self.assertIsNotNone(self._frozen("src/stamp.py"))
        self.assertIsNone(self._frozen("src/other.py"))

    def test_the_frozen_check_ignores_a_tree_fence(self) -> None:
        """Ruling 146: every other fence keeps its demotion, ruling 58's included."""
        self.block()
        self.assertIsNotNone(self._write("src/other.py"))
        self.assertIsNone(self._frozen("src/other.py"))

    def test_a_stopped_orders_close_lifts_its_fence(self) -> None:
        """Ruling 58: an order holds the fence only while commenced or accepted, never closed."""
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertEqual([f.reason for f in self._fences() if f.order == _ORDER], ["stopped"])
        self.move("accepted", acceptance_ready=True)
        self.move("closed", **_CLOSE)
        self.assertEqual([f for f in self._fences() if f.order == _ORDER], [])

    def test_commencement_lifts_the_frozen_fence(self) -> None:
        """Ruling 116: the footprint is held only while the order is frozen."""
        self.commence_second()
        self.assertEqual(self._fences(), ())

    def test_tests_stay_open_under_a_frozen_fence(self) -> None:
        """Ruling 145: the fence holds production writes, `src/`, alone."""
        self.freeze_second()
        self.assertIsNone(self._write("tests/test_stamp.py"))

    def test_an_empty_seal_fences_the_whole_tree(self) -> None:
        """Ruling 147: a frozen order whose seal names nothing fails closed."""
        seated = OrderTransitionedEvent(
            event="order_transitioned",
            id=_SECOND,
            order=_SECOND,
            work_package="WP-03-other",
            from_state="opened",
            to_state="frozen",
            evidence="seated",
            modules=(),
        )
        self.ledger.append(ledger_row(seated))
        fence = next(f for f in self._fences() if f.order == _SECOND)
        self.assertIsNone(fence.footprint)
        self.assertIsNotNone(self._frozen("src/anything.py"))

    def test_a_frozen_fence_names_its_order(self) -> None:
        """Ruling 116: the frozen fence is an order's; one with no order is refused."""
        with self.assertRaises(ValueError):
            FencedPackage(work_package=_PACKAGE, reason="frozen")

    def test_the_refusal_names_the_tags_and_the_commencement(self) -> None:
        """Rulings 108 and 116: the recovery is the hang and the commence, not a dispatch."""
        self.freeze_second()
        refusal = self._write("src/stamp.py") or ""
        # output-contract: the next step names the tag log, the hang and the commence
        for named in ("gz wp tag show", "gz wp tag hang", f"gz wp order commence {_SECOND}"):
            self.assertIn(named, refusal)

    def test_the_refusal_says_the_order_is_frozen_and_what_it_holds(self) -> None:
        """Refusal 2 and ruling 147: the why names the freeze, then the footprint or the tree."""
        self.freeze_second()
        footprint = self._write("src/stamp.py") or ""
        self.seat_frozen("WP-03-other", ())
        tree = self._frozen("src/anything.py") or ""
        # output-contract: refusal 2 says why the write is held, before the recovery
        self.assertIn("frozen and not commenced", footprint)
        self.assertIn("its sealed footprint", footprint)
        self.assertIn("the whole tree, its seal empty", tree)

    def test_a_change_order_after_the_seal_widens_what_the_frozen_order_holds(self) -> None:
        """Rulings 56 and 116: the fence reads the seal plus each later change order."""
        self.freeze_second()
        self.assertIsNone(self._frozen("src/extra.py"))
        request = ChangeRequest(
            work_package=_PACKAGE, rung="change_order", approver="operator",
            change="The matcher needs its helper.", superseded="src/stamp.py alone",
            work_stopped=True, modules=("src/extra.py",),
        )  # fmt: skip
        record_work_package_change(self.catalog, self.ledger, request)
        (fence,) = self._fences()
        self.assertEqual(fence.footprint, ("src/stamp.py", "src/extra.py"))
        self.assertIsNotNone(self._frozen("src/extra.py"))

    def test_a_footprint_path_outside_src_stays_open_above_the_demotion(self) -> None:
        """Ruling 145: the pre-demotion check holds production writes alone, a footprint's too."""
        self.seat_frozen("WP-03-other", ("tests/test_stamp.py",))
        self.assertIsNone(self._frozen("tests/test_stamp.py"))
        self.assertIsNone(self._write("tests/test_stamp.py"))

    def test_an_unreadable_ledger_holds_a_production_write_above_the_demotion(self) -> None:
        """Ruling 148: the pre-demotion check fails closed when the fence cannot read."""
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write("{not json\n")
        (fence,) = self._fences()
        self.assertEqual(fence.reason, "unreadable")
        self.assertIsNotNone(self._frozen("src/anything.py"))
        self.assertIsNone(self._frozen("tests/test_anything.py"))

    def seat_frozen(self, package: str, modules: tuple[str, ...]) -> None:
        """Seat a frozen order on a package with the footprint given, past the writer."""
        seated = OrderTransitionedEvent(
            event="order_transitioned", id=_SECOND, order=_SECOND, work_package=package,
            from_state="opened", to_state="frozen", evidence="seated", modules=modules,
        )  # fmt: skip
        self.ledger.append(ledger_row(seated))


class InFlightOnAnOrder(_OrderRun):
    """Every reader of a run in flight reads the order, whose package stays initiated."""

    def open_dispatches(self) -> list[str]:
        held: list[list[str]] = []
        self.assertIsNone(
            _raised(lambda: held.append(open_unclaimed_dispatches(self.ledger, "/here")))
        )
        return held[0]

    def runs(self) -> list[RunPosition]:
        held: list[RunPosition] = []
        self.assertIsNone(_raised(lambda: held.extend(run_positions(self.catalog, self.ledger))))
        return held

    def test_an_unclaimed_order_dispatch_for_another_root_is_open(self) -> None:
        """Ruling 40's guard does not go silent on repair work."""
        event = self.dispatch()
        self.assertEqual(self.open_dispatches(), [event.dispatch_id])

    def test_an_unclaimed_repair_dispatch_on_a_frozen_order_is_open(self) -> None:
        """Ruling 40's guard does not go silent on a Repair dispatch before commencement."""
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        event = self.dispatch("Repair", order=_SECOND, req=None)
        self.assertEqual(self.open_dispatches(), [event.dispatch_id])

    def test_it_stays_open_while_the_order_is_accepted(self) -> None:
        event = self.dispatch()
        self.move("accepted", **_PAYLOADS["accepted"])
        self.assertEqual(self.open_dispatches(), [event.dispatch_id])

    def test_a_dispatch_of_a_closed_order_is_not_open(self) -> None:
        """Ruling 40's guard reads runs in flight; a closed order's run is over."""
        self.dispatch()
        self.move("accepted", **_PAYLOADS["accepted"])
        self.move("closed", decision="terminate", attestor="g0", attestation_text="stop")
        self.assertEqual(self.open_dispatches(), [])

    def test_a_voided_order_dispatch_is_not_open(self) -> None:
        event = self.dispatch()
        record_dispatch_void(self.ledger, _PACKAGE, str(event.dispatch_id), "never spawned")
        self.assertEqual(self.open_dispatches(), [])

    def test_the_runs_in_flight_include_the_commenced_order(self) -> None:
        self.dispatch()
        self.block()
        [run] = self.runs()
        self.assertEqual(
            (run.work_package, run.order, run.kind, run.state, run.blocked, run.subject),
            (_PACKAGE, _ORDER, "repair", "commenced", True, "REQ-1@1"),
        )
        self.assertEqual(run.event, "work_package_blocked")

    def test_a_commenced_order_with_no_dispatch_is_in_flight_with_no_subject(self) -> None:
        self.assertEqual([(run.order, run.subject) for run in self.runs()], [(_ORDER, None)])

    def test_an_order_not_commenced_is_not_in_flight(self) -> None:
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        self.assertEqual([run.order for run in self.runs()], [_ORDER])

    def test_a_frozen_order_holding_a_live_dispatch_is_in_flight(self) -> None:
        """Ruling 136: the run view reads a frozen order's dispatch as ruling 134's guard does."""
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        self.dispatch("Repair", order=_SECOND, req=None)
        frozen = [run for run in self.runs() if run.order == _SECOND]
        self.assertEqual(
            [(run.state, run.subject, run.event) for run in frozen],
            [("frozen", _SECOND, "work_package_dispatched")],
        )

    def test_a_frozen_order_whose_dispatch_is_voided_is_not_in_flight(self) -> None:
        """Ruling 136: a voided dispatch is no dispatch (ruling 42), so the order reads unrun."""
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        event = self.dispatch("Repair", order=_SECOND, req=None)
        record_dispatch_void(self.ledger, _PACKAGE, str(event.dispatch_id), "never spawned")
        self.assertEqual([run.order for run in self.runs()], [_ORDER])


class OrderFenceRecovery(unittest.TestCase):
    """The refusal names the order and the step that lifts it (ruling 58)."""

    def refusals(self, reason: str) -> tuple[str, str]:
        fence = FencedPackage.model_validate(
            {"work_package": _PACKAGE, "order": _ORDER, "reason": reason}
        )
        return (
            work_package_write_message(fence, "src/gzkit/x.py"),
            work_package_commit_message(fence, ["src/gzkit/x.py"]),
        )

    def test_an_unreadable_ledger_says_no_state_can_be_shown(self) -> None:
        """The fence an unreadable ledger raises names that cause, never a package's state."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".gzkit.json").write_text("{", encoding="utf-8")
            fences: list[FencedPackage] = []
            self.assertIsNone(_raised(lambda: fences.extend(fenced_packages(Path(tmp)))))
        fence = FencedPackage(work_package="the ledger", reason="unreadable")
        self.assertEqual(fences, [fence])
        messages: list[str] = []
        self.assertIsNone(
            _raised(
                lambda: messages.extend(
                    (
                        work_package_write_message(fence, "src/gzkit/x.py"),
                        work_package_commit_message(fence, ["src/gzkit/x.py"]),
                    )
                )
            )
        )
        self.assertEqual(len(messages), 2)
        for message in messages:
            self.assertIn("cannot be read", message)

    def test_each_reason_names_the_order(self) -> None:
        for reason in ("blocked", "accepted", "stopped"):
            for message in self.refusals(reason):
                with self.subTest(reason=reason):
                    self.assertIn(f"order {_ORDER}", message)

    def test_the_why_names_the_order_or_the_package_fenced(self) -> None:
        # output-contract: the fence message's why part, RP-12 ruling 101
        order = FencedPackage(work_package=_PACKAGE, order=_ORDER, reason="blocked")
        package = FencedPackage(work_package=_PACKAGE, reason="blocked")
        for fence, why in (
            (
                order,
                (
                    f"order {_ORDER} of work package {_PACKAGE} is blocked, and `gz wp dispatch "
                    "--order` refuses implementing work on it, so a write here would step "
                    "around that refusal (RP-12 ruling 58)"
                ),
            ),
            (
                package,
                (
                    f"work package {_PACKAGE} is blocked, and `gz wp dispatch` refuses "
                    "implementing work on it, so a write here would step around that refusal"
                ),
            ),
        ):
            with self.subTest(order=fence.order):
                message = " ".join(work_package_write_message(fence, "src/gzkit/x.py").split())
                self.assertIn(why, message)

    def test_a_blocked_order_names_the_unblock_on_the_order(self) -> None:
        for message in self.refusals("blocked"):
            self.assertIn(f"gz wp unblock {_PACKAGE} --order {_ORDER} --ruling", message)

    def test_a_stopped_order_names_the_orders_accept(self) -> None:
        for message in self.refusals("stopped"):
            self.assertIn(f"gz wp order accept {_ORDER} --evidence", message)

    def test_an_accepted_or_stopped_order_names_gate_5_at_the_order(self) -> None:
        """Gate 5 at the order lifts the fence (rulings 58, 73): the refusal names it."""
        for reason in ("accepted", "stopped"):
            for message in self.refusals(reason):
                with self.subTest(reason=reason):
                    self.assertIn(f"gz wp order close {_ORDER} --decision", message)
                    self.assertNotIn("nothing lifts this fence", message)

    def test_an_accepted_or_stopped_orders_recovery_is_not_the_packages(self) -> None:
        for reason in ("accepted", "stopped"):
            for message in self.refusals(reason):
                with self.subTest(reason=reason):
                    self.assertNotIn(f"gz wp close {_PACKAGE}", message)
                    self.assertNotIn(f"gz wp accept {_PACKAGE}", message)


if __name__ == "__main__":
    unittest.main()
