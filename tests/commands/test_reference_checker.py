"""BEHAVIOR tests for the ``gh`` adapter behind the ``ReferenceChecker`` port.

The adapter reads ONE repository — the project root it is built for. A citation
that names another repository is outside what it can answer, and answering it
from the local repository is worse than not answering: the number resolves, so
the wrong verdict arrives wearing the same confidence as a right one.

Observed instance (2026-09-21): a handoff advised "Rule on gz-skills#1". That
issue is OPEN in ``tvproductions/gz-skills``; ``tvproductions/gzkit`` issue 1 is
a closed Gate-5 attestation from the project's first week. The adapter resolved
the local one and the annotator stamped the step ``gz-skills#1 [settled]``.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.reference_checker import (
    adr_ledger_state,
    live_reference_checker,
    obpi_ledger_state,
)
from gzkit.handoff_api import ReferenceKind, ReferenceState, StepReference


class TestForeignRepositoryReferencesAreNotResolvedLocally(unittest.TestCase):
    """A citation naming another repository resolves UNKNOWN, unread."""

    def setUp(self) -> None:
        self._root = tempfile.TemporaryDirectory()
        self.addCleanup(self._root.cleanup)
        self.root = Path(self._root.name)
        self.calls: list[str] = []
        patcher = mock.patch(
            "gzkit.commands.reference_checker.gh_issue_state",
            side_effect=self._record,
        )
        self.gh = patcher.start()
        self.addCleanup(patcher.stop)

    def _record(self, number: str, _root: Path) -> ReferenceState:
        self.calls.append(number)
        return ReferenceState.SETTLED

    def test_foreign_citation_is_never_asked_of_the_local_repository(self) -> None:
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.GHI, identifier="1", repo="gz-skills"))

        self.assertEqual(state, ReferenceState.UNKNOWN)
        self.assertEqual(
            self.calls,
            [],
            "the local repository was read for another repository's issue number",
        )

    def test_local_citation_is_still_resolved(self) -> None:
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.GHI, identifier="1069"))

        self.assertEqual(state, ReferenceState.SETTLED)
        self.assertEqual(self.calls, ["1069"])

    def test_a_foreign_citation_does_not_latch_the_adapter_off(self) -> None:
        """Refusing to answer is not a failure — the next local citation still resolves.

        The adapter latches off after an UNKNOWN from ``gh`` so an offline run
        costs one failed call. A foreign reference never reaches ``gh``, so it
        must not consume that latch and blind every citation after it.
        """
        check = live_reference_checker(self.root)

        check(StepReference(kind=ReferenceKind.GHI, identifier="4", repo="owner/other"))
        state = check(StepReference(kind=ReferenceKind.GHI, identifier="1069"))

        self.assertEqual(state, ReferenceState.SETTLED)
        self.assertEqual(self.calls, ["1069"])

    def test_same_number_in_two_repositories_does_not_share_one_verdict(self) -> None:
        """The memo is keyed per citation, so a local answer cannot leak abroad."""
        check = live_reference_checker(self.root)

        local = check(StepReference(kind=ReferenceKind.GHI, identifier="1"))
        foreign = check(StepReference(kind=ReferenceKind.GHI, identifier="1", repo="gz-skills"))

        self.assertEqual(local, ReferenceState.SETTLED)
        self.assertEqual(foreign, ReferenceState.UNKNOWN)


if __name__ == "__main__":
    unittest.main()


class TestObpiCitationsResolveFromTheLedger(unittest.TestCase):
    """An OBPI citation resolves against Layer-2, not against a Layer-3 index.

    ``adr-status.md`` is a derived view and reading it as truth is forbidden, but
    it was never the only repo-local surface: the ledger records OBPI completion
    directly, and ``gz obpi status`` already derives runtime state from it. The
    adapter answered ``UNKNOWN`` for both kinds on a rationale that holds only
    for ADR (GHI #1076).
    """

    def setUp(self) -> None:
        self._root = tempfile.TemporaryDirectory()
        self.addCleanup(self._root.cleanup)
        self.root = Path(self._root.name)
        self.ledger = self.root / ".gzkit" / "ledger.jsonl"
        self.ledger.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, *rows: dict[str, object]) -> None:
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    @staticmethod
    def _created(obpi_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_created",
            "id": obpi_id,
            "ts": ts,
            "parent": "ADR-0.1.0-example",
        }

    @staticmethod
    def _completed(obpi_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_receipt_emitted",
            "id": obpi_id,
            "ts": ts,
            "parent": "ADR-0.1.0-example",
            "receipt_event": "completed",
            "attestor": "g0",
            "obpi_completion": "attested_completed",
            "anchor": {"commit": "19f5230", "semver": "0.1.0"},
        }

    @staticmethod
    def _withdrawn(obpi_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_withdrawn",
            "id": obpi_id,
            "ts": ts,
            "parent": "ADR-0.1.0-example",
            "reason": "phantom from promotion auto-generation",
        }

    def test_an_attested_complete_obpi_is_settled(self) -> None:
        obpi = "OBPI-0.1.0-01-example"
        self._write(
            self._created(obpi, "2026-01-01T00:00:00+00:00"),
            self._completed(obpi, "2026-01-02T00:00:00+00:00"),
        )

        self.assertEqual(obpi_ledger_state(obpi, self.root), ReferenceState.SETTLED)

    def test_a_receipt_without_a_completion_field_is_live(self) -> None:
        """A receipt is not a completion. ``obpi_completion`` is what records one.

        ``_apply_obpi_receipt_metadata`` sets ``ledger_completed`` only when the
        receipt carries ``obpi_completion``; a bare ``receipt_event: completed``
        leaves the ledger's completion field unset, so the work is not recorded
        done and the citation is still live.
        """
        obpi = "OBPI-0.1.0-08-example"
        receipt = self._completed(obpi, "2026-01-02T00:00:00+00:00")
        del receipt["obpi_completion"]
        self._write(self._created(obpi, "2026-01-01T00:00:00+00:00"), receipt)

        self.assertEqual(obpi_ledger_state(obpi, self.root), ReferenceState.LIVE)

    def test_an_obpi_with_no_completion_record_is_live(self) -> None:
        obpi = "OBPI-0.1.0-02-example"
        self._write(self._created(obpi, "2026-01-01T00:00:00+00:00"))

        self.assertEqual(obpi_ledger_state(obpi, self.root), ReferenceState.LIVE)

    def test_a_plain_completed_obpi_is_settled(self) -> None:
        """``completed`` settles a citation exactly as ``attested_completed`` does.

        Both are members of ``_SETTLED_COMPLETIONS`` and both set
        ``ledger_completed``; a predicate reaching only the attested form would
        report 36 completed OBPIs in this repository as still live.
        """
        obpi = "OBPI-0.1.0-09-example"
        receipt = self._completed(obpi, "2026-01-02T00:00:00+00:00")
        receipt["obpi_completion"] = "completed"
        self._write(self._created(obpi, "2026-01-01T00:00:00+00:00"), receipt)

        self.assertEqual(obpi_ledger_state(obpi, self.root), ReferenceState.SETTLED)

    def test_a_repudiated_completion_is_live_again(self) -> None:
        """Repudiation reverses a completion while the work intent stands.

        ADR-0.0.71: a repudiated OBPI is re-completable by genuine
        re-attestation, so the citation is LIVE. The check must sit ahead of the
        completion check, because ``_apply_obpi_completion_repudiated_metadata``
        clears ``ledger_completed`` but leaves ``obpi_completion`` in place — so
        a completion-first predicate would read the stale receipt and report
        settled work that was explicitly un-completed.
        """
        obpi = "OBPI-0.1.0-10-example"
        self._write(
            self._created(obpi, "2026-01-01T00:00:00+00:00"),
            self._completed(obpi, "2026-01-02T00:00:00+00:00"),
            {
                "schema": "gzkit.ledger.v1",
                "event": "obpi_completion_repudiated",
                "id": obpi,
                "ts": "2026-01-03T00:00:00+00:00",
                "parent": "ADR-0.1.0-example",
                "cause": "model-induced-fabrication",
                "attestor": "g0",
                "reason": "evidence was invalid",
            },
        )

        self.assertEqual(obpi_ledger_state(obpi, self.root), ReferenceState.LIVE)

    def test_a_withdrawn_obpi_is_settled(self) -> None:
        obpi = "OBPI-0.1.0-03-example"
        self._write(
            self._created(obpi, "2026-01-01T00:00:00+00:00"),
            self._withdrawn(obpi, "2026-01-02T00:00:00+00:00"),
        )

        self.assertEqual(obpi_ledger_state(obpi, self.root), ReferenceState.SETTLED)

    def test_an_obpi_absent_from_the_ledger_is_unknown(self) -> None:
        self._write(self._created("OBPI-0.1.0-04-example", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(
            obpi_ledger_state("OBPI-9.9.9-99-never-recorded", self.root),
            ReferenceState.UNKNOWN,
        )

    def test_a_missing_ledger_is_unknown_not_live(self) -> None:
        self.assertEqual(
            obpi_ledger_state("OBPI-0.1.0-05-example", self.root),
            ReferenceState.UNKNOWN,
            "an unreadable Layer-2 surface must not degrade to a verified verdict",
        )

    def test_the_checker_routes_obpi_citations_to_the_ledger(self) -> None:
        obpi = "OBPI-0.1.0-06-example"
        self._write(
            self._created(obpi, "2026-01-01T00:00:00+00:00"),
            self._withdrawn(obpi, "2026-01-02T00:00:00+00:00"),
        )
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.OBPI, identifier=obpi))

        self.assertEqual(state, ReferenceState.SETTLED)

    def test_a_foreign_obpi_citation_is_not_read_locally(self) -> None:
        check = live_reference_checker(self.root)

        state = check(
            StepReference(
                kind=ReferenceKind.OBPI, identifier="OBPI-0.1.0-07-example", repo="gz-skills"
            )
        )

        self.assertEqual(state, ReferenceState.UNKNOWN)


class TestAdrCitationsResolveFromRecordedCloseout(unittest.TestCase):
    """An ADR citation is SETTLED when its closeout is RECORDED (GHI #1078).

    GHI #1076 shipped the OBPI arm and left this one UNKNOWN, because what
    ``SETTLED`` asserts for an ADR was unruled: closeout recorded complete, or
    every child OBPI attested. Operator ruling 2026-09-21 chose the first.

    The two readings agree on 84 of this repository's 85 candidate ADRs. The one
    divergence is the whole point of the ruling: an ADR whose children are all
    attested but whose closeout was never recorded still has gate-covenant work,
    so it reads LIVE and a step advising it is not silenced.
    """

    def setUp(self) -> None:
        self._root = tempfile.TemporaryDirectory()
        self.addCleanup(self._root.cleanup)
        self.root = Path(self._root.name)
        self.ledger = self.root / ".gzkit" / "ledger.jsonl"
        self.ledger.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, *rows: dict[str, object]) -> None:
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    @staticmethod
    def _created(adr_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": adr_id,
            "ts": ts,
            "lane": "heavy",
        }

    @staticmethod
    def _validated(adr_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "audit_receipt_emitted",
            "id": adr_id,
            "ts": ts,
            "receipt_event": "validated",
            "attestor": "g0",
            "evidence": {"adr_completion": "completed"},
        }

    @staticmethod
    def _attested(adr_id: str, ts: str, status: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "attested",
            "id": adr_id,
            "ts": ts,
            "status": status,
            "by": "g0",
        }

    def test_a_validated_adr_is_settled(self) -> None:
        adr = "ADR-0.1.0-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            self._validated(adr, "2026-01-02T00:00:00+00:00"),
        )

        self.assertEqual(adr_ledger_state(adr, self.root), ReferenceState.SETTLED)

    def test_an_attested_completed_adr_is_settled(self) -> None:
        adr = "ADR-0.2.0-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            self._attested(adr, "2026-01-02T00:00:00+00:00", "completed"),
        )

        self.assertEqual(adr_ledger_state(adr, self.root), ReferenceState.SETTLED)

    def test_an_abandoned_adr_is_settled(self) -> None:
        """``dropped`` attestation reads Abandoned, and abandoned work is not advised.

        SETTLED is the GHI sense — stop advising this — not a claim that the work
        shipped. This repository holds zero Abandoned ADRs today, so the verdict
        exists only here; that is stated in GHI #1078 rather than buried in a
        predicate.
        """
        adr = "ADR-0.3.0-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            self._attested(adr, "2026-01-02T00:00:00+00:00", "dropped"),
        )

        self.assertEqual(adr_ledger_state(adr, self.root), ReferenceState.SETTLED)

    def test_a_pending_adr_is_live(self) -> None:
        adr = "ADR-0.4.0-example"
        self._write(self._created(adr, "2026-01-01T00:00:00+00:00"))

        self.assertEqual(adr_ledger_state(adr, self.root), ReferenceState.LIVE)

    def test_an_adr_whose_closeout_is_merely_initiated_is_live(self) -> None:
        """Initiated is not recorded. This is the ruling's load-bearing distinction.

        ``derive_adr_semantics`` reads a bare ``closeout_initiated`` as lifecycle
        ``Pending`` with phase ``closeout_initiated``. A predicate keyed on the
        phase rather than the lifecycle would settle an ADR whose ceremony had
        only begun — 142 ``closeout_initiated`` events stand in this ledger
        against 84 ADRs that actually reach a closed-out lifecycle.
        """
        adr = "ADR-0.5.0-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            {
                "schema": "gzkit.ledger.v1",
                "event": "closeout_initiated",
                "id": adr,
                "ts": "2026-01-02T00:00:00+00:00",
                "by": "g0",
                "mode": "heavy",
            },
        )

        self.assertEqual(adr_ledger_state(adr, self.root), ReferenceState.LIVE)

    def test_an_adr_absent_from_the_ledger_is_unknown(self) -> None:
        self._write(self._created("ADR-0.6.0-example", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(
            adr_ledger_state("ADR-9.9.9-never-recorded", self.root),
            ReferenceState.UNKNOWN,
        )

    def test_a_missing_ledger_is_unknown_not_live(self) -> None:
        self.assertEqual(
            adr_ledger_state("ADR-0.7.0-example", self.root),
            ReferenceState.UNKNOWN,
            "an unreadable Layer-2 surface must not degrade to a verified verdict",
        )

    def test_an_obpi_id_is_not_answered_by_the_adr_arm(self) -> None:
        """The arms read different fields of the same graph; ids must not cross.

        An OBPI node carries no ``validated`` closeout of the ADR kind, so an
        OBPI id reaching this arm would read LIVE regardless of its completion —
        a wrong verdict wearing a right one's confidence.
        """
        obpi = "OBPI-0.1.0-01-example"
        self._write(
            {
                "schema": "gzkit.ledger.v1",
                "event": "obpi_created",
                "id": obpi,
                "ts": "2026-01-01T00:00:00+00:00",
                "parent": "ADR-0.1.0-example",
            },
        )
        check = live_reference_checker(self.root)

        self.assertEqual(
            check(StepReference(kind=ReferenceKind.OBPI, identifier=obpi)),
            ReferenceState.LIVE,
        )

    def test_the_checker_routes_adr_citations_to_the_ledger(self) -> None:
        adr = "ADR-0.8.0-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            self._validated(adr, "2026-01-02T00:00:00+00:00"),
        )
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.ADR, identifier=adr))

        self.assertEqual(state, ReferenceState.SETTLED)

    def test_a_foreign_adr_citation_is_not_read_locally(self) -> None:
        adr = "ADR-0.9.0-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            self._validated(adr, "2026-01-02T00:00:00+00:00"),
        )
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.ADR, identifier=adr, repo="gz-skills"))

        self.assertEqual(state, ReferenceState.UNKNOWN)
