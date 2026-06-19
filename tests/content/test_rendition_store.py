"""Committed-rendition store tests — OBPI-0.0.37-22 (REQ-0.0.37-22-01).

Covers the store contract: per-(surface×consumer) artifact at
``.gzkit/renditions/<surface>/<consumer>.md``, deterministic load
(same file → same bytes), fail-closed absent behavior, and the corpus
content-fingerprint provenance sidecar that the freshness gate compares
against (REQ-0.0.37-22-03 substance — replaces the mtime tautology).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    load_fingerprint,
    load_rendition,
    rendition_exists,
    rendition_path,
    save_fingerprint,
    save_rendition,
)
from gzkit.traceability import covers


def _entry(
    entry_id: str = "e1", text: str = "body text", tier: str = "compressible"
) -> CorpusEntry:
    """Build a minimal valid CorpusEntry for fingerprint tests."""
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="behavior-rules",
        tier=tier,  # type: ignore[arg-type]
        classification="Mechanical",
        text=text,
        origin="test",
        ts="2026-06-19T00:00:00+00:00",
    )


class TestRenditionStorePath(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-22-01")
    def test_rendition_path_is_per_surface_consumer_md_under_gzkit_renditions(self) -> None:
        """The store artifact is .gzkit/renditions/<surface>/<consumer>.md."""
        path = rendition_path(self._root, "AGENTS.md", "claude")
        self.assertEqual(path, self._root / ".gzkit" / "renditions" / "AGENTS.md" / "claude.md")

    @covers("REQ-0.0.37-22-01")
    def test_rendition_path_uses_consumer_as_filename(self) -> None:
        """Different consumers under the same surface get distinct artifact paths."""
        claude_path = rendition_path(self._root, "AGENTS.md", "claude")
        codex_path = rendition_path(self._root, "AGENTS.md", "codex")
        self.assertNotEqual(claude_path, codex_path)
        self.assertEqual(claude_path.parent, codex_path.parent)


class TestRenditionStoreExists(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-22-01")
    def test_rendition_exists_returns_false_when_artifact_absent(self) -> None:
        """rendition_exists returns False when no artifact has been committed."""
        self.assertFalse(rendition_exists(self._root, "AGENTS.md", "claude"))

    @covers("REQ-0.0.37-22-01")
    def test_rendition_exists_returns_true_after_save(self) -> None:
        """rendition_exists returns True after save_rendition commits the artifact."""
        save_rendition(self._root, "AGENTS.md", "claude", b"content")
        self.assertTrue(rendition_exists(self._root, "AGENTS.md", "claude"))


class TestRenditionStoreLoadSave(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-22-01")
    def test_load_raises_when_artifact_absent(self) -> None:
        """load_rendition fails closed with FileNotFoundError when artifact is absent."""
        with self.assertRaises(FileNotFoundError):
            load_rendition(self._root, "AGENTS.md", "claude")

    @covers("REQ-0.0.37-22-01")
    def test_save_creates_parent_dirs_on_first_use(self) -> None:
        """save_rendition creates .gzkit/renditions/<surface>/ on first use."""
        path = rendition_path(self._root, "AGENTS.md", "claude")
        self.assertFalse(path.parent.exists())
        save_rendition(self._root, "AGENTS.md", "claude", b"hello")
        self.assertTrue(path.exists())

    @covers("REQ-0.0.37-22-01")
    def test_load_returns_byte_identical_content_to_saved(self) -> None:
        """load_rendition returns the exact bytes that were committed via save_rendition."""
        content = b"deterministic rendition content\nline two\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        loaded = load_rendition(self._root, "AGENTS.md", "claude")
        self.assertEqual(loaded, content)

    @covers("REQ-0.0.37-22-01")
    def test_load_is_deterministic_same_file_same_bytes(self) -> None:
        """Same committed artifact yields byte-identical bytes across multiple loads."""
        content = b"# AGENTS.md\n\nsome content\n"
        save_rendition(self._root, "AGENTS.md", "claude", content)
        first = load_rendition(self._root, "AGENTS.md", "claude")
        second = load_rendition(self._root, "AGENTS.md", "claude")
        self.assertEqual(first, second)
        self.assertIs(type(first), bytes)

    @covers("REQ-0.0.37-22-01")
    def test_each_surface_consumer_pair_has_isolated_store(self) -> None:
        """A save to one (surface, consumer) does not affect another pair."""
        save_rendition(self._root, "AGENTS.md", "claude", b"claude content")
        self.assertFalse(rendition_exists(self._root, "AGENTS.md", "codex"))
        with self.assertRaises(FileNotFoundError):
            load_rendition(self._root, "AGENTS.md", "codex")

    @covers("REQ-0.0.37-22-01")
    def test_save_overwrites_existing_artifact(self) -> None:
        """save_rendition replaces a prior committed rendition (recompose flow)."""
        save_rendition(self._root, "AGENTS.md", "claude", b"v1 content")
        save_rendition(self._root, "AGENTS.md", "claude", b"v2 content")
        loaded = load_rendition(self._root, "AGENTS.md", "claude")
        self.assertEqual(loaded, b"v2 content")


class TestCorpusFingerprint(unittest.TestCase):
    """corpus_fingerprint hashes canonical model content — not raw file bytes (REQ-0.0.37-22-03)."""

    @covers("REQ-0.0.37-22-03")
    def test_fingerprint_is_deterministic_for_same_corpus(self) -> None:
        """The same corpus content yields the same digest across calls."""
        corpus = Corpus(entries=(_entry("a"), _entry("b", text="other")))
        self.assertEqual(corpus_fingerprint(corpus), corpus_fingerprint(corpus))

    @covers("REQ-0.0.37-22-03")
    def test_fingerprint_changes_when_entry_text_changes(self) -> None:
        """A content edit to any entry changes the digest (drift is detectable)."""
        before = Corpus(entries=(_entry("a", text="original"),))
        after = Corpus(entries=(_entry("a", text="mutated"),))
        self.assertNotEqual(corpus_fingerprint(before), corpus_fingerprint(after))

    @covers("REQ-0.0.37-22-03")
    def test_fingerprint_stable_across_crlf_vs_lf_corpus(self) -> None:
        """Identical entries serialized with CRLF vs LF separators yield equal digests.

        This is the cross-platform invariant: the fingerprint is over the canonical
        model serialization, never the on-disk file bytes (Windows writes CRLF).
        """
        line_a = _entry("a").model_dump_json()
        line_b = _entry("b", text="second").model_dump_json()
        lf_corpus = Corpus.loads(line_a + "\n" + line_b)
        crlf_corpus = Corpus.loads(line_a + "\r\n" + line_b)
        self.assertEqual(corpus_fingerprint(lf_corpus), corpus_fingerprint(crlf_corpus))

    @covers("REQ-0.0.37-22-03")
    def test_empty_corpus_has_stable_digest(self) -> None:
        """An empty corpus has a well-defined, stable fingerprint."""
        self.assertEqual(corpus_fingerprint(Corpus()), corpus_fingerprint(Corpus()))


class TestRenditionProvenanceSidecar(unittest.TestCase):
    """The provenance sidecar freezes the corpus fingerprint at commit time (REQ-0.0.37-22-03)."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _provenance(self) -> RenditionProvenance:
        return RenditionProvenance(
            corpus_fingerprint="deadbeef",
            corpus_entry_count=2,
            committed_ts="2026-06-19T00:00:00+00:00",
            attestor="g0",
            attestation_text="attest completed",
        )

    @covers("REQ-0.0.37-22-03")
    def test_fingerprint_path_is_corpus_json_sibling_of_rendition(self) -> None:
        """The sidecar lives beside the rendition as <consumer>.corpus.json."""
        path = fingerprint_path(self._root, "AGENTS.md", "claude")
        self.assertEqual(
            path, self._root / ".gzkit" / "renditions" / "AGENTS.md" / "claude.corpus.json"
        )

    @covers("REQ-0.0.37-22-03")
    def test_sidecar_is_invisible_to_md_glob(self) -> None:
        """The sidecar suffix is .corpus.json so the *.md rendition glob never sees it."""
        path = fingerprint_path(self._root, "AGENTS.md", "claude")
        self.assertFalse(path.name.endswith(".md"))

    @covers("REQ-0.0.37-22-03")
    def test_save_then_load_roundtrips_provenance(self) -> None:
        """A saved provenance sidecar loads back equal."""
        prov = self._provenance()
        save_fingerprint(self._root, "AGENTS.md", "claude", prov)
        loaded = load_fingerprint(self._root, "AGENTS.md", "claude")
        self.assertEqual(loaded, prov)

    @covers("REQ-0.0.37-22-03")
    def test_load_returns_none_when_sidecar_absent(self) -> None:
        """A missing sidecar loads as None (the freshness gate treats this as drift)."""
        self.assertIsNone(load_fingerprint(self._root, "AGENTS.md", "claude"))

    @covers("REQ-0.0.37-22-03")
    def test_provenance_model_rejects_unknown_fields(self) -> None:
        """RenditionProvenance is frozen + extra='forbid' (typo defense)."""
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            RenditionProvenance(
                corpus_fingerprint="x",
                corpus_entry_count=0,
                committed_ts="t",
                attestor="a",
                attestation_text="b",
                bogus="nope",  # type: ignore[call-arg]
            )


if __name__ == "__main__":
    unittest.main()
