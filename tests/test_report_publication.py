"""Publication preserves interpretations and books only durable reports."""

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.config import GzkitConfig, PathConfig
from gzkit.ledger import Ledger
from gzkit.reports import publish_report


class TestReportPublication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "draft.md"
        self.body = b"# Perspective\r\n\r\nValue, with uncertainty.\r\n"
        self.source.write_bytes(self.body)
        self.config = GzkitConfig(paths=PathConfig(docs_root="manual", ledger="state/events.jsonl"))

    def publish(self, report_id="2026-09-19-first", **kwargs):
        return publish_report(self.root, self.config, self.source, report_id, **kwargs)

    def events(self):
        return Ledger(self.root / "state/events.jsonl").read_all()

    def test_preserves_bytes_and_configured_paths_with_witness(self):
        result = self.publish(period="last 60 days", evidence_cutoff="2026-09-19")
        self.assertEqual((self.root / result["path"]).read_bytes(), self.body)
        event = self.events()[0]
        self.assertEqual(event.event, "report_published")
        self.assertEqual(event.extra["sha256"], hashlib.sha256(self.body).hexdigest())
        self.assertEqual(event.extra["period"], "last 60 days")
        self.assertFalse((self.root / ".gzkit/ledger.jsonl").exists())

    def test_rotation_retains_prior_report_and_links_predecessor(self):
        first = self.publish()
        self.source.write_text("# New assessment\n", encoding="utf-8")
        second = self.publish("2026-10-01-second")
        self.assertEqual((self.root / first["path"]).read_bytes(), self.body)
        self.assertEqual(self.events()[1].extra["predecessor"], first["id"])
        current = self.root / "manual/reports/big-picture/current.md"
        self.assertEqual(current.read_bytes(), self.source.read_bytes())
        index = current.with_name("index.md").read_text(encoding="utf-8")
        self.assertIn(first["id"], index)
        self.assertIn(second["id"], index)

    def test_retry_repairs_views_without_duplicate_or_rewinding_current(self):
        first = self.publish()
        self.source.write_text("# Second\n", encoding="utf-8")
        self.publish("2026-10-01-second")
        current = self.root / "manual/reports/big-picture/current.md"
        current.unlink()
        self.source.write_bytes(self.body)
        self.publish()
        self.assertEqual(len(self.events()), 2)
        self.assertEqual(current.read_bytes(), b"# Second\n")
        self.assertEqual((self.root / first["path"]).read_bytes(), self.body)

    def test_identity_conflict_does_not_overwrite(self):
        result = self.publish()
        self.source.write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual((self.root / result["path"]).read_bytes(), self.body)
        self.assertEqual(len(self.events()), 1)

    def test_failed_ledger_append_can_retry_retained_report(self):
        with (
            patch("gzkit.reports.Ledger.append", side_effect=OSError("disk full")),
            self.assertRaises(OSError),
        ):
            self.publish()
        self.assertFalse((self.root / "manual/reports/big-picture/current.md").exists())
        self.publish()
        self.assertEqual(len(self.events()), 1)

    def test_invalid_id_and_escaping_config_write_nothing(self):
        with self.assertRaises(ValueError):
            self.publish("../escape")
        self.config = GzkitConfig(paths=PathConfig(docs_root="../outside"))
        with self.assertRaises(ValueError):
            self.publish()
        self.assertFalse((self.root / "manual").exists())

    def test_changed_published_bytes_fail_closed(self):
        result = self.publish()
        (self.root / result["path"]).write_text("tampered", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.publish("2026-10-01-second")
        self.assertEqual(len(self.events()), 1)

    def test_metadata_conflict_refuses_retry(self):
        self.publish(period="September")
        with self.assertRaises(ValueError):
            self.publish(period="October")
        self.assertEqual(len(self.events()), 1)

    def test_view_failure_retry_does_not_duplicate_event(self):
        with (
            patch("gzkit.reports._refresh_views", side_effect=OSError("disk full")),
            self.assertRaises(OSError),
        ):
            self.publish()
        self.assertEqual(len(self.events()), 1)
        self.publish()
        self.assertEqual(len(self.events()), 1)
        self.assertEqual(
            (self.root / "manual/reports/big-picture/current.md").read_bytes(), self.body
        )

    def test_empty_or_invalid_utf8_never_publishes(self):
        for content in (b" ", b"\xff"):
            self.source.write_bytes(content)
            with self.assertRaises(ValueError):
                self.publish()
        self.assertFalse((self.root / "manual").exists())

    def test_reserved_or_case_colliding_id_is_rejected(self):
        for report_id in (
            "index",
            "current",
            "INDEX",
            "CURRENT",
            "Report",
            "2026-CON",
            "con",
            "aux",
            "lpt1",
        ):
            with self.assertRaises(ValueError):
                self.publish(report_id)
        self.assertFalse((self.root / "manual").exists())
