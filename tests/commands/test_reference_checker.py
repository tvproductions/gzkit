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

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import override
from unittest import mock

from gzkit.commands.common import _prefix_match_candidates
from gzkit.commands.reference_checker import (
    ISSUES_PER_QUERY,
    IssueAnswer,
    IssueRead,
    _unique_prefix_entry,
    adr_ledger_state,
    gh_issue_read,
    gh_issue_reads,
    gh_issue_state,
    live_reference_checker,
    obpi_ledger_state,
)
from gzkit.handoff_api import ReferenceKind, ReferenceState, StepReference
from gzkit.ledger import Ledger


class TestForeignRepositoryReferencesAreNotResolvedLocally(unittest.TestCase):
    """A citation naming another repository resolves UNKNOWN, unread."""

    @override
    def setUp(self) -> None:
        self._root = tempfile.TemporaryDirectory()
        self.addCleanup(self._root.cleanup)
        self.root = Path(self._root.name)
        self.calls: list[str] = []
        patcher = mock.patch(
            "gzkit.commands.reference_checker.gh_issue_read",
            side_effect=self._record,
        )
        self.gh = patcher.start()
        self.addCleanup(patcher.stop)

    def _record(self, number: str, _root: Path) -> IssueRead:
        self.calls.append(number)
        return IssueRead(answer=IssueAnswer.CLOSED)

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


class TestObpiCitationsResolveFromTheLedger(unittest.TestCase):
    """An OBPI citation resolves against Layer-2, not against a Layer-3 index.

    ``adr-status.md`` is a derived view and reading it as truth is forbidden, but
    it was never the only repo-local surface: the ledger records OBPI completion
    directly, and ``gz obpi status`` already derives runtime state from it. The
    adapter answered ``UNKNOWN`` for both kinds on a rationale that holds only
    for ADR (GHI #1076).
    """

    @override
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

    @override
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

    def test_a_partially_attested_adr_is_settled(self) -> None:
        """``partial`` derives ``Completed`` too, so it settles by the same rule.

        Found by reading the cause->test table for empty right cells rather than
        by review of the diff: ``derive_adr_semantics`` maps
        ``{"completed", "partial"}`` to one lifecycle, and only the first member
        had a test. The arm defers to that derivation instead of re-deriving it,
        and this pins that deference.
        """
        adr = "ADR-0.2.1-example"
        self._write(
            self._created(adr, "2026-01-01T00:00:00+00:00"),
            self._attested(adr, "2026-01-02T00:00:00+00:00", "partial"),
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


class TestCitationsResolveThroughPrefixesTheProseActuallyWrites(unittest.TestCase):
    """A citation is the id the PROSE wrote, which is rarely the full slug (GHI #1079).

    ``_extract_references`` takes ``match.group(0)``, so the identifier is
    whatever the handoff author typed. Measured over every handoff in
    ``.gzkit/handoffs/`` before this change:

        citation shape        ADR    OBPI
        exact graph id        288       0
        unique prefix        1264     397
        ambiguous prefix        0     466
        no graph match        302       4

    Both ledger arms looked the citation up as an exact graph key, so the OBPI
    arm GHI #1076 shipped answered NONE of the 867 real OBPI citations.

    ``Ledger.resolve_artifact_id`` already folds renames and already resolves a
    unique ADR prefix (GHI #222); the fallback here extends that rule to the
    other kinds. An AMBIGUOUS prefix resolves ``UNKNOWN`` and is never guessed —
    GHI #826: "never on a prefix derived from it ... one prefix can name two
    OBPIs under two different parent ADRs." A parked or withdrawn sibling is not
    that hazard (GHI #1162): ``OBPI-0.35.0-08`` extends to a parked
    ``-forbid-pytest`` and the live ``-remember-post-append-advisory``, and names
    the live one. Ambiguity is two or more ACTIVE siblings.
    """

    @override
    def setUp(self) -> None:
        self._root = tempfile.TemporaryDirectory()
        self.addCleanup(self._root.cleanup)
        self.root = Path(self._root.name)
        self.ledger = self.root / ".gzkit" / "ledger.jsonl"
        self.ledger.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, *rows: dict[str, object]) -> None:
        self.ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    @staticmethod
    def _obpi(obpi_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_created",
            "id": obpi_id,
            "ts": ts,
            "parent": "ADR-0.1.0-example",
        }

    @staticmethod
    def _adr(adr_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": adr_id,
            "ts": ts,
            "lane": "heavy",
        }

    def test_a_unique_obpi_prefix_resolves(self) -> None:
        self._write(self._obpi("OBPI-0.1.0-01-only-one", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(
            obpi_ledger_state("OBPI-0.1.0-01", self.root),
            ReferenceState.LIVE,
            "the shape every real handoff writes resolved to nothing",
        )

    def test_an_ambiguous_obpi_prefix_is_unknown_not_guessed(self) -> None:
        """GHI #826's hazard: the prefix names two OBPIs, so it names neither."""
        self._write(
            self._obpi("OBPI-0.1.0-08-forbid-pytest", "2026-01-01T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-08-remember-advisory", "2026-01-02T00:00:00+00:00"),
        )

        self.assertEqual(
            obpi_ledger_state("OBPI-0.1.0-08", self.root),
            ReferenceState.UNKNOWN,
            "an ambiguous prefix was resolved to a sibling instead of refused",
        )

    def test_the_ambiguity_control_is_real(self) -> None:
        """Proves the previous test refuses because of ambiguity, not absence.

        Without this, a resolver that simply never matched prefixes would pass
        `test_an_ambiguous_obpi_prefix_is_unknown_not_guessed` for the wrong
        reason. Same ledger, same prefix, one sibling removed -> it resolves.
        """
        self._write(self._obpi("OBPI-0.1.0-08-forbid-pytest", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-08", self.root), ReferenceState.LIVE)

    @staticmethod
    def _parked(obpi_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_parked",
            "id": obpi_id,
            "ts": ts,
            "parent": "ADR-0.1.0-example",
            "parked_to": "ADR-pool.example",
            "reason": "pool_demotion",
        }

    @staticmethod
    def _withdrawn(obpi_id: str, ts: str) -> dict[str, object]:
        return {
            "schema": "gzkit.ledger.v1",
            "event": "obpi_withdrawn",
            "id": obpi_id,
            "ts": ts,
            "parent": "ADR-0.1.0-example",
            "reason": "phantom: rescoped; no on-disk file",
        }

    def test_a_parked_sibling_does_not_hide_the_live_obpi(self) -> None:
        """A pool demotion parks the old OBPI but the reused semver mints a live one (GHI #1162).

        The parked phantom is LIVE and the real OBPI is SETTLED, so resolving to
        the phantom and refusing both fail this test, each with its own verdict.
        """
        live = "OBPI-0.1.0-02-real-work"
        self._write(
            self._obpi("OBPI-0.1.0-02-demoted-work", "2026-01-01T00:00:00+00:00"),
            self._parked("OBPI-0.1.0-02-demoted-work", "2026-01-02T00:00:00+00:00"),
            self._obpi(live, "2026-01-03T00:00:00+00:00"),
            TestObpiCitationsResolveFromTheLedger._completed(live, "2026-01-04T00:00:00+00:00"),
        )

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-02", self.root), ReferenceState.SETTLED)

    def test_a_withdrawn_sibling_does_not_hide_the_live_obpi(self) -> None:
        """A withdrawn phantom is SETTLED and the real OBPI is LIVE: the pick is observable."""
        self._write(
            self._obpi("OBPI-0.1.0-03-phantom", "2026-01-01T00:00:00+00:00"),
            self._withdrawn("OBPI-0.1.0-03-phantom", "2026-01-02T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-03-real-work", "2026-01-03T00:00:00+00:00"),
        )

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-03", self.root), ReferenceState.LIVE)

    def test_a_prefix_whose_every_candidate_is_inactive_stays_ambiguous(self) -> None:
        """Inactive siblings are dropped only when a survivor remains; two parked name neither."""
        self._write(
            self._obpi("OBPI-0.1.0-04-first", "2026-01-01T00:00:00+00:00"),
            self._parked("OBPI-0.1.0-04-first", "2026-01-02T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-04-second", "2026-01-03T00:00:00+00:00"),
            self._parked("OBPI-0.1.0-04-second", "2026-01-04T00:00:00+00:00"),
        )

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-04", self.root), ReferenceState.UNKNOWN)

    def test_a_lone_withdrawn_obpi_cited_by_short_id_is_still_settled(self) -> None:
        """Dropping inactive keys must never empty the candidate set (GHI #1162).

        A withdrawn OBPI is a settled citation (ADR-0.0.71). When it is the only
        key its short id names, filtering it out would answer ``unknown`` for a
        reference the ledger settles.
        """
        self._write(
            self._obpi("OBPI-0.1.0-05-retired", "2026-01-01T00:00:00+00:00"),
            self._withdrawn("OBPI-0.1.0-05-retired", "2026-01-02T00:00:00+00:00"),
        )

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-05", self.root), ReferenceState.SETTLED)

    def test_the_citation_resolver_and_obpi_status_agree_on_every_shape(self) -> None:
        """One short id has one meaning in both resolvers (GHI #1162).

        ``gz obpi status`` resolves through ``common._prefix_match_candidates``;
        handoff citations through ``reference_checker._unique_prefix_entry``.
        Before GHI #1162 the first dropped phantoms and the second did not, so
        the same id resolved in one surface and was ``unknown`` in the other.
        """
        self._write(
            self._obpi("OBPI-0.1.0-02-demoted-work", "2026-01-01T00:00:00+00:00"),
            self._parked("OBPI-0.1.0-02-demoted-work", "2026-01-02T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-02-real-work", "2026-01-03T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-03-phantom", "2026-01-01T00:00:00+00:00"),
            self._withdrawn("OBPI-0.1.0-03-phantom", "2026-01-02T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-03-real-work", "2026-01-03T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-08-forbid-pytest", "2026-01-01T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-08-remember-advisory", "2026-01-02T00:00:00+00:00"),
            self._obpi("OBPI-0.1.0-09-only-one", "2026-01-01T00:00:00+00:00"),
        )
        graph = Ledger(self.ledger).get_artifact_graph()
        expected = {
            "OBPI-0.1.0-02": "OBPI-0.1.0-02-real-work",
            "OBPI-0.1.0-03": "OBPI-0.1.0-03-real-work",
            "OBPI-0.1.0-08": None,
            "OBPI-0.1.0-09": "OBPI-0.1.0-09-only-one",
        }

        for short_id, want in expected.items():
            with self.subTest(short_id=short_id):
                status_hits = _prefix_match_candidates(graph, short_id)
                status_pick = status_hits[0] if len(status_hits) == 1 else None
                citation_entry = _unique_prefix_entry(graph, short_id)
                citation_pick = next(
                    (key for key, info in graph.items() if info is citation_entry), None
                )
                self.assertEqual(status_pick, want)
                self.assertEqual(citation_pick, want)

    def test_a_prefix_must_stop_at_a_segment_boundary(self) -> None:
        """``OBPI-0.1.0-1`` is not a prefix of ``OBPI-0.1.0-10-x``.

        Matching raw text rather than ``<id>-`` would make every truncated
        citation resolve to a numerically adjacent OBPI — a wrong verdict
        wearing a right one's confidence. The corpus measurement found 4 such
        truncations (`OBPI-0.51.0-0`), produced by the extractor's own pattern.
        """
        self._write(self._obpi("OBPI-0.1.0-10-ten", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-1", self.root), ReferenceState.UNKNOWN)

    def test_a_unique_adr_prefix_resolves(self) -> None:
        self._write(
            self._adr("ADR-0.1.0-example", "2026-01-01T00:00:00+00:00"),
            {
                "schema": "gzkit.ledger.v1",
                "event": "audit_receipt_emitted",
                "id": "ADR-0.1.0-example",
                "ts": "2026-01-02T00:00:00+00:00",
                "receipt_event": "validated",
                "attestor": "g0",
                "evidence": {"adr_completion": "completed"},
            },
        )

        self.assertEqual(adr_ledger_state("ADR-0.1.0", self.root), ReferenceState.SETTLED)

    def test_an_exact_id_keeps_its_verdict(self) -> None:
        self._write(self._obpi("OBPI-0.1.0-01-exact", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(obpi_ledger_state("OBPI-0.1.0-01-exact", self.root), ReferenceState.LIVE)

    def test_a_prefix_matching_nothing_is_unknown(self) -> None:
        self._write(self._obpi("OBPI-0.1.0-01-only-one", "2026-01-01T00:00:00+00:00"))

        self.assertEqual(obpi_ledger_state("OBPI-9.9.9-99", self.root), ReferenceState.UNKNOWN)

    def test_a_renamed_artifact_resolves_through_its_current_id(self) -> None:
        """The rename fold is why this routes through ``resolve_artifact_id``."""
        self._write(
            self._obpi("OBPI-0.1.0-01-old-name", "2026-01-01T00:00:00+00:00"),
            {
                "schema": "gzkit.ledger.v1",
                "event": "artifact_renamed",
                "id": "OBPI-0.1.0-01-old-name",
                "ts": "2026-01-02T00:00:00+00:00",
                "new_id": "OBPI-0.1.0-01-new-name",
            },
        )

        self.assertEqual(
            obpi_ledger_state("OBPI-0.1.0-01-old-name", self.root), ReferenceState.LIVE
        )

    def test_a_foreign_prefix_citation_is_still_not_read_locally(self) -> None:
        self._write(self._obpi("OBPI-0.1.0-01-only-one", "2026-01-01T00:00:00+00:00"))
        check = live_reference_checker(self.root)

        state = check(
            StepReference(kind=ReferenceKind.OBPI, identifier="OBPI-0.1.0-01", repo="gz-skills")
        )

        self.assertEqual(state, ReferenceState.UNKNOWN)


class TestCitationExtractorRefusesWildcards(unittest.TestCase):
    """A wildcard over an id stem is notation, not a citation.

    Handoffs and briefs legitimately write shell and regex notation over an
    OBPI stem. Matching the digits before the wildcard invents an identifier
    the ledger never recorded, which then resolves UNKNOWN -- and an UNKNOWN
    that came from a truncation is indistinguishable from one that came from
    a real citation to a missing artifact.
    """

    def test_a_wildcard_suffix_yields_no_reference(self) -> None:
        from gzkit.handoff_api import _extract_references  # noqa: PLC0415

        for wildcard in ("OBPI-0.51.0-0x", "OBPI-0.0.70-0N", "OBPI-0.0.74-1[5-9]"):
            with self.subTest(wildcard=wildcard):
                refs = _extract_references(f"Re-claim per OBPI ({wildcard}) before work.")
                obpis = [r.identifier for r in refs if r.kind.name == "OBPI"]
                self.assertEqual(obpis, [], f"{wildcard} produced {obpis}")

    def test_a_real_obpi_citation_is_unaffected(self) -> None:
        """The extractor yields the SHORT form, and both spellings fold to it.

        It carries no slug-suffix group by design: a cited long slug reduces
        to ``OBPI-X.Y.Z-NN``, which is the key GHI #1079 taught
        ``_artifact_info`` to resolve by unique prefix. The refusal above is
        of ambiguity, not of breadth, so this folding must survive it.
        """
        from gzkit.handoff_api import _extract_references  # noqa: PLC0415

        refs = _extract_references(
            "OBPI-0.35.0-08 and OBPI-0.35.0-08-remember-post-append-advisory stay cited."
        )
        obpis = [r.identifier for r in refs if r.kind.name == "OBPI"]
        self.assertEqual(obpis, ["OBPI-0.35.0-08"])


#: One issue as GitHub's REST API returns it to `gh api --include` (headers, a blank
#: line, the body), observed 2026-11-20 against this repository.
def _answer(status: str, body: str) -> str:
    """One `gh api --include` answer in gh's own line endings (observed 2026-11-20).

    The status line ends LF and each header CRLF, then a blank CRLF line and the body.

    Returns:
        The stdout `gh api --include` prints for *status* and *body*.

    """
    return f"HTTP/2.0 {status}\nContent-Type: application/json\r\n\r\n{body}"


_ISSUE = '{"number": 1412, "state": "open", "created_at": "2026-10-18T13:00:00Z"}'


class TestGhIssueReadTellsMissingFromUnanswered(unittest.TestCase):
    """RP-12 ruling 182: an issue the API says does not exist is not an outage.

    Canonical: `gh help exit-codes` (gh exits 1 for any failure, so the exit code
    cannot tell them apart); https://docs.github.com/en/rest/issues/issues#get-an-issue
    (404 "Resource not found", 410 "Gone", a pull request carries `pull_request`);
    https://cli.github.com/manual/gh_api (`--include` prints the status line).
    """

    def _read(self, rc: int, out: str) -> IssueRead:
        with mock.patch(
            "gzkit.commands.reference_checker.run_exec", return_value=(rc, out, "")
        ) as run:
            read = gh_issue_read("1412", Path("."))
        self.assertEqual(
            run.call_args.args[0],
            ["gh", "api", "--include", "repos/{owner}/{repo}/issues/1412"],
        )
        return read

    def test_each_answer_the_api_gives(self) -> None:
        closed = _ISSUE.replace('"open"', '"closed"')
        pull = _ISSUE.replace("}", ', "pull_request": {}}')
        table = [
            ("open", 0, _answer("200 OK", _ISSUE), IssueAnswer.OPEN),
            ("closed", 0, _answer("200 OK", closed), IssueAnswer.CLOSED),
            (
                "not found",
                1,
                _answer("404 Not Found", '{"message": "Not Found"}'),
                IssueAnswer.MISSING,
            ),
            ("deleted", 1, _answer("410 Gone", '{"message": "Gone"}'), IssueAnswer.MISSING),
            ("a pull request", 0, _answer("200 OK", pull), IssueAnswer.MISSING),
            ("no answer", 1, "", IssueAnswer.UNANSWERED),
            ("a server error", 1, _answer("502 Bad Gateway", "{}"), IssueAnswer.UNANSWERED),
            ("an unreadable body", 0, _answer("200 OK", "not json"), IssueAnswer.UNANSWERED),
            ("a body not an object", 0, _answer("200 OK", "[]"), IssueAnswer.UNANSWERED),
            ("a body with no state", 0, _answer("200 OK", "{}"), IssueAnswer.UNANSWERED),
            ("a 200 the call failed on", 1, _answer("200 OK", _ISSUE), IssueAnswer.UNANSWERED),
        ]
        for case, rc, out, expected in table:
            with self.subTest(case=case):
                self.assertEqual(self._read(rc, out).answer, expected)

    def test_a_found_issue_carries_its_creation_time(self) -> None:
        read = self._read(0, _answer("200 OK", _ISSUE))
        self.assertEqual(read.created_at, datetime(2026, 10, 18, 13, tzinfo=UTC))

    def test_an_unusable_creation_time_is_none_and_the_answer_stands(self) -> None:
        for created in ("7", '"yesterday"', "null"):
            body = _ISSUE.replace('"2026-10-18T13:00:00Z"', created)
            with self.subTest(created=created):
                read = self._read(0, _answer("200 OK", body))
                self.assertEqual((read.answer, read.created_at), (IssueAnswer.OPEN, None))

    def test_the_handoff_verdict_reads_from_the_same_answer(self) -> None:
        table = [
            (_answer("200 OK", _ISSUE), 0, ReferenceState.LIVE),
            (_answer("404 Not Found", "{}"), 1, ReferenceState.UNKNOWN),
            ("", 1, ReferenceState.UNKNOWN),
        ]
        for out, rc, expected in table:
            with (
                self.subTest(out=out[:20]),
                mock.patch("gzkit.commands.reference_checker.run_exec", return_value=(rc, out, "")),
            ):
                self.assertEqual(gh_issue_state("1412", Path(".")), expected)


#: The GraphQL answer GitHub gives `gh api graphql` for an issueOrPullRequest batch,
#: observed 2026-11-20 against this repository: an Issue node carries its state and
#: creation time, a pull request is typed PullRequest, and a number with neither is
#: null beside a NOT_FOUND error whose path names the alias.
def _batch_answer(nodes: dict[str, object], not_found: tuple[str, ...] = ()) -> str:
    """One `gh api graphql` stdout for *nodes*, keyed by alias.

    Returns:
        The JSON gh prints, errors included when *not_found* names an alias.

    """
    payload: dict[str, object] = {"data": {"repository": nodes}}
    if not_found:
        payload["errors"] = [
            {"type": "NOT_FOUND", "path": ["repository", alias], "message": "Could not resolve"}
            for alias in not_found
        ]
    return json.dumps(payload)


def _issue_node(state: str, created: str | None = "2026-10-18T13:00:00Z") -> dict[str, object]:
    return {"__typename": "Issue", "state": state, "createdAt": created}


class TestGhIssueReadsAnswerManyIssuesInOneCall(unittest.TestCase):
    """GHI #1334: many issue numbers are answered by one `gh` call, not one call each.

    `gz adr status ADR-0.35.0` made 31 serial `gh api` round trips, ~0.63 s each, and
    took ~21 s, past the SessionStart hook's 15 s timeout. The batch must keep RP-12
    ruling 182's distinction: a number the API says is no issue is MISSING, and a
    call that gave no answer is UNANSWERED, never either read as the other.
    """

    def _reads(self, numbers: list[str], *outs: str) -> tuple[dict[str, IssueRead], mock.Mock]:
        answers = [(1 if '"errors"' in out else 0, out, "") for out in outs]
        with mock.patch("gzkit.commands.reference_checker.run_exec", side_effect=answers) as run:
            reads = gh_issue_reads(numbers, Path("."))
        return reads, run

    def test_each_answer_one_query_gives(self) -> None:
        # given one query's answer covering every shape GitHub returns, and some it must not
        out = _batch_answer(
            {
                "i11": _issue_node("OPEN"),
                "i12": _issue_node("CLOSED"),
                "i13": {"__typename": "PullRequest"},
                "i14": None,
                "i15": None,
                "i16": {"__typename": "Discussion", "state": "OPEN"},
                "i17": _issue_node("LOCKED"),
                "i18": "not a node",
                "i19": None,
            },
            not_found=("i14",),
        )
        payload = json.loads(out)
        payload["errors"].append({"type": "FORBIDDEN", "path": ["repository", "i19"]})
        # when the numbers are read together
        numbers = [str(n) for n in range(11, 20)]
        reads, run = self._reads(numbers, json.dumps(payload))
        # then one call answered all of them, each as the API said
        self.assertEqual(run.call_count, 1)
        created = datetime(2026, 10, 18, 13, tzinfo=UTC)
        unanswered = IssueRead(answer=IssueAnswer.UNANSWERED)
        expected = {
            "11": IssueRead(answer=IssueAnswer.OPEN, created_at=created),
            "12": IssueRead(answer=IssueAnswer.CLOSED, created_at=created),
            "13": IssueRead(answer=IssueAnswer.MISSING),
            "14": IssueRead(answer=IssueAnswer.MISSING),
            "15": unanswered,
            "16": unanswered,
            "17": unanswered,
            "18": unanswered,
            "19": unanswered,
        }
        self.assertEqual(reads, expected)

    def test_errors_that_are_not_a_list_name_no_missing_issue(self) -> None:
        # given an answer whose errors field is not the list GraphQL returns
        out = json.dumps({"data": {"repository": {"i14": None}}, "errors": {"i14": "x"}})
        # when the number is read
        reads, _ = self._reads(["14"], out)
        # then it is unanswered, never missing
        self.assertEqual(reads, {"14": IssueRead(answer=IssueAnswer.UNANSWERED)})

    def test_the_call_asks_this_repository_through_graphql(self) -> None:
        _, run = self._reads(["11"], _batch_answer({"i11": _issue_node("OPEN")}))
        argv = run.call_args.args[0]
        self.assertEqual(argv[:3], ["gh", "api", "graphql"])
        self.assertIn("owner={owner}", argv)
        self.assertIn("name={repo}", argv)

    def test_no_usable_answer_leaves_every_number_unanswered(self) -> None:
        for out in (
            "",
            "not json",
            "[]",
            '{"data": null, "errors": [{"type": "RATE_LIMITED"}]}',
            '{"data": {"repository": null}}',
        ):
            with self.subTest(out=out):
                reads, _ = self._reads(["11", "12"], out)
                self.assertEqual({read.answer for read in reads.values()}, {IssueAnswer.UNANSWERED})
                self.assertEqual(set(reads), {"11", "12"})

    def test_a_null_node_is_missing_only_when_its_own_alias_was_not_found(self) -> None:
        # given a NOT_FOUND error that names a different alias
        out = _batch_answer({"i14": None, "i15": None}, not_found=("i14",))
        # when both are read
        reads, _ = self._reads(["14", "15"], out)
        # then only the named one is missing
        self.assertEqual(reads["14"].answer, IssueAnswer.MISSING)
        self.assertEqual(reads["15"].answer, IssueAnswer.UNANSWERED)

    def test_many_numbers_are_asked_in_bounded_batches(self) -> None:
        # given more numbers than one query carries, some repeated
        numbers = [str(n) for n in range(1, 121)] + ["5", "7"]
        size = ISSUES_PER_QUERY
        chunks = [list(range(start, min(start + size, 121))) for start in range(1, 121, size)]
        outs = [_batch_answer({f"i{n}": _issue_node("OPEN") for n in chunk}) for chunk in chunks]
        # when they are read
        reads, run = self._reads(numbers, *outs)
        # then each number is asked once, in ceil(120 / size) calls
        self.assertEqual(run.call_count, len(chunks))
        self.assertEqual(set(reads), {str(n) for n in range(1, 121)})
        self.assertEqual({read.answer for read in reads.values()}, {IssueAnswer.OPEN})

    def test_an_identifier_that_is_not_a_number_never_reaches_the_query(self) -> None:
        reads, run = self._reads(["12){x}", "١٢"])
        run.assert_not_called()
        self.assertEqual({read.answer for read in reads.values()}, {IssueAnswer.UNANSWERED})


class TestLiveCheckerPrefetchesCitationsInOneRead(unittest.TestCase):
    """GHI #1334: the live checker answers a known set of GHI citations in one read.

    ``prefetch`` hands the batch transport every GHI the caller is about to check,
    so the per-citation calls that follow are answered from the memo. It never
    changes a verdict: the same answer maps to the same state on either transport.
    """

    @override
    def setUp(self) -> None:
        self.batches: list[list[str]] = []
        self.answers: dict[str, IssueAnswer] = {}
        reads = mock.patch(
            "gzkit.commands.reference_checker.gh_issue_reads", side_effect=self._reads
        )
        single = mock.patch("gzkit.commands.reference_checker.gh_issue_read")
        reads.start()
        self.single = single.start()
        self.addCleanup(reads.stop)
        self.addCleanup(single.stop)

    def _reads(self, numbers, _root: Path) -> dict[str, IssueRead]:
        asked = list(numbers)
        self.batches.append(asked)
        return {n: IssueRead(answer=self.answers.get(n, IssueAnswer.UNANSWERED)) for n in asked}

    @staticmethod
    def _ghi(number: str, repo: str | None = None) -> StepReference:
        return StepReference(kind=ReferenceKind.GHI, identifier=number, repo=repo)

    def test_every_prefetched_citation_is_answered_from_one_read(self) -> None:
        # given three local GHI citations GitHub answers closed, open and missing
        self.answers = {"11": IssueAnswer.CLOSED, "12": IssueAnswer.OPEN, "13": IssueAnswer.MISSING}
        check = live_reference_checker(Path("."))
        refs = [self._ghi("11"), self._ghi("12"), self._ghi("13")]
        # when the checker prefetches them and then checks each
        check.prefetch(refs)
        states = [check(ref) for ref in refs]
        # then one batch answered all three and no per-citation call was made
        self.assertEqual(self.batches, [["11", "12", "13"]])
        self.single.assert_not_called()
        self.assertEqual(
            states, [ReferenceState.SETTLED, ReferenceState.LIVE, ReferenceState.UNKNOWN]
        )

    def test_only_uncached_local_numeric_ghi_citations_are_asked(self) -> None:
        # given a checker that has already answered #11
        self.answers = {"11": IssueAnswer.CLOSED, "14": IssueAnswer.OPEN}
        check = live_reference_checker(Path("."))
        check.prefetch([self._ghi("11")])
        # when it prefetches #11 again beside citations it cannot or need not ask
        check.prefetch(
            [
                self._ghi("11"),
                self._ghi("14"),
                self._ghi("15", repo="gz-skills"),
                self._ghi("x7"),
                StepReference(kind=ReferenceKind.OBPI, identifier="OBPI-0.1.0-01"),
            ]
        )
        # then the second batch asked only #14
        self.assertEqual(self.batches, [["11"], ["14"]])

    def test_a_batch_with_nothing_to_ask_makes_no_call(self) -> None:
        check = live_reference_checker(Path("."))
        check.prefetch([self._ghi("15", repo="gz-skills")])
        self.assertEqual(self.batches, [])

    def test_a_batch_that_got_no_answer_latches_the_ghi_arm_off(self) -> None:
        # given gh offline: every number in the batch is unanswered
        check = live_reference_checker(Path("."))
        # when the checker prefetches and then checks
        check.prefetch([self._ghi("11"), self._ghi("12")])
        state = check(self._ghi("12"))
        check.prefetch([self._ghi("16")])
        # then the offline run cost one call, and the citation is unknown, never live
        self.assertEqual(state, ReferenceState.UNKNOWN)
        self.assertEqual(self.batches, [["11", "12"]])
        self.single.assert_not_called()

    def test_a_citation_already_answered_is_not_asked_again(self) -> None:
        # given a single read that answers #11 closed
        self.single.return_value = IssueRead(answer=IssueAnswer.CLOSED)
        check = live_reference_checker(Path("."))
        # when #11 is checked twice
        states = [check(self._ghi("11")), check(self._ghi("11"))]
        # then one read answered both
        self.assertEqual(states, [ReferenceState.SETTLED, ReferenceState.SETTLED])
        self.assertEqual(self.single.call_count, 1)

    def test_a_single_read_with_no_answer_latches_the_arm_off(self) -> None:
        # given gh unreachable for a single read
        self.single.return_value = IssueRead(answer=IssueAnswer.UNANSWERED)
        check = live_reference_checker(Path("."))
        # when two different citations are checked
        states = [check(self._ghi("11")), check(self._ghi("12"))]
        # then the second was not asked
        self.assertEqual(states, [ReferenceState.UNKNOWN, ReferenceState.UNKNOWN])
        self.assertEqual(self.single.call_count, 1)

    def test_a_number_an_answering_batch_left_unanswered_is_asked_singly(self) -> None:
        # given a batch that answered #11 and said nothing of #12
        self.answers = {"11": IssueAnswer.CLOSED}
        self.single.return_value = IssueRead(answer=IssueAnswer.OPEN)
        check = live_reference_checker(Path("."))
        check.prefetch([self._ghi("11"), self._ghi("12")])
        # when both are checked
        states = [check(self._ghi("11")), check(self._ghi("12"))]
        # then #12 got its own read, and #11 none
        self.assertEqual(states, [ReferenceState.SETTLED, ReferenceState.LIVE])
        self.single.assert_called_once_with("12", Path("."))

    def test_a_missing_issue_in_a_batch_does_not_latch_the_arm_off(self) -> None:
        # given a batch that answered, one of its numbers no issue
        self.answers = {"11": IssueAnswer.MISSING, "12": IssueAnswer.CLOSED}
        check = live_reference_checker(Path("."))
        check.prefetch([self._ghi("11"), self._ghi("12")])
        # when a later citation is prefetched
        self.answers["16"] = IssueAnswer.OPEN
        check.prefetch([self._ghi("16")])
        # then it is still asked and answered
        self.assertEqual(self.batches, [["11", "12"], ["16"]])
        self.assertEqual(check(self._ghi("16")), ReferenceState.LIVE)

    def test_a_missing_issue_in_a_single_read_does_not_latch_the_arm_off(self) -> None:
        """GHI #1335: a MISSING read is an answer, so later citations are still asked."""
        # given single reads answering #999999 no issue and #12 open
        answers = {"999999": IssueAnswer.MISSING, "12": IssueAnswer.OPEN}
        self.single.side_effect = lambda number, _root: IssueRead(answer=answers[number])
        check = live_reference_checker(Path("."))
        # when the missing number is checked, then the open one
        states = [check(self._ghi("999999")), check(self._ghi("12"))]
        # then the missing one is unknown, never live, and the open one was asked and is live
        self.assertEqual(states, [ReferenceState.UNKNOWN, ReferenceState.LIVE])
        self.assertEqual([c.args[0] for c in self.single.call_args_list], ["999999", "12"])

    def test_both_transports_latch_on_the_same_answers(self) -> None:
        """GHI #1335 and RP-12 ruling 182: one answer gives one verdict and one latch."""
        for answer, latched in ((IssueAnswer.MISSING, False), (IssueAnswer.UNANSWERED, True)):
            with self.subTest(answer=answer):
                # given #11 answered `answer` and #12 open, on each transport
                self.answers = {"11": answer, "12": IssueAnswer.OPEN}
                self.single.side_effect = lambda n, _r: IssueRead(answer=self.answers[n])
                batch, single = live_reference_checker(Path(".")), live_reference_checker(Path("."))
                # when #11 is read first, then #12
                batch.prefetch([self._ghi("11")])
                batch_states = [batch(self._ghi("11")), batch(self._ghi("12"))]
                single_states = [single(self._ghi("11")), single(self._ghi("12"))]
                # then both give #11 the same verdict and latch, or not, the same way
                self.assertEqual(batch_states, single_states)
                expected = ReferenceState.UNKNOWN if latched else ReferenceState.LIVE
                self.assertEqual(single_states[1], expected)


if __name__ == "__main__":
    unittest.main()
