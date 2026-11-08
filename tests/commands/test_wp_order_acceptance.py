"""Acceptance on an order and ``gz wp order accept``: RP-12 O2 task 3, act 4.

`docs/governance/harbor-ro12-contractor-kit.md` § Ruling 60: `gz wp order accept`
refuses until the acceptance runtime reads the order ready. The order's
obligations are its frozen REQs at their frozen revisions, its proofs and reviews
are recorded under the order's id, a stopped order is excused, and the footprint
check reads the package's sealed footprint. The review-round limit of GHI #1028
holds the order as it holds a package. A refusal exits 3 and books nothing.
"""

import json
import os
import unittest
import uuid
from pathlib import Path
from unittest import mock

from gzkit.acceptance import Proof
from gzkit.acceptance_execution import canonical_obligations, input_digest
from gzkit.acceptance_store import (
    acceptance_status,
    load_history,
    record_proof,
    record_review,
    resolve_brief,
    round_bound_refusal,
)
from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV
from tests.commands.test_wp_acceptance import _receipt
from tests.commands.test_wp_order_run import _ORDER, _PACKAGE, _CommencedOrder

_FOOTPRINT = "gzkit.commands.wp_order.footprint_refusal"
#: The readiness an `accepted` move books (ruling 84), compared by identity.
_READY, _NOT_READY = True, False


class _OrderAcceptance(_CommencedOrder):
    def setUp(self) -> None:
        super().setUp()
        self.root = Path.cwd()

    def init(self) -> None:
        self.wp("acceptance", _ORDER, "init", "--author", "implementing-session")

    def proof(self) -> Proof:
        source = resolve_brief(self.root, _ORDER)
        held = {item.id: item for item in canonical_obligations(self.root, source)}
        proof = Proof(
            id=f"proof-{uuid.uuid4().hex}",
            obligation_id="REQ-1",
            contract_digest=held["REQ-1"].contract_digest,
            input_digest=input_digest(self.root, source),
            selectors=("tests.test_x.Case.test_y",),
            evidence='{"fixture":"synthetic"}',
            valid=True,
        )
        record_proof(self.root, _ORDER, proof)
        return proof

    def review(self, proof: Proof, stage: str = "adversarial", verdict: str = "refuted") -> None:
        record_review(self.root, _ORDER, _receipt(proof, stage, verdict=verdict))

    def approve(self, proof: Proof) -> None:
        for stage in ("spec", "quality", "adversarial"):
            self.review(proof, stage, "accepted")

    def accept(self, code: int = 0) -> str:
        return self.wp("order", "accept", _ORDER, "--evidence", "final inspection", code=code)

    def state(self) -> str | None:
        moves = [row for row in self.rows("order_transitioned") if row["order"] == _ORDER]
        return moves[-1]["to_state"] if moves else None


class TestTheOrdersContract(_OrderAcceptance):
    def test_the_order_owes_its_frozen_reqs_alone(self) -> None:
        self.wp(
            "req", "new", _PACKAGE, "--statement", "The matcher holds.", "--criterion",
            "a match|ok|a test", "--kind", "BEHAVIOR", "--problem-report", "1301",
        )  # fmt: skip
        obligations = canonical_obligations(self.root, resolve_brief(self.root, _ORDER))
        self.assertEqual([(item.id, item.kind) for item in obligations], [("REQ-1", "BEHAVIOR")])
        self.assertIn("The stamp imports again.", obligations[0].statement)

    def test_the_records_are_kept_under_the_orders_id(self) -> None:
        self.init()
        self.assertIsNotNone(load_history(self.root, _ORDER).contract)
        self.assertEqual({row["id"] for row in self.rows("acceptance_recorded")}, {_ORDER})

    def test_acceptance_starts_only_on_a_commenced_order(self) -> None:
        self.new("matcher")
        output = self.wp("acceptance", "ORD-02-matcher", "init", "--author", "a", code=3)
        self.assertIn("not commenced", output)

    def test_a_req_moved_past_its_frozen_revision_is_refused(self) -> None:
        store = Path("data") / "catalog" / "reqs.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["reqs"][0]["revision"] = 2
        store.write_text(json.dumps(held), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "no longer at the frozen revision 1"):
            resolve_brief(self.root, _ORDER)

    def test_a_repair_package_id_runs_no_acceptance_of_its_own(self) -> None:
        """RP-12 rulings 44 and 64: a repair package's acceptance runs on its orders."""
        with self.assertRaisesRegex(ValueError, "gz wp acceptance <ORD-id>"):
            resolve_brief(self.root, _PACKAGE)

    def test_an_order_the_store_lacks_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "ORD-09-ghost"):
            resolve_brief(self.root, "ORD-09-ghost")


class TestTheOrdersGate(_OrderAcceptance):
    def test_accept_refuses_an_order_with_no_acceptance_and_books_nothing(self) -> None:
        self.assertIn(f"gz wp acceptance {_ORDER} status", self.accept(code=3))
        self.assertEqual(self.state(), "commenced")

    def test_a_finding_refuses_an_order_every_channel_approved(self) -> None:
        self.init()
        proof = self.proof()
        self.approve(proof)
        self.assertTrue(acceptance_status(self.root, _ORDER).ready)
        self.review(proof)
        self.accept(code=3)
        self.assertEqual(self.state(), "commenced")

    def test_accept_admits_a_ready_order(self) -> None:
        self.init()
        self.approve(self.proof())
        with mock.patch(_FOOTPRINT, return_value=None) as footprint:
            payload = json.loads(
                self.wp("order", "accept", _ORDER, "--evidence", "final inspection", "--json")
            )
        self.assertEqual((payload["order"], payload["to_state"]), (_ORDER, "accepted"))
        self.assertEqual(footprint.call_args.args[1].id, _PACKAGE)

    def test_the_sealed_footprint_holds_a_ready_order(self) -> None:
        self.init()
        self.approve(self.proof())
        with mock.patch(_FOOTPRINT, return_value="1 changed file outside the footprint"):
            self.assertIn("outside the footprint", self.accept(code=3))
        self.assertEqual(self.state(), "commenced")

    def test_a_terminated_order_is_accepted_with_no_proof(self) -> None:
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self.wp("dispatch", _PACKAGE, "--order", _ORDER, "--role", role, "--model", "m",
                    "--req", "REQ-1")  # fmt: skip
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator", "g0",
                "--exit", "terminate")  # fmt: skip
        with mock.patch(_FOOTPRINT, return_value="outside"):
            self.accept()
        # Ruling 84: excused, yet its readiness is read and booked: no proof, not ready.
        self.assertEqual(self.state(), "accepted")
        self.assertIs(self.rows("order_transitioned")[-1]["acceptance_ready"], _NOT_READY)


class TestTheOrdersRoundBound(_OrderAcceptance):
    def refute(self, rounds: int) -> None:
        self.init()
        proof = self.proof()
        for _ in range(rounds):
            self.review(proof)

    def test_three_rounds_stop_dispatch_and_accept_and_name_the_orders_block(self) -> None:
        self.refute(3)
        for output in (self.dispatch(code=3), self.accept(code=3)):
            self.assertIn(f"gz wp block {_PACKAGE} --order {_ORDER}", output)

    def test_two_rounds_leave_the_orders_dispatch_open(self) -> None:
        self.refute(2)
        self.dispatch()
        self.assertIsNone(round_bound_refusal(self.root, _ORDER))

    def test_the_orders_unblock_restarts_the_count(self) -> None:
        self.refute(3)
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "go", "--operator", "g0")
        self.dispatch()

    def test_the_orders_block_writes_the_orders_refutations(self) -> None:
        self.refute(1)
        payload = json.loads(
            self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n",
                    "--json")
        )  # fmt: skip
        self.assertEqual(payload["refutations"], {"REQ-1@1": 1})


class TestTheOrdersDeparture(_OrderAcceptance):
    """A departure exit on the order moves its REQ out of the order's acceptance."""

    def setUp(self) -> None:
        super().setUp()
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["work_packages"][0]["departures"] = [
            {"id": f"DFS-{n}", "description": "The claim is bounded.", "form": "waiver",
             "duration": "permanent", "clear_by": None, "req": req}
            for n, req in ((1, "REQ-1"), (3, "REQ-3"))
        ]  # fmt: skip
        store.write_text(json.dumps(held), encoding="utf-8")
        for statement in ("The matcher holds.", "The matcher's edge holds."):
            self.wp(
                "req", "new", _PACKAGE, "--statement", statement, "--criterion",
                "a match|ok|a test", "--kind", "BEHAVIOR", "--problem-report", "1301",
            )  # fmt: skip
        self.new("matcher")
        self.gz(
            "freeze", "ORD-02-matcher", "--baseline", "REQ-2@1", "--baseline", "REQ-3@1",
            "--risk-note", "Touches the matcher.", "--review-receipt", "v", "--evidence", "E",
        )  # fmt: skip
        self.gz("commence", "ORD-02-matcher", "--evidence", "tags")

    def depart(self, order: str, req: str, item: str) -> None:
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self.wp("dispatch", _PACKAGE, "--order", order, "--role", role, "--model", "m",
                    "--req", req)  # fmt: skip
        self.wp("block", _PACKAGE, "--order", order, "--reason", "r", "--next-action", "n")
        self.wp("change", _PACKAGE, "--rung", "departure", "--approver", "operator",
                "--change", "bounded", "--item", item)  # fmt: skip
        self.wp("unblock", _PACKAGE, "--order", order, "--ruling", "depart", "--operator", "g0",
                "--exit", "departure", "--req", req)  # fmt: skip

    def test_a_departed_req_leaves_the_orders_obligations_and_roster(self) -> None:
        order = "ORD-02-matcher"
        self.wp("acceptance", order, "init", "--author", "implementing-session")
        source = resolve_brief(self.root, order)
        held = {item.id: item for item in canonical_obligations(self.root, source)}
        record_proof(
            self.root,
            order,
            Proof(
                id=f"proof-{uuid.uuid4().hex}", obligation_id="REQ-3",
                contract_digest=held["REQ-3"].contract_digest,
                input_digest=input_digest(self.root, source),
                selectors=("tests.test_x.Case.test_y",), evidence="{}", valid=True,
            ),
        )  # fmt: skip
        self.depart(order, "REQ-3", "DFS-3")
        self.assertEqual(load_history(self.root, order).proofs, [])
        obligations = canonical_obligations(self.root, resolve_brief(self.root, order))
        self.assertEqual([item.id for item in obligations], ["REQ-2"])
        self.wp("acceptance", order, "init", "--author", "implementing-session")
        blockers = " ".join(acceptance_status(self.root, order).blockers)
        self.assertNotIn("roster changed", blockers)

    def test_an_order_whose_every_req_departed_owes_nothing_to_accept(self) -> None:
        self.depart(_ORDER, "REQ-1", "DFS-1")
        with self.assertRaisesRegex(ValueError, "holds no acceptance obligation"):
            resolve_brief(self.root, _ORDER)


class TestTheOrdersHumanReview(_OrderAcceptance):
    def human_review(self, code: int = 0) -> str:
        return self.wp("acceptance", _ORDER, "human-review", "--attestor", "g0", "--ruling",
                       "as it stands", code=code)  # fmt: skip

    def test_the_operators_review_is_recorded_on_the_order(self) -> None:
        self.init()
        self.proof()
        self.human_review()
        records = [
            r for r in self.rows("acceptance_recorded") if r["record_type"] == "human-review"
        ]
        self.assertEqual([r["id"] for r in records], [_ORDER])

    def test_a_human_review_past_the_orders_limit_is_refused(self) -> None:
        self.init()
        proof = self.proof()
        for _ in range(3):
            self.review(proof)
        self.assertIn(f"gz wp block {_PACKAGE} --order {_ORDER}", self.human_review(code=3))


class TestTheOrdersAcceptRefusal(_OrderAcceptance):
    def test_a_stopped_order_blocked_again_names_the_accept_to_rerun(self) -> None:
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self.wp("dispatch", _PACKAGE, "--order", _ORDER, "--role", role, "--model", "m",
                    "--req", "REQ-1")  # fmt: skip
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator", "g0",
                "--exit", "terminate")  # fmt: skip
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        output = self.accept(code=3)
        self.assertIn("re-run `uv run gz wp order accept <ORD-id> --evidence <text>`", output)
        self.assertEqual(self.state(), "commenced")

    def test_a_blocked_order_is_refused_for_its_block_before_its_readiness(self) -> None:
        """Ruling 59: a blocked order does not move, so its accept names the block."""
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        output = self.accept(code=3)
        self.assertIn("blocked on the operator", output)
        self.assertNotIn(f"gz wp acceptance {_ORDER} status", output)
        self.assertEqual(self.state(), "commenced")

    def test_an_order_not_commenced_is_refused_for_its_lifecycle_first(self) -> None:
        self.new("matcher")
        output = self.wp("order", "accept", "ORD-02-matcher", "--evidence", "e", code=3)
        self.assertIn("cannot move from opened", output)

    def test_a_commenced_order_is_refused_a_freeze_for_its_lifecycle_first(self) -> None:
        with mock.patch("gzkit.commands.wp_order.freeze_refusal", return_value="Unsealed.") as fp:
            output = self.gz(
                "freeze", _ORDER, "--baseline", "REQ-1@1", "--risk-note", "r",
                "--review-receipt", "v", "--evidence", "E", code=3,
            )  # fmt: skip
        fp.assert_not_called()
        self.assertIn("cannot move from commenced", " ".join(output.split()))


class TestAStoppedOrdersGateFive(_OrderAcceptance):
    """A stopped order accepted without its proof delivered nothing to proceed with."""

    def test_proceed_is_refused_and_the_other_decisions_close_it(self) -> None:
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self.wp("dispatch", _PACKAGE, "--order", _ORDER, "--role", role, "--model", "m",
                    "--req", "REQ-1")  # fmt: skip
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator", "g0",
                "--exit", "terminate")  # fmt: skip
        self.accept()
        words = ("--attestor", "g0", "--attestation-text", "ruled", "--evidence", "gate 5")
        output = self.wp("order", "close", _ORDER, "--decision", "proceed", *words,
                         "--residual-risk", "none", code=3)  # fmt: skip
        self.assertIn("delivered nothing to proceed with", output)
        self.assertEqual(self.state(), "accepted")
        self.wp("order", "close", _ORDER, "--decision", "terminate", *words)
        self.assertEqual(self.state(), "closed")

    def test_a_stopped_order_whose_acceptance_reads_ready_may_proceed(self) -> None:
        """Ruling 80: the verb hands the writer acceptance readiness, so a proof earns it."""
        self.init()
        self.approve(self.proof())
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator", "g0",
                "--exit", "terminate")  # fmt: skip
        with mock.patch(_FOOTPRINT, return_value=None):
            self.accept()
        self.assertIs(self.rows("order_transitioned")[-1]["acceptance_ready"], _READY)
        self.wp("order", "close", _ORDER, "--decision", "proceed", "--attestor", "g0",
                "--attestation-text", "it holds", "--residual-risk", "none",
                "--evidence", "gate 5")  # fmt: skip
        self.assertEqual(self.state(), "closed")

    def test_a_stopped_order_outside_its_footprint_books_not_ready(self) -> None:
        """Ruling 84: a stopped order's footprint is read, though it is excused."""
        self.init()
        self.approve(self.proof())
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator", "g0",
                "--exit", "terminate")  # fmt: skip
        with mock.patch(_FOOTPRINT, return_value="outside"):
            self.accept()
        self.assertEqual(self.state(), "accepted")
        self.assertIs(self.rows("order_transitioned")[-1]["acceptance_ready"], _NOT_READY)

    def test_readiness_earned_after_acceptance_earns_no_proceed(self) -> None:
        """Ruling 84: Gate 5 reads the readiness booked at acceptance, not a later one."""
        self.init()
        self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
        self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator", "g0",
                "--exit", "terminate")  # fmt: skip
        with mock.patch(_FOOTPRINT, return_value=None):
            self.accept()
        self.approve(self.proof())
        self.assertTrue(acceptance_status(self.root, _ORDER).ready)
        output = self.wp("order", "close", _ORDER, "--decision", "proceed", "--attestor", "g0",
                         "--attestation-text", "it holds", "--residual-risk", "none",
                         "--evidence", "gate 5", code=3)  # fmt: skip
        self.assertIn("80 and 84", " ".join(output.split()))
        self.assertEqual(self.state(), "accepted")

    def test_a_stopped_order_past_its_round_bound_books_not_ready(self) -> None:
        """Ruling 84: the full readiness, the review-round bound included, is booked."""
        self.init()
        proof = self.proof()
        self.approve(proof)
        with mock.patch("gzkit.commands.wp_order.round_bound_refusal", return_value="three rounds"):
            self.wp("block", _PACKAGE, "--order", _ORDER, "--reason", "r", "--next-action", "n")
            self.wp("unblock", _PACKAGE, "--order", _ORDER, "--ruling", "stop", "--operator",
                    "g0", "--exit", "terminate")  # fmt: skip
            with mock.patch(_FOOTPRINT, return_value=None):
                self.accept()
        self.assertIs(self.rows("order_transitioned")[-1]["acceptance_ready"], _NOT_READY)


class TestTheOrdersGateFive(_OrderAcceptance):
    """`gz wp order close`: Gate 5 at the order (RP-12 rulings 73 to 77)."""

    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.approve(self.proof())
        with mock.patch(_FOOTPRINT, return_value=None):
            self.accept()

    def close(self, *extra: str, code: int = 0) -> str:
        words = ("--attestor", "g0", "--attestation-text", "the import holds")
        return self.wp("order", "close", _ORDER, *words, "--evidence", "gate 5", *extra, code=code)

    def test_proceed_books_gate_5_on_the_operators_words(self) -> None:
        payload = json.loads(
            self.close("--decision", "proceed", "--residual-risk", "none", "--json")
        )
        self.assertEqual(
            (payload["to_state"], payload["decision"], payload["attestation_text"]),
            ("closed", "proceed", "the import holds"),
        )
        self.assertEqual(self.state(), "closed")
        # output-contract: show's text form names the REQs a proceed holds (ruling 78)
        self.assertIn("  holds: REQ-1@1", self.wp("order", "show", _ORDER).splitlines())
        shown = json.loads(self.wp("order", "show", _ORDER, "--json"))
        self.assertEqual(shown["holds"], {"REQ-1": 1})

    def test_a_subagents_call_is_refused_and_books_nothing(self) -> None:
        """Ruling 77: Gate 5 is the operator's act."""
        stamp = {STAMP_ROOT_ENV: Path.cwd().resolve().as_posix(), STAMP_ID_ENV: ""}
        with mock.patch.dict(os.environ, stamp):
            output = self.close("--decision", "proceed", "--residual-risk", "none", code=3)
        self.assertIn("ruling 77", output)
        self.assertEqual(self.state(), "accepted")

    def test_a_refused_close_names_the_call_to_rerun(self) -> None:
        output = self.close("--decision", "proceed", code=3)
        self.assertIn("residual-risk (RP-12 ruling 73)", output)
        self.assertIn("re-run `uv run gz wp order close <ORD-id>", output)
        self.assertEqual(self.state(), "accepted")


if __name__ == "__main__":
    unittest.main()
