"""Which QUESTION each ledger consumer asks, and which stream answers it (GHI #611).

`Ledger.read_all()` was made correction-aware by default, which was right: netting
per call site is the hand-patching the primitive exists to end, and it fails OPEN
because a consumer written next year is correction-blind unless its author
remembers. But "corrected" is not one stream — it is two, and the default is the
narrower of them:

* :func:`~gzkit.ledger_corrections.live_events` — *what is in force NOW*. Drops
  `void` and `discharged`.
* :func:`~gzkit.ledger_corrections.evidence_events` — *what is TRUE*. Drops only
  `void`, because discharging a row asserts its condition ended, never that it
  was false.
* `Ledger.read_history()` — the raw append-only history, for readers whose subject
  genuinely is every row.

Flipping the default therefore moved every consumer to the STATE reading,
including the ones asking an evidence question. This module tests the three
consumers where the difference is observable, through the behavior an operator
actually sees — archive eligibility, Stage-2 reconciliation readiness, Stage-5
completion — rather than through the helper's return value, because a helper can
be right while its caller ignores it.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.ledger_corrections import CORRECTION_EVENT


def _row(event: str, ident: str, ts: str, **payload: Any) -> dict[str, Any]:
    return {"schema": "gzkit.ledger.v1", "event": event, "id": ident, "ts": ts, **payload}


def _correction(
    subject: dict[str, Any], disposition: str, *, ts: str, cause: str
) -> dict[str, Any]:
    return _row(
        CORRECTION_EVENT,
        subject["id"],
        ts,
        subject_event=subject["event"],
        subject_id=subject["id"],
        subject_ts=subject["ts"],
        disposition=disposition,
        cause=cause,
        attestor="g0",
        reason="corrected for the test's stated premise",
    )


#: mtime for the allowlist domain: 2026-01-01, comfortably before every
#: receipt timestamp in this module, so freshness never decides these tests.
_DOMAIN_MTIME = datetime(2026, 1, 1, tzinfo=UTC).timestamp()


def _write_ledger(root: Path, rows: list[dict[str, Any]]) -> None:
    path = root / ".gzkit" / "ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8"
    )


class DischargedLockReleaseStillProtectsItsHandoff(unittest.TestCase):
    """A discharged lock release is EVIDENCE, so its handoff stays protected.

    `handoff_archive._locked_paths` reads `obpi_lock_released` events to learn
    which handoff files a token surrender cited, and `plan_archive` refuses to
    archive those. It reaches the ledger through `Ledger.query()`, which now nets
    to the LIVE stream — so discharging a lock release deletes the protection and
    the handoff it names becomes archivable.

    That is the wrong reading of `discharged`. The release HAPPENED; discharging
    it says the condition it recorded has ended, never that the surrender was
    fictitious. The file it cited is still the exchange record for a real token
    handover. Only `void` — this never happened — should return the handoff to
    the eligible pool.
    """

    HANDOFF_REL = ".gzkit/handoffs/20260101T000000Z-subject.md"

    def _plan(self, rows: list[dict[str, Any]]) -> Any:
        from gzkit.handoff_archive import plan_archive

        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        handoff = root / self.HANDOFF_REL
        handoff.parent.mkdir(parents=True, exist_ok=True)
        # Quoted, matching what `gz handoff create` writes: unquoted YAML yields a
        # datetime object, `_parse_ts` requires a str, and the handoff would land in
        # `skipped_undatable` — a pass for a reason that has nothing to do with locks.
        handoff.write_text(
            "---\ntimestamp: '2026-01-01T00:00:00Z'\n---\n\n# Subject handoff\n",
            encoding="utf-8",
        )
        _write_ledger(root, rows)
        return plan_archive(
            base_path=root, older_than_days=30, now=datetime(2026, 9, 6, tzinfo=UTC)
        )

    @property
    def _release(self) -> dict[str, Any]:
        return _row(
            "obpi_lock_released",
            "OBPI-X",
            "2026-01-02T00:00:00+00:00",
            agent="implementer",
            handoff_path=self.HANDOFF_REL,
        )

    def test_an_uncorrected_release_protects_the_handoff(self) -> None:
        """Guard: without this the assertions below could pass for the wrong reason."""
        plan = self._plan([self._release])
        self.assertEqual(plan.skipped_locked, [self.HANDOFF_REL])
        self.assertEqual(plan.eligible, [])

    def test_a_discharged_release_still_protects_the_handoff(self) -> None:
        plan = self._plan(
            [
                self._release,
                _correction(
                    self._release,
                    "discharged",
                    ts="2026-02-01T00:00:00+00:00",
                    cause="condition-resolved",
                ),
            ]
        )
        self.assertEqual(
            plan.skipped_locked,
            [self.HANDOFF_REL],
            "discharging the lock release removed archival protection from the "
            "exchange record it cited — a discharged row is still evidence",
        )
        self.assertEqual(plan.eligible, [])

    def test_a_voided_release_returns_the_handoff_to_the_eligible_pool(self) -> None:
        """`void` is the disposition that SHOULD drop it: the release never happened."""
        plan = self._plan(
            [
                self._release,
                _correction(
                    self._release, "void", ts="2026-02-01T00:00:00+00:00", cause="agent-error"
                ),
            ]
        )
        self.assertEqual(plan.skipped_locked, [])
        self.assertEqual(plan.eligible, [self.HANDOFF_REL])


class VoidedReconcileReceiptsStopCountingAsReceipts(unittest.TestCase):
    """The two reconciliation readers parse the JSONL themselves, so corrections miss them.

    `check_reconcile_receipt_gate` (Stage-2 entry) and `_latest_reconcile_receipt`
    (Stage-5 completion) each `read_text().splitlines()` over `.gzkit/ledger.jsonl`
    and scan for the newest `brief_reconciled` event. Neither goes through
    `Ledger`, so making `read_all()` correction-aware reached neither: a voided
    receipt — one recorded in error, which the operator has said was never a real
    reconciliation — still opened Stage 2 and still satisfied Stage 5.

    A gate that credits a receipt its own ledger says never happened is the
    laundering the correction primitive exists to refuse.
    """

    OBPI = "OBPI-0.0.37-08"

    def _receipt(self, ts: str, *, has_drift: bool = False) -> dict[str, Any]:
        return _row(
            "brief_reconciled",
            self.OBPI,
            ts,
            brief_id=self.OBPI,
            has_drift=has_drift,
            allowlist_delta_count=0,
            discovery_delta_count=0,
            verification_delta_count=0,
            req_count_delta=0,
            citation_delta_count=0,
        )

    def _root(self, rows: list[dict[str, Any]]) -> tuple[Path, Path]:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        brief = root / "brief.md"
        brief.write_text(
            f"---\nid: {self.OBPI}\n---\n\n## Allowed Paths\n\n- `src/gzkit/subject.py`\n",
            encoding="utf-8",
        )
        # The allowlist domain must EXIST and predate the receipt, or the gate
        # blocks on staleness and every assertion here reports the wrong reason.
        subject = root / "src" / "gzkit" / "subject.py"
        subject.parent.mkdir(parents=True, exist_ok=True)
        subject.write_text("", encoding="utf-8")
        os.utime(subject, (_DOMAIN_MTIME, _DOMAIN_MTIME))
        _write_ledger(root, rows)
        return root, brief

    def _stage2_blockers(self, rows: list[dict[str, Any]]) -> list[str]:
        from gzkit.pipeline_runtime import check_reconcile_receipt_gate

        root, brief = self._root(rows)
        return check_reconcile_receipt_gate(self.OBPI, brief, root)

    def _completion_receipt(self, rows: list[dict[str, Any]]) -> Any:
        from gzkit.commands.obpi_complete import _latest_reconcile_receipt

        root, _brief = self._root(rows)
        return _latest_reconcile_receipt(self.OBPI, root)[0]

    def test_an_uncorrected_receipt_opens_stage_two(self) -> None:
        """Guard: the gate must be satisfiable, or every assertion below is vacuous."""
        self.assertEqual(self._stage2_blockers([self._receipt("2026-09-01T00:00:00+00:00")]), [])

    def test_a_voided_receipt_no_longer_opens_stage_two(self) -> None:
        receipt = self._receipt("2026-09-01T00:00:00+00:00")
        blockers = self._stage2_blockers(
            [
                receipt,
                _correction(receipt, "void", ts="2026-09-02T00:00:00+00:00", cause="agent-error"),
            ]
        )
        self.assertTrue(blockers, "a voided brief_reconciled receipt still opened Stage 2 entry")
        self.assertIn("no `brief_reconciled` receipt", blockers[0])

    def test_a_voided_receipt_no_longer_satisfies_completion(self) -> None:
        receipt = self._receipt("2026-09-01T00:00:00+00:00")
        latest = self._completion_receipt(
            [
                receipt,
                _correction(receipt, "void", ts="2026-09-02T00:00:00+00:00", cause="agent-error"),
            ]
        )
        self.assertIsNone(latest, "a voided receipt still satisfied the completion gate")

    def test_an_earlier_receipt_resurfaces_when_the_later_one_is_voided(self) -> None:
        """Voiding must not erase legitimate intervening work.

        The reader takes the NEWEST matching receipt. Dropping the voided row has
        to fall back to the real one beneath it, not report "no receipt" — which
        would turn a correction into a bigger outage than the error it repairs.
        """
        earlier = self._receipt("2026-08-01T00:00:00+00:00")
        later = self._receipt("2026-09-01T00:00:00+00:00")
        rows = [
            earlier,
            later,
            _correction(later, "void", ts="2026-09-02T00:00:00+00:00", cause="agent-error"),
        ]
        latest = self._completion_receipt(rows)
        self.assertIsNotNone(latest)
        self.assertEqual(latest.isoformat(), "2026-08-01T00:00:00+00:00")

    def test_a_discharged_receipt_is_still_a_receipt(self) -> None:
        """A reconciliation that HAPPENED is evidence it happened.

        `discharged` says the condition ended, not that the run was fictitious.
        Reconciliation freshness is already a time-based judgment — the receipt
        going stale is what `is_receipt_fresh` decides — so a discharge must not
        additionally erase the record that the run occurred.
        """
        receipt = self._receipt("2026-09-01T00:00:00+00:00")
        latest = self._completion_receipt(
            [
                receipt,
                _correction(
                    receipt,
                    "discharged",
                    ts="2026-09-02T00:00:00+00:00",
                    cause="condition-resolved",
                ),
            ]
        )
        self.assertIsNotNone(latest, "a discharged receipt was treated as though never run")

    def test_the_raw_history_still_carries_every_row(self) -> None:
        """Corrections never erase; the file keeps both rows and the correction."""
        from gzkit.ledger import Ledger

        receipt = self._receipt("2026-09-01T00:00:00+00:00")
        rows = [
            receipt,
            _correction(receipt, "void", ts="2026-09-02T00:00:00+00:00", cause="agent-error"),
        ]
        root, _brief = self._root(rows)
        history = Ledger(root / ".gzkit" / "ledger.jsonl").read_history()
        self.assertEqual([e.event for e in history], ["brief_reconciled", CORRECTION_EVENT])


class LockCouplingAuditReadsEvidence(unittest.TestCase):
    """`validate_lock_exchange_coupling` audits what HAPPENED, so it reads evidence.

    Same class as `_locked_paths` one class up, and fixed with it rather than
    after it: both ask an evidence question about `obpi_lock_released`, and both
    reached the ledger through the now-live-by-default boundary. A discharged
    release still owes the exchange record it cited — discharging it does not
    retract the surrender, so the coupling obligation stands.
    """

    def test_a_discharged_release_still_owes_its_exchange_record(self) -> None:
        from gzkit.governance.trust_audits.lock_exchange_coupling import (
            validate_lock_exchange_coupling,
        )

        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        cutover = _row(
            "obpi_receipt_emitted",
            "OBPI-0.0.41-02-exchange-record-primitive",
            "2026-01-01T00:00:00+00:00",
            receipt_event="completed",
            attestor="g0",
        )
        release = _row(
            "obpi_lock_released",
            "OBPI-X",
            "2026-02-01T00:00:00+00:00",
            agent="implementer",
        )
        _write_ledger(
            root,
            [
                cutover,
                release,
                _correction(
                    release,
                    "discharged",
                    ts="2026-03-01T00:00:00+00:00",
                    cause="condition-resolved",
                ),
            ],
        )
        errors = validate_lock_exchange_coupling(root)
        self.assertTrue(
            errors,
            "discharging a lock release hid it from the coupling audit; a discharged "
            "release still happened and still owes its exchange record",
        )

    def test_a_voided_release_owes_nothing(self) -> None:
        """`void` says the release never happened, so there is nothing to couple."""
        from gzkit.governance.trust_audits.lock_exchange_coupling import (
            validate_lock_exchange_coupling,
        )

        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        cutover = _row(
            "obpi_receipt_emitted",
            "OBPI-0.0.41-02-exchange-record-primitive",
            "2026-01-01T00:00:00+00:00",
            receipt_event="completed",
            attestor="g0",
        )
        release = _row(
            "obpi_lock_released",
            "OBPI-X",
            "2026-02-01T00:00:00+00:00",
            agent="implementer",
        )
        _write_ledger(
            root,
            [
                cutover,
                release,
                _correction(release, "void", ts="2026-03-01T00:00:00+00:00", cause="agent-error"),
            ],
        )
        self.assertEqual(validate_lock_exchange_coupling(root), [])


if __name__ == "__main__":
    unittest.main()
