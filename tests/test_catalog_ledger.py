"""The catalog's Layer-2 writers: RO-3 tranche 2.

`docs/governance/harbor-ro3-requirements-store.md` § The events: an outcome moves
only along decision 4's lifecycle, and a REQ's proof carries one of three verdicts
against a revision the catalog holds. The transition grammar is the operator's
'Return-to-origin (Rec.)' selection of 2026-10-22.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.catalog_ledger import (
    CatalogLedgerError,
    outcome_state,
    record_outcome_transition,
    record_req_proof,
)
from gzkit.events import OutcomeTransitionedEvent, ReqProofRecordedEvent, parse_typed_event
from gzkit.ledger import Ledger
from gzkit.models.catalog import Catalog, Criterion, Outcome, Req
from gzkit.ontology.corpus import project_corpus

_LIFECYCLE = (
    "queued",
    "designing",
    "specified",
    "planned",
    "in_progress",
    "implemented",
    "reviewed",
    "verified",
    "validated",
    "released",
)


def _outcome(code: str = "H1") -> Outcome:
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


def _req(revision: int = 2, applies_to: tuple[str, ...] = ()) -> Req:
    return Req(
        id="REQ-1",
        member_of="H1",
        statement="A resumed session names its predecessor.",
        criteria=(
            Criterion(
                state_or_input="a handoff with a predecessor",
                required_outcome="the resume names it",
                evidence="the resume report",
            ),
        ),
        kind="BEHAVIOR",
        revision=revision,
        derives_from=("FR-001",),
        applies_to=applies_to,
    )


def _catalog(applies_to: tuple[str, ...] = ()) -> Catalog:
    return Catalog(families=(), outcomes=(_outcome(),), reqs=(_req(applies_to=applies_to),))


def _rows(ledger_path: Path) -> list[dict[str, object]]:
    if not ledger_path.is_file():
        return []
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


class _LedgerCase(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.path = Path(self._dir.name) / "ledger.jsonl"
        self.ledger = Ledger(self.path)

    def tearDown(self) -> None:
        self._dir.cleanup()

    def move(self, to_state: str, attestor: str | None = None) -> OutcomeTransitionedEvent:
        return record_outcome_transition(
            _catalog(), self.ledger, "H1", to_state, evidence="evt-1", attestor=attestor
        )

    def walk_to(self, state: str) -> None:
        for step in _LIFECYCLE[1 : _LIFECYCLE.index(state) + 1]:
            self.move(step, attestor="g0" if step == "validated" else None)


class OutcomeTransitionTests(_LedgerCase):
    def test_an_outcome_with_no_event_is_queued(self) -> None:
        self.assertEqual(outcome_state(self.ledger, "H1"), ("queued", None))

    def test_one_forward_step_is_booked_with_the_ledger_derived_origin(self) -> None:
        event = self.move("designing")
        rows = _rows(self.path)
        self.assertEqual(len(rows), 1)
        persisted = parse_typed_event(rows[0])
        self.assertIsInstance(persisted, OutcomeTransitionedEvent)
        self.assertEqual(
            (persisted.id, persisted.outcome, persisted.from_state, persisted.to_state),
            ("H1", "H1", "queued", "designing"),
        )
        self.assertEqual(persisted.evidence, "evt-1")
        self.assertEqual(event.to_state, "designing")
        self.assertEqual(outcome_state(self.ledger, "H1"), ("designing", None))

    def test_the_whole_main_chain_walks_one_step_at_a_time(self) -> None:
        self.walk_to("released")
        self.assertEqual(outcome_state(self.ledger, "H1"), ("released", None))
        self.assertEqual(len(_rows(self.path)), len(_LIFECYCLE) - 1)

    def test_a_skip_a_step_back_and_a_standstill_are_refused(self) -> None:
        self.walk_to("planned")
        for to_state in ("implemented", "specified", "planned", "queued"):
            with self.subTest(to_state=to_state), self.assertRaises(CatalogLedgerError):
                self.move(to_state)
        self.assertEqual(len(_rows(self.path)), 3)

    def test_nothing_moves_out_of_released(self) -> None:
        self.walk_to("released")
        for to_state in ("blocked", "deferred", "validated", "queued"):
            with self.subTest(to_state=to_state), self.assertRaises(CatalogLedgerError):
                self.move(to_state)

    def test_a_side_state_is_entered_from_queued_through_verified_only(self) -> None:
        for state in _LIFECYCLE[:8]:
            for side in ("blocked", "deferred"):
                with self.subTest(state=state, side=side):
                    self.tearDown()
                    self.setUp()
                    self.walk_to(state)
                    self.move(side)
                    self.assertEqual(outcome_state(self.ledger, "H1"), (side, state))
        for state in ("validated", "released"):
            with self.subTest(state=state):
                self.tearDown()
                self.setUp()
                self.walk_to(state)
                with self.assertRaises(CatalogLedgerError):
                    self.move("blocked")

    def test_leaving_a_side_state_returns_only_to_its_origin(self) -> None:
        self.walk_to("planned")
        self.move("blocked")
        for to_state in ("in_progress", "specified", "deferred", "queued"):
            with self.subTest(to_state=to_state), self.assertRaises(CatalogLedgerError):
                self.move(to_state)
        event = self.move("planned")
        self.assertEqual((event.from_state, event.to_state), ("blocked", "planned"))
        self.assertEqual(outcome_state(self.ledger, "H1"), ("planned", None))

    def test_validated_requires_an_attestor(self) -> None:
        self.walk_to("verified")
        for attestor in (None, "", "  "):
            with self.subTest(attestor=attestor), self.assertRaises(CatalogLedgerError):
                self.move("validated", attestor=attestor)
        event = self.move("validated", attestor="g0")
        self.assertEqual(event.attestor, "g0")

    def test_an_outcome_the_catalog_does_not_hold_is_refused(self) -> None:
        with self.assertRaises(CatalogLedgerError):
            record_outcome_transition(_catalog(), self.ledger, "H9", "designing", evidence="e")
        self.assertEqual(_rows(self.path), [])

    def test_an_unnamed_state_and_empty_evidence_are_refused(self) -> None:
        for to_state, evidence in (("withdrawn", "e"), ("designing", ""), ("designing", " ")):
            with (
                self.subTest(to_state=to_state, evidence=evidence),
                self.assertRaises(CatalogLedgerError),
            ):
                record_outcome_transition(
                    _catalog(), self.ledger, "H1", to_state, evidence=evidence
                )
        self.assertEqual(_rows(self.path), [])

    def test_another_outcomes_moves_do_not_count(self) -> None:
        catalog = Catalog(families=(), outcomes=(_outcome(), _outcome("H2")), reqs=())
        record_outcome_transition(catalog, self.ledger, "H2", "designing", evidence="e")
        self.assertEqual(outcome_state(self.ledger, "H1"), ("queued", None))


class CorpusAccountingTests(_LedgerCase):
    def test_a_ledger_carrying_both_catalog_events_replays_as_a_complete_corpus(self) -> None:
        self.move("designing")
        record_req_proof(
            _catalog(), self.ledger, "REQ-1", 2, commit="abc1234", verdict="UNKNOWN", evidence="e"
        )
        fidelity = project_corpus(self.ledger).fidelity
        self.assertTrue(fidelity.complete, fidelity)


class ReqProofTests(_LedgerCase):
    def prove(
        self,
        verdict: str = "SATISFIED",
        revision: int = 2,
        target: str | None = None,
        applies_to: tuple[str, ...] = (),
    ) -> ReqProofRecordedEvent:
        return record_req_proof(
            _catalog(applies_to),
            self.ledger,
            "REQ-1",
            revision,
            commit="abc1234",
            verdict=verdict,
            evidence="arb-step-1",
            target=target,
        )

    def test_each_of_the_three_verdicts_is_booked(self) -> None:
        for verdict in ("SATISFIED", "UNSATISFIED", "UNKNOWN"):
            with self.subTest(verdict=verdict):
                self.prove(verdict)
        rows = _rows(self.path)
        self.assertEqual(len(rows), 3)
        persisted = parse_typed_event(rows[0])
        self.assertIsInstance(persisted, ReqProofRecordedEvent)
        self.assertEqual(
            (persisted.id, persisted.req, persisted.revision, persisted.commit, persisted.verdict),
            ("REQ-1", "REQ-1", 2, "abc1234", "SATISFIED"),
        )
        self.assertIsNone(persisted.target)

    def test_a_fourth_verdict_is_refused(self) -> None:
        for verdict in ("PASS", "satisfied", "WAIVED", ""):
            with self.subTest(verdict=verdict), self.assertRaises(CatalogLedgerError):
                self.prove(verdict)
        self.assertEqual(_rows(self.path), [])

    def test_a_revision_the_catalog_does_not_hold_is_refused(self) -> None:
        for revision in (1, 3):
            with self.subTest(revision=revision), self.assertRaises(CatalogLedgerError):
                self.prove(revision=revision)
        self.assertEqual(_rows(self.path), [])

    def test_a_req_the_catalog_does_not_hold_is_refused(self) -> None:
        with self.assertRaises(CatalogLedgerError):
            record_req_proof(
                _catalog(),
                self.ledger,
                "REQ-2",
                2,
                commit="abc1234",
                verdict="SATISFIED",
                evidence="e",
            )
        self.assertEqual(_rows(self.path), [])

    def test_a_target_must_be_one_the_req_applies_to(self) -> None:
        with self.assertRaises(CatalogLedgerError):
            self.prove(target="windows", applies_to=("linux",))
        event = self.prove(target="linux", applies_to=("linux",))
        self.assertEqual(event.target, "linux")
        self.assertEqual(len(_rows(self.path)), 1)

    def test_empty_commit_and_evidence_are_refused(self) -> None:
        for field in ("commit", "evidence"):
            with self.subTest(field=field), self.assertRaises(CatalogLedgerError):
                record_req_proof(
                    _catalog(),
                    self.ledger,
                    "REQ-1",
                    2,
                    commit=" " if field == "commit" else "abc1234",
                    verdict="SATISFIED",
                    evidence=" " if field == "evidence" else "e",
                )
        self.assertEqual(_rows(self.path), [])


if __name__ == "__main__":
    unittest.main()
