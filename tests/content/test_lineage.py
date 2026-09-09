"""Rendition provenance-map artifact tests (ADR-0.35.0 Decision 5, OBPI-0.35.0-05 Task 2).

Covers the ``SectionLineage``/``ConsumerLineage`` models, the staged/committed
path helpers, and the candidate staging writer/reader this task builds. The
generator that POPULATES lineage from a corpus + candidate pair is a later
task and is NOT covered here.
"""

from __future__ import annotations

import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from pydantic import ValidationError

from gzkit.content.lineage import (
    ConsumerLineage,
    SectionLineage,
    candidate_lineage_path,
    lineage_path,
    load_candidate_lineage,
    save_candidate_lineage,
)
from gzkit.traceability import covers


class TestSectionLineageSpanValidation(unittest.TestCase):
    def test_rejects_reversed_span(self) -> None:
        """A byte_span whose start exceeds its end must be rejected at construction."""
        with self.assertRaises(ValidationError):
            SectionLineage(owned=True, entry_ids=("e-1",), byte_span=(10, 3))

    def test_rejects_negative_span(self) -> None:
        """A byte_span with a negative offset must be rejected at construction."""
        with self.assertRaises(ValidationError):
            SectionLineage(owned=False, entry_ids=(), byte_span=(-1, 5))

    def test_accepts_valid_span(self) -> None:
        """A well-formed half-open span constructs cleanly."""
        section = SectionLineage(owned=True, entry_ids=("e-1", "e-2"), byte_span=(0, 10))
        self.assertEqual(section.byte_span, (0, 10))
        self.assertEqual(section.entry_ids, ("e-1", "e-2"))


class TestSaveCandidateLineageShape(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    @covers("REQ-0.35.0-05-04")
    def test_writes_bare_adr_decision_5_shape(self) -> None:
        """The written JSON is exactly the bare {section_id: {owned, entry_ids, byte_span}} map."""
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="root",
            sections={
                "prime-directive": SectionLineage(
                    owned=True, entry_ids=("e-invariant",), byte_span=(0, 42)
                ),
                "behavior-rules": SectionLineage(owned=False, entry_ids=(), byte_span=(42, 100)),
            },
        )

        path = save_candidate_lineage(self._root, lineage)

        on_disk = json.loads(path.read_text(encoding="utf-8"))
        expected = {
            "prime-directive": {
                "owned": True,
                "entry_ids": ["e-invariant"],
                "byte_span": [0, 42],
            },
            "behavior-rules": {
                "owned": False,
                "entry_ids": [],
                "byte_span": [42, 100],
            },
        }
        self.assertEqual(on_disk, expected)


class TestSaveCandidateLineagePersistsExactBytes(unittest.TestCase):
    """REQ-0.35.0-05-08 (determinism): persisted bytes must be platform-independent.

    ``save_candidate_lineage``'s sibling writer for the same staged artifact
    pair (``compose.py``'s candidate rendition writer, Fix 3 of this OBPI's
    round-1 adversarial review) already avoids ``Path.write_text`` because it
    opens with ``newline=None`` and performs platform-dependent line-ending
    translation (LF -> CRLF on Windows). This class proves the lineage
    writer carries the same guarantee: two runs must produce byte-identical
    lineage regardless of platform, not merely byte-identical on macOS/Linux
    where the translation happens to be a no-op.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    def test_does_not_route_through_write_text(self) -> None:
        """save_candidate_lineage must not persist via Path.write_text.

        Patching ``write_text`` to raise proves the writer takes the
        ``write_bytes`` path instead of merely happening to match on a
        platform where the two are byte-equivalent.
        """
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="root",
            sections={
                "prime-directive": SectionLineage(
                    owned=True, entry_ids=("e-1",), byte_span=(0, 10)
                ),
            },
        )

        def _raise_if_called(*_args: object, **_kwargs: object) -> None:
            raise AssertionError("write_text must not be used: it newline-translates on Windows")

        with unittest.mock.patch.object(Path, "write_text", _raise_if_called):
            path = save_candidate_lineage(self._root, lineage)

        expected_document = {
            "prime-directive": {
                "owned": True,
                "entry_ids": ["e-1"],
                "byte_span": [0, 10],
            },
        }
        expected_bytes = (json.dumps(expected_document, indent=2) + "\n").encode("utf-8")

        persisted = path.read_bytes()
        self.assertEqual(persisted, expected_bytes)
        self.assertNotIn(b"\r\n", persisted)


class TestLineagePaths(unittest.TestCase):
    def test_candidate_and_committed_paths_differ(self) -> None:
        """Staged and committed lineage paths differ; staged ends `.candidate.lineage.json`."""
        root = Path("/tmp/does-not-need-to-exist")
        committed = lineage_path(root, "AGENTS.md", "root")
        staged = candidate_lineage_path(root, "AGENTS.md", "root")

        self.assertNotEqual(committed, staged)
        self.assertTrue(staged.name.endswith(".candidate.lineage.json"))
        self.assertEqual(committed.name, "root.lineage.json")


class TestCandidateLineageRoundTrip(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    def test_round_trip_returns_equal_model(self) -> None:
        """save then load returns a model equal to the one saved."""
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="codex",
            sections={
                "prime-directive": SectionLineage(
                    owned=True, entry_ids=("e-1",), byte_span=(0, 10)
                ),
            },
        )

        save_candidate_lineage(self._root, lineage)
        loaded = load_candidate_lineage(self._root, "AGENTS.md", "codex")

        self.assertEqual(loaded, lineage)

    def test_absent_file_returns_none(self) -> None:
        """A missing staged lineage artifact is not an error — it returns None."""
        result = load_candidate_lineage(self._root, "AGENTS.md", "nonexistent-consumer")
        self.assertIsNone(result)


class TestAssertCompletePartition(unittest.TestCase):
    def test_contiguous_partition_passes(self) -> None:
        """A disjoint, contiguous partition covering [0, total_bytes) raises nothing."""
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="root",
            sections={
                "a": SectionLineage(owned=True, entry_ids=("e-1",), byte_span=(0, 5)),
                "b": SectionLineage(owned=False, entry_ids=(), byte_span=(5, 12)),
            },
        )
        lineage.assert_complete_partition(12)

    def test_gap_fails_closed(self) -> None:
        """A gap between spans raises ValueError."""
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="root",
            sections={
                "a": SectionLineage(owned=True, entry_ids=("e-1",), byte_span=(0, 5)),
                "b": SectionLineage(owned=False, entry_ids=(), byte_span=(7, 12)),
            },
        )
        with self.assertRaises(ValueError):
            lineage.assert_complete_partition(12)

    def test_overlap_fails_closed(self) -> None:
        """An overlap between spans raises ValueError."""
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="root",
            sections={
                "a": SectionLineage(owned=True, entry_ids=("e-1",), byte_span=(0, 8)),
                "b": SectionLineage(owned=False, entry_ids=(), byte_span=(5, 12)),
            },
        )
        with self.assertRaises(ValueError):
            lineage.assert_complete_partition(12)

    def test_incomplete_coverage_fails_closed(self) -> None:
        """A partition that does not reach total_bytes raises ValueError."""
        lineage = ConsumerLineage(
            surface="AGENTS.md",
            consumer="root",
            sections={
                "a": SectionLineage(owned=True, entry_ids=("e-1",), byte_span=(0, 5)),
            },
        )
        with self.assertRaises(ValueError):
            lineage.assert_complete_partition(12)


if __name__ == "__main__":
    unittest.main()
