"""A fresh real producer must persist the canonical subject before receiving credit."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.acceptance_store import initialize
from gzkit.events import parse_typed_event
from gzkit.ledger_producer_probe import probe_producer
from gzkit.reports import publish_report


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
                self.assertEqual(observation.subject, "WP-02-producer-probe")

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
        self.assertEqual(observation.error, "ValueError: Producer persisted the wrong event type")

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

        with patch.object(work_package_ledger, "STATES", ("initiated", "commenced")):
            observation = probe_producer("work_package_transitioned")
        self.assertEqual(observation.status, "failed")
        with patch.object(work_package_ledger, "_refuse", lambda message: None):
            observation = probe_producer("work_package_changed")
        self.assertEqual(observation.status, "failed")
        with patch.object(work_package_ledger, "_refuse", lambda message: None):
            observation = probe_producer("work_package_issue_closed")
        self.assertEqual(observation.status, "failed")
