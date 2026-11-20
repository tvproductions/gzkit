"""A fresh real producer must persist the canonical subject before receiving credit."""

import json
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from gzkit import legacy_units, work_package_ledger, work_package_run
from gzkit.acceptance_store import initialize
from gzkit.events import parse_typed_event
from gzkit.ledger_events import legacy_unit_withdrawn_event, obpi_withdrawn_event
from gzkit.ledger_producer_probe import probe_producer
from gzkit.pipeline_dispatch import MAX_REVIEW_FIX_CYCLES
from gzkit.reports import publish_report

if TYPE_CHECKING:
    from collections.abc import Callable

    from gzkit.models.catalog import WorkPackage


class ProducerProbeTests(unittest.TestCase):
    def test_the_run_writers_are_verified_and_their_refusals_proven(self) -> None:
        for event_type in (
            "work_package_dispatched",
            "work_package_blocked",
            "work_package_unblocked",
        ):
            with self.subTest(event_type=event_type):
                observation = probe_producer(event_type)
                self.assertEqual(observation.status, "verified", observation.error)
                # A repair package's run is its orders' (RP-12 ruling 44): the delivery one.
                self.assertEqual(observation.subject, "WP-01-producer-probe")

    def test_a_refusal_for_another_reason_past_the_bound_gets_no_credit(self) -> None:
        """Only the bound's own refusal proves the bound; any other proves nothing."""
        real = work_package_run._check_role
        calls: list[int] = []
        booked = 2 * (MAX_REVIEW_FIX_CYCLES + 1)

        def refuse_past_the_bound(
            package: WorkPackage, request: work_package_run.DispatchRequest
        ) -> None:
            calls.append(1)
            if len(calls) > booked:
                msg = "refused for another reason"
                raise work_package_ledger.WorkPackageLedgerError(msg)
            return real(package, request)

        with patch.object(work_package_run, "_check_role", refuse_past_the_bound):
            observation = probe_producer("work_package_dispatched")
        self.assertEqual(observation.status, "failed")

    def test_the_order_writer_is_verified_and_refuses_a_second_opening(self) -> None:
        """RP-12 ruling 52: the order's opening is booked once, in its repair package."""
        observation = probe_producer("order_transitioned")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.order_ledger.record_order_transition")
        self.assertEqual(observation.subject, "ORD-01-producer-probe")

    def test_the_tag_issue_writer_is_verified_and_refuses_a_second_tag_on_a_surface(
        self,
    ) -> None:
        """RP-12 rulings 120 and 122: one issue booked, a second on its surface refused."""
        observation = probe_producer("tag_issued")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.tag_out.record_tag_issue")
        self.assertEqual(observation.subject, "TAG-01-producer-probe")

    def test_the_entry_writer_is_verified_and_refuses_an_unstamped_entry(self) -> None:
        """RP-12 rulings 8, 167 and 169: one entry booked by its performer, unstamped refused."""
        observation = probe_producer("entry_booked")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.entries.record_entry_book")
        self.assertEqual(observation.subject, "ENT-01-producer-probe")

    def test_the_tag_hang_writer_is_verified_and_refuses_a_second_hang(self) -> None:
        """RP-12 rulings 6, 120 and 133: one hang booked, a second refused."""
        observation = probe_producer("tag_hung")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.tag_out.record_tag_hang")
        self.assertEqual(observation.subject, "TAG-01-producer-probe")

    def test_the_clearance_writer_is_verified_and_refuses_a_second_clearance(self) -> None:
        """RP-12 rulings 7 and 138: one clearance, not available from the end, a second refused."""
        observation = probe_producer("tag_clearance_authorized")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.tag_out.record_tag_clearance")
        self.assertEqual(observation.subject, "TAG-01-producer-probe")

    def test_the_clear_writer_is_verified_and_refuses_a_second_clear(self) -> None:
        """RP-12 rulings 6 and 129: one clear by a Restoration dispatch, a second refused."""
        observation = probe_producer("tag_cleared")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.tag_out.record_tag_clear")
        self.assertEqual(observation.subject, "TAG-01-producer-probe")

    def test_the_claim_writer_is_verified_and_books_each_pair_once(self) -> None:
        """RP-12 ruling 40: one claim per dispatch and agent, none for no dispatch."""
        observation = probe_producer("dispatch_claimed")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertRegex(observation.subject or "", r"^D-[0-9a-f]{16}$")

    def test_the_void_writer_is_verified_and_its_refusals_proven(self) -> None:
        """RP-12 ruling 42: one void, none for a voided or unknown dispatch."""
        observation = probe_producer("dispatch_voided")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertRegex(observation.subject or "", r"^D-[0-9a-f]{16}$")

    def test_the_end_writer_is_verified_and_books_each_live_pair_once(self) -> None:
        """RP-12 ruling 115: one end per dispatch and agent, none for no live dispatch."""
        observation = probe_producer("dispatch_ended")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.work_package_run.record_dispatch_end")
        self.assertRegex(observation.subject or "", r"^D-[0-9a-f]{16}$")

    def test_real_initializer_persists_obligation_and_disposes_the_project(self) -> None:
        roots: list[Path] = []

        def produce(root, obpi_id, author_id):
            roots.append(root)
            self.assertFalse((root / ".gzkit/ledger.jsonl").exists())
            return initialize(root, obpi_id, author_id)

        with patch("gzkit.acceptance_store.initialize", side_effect=produce):
            observation = probe_producer("acceptance_recorded")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.subject, "OBPI-0.1.0-01-producer-probe")
        self.assertEqual(observation.author_id, "isolated-producer-probe")
        self.assertEqual(observation.obligation_ids, ("REQ-0.1.0-01-01",))
        self.assertEqual(observation.record_count, 1)
        self.assertEqual(len(observation.ledger_sha256), 64)
        self.assertEqual(len(roots), 1)
        self.assertFalse(roots[0].exists())

    def test_noop_return_value_is_not_evidence_of_a_persisted_contract(self) -> None:
        with patch("gzkit.acceptance_store.initialize", return_value={"success": True}):
            observation = probe_producer("acceptance_recorded")
        self.assertEqual(observation.status, "failed")
        self.assertEqual(observation.record_count, 0)
        self.assertEqual(observation.obligation_ids, ())

    def test_failed_producer_cannot_receive_credit(self) -> None:
        with patch(
            "gzkit.acceptance_store.initialize", side_effect=RuntimeError("broken producer")
        ):
            observation = probe_producer("acceptance_recorded")
        self.assertEqual(observation.status, "failed")
        self.assertEqual(observation.error, "RuntimeError: broken producer")

    def test_unknown_event_cannot_borrow_a_registered_producer(self) -> None:
        with patch("gzkit.acceptance_store.initialize") as producer:
            observation = probe_producer("invented_event")
        producer.assert_not_called()
        self.assertEqual(observation.status, "unsupported")

    def test_valid_other_event_does_not_prove_acceptance_contract_emission(self) -> None:
        def produce(root, obpi_id, author_id):
            result = initialize(root, obpi_id, author_id)
            ledger = root / ".gzkit/ledger.jsonl"
            row = json.loads(ledger.read_text(encoding="utf-8"))
            row["event"] = "prd_created"
            del row["payload"]
            del row["record_type"]
            parse_typed_event(row)
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            return result

        with patch("gzkit.acceptance_store.initialize", side_effect=produce):
            observation = probe_producer("acceptance_recorded")
        self.assertEqual(observation.status, "failed")
        self.assertEqual(
            observation.error, "AcceptanceEventTypeError: Producer persisted the wrong event type"
        )

    def test_malformed_empty_or_duplicate_persistence_is_not_valid_emission(self) -> None:
        for corruption in ("", "not JSON\n", "{}\n", "duplicate"):
            with self.subTest(corruption=corruption):

                def produce(root, obpi_id, author_id, corruption=corruption):
                    result = initialize(root, obpi_id, author_id)
                    ledger = root / ".gzkit/ledger.jsonl"
                    replacement = ledger.read_text(encoding="utf-8") * 2
                    if corruption != "duplicate":
                        replacement = corruption
                    ledger.write_text(replacement, encoding="utf-8")
                    return result

                with patch("gzkit.acceptance_store.initialize", side_effect=produce):
                    observation = probe_producer("acceptance_recorded")
                self.assertEqual(observation.status, "failed", observation)

    def test_typed_but_wrong_contract_cannot_receive_credit(self) -> None:
        changes = (
            (("event",), "created"),
            (("id",), "OBPI-0.1.0-02-wrong-subject"),
            (("record_type",), "proof"),
            (("payload", "author_id"), "wrong-author"),
            (("payload", "obligations"), []),
            (("payload", "obligations", 0, "id"), "REQ-0.1.0-01-02"),
            (("payload", "obligations", 0, "kind"), "SUPPORT"),
            (("payload", "obligations", 0, "statement"), "Wrong requirement."),
            (("payload", "obligations", 0, "authority"), "wrong-brief.md"),
            (("payload", "obligations", 0, "contract_digest"), ""),
        )
        for keys, value in changes:
            with self.subTest(keys=keys):

                def produce(root, obpi_id, author_id, keys=keys, value=value):
                    result = initialize(root, obpi_id, author_id)
                    ledger = root / ".gzkit/ledger.jsonl"
                    row = json.loads(ledger.read_text(encoding="utf-8"))
                    target = row
                    for key in keys[:-1]:
                        target = target[key]
                    target[keys[-1]] = value
                    ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
                    return result

                with patch("gzkit.acceptance_store.initialize", side_effect=produce):
                    observation = probe_producer("acceptance_recorded")
                self.assertEqual(observation.status, "failed", observation)

    def test_old_success_cannot_replace_a_new_execution(self) -> None:
        previous = probe_producer("acceptance_recorded")
        self.assertEqual(previous.status, "verified", previous.error)

        def cached_report_only(root, obpi_id, author_id):
            (root / "producer-report.json").write_text(previous.model_dump_json(), encoding="utf-8")
            return previous

        with patch("gzkit.acceptance_store.initialize", side_effect=cached_report_only):
            current = probe_producer("acceptance_recorded")
        self.assertEqual(current.status, "failed")
        self.assertEqual(current.record_count, 0)


class ReportProducerProbeTests(unittest.TestCase):
    def test_real_publication_is_observed_and_disposable(self):
        roots = []

        def produce(root, *args, **kwargs):
            roots.append(root)
            self.assertFalse((root / "state/events.jsonl").exists())
            return publish_report(root, *args, **kwargs)

        with patch("gzkit.reports.publish_report", side_effect=produce):
            observation = probe_producer("report_published")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.record_count, 1)
        self.assertEqual(observation.subject, "isolated-report-probe")
        self.assertEqual(len(observation.ledger_sha256), 64)
        self.assertEqual(len(roots), 1)
        self.assertFalse(roots[0].exists())

    def test_noop_publication_gets_no_credit(self):
        with patch("gzkit.reports.publish_report", return_value={"published": True}):
            observation = probe_producer("report_published")
        self.assertEqual(observation.status, "failed")
        self.assertEqual(observation.record_count, 0)

    def test_corrupt_report_event_or_projection_gets_no_credit(self):
        for target in ("report", "current", "event", "index"):
            with self.subTest(target=target):

                def produce(root, *args, target=target, **kwargs):
                    result = publish_report(root, *args, **kwargs)
                    directory = root / "manual/reports/big-picture"
                    path = {
                        "report": directory / "isolated-report-probe.md",
                        "current": directory / "current.md",
                        "index": directory / "index.md",
                        "event": root / "state/events.jsonl",
                    }[target]
                    path.write_text("wrong content", encoding="utf-8")
                    return result

                with patch("gzkit.reports.publish_report", side_effect=produce):
                    observation = probe_producer("report_published")
                self.assertEqual(observation.status, "failed")
                self.assertEqual(observation.record_count, 0)


class DiscrepancyProducerProbeTests(unittest.TestCase):
    """The list of discrepancies' two writers, each probed with a refusal (RP-12 O4 task 2)."""

    def test_the_discrepancy_writer_is_verified_and_refuses_a_stamped_left_broken(self) -> None:
        """RP-12 rulings 9, 172 and 178: one line on its order, a performer's non-find refused."""
        observation = probe_producer("discrepancy_recorded")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.discrepancies.record_discrepancy")
        self.assertEqual(observation.subject, "DSC-01-producer-probe")

    def test_the_discrepancy_clear_is_verified_and_refuses_a_stamped_clear(self) -> None:
        """RP-12 rulings 172 and 181: one clear on an entry, a stamped clear refused."""
        observation = probe_producer("discrepancy_cleared")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.mx.discrepancies.record_discrepancy_clear")
        self.assertEqual(observation.subject, "DSC-01-producer-probe")


if __name__ == "__main__":
    unittest.main()


class LockLeaseExpiryProducerProbeTests(unittest.TestCase):
    """The lock reaper books an expired work lock's lease and keeps the lock held."""

    def test_the_real_reaper_books_the_expiry_in_a_disposable_project(self):
        observation = probe_producer("obpi_lock_lease_expired")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.lock_manager.reap_expired_locks")
        self.assertEqual(observation.record_count, 1)
        self.assertEqual(len(observation.ledger_sha256), 64)

    def test_a_reaper_that_books_nothing_gets_no_credit(self):
        with patch("gzkit.lock_manager.reap_expired_locks", return_value=[]):
            observation = probe_producer("obpi_lock_lease_expired")
        self.assertEqual(observation.status, "failed")
        self.assertEqual(observation.record_count, 0)

    def test_a_reaper_that_evicts_the_lock_gets_no_credit(self):
        from gzkit import lock_manager  # noqa: PLC0415

        real = lock_manager.reap_expired_locks

        def evict(root, **kwargs):
            reaped = real(root, **kwargs)
            for lock in lock_manager.list_locks(root):
                lock_manager.delete_lock(root, lock.obpi_id)
            return reaped

        with patch("gzkit.lock_manager.reap_expired_locks", side_effect=evict):
            observation = probe_producer("obpi_lock_lease_expired")
        self.assertEqual(observation.status, "failed")


class MxLeaseRenewalProducerProbeTests(unittest.TestCase):
    """The real `gz mx renew` books one renewal and keeps the session open (GHI #1261)."""

    def test_the_real_renewal_books_the_lease_in_a_disposable_project(self):
        observation = probe_producer("mx_session_lease_renewed")
        self.assertEqual(observation.status, "verified", observation.error)
        self.assertEqual(observation.producer, "gzkit.commands.mx_cmd.mx_renew_cmd")
        self.assertEqual(observation.record_count, 1)
        self.assertEqual(len(observation.ledger_sha256), 64)

    def test_a_renewal_that_books_nothing_gets_no_credit(self):
        with patch("gzkit.commands.mx_cmd.Ledger.append", return_value=None):
            observation = probe_producer("mx_session_lease_renewed")
        self.assertEqual(observation.status, "failed")
        self.assertEqual(observation.record_count, 0)

    def test_a_renewal_that_ends_the_session_gets_no_credit(self):
        from gzkit.commands import mx_cmd  # noqa: PLC0415

        real = mx_cmd.mx_renew_cmd

        def renew_then_drop_marker(attestor: str, project_root: Path) -> None:
            real(attestor, project_root=project_root)
            (project_root / ".gzkit" / "mx.json").unlink()

        with patch.object(mx_cmd, "mx_renew_cmd", renew_then_drop_marker):
            observation = probe_producer("mx_session_lease_renewed")
        self.assertEqual(observation.status, "failed")


class CatalogProducerProbeTests(unittest.TestCase):
    """The catalog writers book their events and refuse what the grammar refuses (RO-3)."""

    def test_the_real_writers_book_one_event_each_in_a_disposable_project(self):
        for event_type, producer in (
            ("outcome_transitioned", "gzkit.catalog_ledger.record_outcome_transition"),
            ("req_proof_recorded", "gzkit.catalog_ledger.record_req_proof"),
        ):
            with self.subTest(event_type=event_type):
                observation = probe_producer(event_type)
                self.assertEqual(observation.status, "verified", observation.error)
                self.assertEqual(observation.producer, producer)
                self.assertEqual(observation.record_count, 1)
                self.assertEqual(len(observation.ledger_sha256), 64)

    def test_a_writer_that_books_nothing_gets_no_credit(self):
        for event_type, writer in (
            ("outcome_transitioned", "record_outcome_transition"),
            ("req_proof_recorded", "record_req_proof"),
        ):
            with (
                self.subTest(event_type=event_type),
                patch(f"gzkit.catalog_ledger.{writer}", return_value=None),
            ):
                observation = probe_producer(event_type)
                self.assertEqual(observation.status, "failed")
                self.assertEqual(observation.record_count, 0)

    def test_a_writer_that_refuses_nothing_gets_no_credit(self):
        from gzkit import catalog_ledger  # noqa: PLC0415

        with patch.object(catalog_ledger, "_allowed_moves", return_value=catalog_ledger.LIFECYCLE):
            observation = probe_producer("outcome_transitioned")
        self.assertEqual(observation.status, "failed")
        with patch.object(catalog_ledger, "VERDICTS", ("SATISFIED", "PASS")):
            observation = probe_producer("req_proof_recorded")
        self.assertEqual(observation.status, "failed")


class WorkPackageProducerProbeTests(unittest.TestCase):
    """The work-package writers book their events and refuse what the grammar refuses (RO-5)."""

    _WRITERS = (
        ("work_package_transitioned", "record_work_package_transition", "WP-01-producer-probe"),
        ("work_package_changed", "record_work_package_change", "WP-01-producer-probe"),
        ("work_package_issue_closed", "record_work_package_issue_closed", "WP-02-producer-probe"),
    )

    def test_the_real_writers_book_one_event_each_in_a_disposable_project(self):
        for event_type, writer, subject in self._WRITERS:
            with self.subTest(event_type=event_type):
                observation = probe_producer(event_type)
                self.assertEqual(observation.status, "verified", observation.error)
                self.assertEqual(observation.producer, f"gzkit.work_package_ledger.{writer}")
                self.assertEqual(observation.record_count, 1)
                self.assertEqual(observation.subject, subject)

    def test_a_writer_that_books_nothing_gets_no_credit(self):
        for event_type, writer, _ in self._WRITERS:
            with (
                self.subTest(event_type=event_type),
                patch(f"gzkit.work_package_ledger.{writer}", return_value=None),
            ):
                observation = probe_producer(event_type)
                self.assertEqual(observation.status, "failed")
                self.assertEqual(observation.record_count, 0)

    def test_a_writer_that_refuses_nothing_gets_no_credit(self):
        from gzkit import work_package_ledger  # noqa: PLC0415

        with patch.dict(work_package_ledger.LIFECYCLES, {"delivery": ("initiated", "commenced")}):
            observation = probe_producer("work_package_transitioned")
        self.assertEqual(observation.status, "failed")
        with patch.object(work_package_ledger, "_refuse", lambda message: None):
            observation = probe_producer("work_package_changed")
        self.assertEqual(observation.status, "failed")
        with patch.object(work_package_ledger, "_refuse", lambda message: None):
            observation = probe_producer("work_package_issue_closed")
        self.assertEqual(observation.status, "failed")


def _then_refuse(first: Callable[..., object]) -> Callable[..., object]:
    """Stand in for the writer: *first* on the first call, the refusal on every later one.

    Returns:
        The stand-in.

    """
    calls: list[str] = []

    def write(ledger: Any, unit: str, reason: str, attestor: str) -> object:
        calls.append(unit)
        if len(calls) > 1:
            raise legacy_units.LegacyUnitRetiredError(unit)
        return first(ledger, unit, reason, attestor)

    return write


class LegacyWithdrawalProducerProbeTests(unittest.TestCase):
    """The withdrawal books one true row and refuses a second (RO-14 act 7)."""

    def test_a_writer_that_books_the_wrong_record_gets_no_credit(self) -> None:
        real = legacy_units.withdraw_legacy_unit
        cases: tuple[tuple[str, Callable[..., object], str], ...] = (
            ("nothing", lambda *_: None, "exactly one"),
            (
                "the old event",
                lambda ledger, unit, reason, attestor: ledger.append(
                    obpi_withdrawn_event(unit, "ADR-0.0.1", reason, attestor)
                ),
                "wrong event type",
            ),
            (
                "another unit",
                lambda ledger, _unit, reason, attestor: ledger.append(
                    legacy_unit_withdrawn_event("OBPI-0.1.0-02", "ADR-0.0.1", reason, attestor)
                ),
                "disagrees",
            ),
            (
                "another attestor",
                lambda ledger, unit, reason, _attestor: real(ledger, unit, reason, "someone-else"),
                "disagrees",
            ),
        )
        for name, first, expected in cases:
            with (
                self.subTest(name),
                patch.object(legacy_units, "withdraw_legacy_unit", side_effect=_then_refuse(first)),
            ):
                observation = probe_producer("legacy_unit_withdrawn")
                self.assertEqual(observation.status, "failed")
                self.assertIn(expected, observation.error or "")

    def test_a_writer_that_withdraws_twice_gets_no_credit(self) -> None:
        with patch.object(legacy_units, "withdraw_transition_available", return_value=True):
            observation = probe_producer("legacy_unit_withdrawn")
        self.assertEqual(observation.status, "failed")
        self.assertIn("withdrawn twice", observation.error or "")

    def test_a_refusal_that_still_books_a_row_gets_no_credit(self) -> None:
        real = legacy_units.withdraw_legacy_unit

        def book_then_refuse(ledger: Any, unit: str, reason: str, attestor: str) -> object:
            if ledger.query(event_type="legacy_unit_withdrawn"):
                ledger.append(legacy_unit_withdrawn_event(unit, "ADR-0.0.1", reason, attestor))
                raise legacy_units.LegacyUnitRetiredError(unit)
            return real(ledger, unit, reason, attestor)

        with patch.object(legacy_units, "withdraw_legacy_unit", side_effect=book_then_refuse):
            observation = probe_producer("legacy_unit_withdrawn")
        self.assertEqual(observation.status, "failed")
        self.assertIn("nothing for a refusal", observation.error or "")


class OrderProducerProbeTests(unittest.TestCase):
    """RP-12 ruling 52: the order writer gets credit only for one true opening."""

    @staticmethod
    def _writer(book: Callable[[Any, Any], None]) -> Callable[..., None]:
        """A writer that books ``book``'s rows once, then refuses as the real one does.

        Returns:
            The stand-in writer.

        """
        from gzkit.order_ledger import OrderLedgerError  # noqa: PLC0415

        calls: list[int] = []

        def write(catalog: Any, ledger: Any, move: Any) -> None:
            if calls:
                msg = "opened already"
                raise OrderLedgerError(msg)
            calls.append(1)
            book(ledger, move)

        return write

    def _observe(self, book: Callable[[Any, Any], None]) -> Any:
        with patch("gzkit.order_ledger.record_order_transition", self._writer(book)):
            return probe_producer("order_transitioned")

    @staticmethod
    def _opening(work_package: str = "WP-02-producer-probe") -> Any:
        from gzkit.events import OrderTransitionedEvent  # noqa: PLC0415

        return OrderTransitionedEvent(
            event="order_transitioned",
            id="ORD-01-producer-probe",
            order="ORD-01-producer-probe",
            work_package=work_package,
            to_state="opened",
            evidence="probe",
            operator_text="probe",
        )

    def test_a_writer_that_books_the_opening_twice_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def twice(ledger: Any, _move: Any) -> None:
            for _ in range(2):
                ledger.append(ledger_row(self._opening()))

        observation = self._observe(twice)
        self.assertEqual(observation.status, "failed")
        self.assertIn("exactly one opening", observation.error)

    def test_a_writer_that_books_another_event_gets_no_credit(self) -> None:
        from gzkit.events import WorkPackageChangedEvent  # noqa: PLC0415
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def other(ledger: Any, _move: Any) -> None:
            event = WorkPackageChangedEvent(
                event="work_package_changed",
                id="WP-02-producer-probe",
                work_package="WP-02-producer-probe",
                rung="attachment",
                approver="operator",
                change="probe",
            )
            ledger.append(ledger_row(event))

        observation = self._observe(other)
        self.assertEqual(observation.status, "failed")
        self.assertIn("wrong event type", observation.error)

    def test_a_writer_that_books_the_wrong_package_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def elsewhere(ledger: Any, _move: Any) -> None:
            ledger.append(ledger_row(self._opening("WP-01-producer-probe")))

        observation = self._observe(elsewhere)
        self.assertEqual(observation.status, "failed")
        self.assertIn("disagrees with the opening", observation.error)


class TagIssueProducerProbeTests(unittest.TestCase):
    """RP-12 O3 task 2: the tag issue writer gets credit only for one true issue."""

    @staticmethod
    def _writer(book: Callable[[Any], None]) -> Callable[..., None]:
        """A writer that books ``book``'s rows once, then refuses as the real one does.

        Returns:
            The stand-in writer.

        """
        from gzkit.mx.tag_out import TagOutError  # noqa: PLC0415

        calls: list[int] = []

        def write(_catalog: Any, ledger: Any, _request: Any, **_fields: Any) -> None:
            if calls:
                msg = "the surface already carries an open tag"
                raise TagOutError(msg)
            calls.append(1)
            book(ledger)

        return write

    def _observe(self, book: Callable[[Any], None]) -> Any:
        with patch("gzkit.mx.tag_out.record_tag_issue", self._writer(book)):
            return probe_producer("tag_issued")

    @staticmethod
    def _issue(order: str = "ORD-01-producer-probe") -> Any:
        from gzkit.events import TagIssuedEvent  # noqa: PLC0415

        return TagIssuedEvent(
            event="tag_issued",
            id="TAG-01-producer-probe",
            tag_id="TAG-01-producer-probe",
            order=order,
            work_package="WP-02-producer-probe",
            tag_class="Danger",
            surface="path:src/producer_probe.py",
            surface_kind="path",
            surface_name="src/producer_probe.py",
            position="off",
            hazard="probe",
            removal_procedure="probe",
            source="order-work",
            check_level="C",
            mx_session_id="isolated-producer-probe",
        )

    def test_a_writer_that_books_the_issue_twice_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def twice(ledger: Any) -> None:
            for _ in range(2):
                ledger.append(ledger_row(self._issue()))

        observation = self._observe(twice)
        self.assertEqual(observation.status, "failed")
        self.assertIn("exactly one issue", observation.error)

    def test_a_writer_that_books_another_event_gets_no_credit(self) -> None:
        from gzkit.events import WorkPackageChangedEvent  # noqa: PLC0415
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def other(ledger: Any) -> None:
            event = WorkPackageChangedEvent(
                event="work_package_changed",
                id="WP-02-producer-probe",
                work_package="WP-02-producer-probe",
                rung="attachment",
                approver="operator",
                change="probe",
            )
            ledger.append(ledger_row(event))

        observation = self._observe(other)
        self.assertEqual(observation.status, "failed")
        self.assertIn("wrong event type", observation.error)

    def test_a_writer_that_books_the_wrong_order_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def elsewhere(ledger: Any) -> None:
            ledger.append(ledger_row(self._issue("ORD-09-elsewhere")))

        observation = self._observe(elsewhere)
        self.assertEqual(observation.status, "failed")
        self.assertIn("disagrees with the issue", observation.error)


class EntryProducerProbeTests(unittest.TestCase):
    """RP-12 O4 task 1: the entry writer gets credit only for one true entry."""

    @staticmethod
    def _writer(book: Callable[[Any], None]) -> Callable[..., None]:
        """A writer that books ``book``'s rows once, then refuses as the real one does.

        Returns:
            The stand-in writer.

        """
        from gzkit.mx.entries import EntryError  # noqa: PLC0415

        calls: list[int] = []

        def write(ledger: Any, _request: Any, **_fields: Any) -> None:
            if calls:
                msg = "This call is not stamped"
                raise EntryError(msg)
            calls.append(1)
            book(ledger)

        return write

    def _observe(self, book: Callable[[Any], None]) -> Any:
        with patch("gzkit.mx.entries.record_entry_book", self._writer(book)):
            return probe_producer("entry_booked")

    @staticmethod
    def _entry(order: str = "ORD-01-producer-probe") -> Any:
        from gzkit.events import EntryBookedEvent  # noqa: PLC0415

        return EntryBookedEvent(
            event="entry_booked",
            id="ENT-01-producer-probe",
            entry_id="ENT-01-producer-probe",
            order=order,
            work_package="WP-02-producer-probe",
            dispatch_id="D-0000000000000000",
            description="probe",
            before="probe",
            after="probe",
            witness="probe",
            mx_session_id="isolated-producer-probe",
        )

    def test_a_writer_that_books_the_entry_twice_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def twice(ledger: Any) -> None:
            for _ in range(2):
                ledger.append(ledger_row(self._entry()))

        observation = self._observe(twice)
        self.assertEqual(observation.status, "failed")
        self.assertIn("exactly one entry", observation.error)

    def test_a_writer_that_books_another_event_gets_no_credit(self) -> None:
        from gzkit.events import WorkPackageChangedEvent  # noqa: PLC0415
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def other(ledger: Any) -> None:
            event = WorkPackageChangedEvent(
                event="work_package_changed",
                id="WP-02-producer-probe",
                work_package="WP-02-producer-probe",
                rung="attachment",
                approver="operator",
                change="probe",
            )
            ledger.append(ledger_row(event))

        observation = self._observe(other)
        self.assertEqual(observation.status, "failed")
        self.assertIn("wrong event type", observation.error)

    def test_a_writer_that_books_another_order_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def elsewhere(ledger: Any) -> None:
            ledger.append(ledger_row(self._entry("ORD-09-elsewhere")))

        observation = self._observe(elsewhere)
        self.assertEqual(observation.status, "failed")
        self.assertIn("disagrees with the dispatch", observation.error)


class TagHangProducerProbeTests(unittest.TestCase):
    """RP-12 O3 task 3: the tag hang writer gets credit only for one true hang."""

    @staticmethod
    def _writer(book: Callable[[Any], None]) -> Callable[..., None]:
        """A writer that books ``book``'s rows once, then refuses as the real one does.

        Returns:
            The stand-in writer.

        """
        from gzkit.mx.tag_out import TagOutError  # noqa: PLC0415

        calls: list[int] = []

        def write(ledger: Any, _tag: Any, _dispatch: Any, **_fields: Any) -> None:
            if calls:
                msg = "the tag is already hung"
                raise TagOutError(msg)
            calls.append(1)
            book(ledger)

        return write

    def _observe(self, book: Callable[[Any], None]) -> Any:
        with patch("gzkit.mx.tag_out.record_tag_hang", self._writer(book)):
            return probe_producer("tag_hung")

    @staticmethod
    def _hang(order: str = "ORD-01-producer-probe") -> Any:
        from gzkit.events import TagHungEvent  # noqa: PLC0415

        return TagHungEvent(
            event="tag_hung",
            id="TAG-01-producer-probe",
            tag_id="TAG-01-producer-probe",
            dispatch_id="D-00000000000000aa",
            order=order,
            work_package="WP-02-producer-probe",
            tag_class="Danger",
            surface="path:src/producer_probe.py",
            surface_kind="path",
            surface_name="src/producer_probe.py",
            position="off",
            hazard="probe",
            removal_procedure="probe",
            source="order-work",
            check_level="C",
            issued_by_session="isolated-producer-probe",
            mx_session_id="isolated-producer-probe",
        )

    def test_a_writer_that_books_the_hang_twice_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def twice(ledger: Any) -> None:
            for _ in range(2):
                ledger.append(ledger_row(self._hang()))

        observation = self._observe(twice)
        self.assertEqual(observation.status, "failed")
        self.assertIn("exactly one hang", observation.error)

    def test_a_writer_that_books_another_event_gets_no_credit(self) -> None:
        from gzkit.events import WorkPackageChangedEvent  # noqa: PLC0415
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def other(ledger: Any) -> None:
            event = WorkPackageChangedEvent(
                event="work_package_changed",
                id="WP-02-producer-probe",
                work_package="WP-02-producer-probe",
                rung="attachment",
                approver="operator",
                change="probe",
            )
            ledger.append(ledger_row(event))

        observation = self._observe(other)
        self.assertEqual(observation.status, "failed")
        self.assertIn("wrong event type", observation.error)

    def test_a_writer_that_books_the_wrong_record_gets_no_credit(self) -> None:
        from gzkit.ledger import ledger_row  # noqa: PLC0415

        def elsewhere(ledger: Any) -> None:
            ledger.append(ledger_row(self._hang("ORD-09-elsewhere")))

        observation = self._observe(elsewhere)
        self.assertEqual(observation.status, "failed")
        self.assertIn("disagrees with the hang", observation.error)
