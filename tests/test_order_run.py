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

import unittest
from pathlib import Path

from gzkit.events import BaselinedReq
from gzkit.order_ledger import (
    OrderMove,
    is_order_blocked,
    order_state,
    order_took_stopping_exit,
    record_order_transition,
)
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.work_package_fence import (
    FencedPackage,
    fenced_packages,
    work_package_commit_message,
    work_package_write_message,
)
from gzkit.work_package_ledger import (
    TransitionRequest,
    is_blocked,
    record_work_package_transition,
)
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    UnblockRequest,
    open_unclaimed_dispatches,
    record_dispatch_void,
    record_work_package_block,
    record_work_package_dispatch,
    record_work_package_unblock,
    run_positions,
    took_stopping_exit,
)
from tests.test_order_ledger import _FREEZE, _PAYLOADS, _OrderCase, _rows

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

    def refused(self, pattern: str, act) -> None:
        before = _rows(self.path)
        with self.assertRaisesRegex(ValueError, pattern):
            act()
        self.assertEqual(_rows(self.path), before)

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
        self.move("accepted")
        self.refused("not commenced", self.dispatch)

    def test_an_order_of_another_package_is_refused(self) -> None:
        self.refused("ORD-03-other", lambda: self.dispatch(order="ORD-03-other"))

    def test_an_order_the_store_lacks_is_refused(self) -> None:
        self.refused("ORD-09-ghost", lambda: self.dispatch(order="ORD-09-ghost"))

    def test_the_fix_cycle_bound_counts_against_the_orders_subject(self) -> None:
        self.reach_the_bound()
        self.refused("bound", self.dispatch)

    def test_an_order_whose_package_closed_takes_no_dispatch(self) -> None:
        """Rulings 44 and 76: the package closes once its orders have, and none works on."""
        self.move("accepted")
        self.move("closed", decision="terminate", attestor="g0", attestation_text="stop")
        close = TransitionRequest(
            work_package=_PACKAGE, to_state="closed", evidence="e", attestor="g0",
            residual_risk="none",
        )  # fmt: skip
        record_work_package_transition(self.catalog, self.ledger, close)
        self.refused("initiated", self.dispatch)

    def test_a_dispatch_on_the_repair_package_names_its_order(self) -> None:
        self.refused("--order", lambda: self.dispatch(order=None))


class BlockOnAnOrder(_OrderRun):
    """Ruling 59: `gz wp block --order` holds that order alone."""

    def test_the_block_holds_the_order_and_not_its_package(self) -> None:
        event = self.block()
        self.assertEqual((event.id, event.work_package, event.order), (_ORDER, _PACKAGE, _ORDER))
        self.assertTrue(is_order_blocked(self.ledger, _ORDER))
        self.assertFalse(is_blocked(self.ledger, _PACKAGE))

    def test_a_blocked_order_takes_no_dispatch(self) -> None:
        self.block()
        self.refused("blocked", self.dispatch)

    def test_a_blocked_order_does_not_move(self) -> None:
        self.block()
        self.refused("blocked", lambda: self.move("accepted"))

    def test_the_packages_other_orders_are_still_dispatched_and_moved(self) -> None:
        self.commence_second()
        self.block()
        self.assertEqual(self.dispatch(order=_SECOND, req="REQ-2").order, _SECOND)
        self.move("accepted", order=_SECOND)
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
        self.unblock(exit_taken="reopen", req="REQ-1")
        self.assertEqual(self.block().reopened, ("REQ-1",))

    def test_a_second_block_while_the_order_is_blocked_is_refused(self) -> None:
        self.block()
        self.refused("already blocked", self.block)

    def test_an_accepted_order_takes_no_block(self) -> None:
        """RP-12 ruling 69: final inspection is done; Gate 5's outcomes remain."""
        self.move("accepted")
        self.refused("accepted", self.block)

    def test_an_order_not_opened_or_of_another_package_takes_no_block(self) -> None:
        for order in ("ORD-02-matcher", "ORD-03-other", "ORD-09-ghost"):
            with self.subTest(order=order):
                self.refused(order, lambda order=order: self.block(order=order))


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
        self.assertFalse(took_stopping_exit(self.ledger, _PACKAGE))
        self.refused("terminate exit", self.dispatch)
        self.assertEqual(self.dispatch(order=_SECOND, req="REQ-2").order, _SECOND)

    def test_a_stopped_order_never_ready_does_not_close_as_proceed(self) -> None:
        """Ruling 80: the writer holds it, reading readiness through its parameter."""
        self.block()
        self.unblock(exit_taken="terminate")
        self.move("accepted")
        proceed = OrderMove(
            order=_ORDER, to_state="closed", evidence="e", decision="proceed", attestor="g0",
            attestation_text="it holds", residual_risk="none",
        )  # fmt: skip
        for ready in (None, lambda _order: False):
            with self.subTest(ready=ready):
                self.refused(
                    "rulings 78 and 80",
                    lambda ready=ready: record_order_transition(
                        self.catalog, self.ledger, proceed, acceptance_ready=ready
                    ),
                )
        event = record_order_transition(
            self.catalog, self.ledger, proceed, acceptance_ready=lambda _order: True
        )
        self.assertEqual(event.decision, "proceed")

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
        self.move("accepted")
        self.assertEqual(self.fences(), [(_PACKAGE, _ORDER, "accepted")])

    def test_an_order_stopped_by_an_exit_fences(self) -> None:
        self.reach_the_bound()
        self.block()
        self.unblock(exit_taken="terminate")
        self.assertEqual(self.fences(), [(_PACKAGE, _ORDER, "stopped")])

    def test_an_order_not_yet_commenced_does_not_fence_even_blocked(self) -> None:
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        self.block(order=_SECOND)
        self.assertEqual(self.fences(), [])

    def test_one_fenced_order_fences_beside_a_working_one(self) -> None:
        self.commence_second()
        self.block(order=_SECOND)
        self.assertEqual(self.fences(), [(_PACKAGE, _SECOND, "blocked")])


class InFlightOnAnOrder(_OrderRun):
    """Every reader of a run in flight reads the order, whose package stays initiated."""

    def test_an_unclaimed_order_dispatch_for_another_root_is_open(self) -> None:
        """Ruling 40's guard does not go silent on repair work."""
        event = self.dispatch()
        self.assertEqual(open_unclaimed_dispatches(self.ledger, "/here"), [event.dispatch_id])

    def test_it_stays_open_while_the_order_is_accepted(self) -> None:
        event = self.dispatch()
        self.move("accepted")
        self.assertEqual(open_unclaimed_dispatches(self.ledger, "/here"), [event.dispatch_id])

    def test_a_voided_order_dispatch_is_not_open(self) -> None:
        event = self.dispatch()
        record_dispatch_void(self.ledger, _PACKAGE, str(event.dispatch_id), "never spawned")
        self.assertEqual(open_unclaimed_dispatches(self.ledger, "/here"), [])

    def test_the_runs_in_flight_include_the_commenced_order(self) -> None:
        self.dispatch()
        self.block()
        [run] = run_positions(self.catalog, self.ledger)
        self.assertEqual(
            (run.work_package, run.order, run.kind, run.state, run.blocked, run.subject),
            (_PACKAGE, _ORDER, "repair", "commenced", True, "REQ-1@1"),
        )
        self.assertEqual(run.event, "work_package_blocked")

    def test_an_order_not_commenced_is_not_in_flight(self) -> None:
        self.walk_to("frozen", order=_SECOND, baseline=(BaselinedReq(req="REQ-2", revision=1),))
        self.assertEqual([run.order for run in run_positions(self.catalog, self.ledger)], [_ORDER])


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

    def test_each_reason_names_the_order(self) -> None:
        for reason in ("blocked", "accepted", "stopped"):
            for message in self.refusals(reason):
                with self.subTest(reason=reason):
                    self.assertIn(f"order {_ORDER}", message)

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
