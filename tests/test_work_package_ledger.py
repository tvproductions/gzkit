"""The work-package Layer-2 writers: RO-5 tranche 1.

`docs/governance/harbor-ro5-work-packages.md`: a package moves `initiated`,
`frozen`, `commenced`, `accepted`, `closed` one step at a time (ruling 5 as
amended 2026-10-28); a freeze carries the risk note, the reviewer's receipt, a
baseline at the catalog's revisions and the operator's approval of every
alteration; a close carries Gate 5's attestor and decision, the residual risk
and every alteration accounted. A change names its rung on the ladder, the
approver the rung requires and what it supersedes (amendments 3 and 4).
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.events import (
    BaselinedReq,
    WorkPackageChangedEvent,
    WorkPackageTransitionedEvent,
    parse_typed_event,
)
from gzkit.ledger import Ledger
from gzkit.models.catalog import (
    Alteration,
    Catalog,
    Criterion,
    Departure,
    Outcome,
    Req,
    WorkPackage,
)
from gzkit.ontology.corpus import project_corpus
from gzkit.work_package_ledger import (
    ChangeRequest,
    TransitionRequest,
    WorkPackageLedgerError,
    record_work_package_change,
    record_work_package_transition,
    work_package_state,
)

_ALTERATION = Alteration(
    id="ALT-1", description="Rekey the matrix.", configuration_change="replaced"
)
_DEPARTURE = Departure(
    id="DFS-1",
    description="The closing test cannot run on Windows yet.",
    form="waiver",
    duration="temporary",
    clear_by="the Windows runner lands",
    req=None,
)


def _req(req_id: str = "REQ-1", member_of: str = "H1", revision: int = 2) -> Req:
    return Req(
        id=req_id,
        member_of=member_of,
        statement="A resumed session names its predecessor.",
        criteria=(
            Criterion(state_or_input="a handoff", required_outcome="named", evidence="a test"),
        ),
        kind="BEHAVIOR",
        revision=revision,
        derives_from=("FR-001",),
        applies_to=(),
    )


def _outcome(code: str) -> Outcome:
    return Outcome(
        code=code,
        statement="The operator can resume a session.",
        owner="g0",
        user_facing=False,
        governed_by=(),
        depends_on=(),
        feature=None,
        retired=False,
    )


def _package(wp_id: str, kind: str = "delivery") -> WorkPackage:
    delivery = kind == "delivery"
    return WorkPackage(
        id=wp_id,
        kind=kind,  # ty: ignore[invalid-argument-type]
        outcome="H1" if delivery else None,
        issues=() if delivery else (1183,),
        lane=None if delivery else "lite",
        aliases=(),
        initial_conditions="NA",
        procedure="Task cards one and two.",
        test_and_inspection="REQ-1 at revision 2.",
        system_restoration="NA",
        oqe=(),
        alterations=(_ALTERATION,),
        departures=(_DEPARTURE,),
    )


def _catalog() -> Catalog:
    return Catalog(
        families=(),
        outcomes=(_outcome("H1"), _outcome("H2")),
        reqs=(_req(), _req("REQ-2", member_of="H2")),
        work_packages=(_package("WP-01-resume"), _package("WP-02-astral", "repair")),
    )


def _unstamped(event: object) -> dict[str, object]:
    """Drop `ts`, which the ledger stamps under its write lock.

    Returns:
        The event's other fields.

    """
    dumped = event.model_dump()  # ty: ignore[unresolved-attribute]
    return {key: value for key, value in dumped.items() if key != "ts"}


def _rows(ledger_path: Path) -> list[dict[str, object]]:
    if not ledger_path.is_file():
        return []
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


_FREEZE = {
    "baseline": (BaselinedReq(req="REQ-1", revision=2),),
    "risk_note": "Resume touches the handoff chain.",
    "review_receipt": "review-01",
    "approved_alterations": ("ALT-1",),
}
_CLOSE = {
    "attestor": "g0",
    "decision": "proceed",
    "residual_risk": "None known.",
    "configuration_changes": ("ALT-1",),
    "open_departures": ("DFS-1",),
}
_PAYLOADS: dict[str, dict[str, object]] = {
    "initiated": {"operator_text": "start the resume package"},
    "frozen": _FREEZE,
    "commenced": {},
    "accepted": {},
    "closed": _CLOSE,
}
_LIFECYCLE = tuple(_PAYLOADS)


class _LedgerCase(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = Path(self._dir.name) / "ledger.jsonl"
        self.ledger = Ledger(self.path)

    def move(self, to_state: str, **fields: object) -> WorkPackageTransitionedEvent:
        request = TransitionRequest.model_validate(
            {"work_package": "WP-01-resume", "to_state": to_state, "evidence": "evt-1", **fields}
        )
        return record_work_package_transition(_catalog(), self.ledger, request)

    def walk_to(self, state: str, **fields: object) -> None:
        for step in _LIFECYCLE[: _LIFECYCLE.index(state) + 1]:
            self.move(step, **fields, **_PAYLOADS[step])

    def change(self, rung: str, **fields: object) -> WorkPackageChangedEvent:
        request = ChangeRequest.model_validate(
            {"work_package": "WP-01-resume", "rung": rung, "change": "Resequence cards.", **fields}
        )
        return record_work_package_change(_catalog(), self.ledger, request)

    def assert_refused(self, call: object, **kwargs: object) -> None:
        before = _rows(self.path)
        with self.assertRaises(WorkPackageLedgerError):
            call(**kwargs)  # ty: ignore[call-non-callable]
        self.assertEqual(_rows(self.path), before)


class TransitionTests(_LedgerCase):
    def test_a_package_with_no_event_is_not_initiated(self) -> None:
        self.assertIsNone(work_package_state(self.ledger, "WP-01-resume"))

    def test_initiation_is_booked_on_the_operators_words(self) -> None:
        event = self.move("initiated", operator_text="start the resume package")
        (row,) = _rows(self.path)
        persisted = parse_typed_event(row)
        self.assertIsInstance(persisted, WorkPackageTransitionedEvent)
        self.assertEqual(_unstamped(persisted), _unstamped(event))
        self.assertEqual(
            (event.id, event.from_state, event.to_state), ("WP-01-resume", None, "initiated")
        )
        self.assertEqual(event.operator_text, "start the resume package")

    def test_initiation_without_the_operators_words_is_refused(self) -> None:
        self.assert_refused(self.move, to_state="initiated")

    def test_the_whole_lifecycle_walks_one_step_at_a_time(self) -> None:
        self.walk_to("closed")
        events = [parse_typed_event(row) for row in _rows(self.path)]
        self.assertEqual(
            [(e.from_state, e.to_state) for e in events],  # ty: ignore[unresolved-attribute]
            list(zip((None, *_LIFECYCLE[:-1]), _LIFECYCLE, strict=True)),
        )
        self.assertEqual(work_package_state(self.ledger, "WP-01-resume"), "closed")

    def test_a_skipped_or_backward_step_is_refused(self) -> None:
        self.assert_refused(self.move, to_state="frozen", **_FREEZE)
        self.walk_to("frozen")
        self.assert_refused(self.move, to_state="accepted")
        self.assert_refused(self.move, to_state="initiated", operator_text="again")

    def test_a_closed_package_moves_no_further(self) -> None:
        self.walk_to("closed")
        for state in _LIFECYCLE:
            with self.subTest(state=state):
                self.assert_refused(self.move, to_state=state, **_PAYLOADS[state])

    def test_a_package_the_store_lacks_is_refused(self) -> None:
        self.assert_refused(
            self.move, to_state="initiated", work_package="WP-09-ghost", operator_text="x"
        )

    def test_a_field_the_target_state_does_not_carry_is_refused(self) -> None:
        self.assert_refused(self.move, to_state="initiated", operator_text="go", risk_note="early")
        self.walk_to("frozen")
        self.assert_refused(self.move, to_state="commenced", attestor="g0")

    def test_each_package_keeps_its_own_state(self) -> None:
        self.walk_to("frozen")
        self.move("initiated", work_package="WP-02-astral", operator_text="start the repair")
        self.assertEqual(work_package_state(self.ledger, "WP-01-resume"), "frozen")
        self.assertEqual(work_package_state(self.ledger, "WP-02-astral"), "initiated")


class FreezeTests(_LedgerCase):
    def setUp(self) -> None:
        super().setUp()
        self.move("initiated", operator_text="start the resume package")

    def test_a_freeze_lacking_its_risk_note_or_receipt_is_refused(self) -> None:
        for missing in ("risk_note", "review_receipt"):
            with self.subTest(missing=missing):
                self.assert_refused(self.move, to_state="frozen", **{**_FREEZE, missing: " "})

    def test_a_delivery_freeze_carries_a_baseline(self) -> None:
        self.assert_refused(self.move, to_state="frozen", **{**_FREEZE, "baseline": ()})

    def test_the_baseline_holds_the_catalogs_revision_of_the_packages_own_outcome(self) -> None:
        for entry in (
            BaselinedReq(req="REQ-1", revision=1),
            BaselinedReq(req="REQ-9", revision=1),
            BaselinedReq(req="REQ-2", revision=2),
        ):
            with self.subTest(entry=entry):
                self.assert_refused(
                    self.move, to_state="frozen", **{**_FREEZE, "baseline": (entry,)}
                )

    def test_every_planned_alteration_is_approved_at_freeze(self) -> None:
        for approved in ((), ("ALT-1", "ALT-2")):
            with self.subTest(approved=approved):
                self.assert_refused(
                    self.move, to_state="frozen", **{**_FREEZE, "approved_alterations": approved}
                )

    def test_the_freeze_event_carries_the_baseline_and_the_approvals(self) -> None:
        event = self.move("frozen", **_FREEZE)
        self.assertEqual(event.baseline, (BaselinedReq(req="REQ-1", revision=2),))
        self.assertEqual(event.approved_alterations, ("ALT-1",))
        self.assertEqual(event.review_receipt, "review-01")

    def test_a_repair_package_may_freeze_with_no_req_baseline(self) -> None:
        self.move("initiated", work_package="WP-02-astral", operator_text="start the repair")
        event = self.move("frozen", work_package="WP-02-astral", **{**_FREEZE, "baseline": ()})
        self.assertEqual(event.to_state, "frozen")


class CloseTests(_LedgerCase):
    def setUp(self) -> None:
        super().setUp()
        self.walk_to("accepted")

    def test_a_close_needs_gate_5s_attestor_decision_and_residual(self) -> None:
        for missing in ("attestor", "decision", "residual_risk"):
            with self.subTest(missing=missing):
                fields = {k: v for k, v in _CLOSE.items() if k != missing}
                self.assert_refused(self.move, to_state="closed", **fields)

    def test_every_alteration_is_accounted_and_only_held_departures_named_open(self) -> None:
        for override in ({"configuration_changes": ()}, {"open_departures": ("DFS-9",)}):
            with self.subTest(override=override):
                self.assert_refused(self.move, to_state="closed", **{**_CLOSE, **override})

    def test_the_close_records_the_decision_and_the_open_departures(self) -> None:
        event = self.move("closed", **_CLOSE)
        self.assertEqual((event.attestor, event.decision), ("g0", "proceed"))
        self.assertEqual(event.open_departures, ("DFS-1",))


class ChangeTests(_LedgerCase):
    def setUp(self) -> None:
        super().setUp()
        self.move("initiated", operator_text="start the resume package")

    def test_pen_and_ink_is_the_coordinators_and_keeps_what_it_supersedes(self) -> None:
        event = self.change("pen_and_ink", approver="coordinator", superseded="Cards two, one.")
        (_, row) = _rows(self.path)
        persisted = parse_typed_event(row)
        self.assertIsInstance(persisted, WorkPackageChangedEvent)
        self.assertEqual(_unstamped(persisted), _unstamped(event))
        self.assertEqual((event.rung, event.approver), ("pen_and_ink", "coordinator"))
        self.assertEqual(event.superseded, "Cards two, one.")
        self.assert_refused(self.change, rung="pen_and_ink", approver="operator", superseded="x")
        self.assert_refused(self.change, rung="pen_and_ink", approver="coordinator")

    def test_every_rung_above_pen_and_ink_is_the_operators(self) -> None:
        self.assert_refused(
            self.change,
            rung="change_order",
            approver="coordinator",
            superseded="x",
            work_stopped=True,
        )
        self.assert_refused(self.change, rung="attachment", approver="coordinator")

    def test_a_change_order_stops_work_and_nothing_else_does(self) -> None:
        self.assert_refused(self.change, rung="change_order", approver="operator", superseded="x")
        self.assert_refused(self.change, rung="attachment", approver="operator", work_stopped=True)
        event = self.change("change_order", approver="operator", superseded="x", work_stopped=True)
        self.assertTrue(event.work_stopped)

    def test_a_supplement_names_another_package_the_store_holds(self) -> None:
        for supplement in (None, "WP-01-resume", "WP-09-ghost"):
            with self.subTest(supplement=supplement):
                self.assert_refused(
                    self.change, rung="supplement", approver="operator", supplement=supplement
                )
        event = self.change("supplement", approver="operator", supplement="WP-02-astral")
        self.assertEqual(event.supplement, "WP-02-astral")

    def test_a_departure_copies_its_form_duration_and_clear_by_from_the_store(self) -> None:
        event = self.change("departure", approver="operator", item="DFS-1")
        self.assertEqual(
            (event.form, event.duration, event.clear_by),
            ("waiver", "temporary", "the Windows runner lands"),
        )
        self.assert_refused(self.change, rung="departure", approver="operator", item="DFS-9")

    def test_an_alteration_names_one_the_package_plans(self) -> None:
        self.assertEqual(self.change("alteration", approver="operator", item="ALT-1").item, "ALT-1")
        self.assert_refused(self.change, rung="alteration", approver="operator", item="ALT-9")
        self.assert_refused(self.change, rung="attachment", approver="operator", item="ALT-1")

    def test_an_unknown_rung_is_refused(self) -> None:
        self.assert_refused(self.change, rung="engineering_order", approver="operator")

    def test_no_change_before_initiation_or_after_close(self) -> None:
        request = ChangeRequest(
            work_package="WP-02-astral", rung="attachment", approver="operator", change="Add."
        )
        with self.assertRaises(WorkPackageLedgerError):
            record_work_package_change(_catalog(), self.ledger, request)
        for step in _LIFECYCLE[1:]:
            self.move(step, **_PAYLOADS[step])
        self.assert_refused(self.change, rung="attachment", approver="operator")


class CorpusTests(_LedgerCase):
    def test_the_corpus_projection_accounts_for_both_events(self) -> None:
        self.walk_to("frozen")
        self.change("attachment", approver="operator")
        fidelity = project_corpus(self.ledger).fidelity
        self.assertTrue(fidelity.complete, fidelity)


if __name__ == "__main__":
    unittest.main()
