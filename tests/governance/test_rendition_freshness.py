"""Freshness gate tests — OBPI-0.0.37-22 (REQ-0.0.37-22-03).

Covers the corpus↔rendition drift gate: exits 3 when the corpus for a surface
has mutated after its committed rendition; exits 0 when they agree or when
either is absent.
"""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from gzkit.content.rendition_store import save_rendition
from gzkit.governance.trust_audits.rendition_freshness import validate_rendition_freshness
from gzkit.traceability import covers


class _TempProjectMixin(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_corpus(self, surface: str, content: str = "entry\n") -> Path:
        """Write a minimal corpus JSONL for *surface* and return the path."""
        corpus_dir = self.root / ".gzkit" / "corpus"
        corpus_dir.mkdir(exist_ok=True)
        path = corpus_dir / f"{surface}.jsonl"
        path.write_text(content, encoding="utf-8")
        return path


class TestRenditionFreshnessNoDrift(_TempProjectMixin):
    """Freshness gate exits 0 when corpus and rendition agree or either is absent."""

    @covers("REQ-0.0.37-22-03")
    def test_exits_0_when_no_corpus_exists(self) -> None:
        """No corpus → no drift possible → gate exits 0 (no errors)."""
        save_rendition(self.root, "AGENTS.md", "claude", b"content")
        errors = validate_rendition_freshness(self.root)
        self.assertEqual(errors, [], "No corpus → no drift")

    @covers("REQ-0.0.37-22-03")
    def test_exits_0_when_no_rendition_exists(self) -> None:
        """No rendition → no committed baseline → gate exits 0 (bootstrap)."""
        self._write_corpus("AGENTS.md")
        errors = validate_rendition_freshness(self.root)
        self.assertEqual(errors, [], "No rendition → no drift check")

    @covers("REQ-0.0.37-22-03")
    def test_exits_0_when_rendition_newer_than_corpus(self) -> None:
        """Rendition is newer than corpus → corpus has not drifted → gate exits 0."""
        self._write_corpus("AGENTS.md")
        time.sleep(0.01)  # ensure mtime ordering
        save_rendition(self.root, "AGENTS.md", "claude", b"rendition after corpus")

        errors = validate_rendition_freshness(self.root)
        self.assertEqual(errors, [], "Rendition newer than corpus → no drift")

    @covers("REQ-0.0.37-22-03")
    def test_exits_0_when_both_absent(self) -> None:
        """Neither corpus nor rendition → gate exits 0."""
        errors = validate_rendition_freshness(self.root)
        self.assertEqual(errors, [], "Both absent → no drift")


class TestRenditionFreshnessDrift(_TempProjectMixin):
    """Freshness gate exits 3 when corpus has mutated after its committed rendition."""

    @covers("REQ-0.0.37-22-03")
    def test_exits_3_when_corpus_newer_than_rendition(self) -> None:
        """Corpus mutated after rendition → drift detected → exits 3 (one error)."""
        save_rendition(self.root, "AGENTS.md", "claude", b"rendition committed first")
        time.sleep(0.01)
        self._write_corpus("AGENTS.md")

        errors = validate_rendition_freshness(self.root)
        self.assertEqual(len(errors), 1, f"Expected 1 drift error, got: {errors}")

    @covers("REQ-0.0.37-22-03")
    def test_drift_error_type_is_rendition_freshness(self) -> None:
        """Drift error has type 'rendition_freshness'."""
        save_rendition(self.root, "AGENTS.md", "claude", b"old rendition")
        time.sleep(0.01)
        self._write_corpus("AGENTS.md")

        errors = validate_rendition_freshness(self.root)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "rendition_freshness")

    @covers("REQ-0.0.37-22-03")
    def test_drift_error_message_contains_recompose_hint(self) -> None:
        """Drift error message names the recompose recovery verb."""
        save_rendition(self.root, "AGENTS.md", "claude", b"old rendition")
        time.sleep(0.01)
        self._write_corpus("AGENTS.md")

        errors = validate_rendition_freshness(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("compose", errors[0].message.lower(), "recovery hint must name compose verb")

    @covers("REQ-0.0.37-22-03")
    def test_drift_emits_composition_drift_detected_event(self) -> None:
        """Corpus drift emits a composition_drift_detected ledger event."""
        import json

        save_rendition(self.root, "AGENTS.md", "claude", b"old rendition")
        time.sleep(0.01)
        self._write_corpus("AGENTS.md")

        validate_rendition_freshness(self.root)

        ledger_path = self.root / ".gzkit" / "ledger.jsonl"
        self.assertTrue(ledger_path.exists(), "Ledger must be written")
        events = [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        drift_events = [e for e in events if e.get("event") == "composition_drift_detected"]
        self.assertEqual(len(drift_events), 1, "Drift must emit composition_drift_detected")


class TestRenditionFreshnessCorpusAbsence(_TempProjectMixin):
    """Gate handles missing corpus directories gracefully."""

    @covers("REQ-0.0.37-22-03")
    def test_missing_corpus_directory_does_not_raise(self) -> None:
        """Missing .gzkit/corpus/ directory → no drift → no error (not a filesystem error)."""
        save_rendition(self.root, "AGENTS.md", "claude", b"some rendition")
        errors = validate_rendition_freshness(self.root)
        self.assertEqual(errors, [], "Missing corpus dir → no drift")

    @covers("REQ-0.0.37-22-03")
    def test_multiple_consumers_checked_independently(self) -> None:
        """Each (surface, consumer) pair is checked independently."""
        save_rendition(self.root, "AGENTS.md", "claude", b"claude rendition")
        time.sleep(0.01)
        self._write_corpus("AGENTS.md")

        errors = validate_rendition_freshness(self.root)
        self.assertEqual(len(errors), 1, "claude rendition is stale → 1 error")


if __name__ == "__main__":
    unittest.main()
