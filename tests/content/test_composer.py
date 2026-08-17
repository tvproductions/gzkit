"""Composer engine tests — OBPI-0.0.37-21 (BEHAVIOR REQ proofs for engine layer).

REQ-derived: composer is deterministic (no network/LLM), invariant-tier entries
appear verbatim in the candidate, and violations are rejected.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.content.composer import compose
from gzkit.content.corpus_store import append_entry
from gzkit.content.models import CorpusEntry
from gzkit.traceability import covers

_VENDOR_MANIFEST = {
    "content_type_routes": {"AgentContract": ["root"]},
    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
}

_INVARIANT_TEXT = "YOU OWN THE WORK COMPLETELY."
_COMPRESSIBLE_TEXT = "Prefer stdlib JSONL for append-only stores."


def _seed_project(root: Path) -> None:
    """Write a minimal project with corpus + vendor manifest into *root*."""
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(
        json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
    )
    (root / ".gzkit").mkdir(exist_ok=True)
    append_entry(
        root,
        "AGENTS.md",
        CorpusEntry(
            id="e-invariant",
            surface="AGENTS.md",
            section="prime-directive",
            tier="invariant",
            classification="Mechanical",
            text=_INVARIANT_TEXT,
            origin="test",
            ts="2026-06-14T00:00:00Z",
        ),
    )
    append_entry(
        root,
        "AGENTS.md",
        CorpusEntry(
            id="e-compressible",
            surface="AGENTS.md",
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text=_COMPRESSIBLE_TEXT,
            origin="test",
            ts="2026-06-14T00:00:00Z",
        ),
    )


class TestComposerEngine(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        _seed_project(self._root)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-21-02")
    def test_deterministic_output(self) -> None:
        """Identical corpus + setpoint + candidate → identical byte evidence; no network call."""
        candidate_text = f"{_INVARIANT_TEXT}\ncompressed content"

        with patch("socket.socket") as mock_sock:
            result1 = compose(self._root, "AGENTS.md", "root", candidate_text)
            result2 = compose(self._root, "AGENTS.md", "root", candidate_text)

        mock_sock.assert_not_called()
        self.assertEqual(result1.byte_evidence, result2.byte_evidence)
        self.assertEqual(result1.setpoint, result2.setpoint)
        self.assertEqual(result1.candidate_text, result2.candidate_text)

    @covers("REQ-0.0.37-21-03")
    def test_invariant_tier_verbatim_presence(self) -> None:
        """Invariant-tier entry text appears verbatim in a valid candidate."""
        candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
        result = compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertIn(_INVARIANT_TEXT, result.candidate_text)
        self.assertGreater(result.byte_evidence.invariant_bytes, 0)

    @covers("REQ-0.0.37-21-03")
    def test_invariant_floor_violation_raises(self) -> None:
        """A candidate dropping an invariant entry is refused with ValueError."""
        candidate_text = "only compressible content, no invariant"

        with self.assertRaises(ValueError) as ctx:
            compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertIn("Invariant-floor violation", str(ctx.exception))

    @covers("REQ-0.0.37-21-04")
    def test_absent_corpus_raises_file_not_found(self) -> None:
        """An absent corpus store raises FileNotFoundError (caller maps to exit 1)."""
        with self.assertRaises(FileNotFoundError):
            compose(self._root, "NONEXISTENT.md", "root", "some text")

    @covers("REQ-0.0.37-21-04")
    def test_undeclared_setpoint_raises_value_error(self) -> None:
        """An undeclared (content_type, consumer) setpoint raises ValueError."""
        candidate_text = f"{_INVARIANT_TEXT}\nsome content"
        with self.assertRaises(ValueError):
            compose(self._root, "AGENTS.md", "unknown-vendor", candidate_text)
