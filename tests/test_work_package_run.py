"""The run's bound: GHI #1200 on the work-package surface (RO-14 tranche 1).

`docs/governance/harbor-ro14-obpi-forward-migration.md`, rulings 6 to 15: the
runtime counts fix cycles against a frozen subject across packages, refuses the
cycle past the bound whatever was ruled, and an unblock at the bound names one
exit. The replayed sequences are the dispatch rows of
`OBPI-0.35.0-15-pipeline-run-position`, the run #1200 measured.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.events import BaselinedReq
from gzkit.ledger import Ledger
from gzkit.models.catalog import Catalog, Criterion, Departure, Outcome, Req, WorkPackage
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.work_package_ledger import (
    ChangeRequest,
    TransitionRequest,
    WorkPackageLedgerError,
    record_work_package_change,
    record_work_package_transition,
)
from gzkit.work_package_run import (
    BlockRequest,
    DispatchRequest,
    UnblockRequest,
    count_fix_cycles,
    record_work_package_block,
    record_work_package_dispatch,
    record_work_package_unblock,
)

_NAMES = {"I": "Implementer", "S": "SpecReviewer", "Q": "QualityReviewer", "D": "SingleDriver"}
#: Task 1 and Task 2 up to the first unblock, as the ledger holds them.
_REPLAY_TASK_1 = "IIISQI"
_REPLAY_TASK_2_BEFORE_THE_REFUSED_DISPATCH = "IISQSISQQSISQ"

_FIRST = "WP-01-resume"
_REPAIR = "WP-02-astral"
_SECOND = "WP-03-again"
_MIXED = "WP-04-mixed"
_WAIVER = Departure(
    id="DFS-1",
    description="The claim is bounded.",
    form="waiver",
    duration="permanent",
    clear_by=None,
    req="REQ-1",
)
_DEVIATION = Departure(
    id="DFS-2",
    description="Requested before the work.",
    form="deviation",
    duration="temporary",
    clear_by="later",
    req="REQ-2",
)
_OTHER_REQ_WAIVER = _WAIVER.model_copy(update={"id": "DFS-3", "req": "REQ-2"})


def _roles(sequence: str) -> list[str]:
    return [_NAMES[letter] for letter in sequence]


def _package(wp_id: str, kind: str = "delivery") -> WorkPackage:
    delivery = kind == "delivery"
    return WorkPackage(
        id=wp_id,
        kind=kind,  # ty: ignore[invalid-argument-type]
        outcome="H1" if delivery else None,
        issues=() if delivery else (1183, 1184),
        lane=None if delivery else "lite",
        aliases=(),
        initial_conditions="NA",
        procedure="NA",
        test_and_inspection="NA",
        system_restoration="NA",
        oqe=(),
        alterations=(),
        departures=(_WAIVER, _DEVIATION, _OTHER_REQ_WAIVER) if delivery else (),
    )


def _req(req_id: str, revision: int = 2) -> Req:
    return Req(
        id=req_id,
        member_of="H1",
        statement="A resumed session names its predecessor.",
        criteria=(Criterion(state_or_input="h", required_outcome="n", evidence="t"),),
        kind="BEHAVIOR",
        revision=revision,
        derives_from=("FR-001",),
        applies_to=(),
    )


def _catalog(revision: int = 2) -> Catalog:
    outcome = Outcome(
        code="H1",
        statement="The operator can resume a session.",
        owner="g0",
        user_facing=False,
        governed_by=(),
        depends_on=(),
        feature=None,
        retired=False,
    )
    return Catalog(
        families=(),
        outcomes=(outcome,),
        reqs=(_req("REQ-1", revision), _req("REQ-2", revision)),
        work_packages=(
            _package(_FIRST),
            _package(_REPAIR, "repair"),
            _package(_SECOND),
            _package(_MIXED, "repair").model_copy(update={"issues": (1190,), "departures": ()}),
        ),
    )


def _count(sequence: str) -> int:
    rows = [("P", "S", role) for role in _roles(sequence)]
    return count_fix_cycles(rows).get("S", 0)


class CountFixCycles(unittest.TestCase):
    """A subject's first dispatch is free; a review arms it; each later one counts."""

    def test_table_on_one_subject(self) -> None:
        for sequence, expected in (
            ("", 0),
            ("III", 0),
            ("SI", 0),  # a review before the first dispatch arms nothing
            ("ISI", 1),
            (_REPLAY_TASK_1, 1),
            (_REPLAY_TASK_2_BEFORE_THE_REFUSED_DISPATCH, MAX_REVIEW_FIX_CYCLES),
            (_REPLAY_TASK_2_BEFORE_THE_REFUSED_DISPATCH + "I", MAX_REVIEW_FIX_CYCLES + 1),
            ("ISIII", 3),  # the real run's Task 2 at 07:48, 08:05 and 08:43
            ("DDD", 2),
            ("DDDI", 3),  # a declared run keeps its count when it changes role
            ("ISDI", 2),
        ):
            with self.subTest(sequence=sequence):
                self.assertEqual(_count(sequence), expected)

    def test_a_review_of_one_subject_arms_the_subjects_its_package_started(self) -> None:
        rows = [
            ("P", "B", "Implementer"),
            ("P", "A", "SpecReviewer"),
            ("P", "B", "Implementer"),
        ]
        self.assertEqual(count_fix_cycles(rows)["B"], 1)

    def test_it_does_not_arm_a_subject_not_yet_started(self) -> None:
        rows = [
            ("P", "A", "Implementer"),
            ("P", "A", "SpecReviewer"),
            ("P", "B", "Implementer"),
            ("P", "A", "SpecReviewer"),
            ("P", "A", "Implementer"),
        ]
        self.assertEqual(count_fix_cycles(rows), {"A": 1, "B": 0})

    def test_it_does_not_arm_another_packages_subject(self) -> None:
        rows = [
            ("P", "B", "Implementer"),
            ("Q", "A", "SpecReviewer"),
            ("P", "B", "Implementer"),
        ]
        self.assertEqual(count_fix_cycles(rows)["B"], 0)

    def test_a_review_of_the_same_subject_in_another_package_arms_it(self) -> None:
        rows = [
            ("P", "A", "Implementer"),
            ("Q", "A", "SpecReviewer"),
            ("P", "A", "Implementer"),
        ]
        self.assertEqual(count_fix_cycles(rows)["A"], 1)

    def test_the_count_follows_a_subject_into_a_new_package(self) -> None:
        rows = [
            ("P", "A", "Implementer"),
            ("P", "A", "SpecReviewer"),
            ("Q", "A", "Implementer"),
        ]
        self.assertEqual(count_fix_cycles(rows)["A"], 1)


class _Run(unittest.TestCase):
    def setUp(self) -> None:
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.ledger = Ledger(Path(directory.name) / "ledger.jsonl")
        self.catalog = _catalog()
        self._commence(_FIRST, ("REQ-1", "REQ-2"))
        self._commence(_REPAIR, ())

    def _commence(self, package: str, reqs: tuple[str, ...], revision: int = 2) -> None:
        baseline = tuple(BaselinedReq(req=req, revision=revision) for req in reqs)
        moves = (
            TransitionRequest(
                work_package=package, to_state="initiated", evidence="e", operator_text="go"
            ),
            TransitionRequest(
                work_package=package,
                to_state="frozen",
                evidence="e",
                baseline=baseline,
                risk_note="r",
                review_receipt="v",
            ),
            TransitionRequest(work_package=package, to_state="commenced", evidence="e"),
        )
        for move in moves:
            record_work_package_transition(self.catalog, self.ledger, move)

    def _dispatch(
        self,
        role: str,
        package: str = _FIRST,
        *,
        req: str | None = "REQ-1",
        issue: int | None = None,
        reason: str | None = None,
    ) -> None:
        request = DispatchRequest(
            work_package=package,
            role=role,
            model="m",
            req=None if issue is not None and req == "REQ-1" else req,
            issue=issue,
            reason=reason,
        )
        record_work_package_dispatch(self.catalog, self.ledger, request)

    def _reach_the_bound(self, package: str = _FIRST, req: str = "REQ-1") -> None:
        for role in _roles("ISQISQISQ"):
            self._dispatch(role, package, req=req)

    def _block(self, package: str = _FIRST) -> None:
        record_work_package_block(
            self.catalog,
            self.ledger,
            BlockRequest(work_package=package, reason="refuted", next_action="rule on it"),
        )

    def _unblock(
        self,
        exit_taken: str | None = None,
        req: str | None = None,
        package: str = _FIRST,
    ) -> None:
        record_work_package_unblock(
            self.catalog,
            self.ledger,
            UnblockRequest(
                work_package=package,
                ruling="a",
                operator="g0",
                exit_taken=exit_taken,
                req=req,
            ),
        )

    def _depart(self, item: str = "DFS-1") -> None:
        record_work_package_change(
            self.catalog,
            self.ledger,
            ChangeRequest(
                work_package=_FIRST,
                rung="departure",
                approver="operator",
                change="bounded",
                item=item,
            ),
        )

    def _rows(self, event_type: str) -> list[dict[str, object]]:
        return [row.extra for row in self.ledger.query(event_type=event_type)]

    def _refused(self, pattern: str, event_type: str, act) -> None:
        booked = len(self._rows(event_type))
        with self.assertRaisesRegex(WorkPackageLedgerError, pattern):
            act()
        self.assertEqual(len(self._rows(event_type)), booked)


class Dispatch(_Run):
    def test_the_cycle_past_the_bound_is_refused_and_books_nothing(self) -> None:
        self._reach_the_bound()
        self._refused("bound", "work_package_dispatched", lambda: self._dispatch("Implementer"))

    def test_another_subject_inside_the_bound_is_unaffected(self) -> None:
        self._reach_the_bound()
        self._dispatch("Implementer", req="REQ-2")

    def test_a_reviewer_may_still_look_at_a_subject_at_the_bound(self) -> None:
        self._reach_the_bound()
        self._dispatch("SpecReviewer")

    def test_repeating_the_implementer_after_a_hold_is_refused(self) -> None:
        for letter in "ISISI":
            self._dispatch(_NAMES[letter])
        self._block()
        self._unblock("hold")
        self._refused("bound", "work_package_dispatched", lambda: self._dispatch("Implementer"))

    def test_no_exit_opens_a_further_repair_cycle_on_the_subject(self) -> None:
        for exit_taken, req in (("hold", None), ("terminate", None), ("reopen", "REQ-1")):
            with self.subTest(exit_taken=exit_taken):
                self.setUp()
                self._reach_the_bound()
                self._block()
                self._unblock(exit_taken, req)
                with self.assertRaises(WorkPackageLedgerError):
                    self._dispatch("Implementer")

    def test_a_departure_carries_the_package_on_but_not_the_subject(self) -> None:
        self._reach_the_bound()
        self._block()
        self._depart()
        self._unblock("departure", "REQ-1")
        self._dispatch("Implementer", req="REQ-2")
        self._refused("bound", "work_package_dispatched", lambda: self._dispatch("Implementer"))

    def test_a_stopping_exit_stops_every_subject_of_the_package(self) -> None:
        for exit_taken, req in (("terminate", None), ("reopen", "REQ-1")):
            with self.subTest(exit_taken=exit_taken):
                self.setUp()
                self._reach_the_bound()
                self._block()
                self._unblock(exit_taken, req)
                self._refused(
                    exit_taken,
                    "work_package_dispatched",
                    lambda: self._dispatch("Implementer", req="REQ-2"),
                )
                self._dispatch("SpecReviewer", req="REQ-2")

    def test_a_hold_leaves_the_other_subjects_open(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._dispatch("Implementer", req="REQ-2")

    def test_separating_reviews_from_fixes_is_bounded(self) -> None:
        for _ in range(MAX_REVIEW_FIX_CYCLES + 1):
            self._dispatch("Implementer", req="REQ-2")
            self._dispatch("SpecReviewer", req="REQ-1")
        self._refused(
            "bound",
            "work_package_dispatched",
            lambda: self._dispatch("Implementer", req="REQ-2"),
        )

    def test_a_reviewer_on_an_issue_arms_a_req_of_the_same_package(self) -> None:
        self._commence(_MIXED, ("REQ-1",))
        for _ in range(MAX_REVIEW_FIX_CYCLES + 1):
            self._dispatch("Implementer", _MIXED, req="REQ-1")
            self._dispatch("SpecReviewer", _MIXED, issue=1190)
        self._refused(
            "bound",
            "work_package_dispatched",
            lambda: self._dispatch("Implementer", _MIXED, req="REQ-1"),
        )

    def test_a_blocked_package_takes_no_dispatch_on_any_subject(self) -> None:
        self._dispatch("Implementer")
        self._block()
        self._refused(
            "blocked",
            "work_package_dispatched",
            lambda: self._dispatch("SpecReviewer", req="REQ-2"),
        )

    def test_work_before_commencement_is_refused(self) -> None:
        record_work_package_transition(
            self.catalog,
            self.ledger,
            TransitionRequest(
                work_package=_SECOND, to_state="initiated", evidence="e", operator_text="go"
            ),
        )
        self._refused(
            "commenced",
            "work_package_dispatched",
            lambda: self._dispatch("Implementer", _SECOND),
        )

    def test_a_dispatch_names_one_held_subject(self) -> None:
        for req, issue, pattern in (
            ("REQ-9", None, "baseline"),
            (None, 9, "carries"),
            ("REQ-2", 1183, "one subject"),
            (None, None, "one subject"),
        ):
            with self.subTest(req=req, issue=issue):
                request = DispatchRequest(
                    work_package=_FIRST, role="Implementer", model="m", req=req, issue=issue
                )
                self._refused(
                    pattern,
                    "work_package_dispatched",
                    lambda r=request: record_work_package_dispatch(self.catalog, self.ledger, r),
                )

    def test_a_repair_package_counts_against_its_issue(self) -> None:
        for letter in "ISISIS":
            self._dispatch(_NAMES[letter], _REPAIR, issue=1183)
        self._refused(
            "bound",
            "work_package_dispatched",
            lambda: self._dispatch("Implementer", _REPAIR, issue=1183),
        )
        self._dispatch("Implementer", _REPAIR, issue=1184)

    def test_an_unknown_role_and_an_empty_model_are_refused(self) -> None:
        self._refused("role", "work_package_dispatched", lambda: self._dispatch("Narrator"))
        request = DispatchRequest(work_package=_FIRST, role="Implementer", model=" ", req="REQ-1")
        self._refused(
            "model",
            "work_package_dispatched",
            lambda: record_work_package_dispatch(self.catalog, self.ledger, request),
        )


class AcrossPackages(_Run):
    """The count follows the REQ at its revision (ruling 15)."""

    def test_a_new_package_at_the_same_revision_starts_where_the_last_stopped(self) -> None:
        self._reach_the_bound()
        self._commence(_SECOND, ("REQ-1",))
        self._refused(
            "bound",
            "work_package_dispatched",
            lambda: self._dispatch("Implementer", _SECOND),
        )
        self._block(_SECOND)
        self.assertEqual(self._rows("work_package_blocked")[0]["at_bound"], ["REQ-1@2"])

    def test_reviews_booked_in_a_second_package_do_not_escape_the_bound(self) -> None:
        self._commence(_SECOND, ("REQ-1",))
        for _ in range(MAX_REVIEW_FIX_CYCLES + 1):
            self._dispatch("Implementer")
            self._dispatch("SpecReviewer", _SECOND)
        self._refused("bound", "work_package_dispatched", lambda: self._dispatch("Implementer"))

    def test_a_raised_revision_starts_clean(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("reopen", "REQ-1")
        self.catalog = _catalog(revision=3)
        self._commence(_SECOND, ("REQ-1",), revision=3)
        self._dispatch("Implementer", _SECOND)
        rows = self._rows("work_package_dispatched")
        self.assertEqual(rows[-1]["subject"], "REQ-1@3")

    def test_reopen_is_once_per_requirement_across_packages(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("reopen", "REQ-1")
        self.catalog = _catalog(revision=3)
        self._commence(_SECOND, ("REQ-1",), revision=3)
        self._reach_the_bound(_SECOND)
        self._block(_SECOND)
        self.assertEqual(self._rows("work_package_blocked")[-1]["reopened"], ["REQ-1"])
        self._refused(
            "once",
            "work_package_unblocked",
            lambda: self._unblock("reopen", "REQ-1", _SECOND),
        )
        self._unblock("hold", package=_SECOND)


class SingleDriver(_Run):
    def test_delivery_declares_it_and_the_same_bound_applies(self) -> None:
        for _ in range(MAX_REVIEW_FIX_CYCLES + 1):
            self._dispatch("SingleDriver", reason="cron, no subagents")
        self._refused(
            "bound",
            "work_package_dispatched",
            lambda: self._dispatch("SingleDriver", reason="cron, no subagents"),
        )

    def test_a_role_switch_does_not_escape_the_bound(self) -> None:
        for _ in range(MAX_REVIEW_FIX_CYCLES + 1):
            self._dispatch("SingleDriver", reason="cron, no subagents")
        self._refused("bound", "work_package_dispatched", lambda: self._dispatch("Implementer"))

    def test_a_repair_package_cannot_be_single_driver(self) -> None:
        self._refused(
            "repair",
            "work_package_dispatched",
            lambda: self._dispatch("SingleDriver", _REPAIR, issue=1183, reason="none"),
        )

    def test_the_reason_goes_with_the_declaration_alone(self) -> None:
        self._refused("reason", "work_package_dispatched", lambda: self._dispatch("SingleDriver"))
        self._refused(
            "reason",
            "work_package_dispatched",
            lambda: self._dispatch("Implementer", reason="why"),
        )


class Block(_Run):
    def test_the_block_carries_the_runtimes_facts_for_every_subject(self) -> None:
        self._reach_the_bound()
        self._dispatch("Implementer", req="REQ-2")
        self._block()
        row = self._rows("work_package_blocked")[0]
        self.assertEqual(row["fix_cycles"], {"REQ-1@2": MAX_REVIEW_FIX_CYCLES, "REQ-2@2": 0})
        self.assertEqual(row["bound"], MAX_REVIEW_FIX_CYCLES)
        self.assertEqual(row["at_bound"], ["REQ-1@2"])
        self.assertEqual(row["exits_used"], [])
        self.assertEqual(row["reopened"], [])

    def test_a_settled_subject_is_not_at_the_bound_again(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._block()
        row = self._rows("work_package_blocked")[1]
        self.assertEqual(row["at_bound"], [])
        self.assertEqual(row["exits_used"], ["hold"])

    def test_a_second_block_while_blocked_is_refused(self) -> None:
        self._block()
        self._refused("already blocked", "work_package_blocked", self._block)

    def test_an_uninitiated_package_takes_no_block(self) -> None:
        self._refused("not initiated", "work_package_blocked", lambda: self._block(_SECOND))

    def test_a_closed_package_takes_no_block(self) -> None:
        for move in (
            TransitionRequest(work_package=_FIRST, to_state="accepted", evidence="e"),
            TransitionRequest(
                work_package=_FIRST,
                to_state="closed",
                evidence="e",
                attestor="g0",
                decision="proceed",
                residual_risk="none",
            ),
        ):
            record_work_package_transition(self.catalog, self.ledger, move)
        self._refused("closed", "work_package_blocked", self._block)

    def test_a_block_holds_the_lifecycle(self) -> None:
        self._block()
        move = TransitionRequest(work_package=_FIRST, to_state="accepted", evidence="e")
        self._refused(
            "blocked",
            "work_package_transitioned",
            lambda: record_work_package_transition(self.catalog, self.ledger, move),
        )
        self._unblock()
        record_work_package_transition(self.catalog, self.ledger, move)


class Unblock(_Run):
    def test_a_block_below_the_bound_clears_on_a_ruling_alone(self) -> None:
        self._dispatch("Implementer")
        self._block()
        self._unblock()
        self._dispatch("SpecReviewer")

    def test_a_later_unrelated_block_clears_on_a_ruling_alone(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._dispatch("Implementer", req="REQ-2")
        self._block()
        self._unblock()

    def test_nothing_to_unblock_is_refused(self) -> None:
        self._refused("not blocked", "work_package_unblocked", self._unblock)

    def test_at_the_bound_the_unblock_names_an_exit(self) -> None:
        self._reach_the_bound()
        self._block()
        self._refused("exit", "work_package_unblocked", self._unblock)

    def test_an_exit_below_the_bound_is_refused(self) -> None:
        self._block()
        self._refused(
            "Nothing is at the bound",
            "work_package_unblocked",
            lambda: self._unblock("reopen", "REQ-1"),
        )

    def test_an_exit_outside_the_four_is_refused(self) -> None:
        self._reach_the_bound()
        self._block()
        self._refused(
            "another-cycle",
            "work_package_unblocked",
            lambda: self._unblock("another-cycle"),
        )

    def test_reopen_and_departure_name_their_requirement_and_hold_does_not(self) -> None:
        self._reach_the_bound()
        self._block()
        for exit_taken, req in (("reopen", None), ("departure", None), ("hold", "REQ-1")):
            with self.subTest(exit_taken=exit_taken):
                self._refused(
                    "REQ",
                    "work_package_unblocked",
                    lambda e=exit_taken, r=req: self._unblock(e, r),
                )

    def test_a_ruling_below_the_bound_names_no_requirement(self) -> None:
        self._block()
        self._refused("REQ", "work_package_unblocked", lambda: self._unblock(None, "REQ-1"))

    def test_the_requirement_is_the_one_at_the_bound(self) -> None:
        self._reach_the_bound()
        self._block()
        self._refused(
            "not at the bound",
            "work_package_unblocked",
            lambda: self._unblock("reopen", "REQ-2"),
        )

    def test_a_hold_covers_the_subjects_at_the_bound(self) -> None:
        self._reach_the_bound()
        self._reach_the_bound(req="REQ-2")
        self._block()
        self._unblock("hold")
        self.assertEqual(self._rows("work_package_unblocked")[0]["covered"], ["REQ-1@2", "REQ-2@2"])

    def test_a_departure_settles_its_requirement_alone(self) -> None:
        self._reach_the_bound()
        self._reach_the_bound(req="REQ-2")
        self._block()
        self._depart("DFS-1")
        self._unblock("departure", "REQ-1")
        self.assertEqual(self._rows("work_package_unblocked")[0]["covered"], ["REQ-1@2"])
        self._block()
        row = self._rows("work_package_blocked")[1]
        self.assertEqual(row["at_bound"], ["REQ-2@2"])

    def test_a_reopen_names_a_requirement_and_never_an_issue(self) -> None:
        for letter in "ISISIS":
            self._dispatch(_NAMES[letter], _REPAIR, issue=1183)
        self._block(_REPAIR)
        self._refused(
            "not at the bound",
            "work_package_unblocked",
            lambda: self._unblock("reopen", "#1183", _REPAIR),
        )

    def test_every_exit_stays_reachable_after_a_hold(self) -> None:
        for exit_taken, req in (("terminate", None), ("reopen", "REQ-1")):
            with self.subTest(exit_taken=exit_taken):
                self.setUp()
                self._reach_the_bound()
                self._block()
                self._unblock("hold")
                self._block()
                self.assertEqual(self._rows("work_package_blocked")[1]["held"], ["REQ-1@2"])
                self._unblock(exit_taken, req)
                with self.assertRaisesRegex(WorkPackageLedgerError, exit_taken):
                    self._dispatch("Implementer", req="REQ-2")

    def test_a_departure_stays_reachable_after_a_hold(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._block()
        self._depart("DFS-1")
        self._unblock("departure", "REQ-1")
        self._block()
        self.assertEqual(self._rows("work_package_blocked")[2]["held"], [])

    def test_a_held_subject_needs_no_exit_and_takes_no_second_hold(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._block()
        self._refused("already held", "work_package_unblocked", lambda: self._unblock("hold"))
        self._unblock()

    def test_a_second_hold_covers_only_the_new_subject(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._reach_the_bound(req="REQ-2")
        self._block()
        self._unblock("hold")
        self.assertEqual(self._rows("work_package_unblocked")[1]["covered"], ["REQ-2@2"])

    def test_terminate_covers_what_a_hold_left_open(self) -> None:
        self._reach_the_bound()
        self._block()
        self._unblock("hold")
        self._block()
        self._unblock("terminate")
        self.assertEqual(self._rows("work_package_unblocked")[1]["covered"], ["REQ-1@2"])

    def test_a_departure_rests_on_a_waiver_on_that_requirement_since_the_block(self) -> None:
        self._reach_the_bound()
        self._depart("DFS-1")
        self._block()
        self._depart("DFS-3")
        self._refused(
            "waiver",
            "work_package_unblocked",
            lambda: self._unblock("departure", "REQ-1"),
        )
        self._depart("DFS-1")
        self._unblock("departure", "REQ-1")

    def test_a_deviation_is_no_departure_exit(self) -> None:
        self._reach_the_bound(req="REQ-2")
        self._block()
        self._depart("DFS-2")
        self._refused(
            "waiver",
            "work_package_unblocked",
            lambda: self._unblock("departure", "REQ-2"),
        )

    def test_an_empty_ruling_is_refused(self) -> None:
        self._block()
        request = UnblockRequest(work_package=_FIRST, ruling=" ", operator="g0")
        self._refused(
            "ruling",
            "work_package_unblocked",
            lambda: record_work_package_unblock(self.catalog, self.ledger, request),
        )


if __name__ == "__main__":
    unittest.main()
