"""Append-only corpus store tests — OBPI-0.0.37-19.

Unit-tier coverage of the store mechanism (where entries live + append-only I/O).
The REQ-level BEHAVIOR proofs (REQ-0.0.37-19-01..04) live in
``tests/commands/test_content_remember.py`` against the command surface; these
assert the lower-level ``corpus_store`` contract the command relies on.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.corpus_store import append_entry, corpus_path, load_corpus
from gzkit.content.models import Corpus, CorpusEntry


def _entry(entry_id: str, *, section: str = "behavior-rules") -> CorpusEntry:
    """Build a conformant CorpusEntry for store round-trip tests."""
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section=section,
        tier="compressible",
        classification="Ambiguous",
        text=f"entry {entry_id}",
        origin="cli:content-remember",
        ts="2026-06-05T00:00:00Z",
    )


class TestCorpusStore(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_corpus_path_is_per_surface_jsonl_under_gzkit_corpus(self) -> None:
        """The store path is .gzkit/corpus/<surface>.jsonl, addressed by surface name."""
        path = corpus_path(self._root, "AGENTS.md")
        self.assertEqual(path, self._root / ".gzkit" / "corpus" / "AGENTS.md.jsonl")

    def test_load_returns_empty_corpus_when_no_file_exists(self) -> None:
        """A surface with no store file loads as an empty corpus, not an error."""
        loaded = load_corpus(self._root, "AGENTS.md")
        self.assertEqual(loaded, Corpus())
        self.assertEqual(len(loaded.entries), 0)

    def test_append_creates_dir_and_file_on_first_use(self) -> None:
        """First append materializes .gzkit/corpus/ and the per-surface file."""
        path = corpus_path(self._root, "AGENTS.md")
        self.assertFalse(path.exists())
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 0)

    def test_append_is_append_only_prior_entries_preserved(self) -> None:
        """A second append preserves the first entry — the store never drops history."""
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        append_entry(self._root, "AGENTS.md", _entry("c2"))
        reloaded = load_corpus(self._root, "AGENTS.md")
        self.assertEqual([e.id for e in reloaded.entries], ["c1", "c2"])

    def test_append_round_trips_all_addressed_fields(self) -> None:
        """A loaded entry carries the exact addressed/provenanced fields that were appended."""
        append_entry(self._root, "AGENTS.md", _entry("c1", section="prime-directive"))
        reloaded = load_corpus(self._root, "AGENTS.md")
        (entry,) = reloaded.entries
        self.assertEqual(entry.id, "c1")
        self.assertEqual(entry.surface, "AGENTS.md")
        self.assertEqual(entry.section, "prime-directive")
        self.assertEqual(entry.tier, "compressible")
        self.assertEqual(entry.classification, "Ambiguous")
        self.assertEqual(entry.origin, "cli:content-remember")

    def test_each_surface_has_an_isolated_store(self) -> None:
        """Appends to one surface do not bleed into another surface's store."""
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        self.assertEqual(len(load_corpus(self._root, "CLAUDE.md").entries), 0)


if __name__ == "__main__":
    unittest.main()
