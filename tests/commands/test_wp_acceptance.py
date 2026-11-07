"""Acceptance on a work package (RO-14 act 5, GHI #1028).

Ruling 4 makes acceptance one runtime, so these read the seam and what the seam
adds: a package supplies the contract a brief supplies, `gz wp accept` refuses until
the reducer reads ready, three refuted adversarial rounds stop for the operator, and
`gz wp block` writes the refutations itself. The reducer's own behaviour stays
proven by `tests/test_acceptance*.py`.
"""

import json
import unittest
import uuid
from pathlib import Path
from unittest import mock

from gzkit.acceptance import Proof
from gzkit.acceptance_execution import canonical_obligations, input_digest, prove
from gzkit.acceptance_package import PackageContract, binds_by_mutation
from gzkit.acceptance_store import (
    REVIEW_SCHEMA,
    acceptance_status,
    load_history,
    record_human_review,
    record_proof,
    record_review,
    refutation_counts,
    refuted_rounds,
    resolve_brief,
    review_round_limit,
    round_bound_refusal,
)
from gzkit.arb.paths import receipts_root
from gzkit.cli import main
from gzkit.mutation_witness import Mutation
from gzkit.work_package_fence import fenced_packages
from tests.commands.common import CliRunner, _quick_init
from tests.test_acceptance_execution import SELECTOR, ExecutionFixture

_PACKAGE = "WP-01-loop"
_REQ = "REQ-7"


def _record(package: str, *, kind: str = "delivery") -> dict[str, object]:
    delivery = kind == "delivery"
    return {
        "id": package,
        "kind": kind,
        "outcome": "H1.1" if delivery else None,
        "issues": [] if delivery else [1206],
        "lane": None if delivery else "lite",
        "aliases": [],
        "modules": [] if delivery else ["data/catalog/"],
        "initial_conditions": "NA",
        "procedure": "NA",
        "test_and_inspection": "The closing test.",
        "system_restoration": "NA",
        "oqe": [],
        "alterations": [],
        "departures": [],
    }


def _seed(packages: list[dict[str, object]], reqs: list[dict[str, object]]) -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    outcome = {
        "code": "H1.1",
        "statement": "s",
        "owner": "o",
        "user_facing": False,
        "governed_by": [],
        "depends_on": [],
        "feature": None,
        "retired": False,
    }
    for kind, entries in (
        ("families", []),
        ("outcomes", [outcome] if reqs else []),
        ("reqs", reqs),
        ("externals", []),
        ("work_packages", packages),
        ("orders", []),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


def _req(revision: int = 2) -> dict[str, object]:
    return {
        "id": _REQ,
        "specialization": "catalog",
        "member_of": "H1.1",
        "statement": "The package carries its frozen requirement.",
        "criteria": [{"state_or_input": "i", "required_outcome": "o", "evidence": "e"}],
        "kind": "BEHAVIOR",
        "revision": revision,
        "derives_from": [],
        "applies_to": [],
    }


def _receipt(
    proof: Proof, stage: str, *, verdict: str = "accepted", observed: bool = False
) -> dict[str, object]:
    refuted = verdict == "refuted"
    finding = {
        "id": f"finding-{uuid.uuid4().hex}",
        "obligation_id": proof.obligation_id,
        "kind": "counterexample",
        "description": "A concrete violation.",
    }
    review = {
        "schema": REVIEW_SCHEMA,
        "stage": stage,
        "input_digest": proof.input_digest,
        "obligation_ids": [proof.obligation_id],
        "proof_ids": [proof.id],
        "accepted_proof_ids": [] if refuted else [proof.id],
        "findings": [finding] if refuted or observed else [],
        "closures": [],
        "reviewer_id": "independent-session",
        "verdict": verdict,
    }
    return {
        "schema": "gzkit.arb.step_receipt.v1",
        "exit_status": 0,
        "run_id": f"arb-step-review-{uuid.uuid4().hex}",
        "step": {"command": ["node", "codex-companion.mjs", "adversarial-review"]},
        "stdout_tail": "```json\n" + json.dumps(review) + "\n```",
        "stderr_tail": "",
    }


class _PackageCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed([_record(_PACKAGE)], [_req()])
        self.root = Path.cwd()

    def _wp(self, *args: str) -> str:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return result.output

    def _refused(self, *args: str) -> str:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertNotEqual(result.exit_code, 0, msg=result.output)
        return result.output

    def _commence(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp(
            "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2",
        )  # fmt: skip
        self._wp("commence", _PACKAGE, "--evidence", "e")

    def _init(self) -> None:
        self._commence()
        self._wp("acceptance", _PACKAGE, "init", "--author", "implementing-session")

    def _proof(self, obligation: str = _REQ) -> Proof:
        source = resolve_brief(self.root, _PACKAGE)
        held = {item.id: item for item in canonical_obligations(self.root, source)}
        proof = Proof(
            id=f"proof-{uuid.uuid4().hex}",
            obligation_id=obligation,
            contract_digest=held[obligation].contract_digest,
            input_digest=input_digest(self.root, source),
            selectors=("tests.test_x.Case.test_y",),
            evidence='{"fixture":"synthetic"}',
            valid=True,
        )
        record_proof(self.root, _PACKAGE, proof)
        return proof

    def _review(self, proof: Proof, stage: str = "adversarial", verdict: str = "refuted") -> None:
        record_review(self.root, _PACKAGE, _receipt(proof, stage, verdict=verdict))

    def _approve(self, proof: Proof) -> None:
        for stage in ("spec", "quality", "adversarial"):
            self._review(proof, stage, "accepted")


class TestTheContract(_PackageCase):
    def test_a_repair_package_runs_no_acceptance_of_its_own(self) -> None:
        """RP-12 rulings 44 and 64: its issues are no obligation; its orders' REQs are."""
        _seed([_record(_PACKAGE, kind="repair")], [])
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        with self.assertRaisesRegex(ValueError, "gz wp acceptance <ORD-id>"):
            resolve_brief(self.root, _PACKAGE)
        message = " ".join(self._refused("acceptance", _PACKAGE, "init", "--author", "a").split())
        self.assertIn("repair package", message)
        self.assertNotIn("..", message)  # output-contract: the reason reads as one sentence

    def test_a_delivery_package_owes_its_frozen_reqs(self) -> None:
        _seed([_record(_PACKAGE, kind="delivery")], [_req()])
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp(
            "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2",
        )  # fmt: skip
        self._wp("commence", _PACKAGE, "--evidence", "e")
        obligations = canonical_obligations(self.root, resolve_brief(self.root, _PACKAGE))
        self.assertEqual([item.id for item in obligations], [_REQ])

    def test_a_req_moved_past_its_frozen_revision_is_refused(self) -> None:
        _seed([_record(_PACKAGE, kind="delivery")], [_req()])
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp(
            "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2",
        )  # fmt: skip
        self._wp("commence", _PACKAGE, "--evidence", "e")
        _seed([_record(_PACKAGE, kind="delivery")], [_req(revision=3)])
        with self.assertRaisesRegex(ValueError, "no longer at the frozen revision"):
            resolve_brief(self.root, _PACKAGE)

    def test_acceptance_starts_only_on_a_commenced_package(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self.assertIn(
            "not commenced", self._refused("acceptance", _PACKAGE, "init", "--author", "a")
        )

    def test_an_edit_to_the_record_makes_the_input_stale(self) -> None:
        self._init()
        before = input_digest(self.root, resolve_brief(self.root, _PACKAGE))
        edited = {**_record(_PACKAGE), "system_restoration": "A new restoration."}
        _seed([edited], [_req()])
        self.assertNotEqual(input_digest(self.root, resolve_brief(self.root, _PACKAGE)), before)

    def test_appending_evidence_makes_no_review_stale(self) -> None:
        self._init()
        before = input_digest(self.root, resolve_brief(self.root, _PACKAGE))
        self._wp("evidence", _PACKAGE, "--oqe", "a commit")
        self.assertEqual(input_digest(self.root, resolve_brief(self.root, _PACKAGE)), before)

    def test_a_source_change_makes_the_input_stale(self) -> None:
        self._init()
        before = input_digest(self.root, resolve_brief(self.root, _PACKAGE))
        Path("tests/changed.py").parent.mkdir(exist_ok=True)
        Path("tests/changed.py").write_text("x = 1\n", encoding="utf-8")
        self.assertNotEqual(input_digest(self.root, resolve_brief(self.root, _PACKAGE)), before)


class TestTheGate(_PackageCase):
    def test_accept_refuses_a_package_with_no_acceptance(self) -> None:
        self._commence()
        message = self._refused("accept", _PACKAGE, "--evidence", "e")
        self.assertIn(f"gz wp acceptance {_PACKAGE} status", message.replace("\n", " "))

    def test_a_finding_refuses_a_package_every_channel_approved(self) -> None:
        self._init()
        proof = self._proof()
        self._approve(proof)
        self.assertTrue(acceptance_status(self.root, _PACKAGE).ready)
        self._review(proof)
        self.assertFalse(acceptance_status(self.root, _PACKAGE).ready)
        self._refused("accept", _PACKAGE, "--evidence", "e")

    def test_accept_admits_a_ready_package(self) -> None:
        self._init()
        self._approve(self._proof())
        self.assertTrue(acceptance_status(self.root, _PACKAGE).ready)
        with mock.patch("gzkit.commands.wp.footprint_refusal", return_value=None):
            self._wp("accept", _PACKAGE, "--evidence", "e")

    def test_a_terminated_package_reaches_gate_5_with_no_proof(self) -> None:
        self._commence()
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self._wp("dispatch", _PACKAGE, "--role", role, "--model", "m", "--req", _REQ)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")
        self._wp("unblock", _PACKAGE, "--ruling", "stop", "--operator", "g0", "--exit", "terminate")
        self._wp("accept", _PACKAGE, "--evidence", "e")
        self._wp(
            "close", _PACKAGE, "--decision", "terminate", "--attestor", "g0",
            "--residual-risk", "none", "--evidence", "e",
        )  # fmt: skip
        self.assertEqual(fenced_packages(self.root), ())


class TestTheRoundBound(_PackageCase):
    def _refute(self, rounds: int) -> Proof:
        proof = self._proof()
        for _ in range(rounds):
            self._review(proof)
        return proof

    def _dispatch(self) -> list[str]:
        return ["dispatch", _PACKAGE, "--role", "Implementer", "--model", "m", "--req", _REQ]

    def test_three_rounds_stop_dispatch_and_accept_and_name_the_block(self) -> None:
        self.assertEqual(review_round_limit(), 3)
        self._init()
        self._refute(3)
        for args in (self._dispatch(), ["accept", _PACKAGE, "--evidence", "e"]):
            message = " ".join(self._refused(*args).split())
            self.assertIn(f"gz wp block {_PACKAGE}", message)

    def test_two_rounds_leave_dispatch_open(self) -> None:
        self._init()
        self._refute(2)
        self._wp(*self._dispatch())

    def test_a_review_past_the_limit_is_still_recorded(self) -> None:
        self._init()
        proof = self._refute(3)
        self._review(proof)
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 4)
        self.assertEqual(refutation_counts(self.root, _PACKAGE), {_REQ: 4})

    def test_a_mapped_finding_counts_whatever_the_verdict_token_says(self) -> None:
        self._init()
        proof = self._proof()
        record_review(
            self.root, _PACKAGE, _receipt(proof, "adversarial", verdict="accepted", observed=True)
        )
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 1)
        self.assertEqual(refutation_counts(self.root, _PACKAGE), {_REQ: 1})

    def test_a_clean_adversarial_round_does_not_count(self) -> None:
        self._init()
        self._review(self._proof(), verdict="accepted")
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 0)

    def test_spec_and_quality_rounds_do_not_count(self) -> None:
        self._init()
        proof = self._proof()
        for _ in range(4):
            self._review(proof, "spec")
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 0)
        self.assertIsNone(round_bound_refusal(self.root, _PACKAGE))

    def test_the_operators_unblock_restarts_the_count(self) -> None:
        self._init()
        self._refute(3)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")
        self._wp("unblock", _PACKAGE, "--ruling", "one more", "--operator", "g0")
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 0)
        self._wp(*self._dispatch())

    def test_a_human_review_is_refused_past_the_limit(self) -> None:
        self._init()
        self._refute(3)
        message = self._refused(
            "acceptance", _PACKAGE, "human-review", "--attestor", "g0", "--ruling", "as it stands"
        )
        self.assertIn(f"gz wp block {_PACKAGE}", " ".join(message.split()))
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 3)

    def test_a_human_review_under_the_limit_keeps_the_count(self) -> None:
        self._init()
        self._refute(2)
        record_human_review(self.root, _PACKAGE, attestor="g0", ruling="as it stands")
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 2)

    def test_a_human_review_after_the_unblock_is_admitted(self) -> None:
        self._init()
        self._refute(3)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")
        self._wp("unblock", _PACKAGE, "--ruling", "as it stands", "--operator", "g0")
        record_human_review(self.root, _PACKAGE, attestor="g0", ruling="as it stands")

    def test_an_identical_receipt_counts_once(self) -> None:
        self._init()
        receipt = _receipt(self._proof(), "adversarial", verdict="refuted")
        record_review(self.root, _PACKAGE, receipt)
        record_review(self.root, _PACKAGE, receipt)
        self.assertEqual(refuted_rounds(self.root, _PACKAGE), 1)


class TestTheCommandSurface(_PackageCase):
    """The verb itself: a package has no launch, so a review marks no OBPI boundary."""

    def _receipt_file(self, receipt: dict[str, object]) -> str:
        directory = receipts_root(project_root=self.root)
        directory.mkdir(parents=True, exist_ok=True)
        run_id = str(receipt["run_id"])
        (directory / f"{run_id}.json").write_text(json.dumps(receipt), encoding="utf-8")
        return run_id

    def test_review_and_status_run_through_the_verb(self) -> None:
        self._init()
        proof = self._proof()
        for stage in ("spec", "quality", "adversarial"):
            run_id = self._receipt_file(_receipt(proof, stage))
            self._wp("acceptance", _PACKAGE, "review", "--receipt", run_id)
        report = json.loads(self._wp("acceptance", _PACKAGE, "status"))
        self.assertTrue(report["ready"])

    def test_status_exits_3_until_ready(self) -> None:
        self._init()
        result = self.runner.invoke(main, ["wp", "acceptance", _PACKAGE, "status"])
        self.assertEqual(result.exit_code, 3)

    def test_a_refused_action_names_the_package_verb(self) -> None:
        self._commence()
        output = self._refused("acceptance", _PACKAGE, "review", "--receipt", "../x")
        self.assertIn(f"gz wp acceptance {_PACKAGE} status", " ".join(output.split()))


class TestTheExits(_PackageCase):
    def _to_the_bound(self) -> None:
        self._commence()
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self._wp("dispatch", _PACKAGE, "--role", role, "--model", "m", "--req", _REQ)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")

    def _exit(self, name: str) -> None:
        self._wp("unblock", _PACKAGE, "--ruling", name, "--operator", "g0", "--exit", name)

    def test_a_hold_stays_refused_at_accept(self) -> None:
        self._to_the_bound()
        self._exit("hold")
        self._refused("accept", _PACKAGE, "--evidence", "e")

    def test_a_terminated_unproved_package_cannot_close_as_proceed(self) -> None:
        self._to_the_bound()
        self._exit("terminate")
        self._wp("accept", _PACKAGE, "--evidence", "e")
        message = self._refused(
            "close", _PACKAGE, "--decision", "proceed", "--attestor", "g0",
            "--residual-risk", "none", "--evidence", "e",
        )  # fmt: skip
        self.assertIn("delivered nothing", " ".join(message.split()))


class TestTheReviewChannels(_PackageCase):
    """Ruling 9: only a delivery run can be single-driver, and it owes the adversary."""

    def _delivery(self) -> None:
        _seed([_record(_PACKAGE, kind="delivery")], [_req()])
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp(
            "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2",
        )  # fmt: skip
        self._wp("commence", _PACKAGE, "--evidence", "e")
        self._wp("acceptance", _PACKAGE, "init", "--author", "implementing-session")

    def test_a_single_driver_delivery_needs_the_adversarial_review_alone(self) -> None:
        self._delivery()
        self._wp(
            "dispatch", _PACKAGE, "--role", "SingleDriver", "--model", "m", "--req", _REQ,
            "--reason", "no dispatch available",
        )  # fmt: skip
        self._review(self._proof(_REQ), verdict="accepted")
        self.assertTrue(acceptance_status(self.root, _PACKAGE).ready)

    def test_any_other_delivery_needs_all_three_reviews(self) -> None:
        self._delivery()
        self._review(self._proof(_REQ), verdict="accepted")
        self.assertFalse(acceptance_status(self.root, _PACKAGE).ready)


class TestTheRoundLimitExit(_PackageCase):
    """#1028: the exit must stop a package with no subject at the fix-cycle bound."""

    def test_terminate_is_open_at_the_round_limit(self) -> None:
        self._init()
        proof = self._proof()
        for _ in range(3):
            self._review(proof)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")
        self._wp("unblock", _PACKAGE, "--ruling", "stop", "--operator", "g0", "--exit", "terminate")
        self._wp("accept", _PACKAGE, "--evidence", "e")


class TestAMalformedReviewRow(_PackageCase):
    def _plant(self) -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "acceptance_recorded",
            "id": _PACKAGE,
            "ts": "2026-11-01T00:00:00+00:00",
            "record_type": "review",
            "payload": ["not a receipt"],
        }
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(row) + "\n")

    def test_it_never_stops_a_dispatch_or_a_block(self) -> None:
        self._init()
        self._plant()
        self._wp("dispatch", _PACKAGE, "--role", "Implementer", "--model", "m", "--req", _REQ)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")

    def test_accept_refuses_that_history(self) -> None:
        self._init()
        self._approve(self._proof())
        self._plant()
        result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)


class TestDeparture(_PackageCase):
    """Ruling 12: the REQ moves out by disposition and the package carries on."""

    def _delivery(self) -> None:
        second = {**_req(), "id": "REQ-8"}
        _seed([_record(_PACKAGE, kind="delivery")], [_req(), second])
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp(
            "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2", "--baseline", "REQ-8@2",
        )  # fmt: skip
        self._wp("commence", _PACKAGE, "--evidence", "e")
        self._wp("acceptance", _PACKAGE, "init", "--author", "implementing-session")

    def _depart(self) -> None:
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "work_package_unblocked",
            "id": _PACKAGE,
            "ts": "2026-11-01T00:00:00+00:00",
            "work_package": _PACKAGE,
            "ruling": "depart",
            "operator": "g0",
            "exit_taken": "departure",
            "req": _REQ,
            "covered": [],
        }
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(row) + "\n")

    def test_a_departed_req_is_no_longer_owed_and_the_rest_is_acceptable(self) -> None:
        self._delivery()
        self._depart()
        obligations = canonical_obligations(self.root, resolve_brief(self.root, _PACKAGE))
        self.assertEqual([item.id for item in obligations], ["REQ-8"])
        self._approve(self._proof("REQ-8"))
        self.assertTrue(acceptance_status(self.root, _PACKAGE).ready)

    def test_a_departed_req_with_history_leaves_the_rest_acceptable(self) -> None:
        self._delivery()
        self._review(self._proof(_REQ))
        self._depart()
        self._approve(self._proof("REQ-8"))
        self.assertTrue(acceptance_status(self.root, _PACKAGE).ready)
        report = json.loads(self._wp("acceptance", _PACKAGE, "status"))
        self.assertTrue(report["ready"])

    def test_a_finding_on_a_departed_req_leaves_a_review_of_both(self) -> None:
        self._delivery()
        departing, staying = self._proof(_REQ), self._proof("REQ-8")
        receipt = _receipt(departing, "adversarial", verdict="refuted")
        review = json.loads(str(receipt["stdout_tail"]).split("```")[1].removeprefix("json\n"))
        review["obligation_ids"] = [_REQ, "REQ-8"]
        review["proof_ids"] = [departing.id, staying.id]
        receipt["stdout_tail"] = "```json\n" + json.dumps(review) + "\n```"
        record_review(self.root, _PACKAGE, receipt)
        self._depart()
        kept = load_history(self.root, _PACKAGE).reviews
        self.assertEqual([item.obligation_ids for item in kept], [("REQ-8",)])
        self.assertEqual(kept[0].findings, ())

    def test_the_departed_history_stays_on_the_ledger(self) -> None:
        self._delivery()
        self._review(self._proof(_REQ))
        self._depart()
        rows = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
        self.assertIn("A concrete violation.", rows)
        self.assertEqual(load_history(self.root, _PACKAGE).reviews, [])

    def test_a_later_block_still_counts_a_departed_reqs_refutations(self) -> None:
        self._delivery()
        self._review(self._proof(_REQ))
        for role in ("Implementer", "SpecReviewer", "Implementer", "Implementer"):
            self._wp("dispatch", _PACKAGE, "--role", role, "--model", "m", "--req", _REQ)
        self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")
        self._wp(
            "change", _PACKAGE, "--rung", "departure", "--approver", "operator",
            "--change", "bounded", "--item", "DFS-1", "--form", "waiver",
            "--duration", "permanent", "--req", _REQ,
        )  # fmt: skip
        self._wp(
            "unblock", _PACKAGE, "--ruling", "depart", "--operator", "g0",
            "--exit", "departure", "--req", _REQ,
        )  # fmt: skip
        ids = [i.id for i in canonical_obligations(self.root, resolve_brief(self.root, _PACKAGE))]
        self.assertEqual(ids, ["REQ-8"])
        output = self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n", "--json")
        self.assertEqual(json.loads(output)["refutations"][f"{_REQ}@2"], 1)

    def test_a_departed_req_may_change_revision(self) -> None:
        self._delivery()
        self._depart()
        _seed([_record(_PACKAGE, kind="delivery")], [_req(revision=3), {**_req(), "id": "REQ-8"}])
        obligations = canonical_obligations(self.root, resolve_brief(self.root, _PACKAGE))
        self.assertEqual([item.id for item in obligations], ["REQ-8"])


class TestTheRefutationCount(_PackageCase):
    def test_a_block_carries_the_runtimes_own_count(self) -> None:
        self._init()
        proof = self._proof()
        self._review(proof)
        self._review(proof)
        self.assertEqual(refutation_counts(self.root, _PACKAGE), {_REQ: 2})
        output = self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n")
        self.assertIn(f"refutations: {_REQ}@2: 2", output)

    def test_an_accepted_review_refutes_nothing(self) -> None:
        self._init()
        self._review(self._proof(), verdict="accepted")
        self.assertEqual(refutation_counts(self.root, _PACKAGE), {})

    def test_a_bad_acceptance_row_never_costs_the_block(self) -> None:
        self._init()
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "acceptance_recorded",
            "id": _PACKAGE,
            "ts": "2026-11-01T00:00:00+00:00",
            "record_type": "contract",
            "payload": {"unexpected": True},
        }
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(row) + "\n")
        output = self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n", "--json")
        self.assertIn("refutations not counted", json.loads(output)["reason"])

    def test_the_count_keys_a_req_at_its_frozen_revision(self) -> None:
        _seed([_record(_PACKAGE, kind="delivery")], [_req()])
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp(
            "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2",
        )  # fmt: skip
        self._wp("commence", _PACKAGE, "--evidence", "e")
        self._wp("acceptance", _PACKAGE, "init", "--author", "implementing-session")
        self._review(self._proof(_REQ))
        output = self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n", "--json")
        self.assertEqual(json.loads(output)["refutations"], {f"{_REQ}@2": 1})

    def test_a_package_with_no_acceptance_counts_zero_for_each_subject(self) -> None:
        self._commence()
        output = self._wp("block", _PACKAGE, "--reason", "r", "--next-action", "n", "--json")
        self.assertEqual(json.loads(output)["refutations"], {f"{_REQ}@2": 0})


class TestWhatBindsByMutation(unittest.TestCase):
    """A catalog REQ binds by mutation; a carried issue is no obligation (RP-12 ruling 64)."""

    def test_only_a_catalog_req_binds_by_mutation(self) -> None:
        for obligation, binds in (("REQ-7", True), ("#1206", False), ("REQ-0.1.0-01-01", False)):
            with self.subTest(obligation=obligation):
                self.assertEqual(binds_by_mutation(obligation), binds)


class TestAMutationProof(ExecutionFixture):
    """A real mutation sweep binds a catalog REQ's tests, in place of `@covers`."""

    def _contract(self) -> PackageContract:
        return PackageContract(
            contract={
                "brief": "data/catalog/work_packages.json",
                "authority": "data/catalog/work_packages.json#WP-01-loop",
                "id": _PACKAGE,
                "requirements": [{"id": _REQ, "kind": "BEHAVIOR", "statement": "s"}],
            }
        )

    def _prove(self, replace: str) -> Proof:
        return prove(
            self.root,
            self._contract(),
            _REQ,
            source=Path("src/engine.py"),
            selectors=[SELECTOR],
            mutations=[
                Mutation(
                    find="return value * 2",
                    replace=replace,
                    label="mutant",
                    expected_tests=[SELECTOR],
                )
            ],
        )

    def test_killing_the_mutant_proves_a_catalog_req(self) -> None:
        proof = self._prove("return value * 3")
        self.assertTrue(proof.valid, proof.evidence)

    def test_a_surviving_mutant_proves_nothing(self) -> None:
        self.assertFalse(self._prove("return 2 * value").valid)

    def test_a_catalog_req_proof_still_needs_selectors(self) -> None:
        with self.assertRaisesRegex(ValueError, "BEHAVIOR proof requires"):
            prove(self.root, self._contract(), _REQ, source=Path("src/engine.py"))


if __name__ == "__main__":
    unittest.main()
