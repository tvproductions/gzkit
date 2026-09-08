"""A fresh real producer must persist the canonical subject before receiving credit."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.acceptance_store import initialize
from gzkit.events import parse_typed_event
from gzkit.ledger_producer_probe import probe_producer


class ProducerProbeTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
