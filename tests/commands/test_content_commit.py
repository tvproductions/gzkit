"""gz content commit command tests — OBPI-0.0.37-22 (REQ-0.0.37-22-07 BEHAVIOR).

REQ-derived: the governed candidate→committed promotion seam. ``gz content commit``
promotes the staged candidate to the durable committed rendition AND freezes the
corpus content-fingerprint in a provenance sidecar, under operator attestation
(Gate 5: ``--attestor`` / ``--attestation-text`` fail-closed on empty). It is the
missing REQ-22-01 substance — ``save_rendition`` previously had no governed caller.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import (
    corpus_fingerprint,
    fingerprint_path,
    load_fingerprint,
    rendition_fingerprint,
    rendition_path,
)
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_CANDIDATE_TEXT = "# AGENTS.md\n\nYOU OWN THE WORK COMPLETELY.\n\ncompressed body\n"


def _entry(entry_id: str, *, tier: str = "compressible", text: str = "body") -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="behavior-rules",
        tier=tier,
        classification="Mechanical",
        text=text,
        origin="test",
        ts="2026-06-19T00:00:00+00:00",
    )


def _seed_corpus_and_candidate() -> None:
    """Seed a corpus and a staged candidate in the current isolated filesystem."""
    Path(".gzkit").mkdir()
    Path(".gzkit", "corpus").mkdir()
    root = Path(".")
    append_entry(root, "AGENTS.md", _entry("e1", text="YOU OWN THE WORK COMPLETELY."))
    append_entry(root, "AGENTS.md", _entry("e2", text="compressible content"))
    cand = candidate_path(root, "AGENTS.md", "codex")
    cand.parent.mkdir(parents=True, exist_ok=True)
    cand.write_text(_CANDIDATE_TEXT, encoding="utf-8")


def _commit_args(attestor: str = "g0", text: str = "attest completed") -> list[str]:
    return [
        "content",
        "commit",
        "AGENTS.md",
        "--consumer",
        "codex",
        "--attestor",
        attestor,
        "--attestation-text",
        text,
    ]


class TestContentCommitCmd(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.0.37-22-07")
    def test_commit_promotes_candidate_and_writes_fingerprint(self) -> None:
        """Success: committed rendition holds candidate bytes; sidecar holds the corpus digest."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args())
            self.assertEqual(result.exit_code, 0, msg=result.output)

            root = Path(".")
            committed = rendition_path(root, "AGENTS.md", "codex")
            self.assertTrue(committed.exists(), "committed rendition must be written")
            self.assertEqual(committed.read_text(encoding="utf-8"), _CANDIDATE_TEXT)

            sidecar = fingerprint_path(root, "AGENTS.md", "codex")
            self.assertTrue(sidecar.exists(), "provenance sidecar must be written")
            prov = load_fingerprint(root, "AGENTS.md", "codex")
            assert prov is not None
            expected_fp = corpus_fingerprint(load_corpus(root, "AGENTS.md"))
            self.assertEqual(prov.corpus_fingerprint, expected_fp)
            self.assertEqual(prov.attestor, "g0")
            # GHI #694: commit also freezes a digest of the bytes it wrote, so a
            # later out-of-seam edit to the rendition is detectable. The digest
            # must be the digest OF the committed bytes, not merely present.
            self.assertEqual(
                prov.rendition_fingerprint,
                rendition_fingerprint(committed.read_bytes()),
                "commit must freeze a digest of the committed rendition bytes",
            )

    @covers("REQ-0.0.37-22-07")
    def test_commit_is_byte_lossless_for_crlf_candidate(self) -> None:
        """A CRLF candidate commits to LF-normalized bytes (playback stays line-ending clean)."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            cand = candidate_path(Path("."), "AGENTS.md", "codex")
            cand.write_bytes(_CANDIDATE_TEXT.replace("\n", "\r\n").encode("utf-8"))
            result = self._runner.invoke(main, _commit_args())
            self.assertEqual(result.exit_code, 0, msg=result.output)
            committed = rendition_path(Path("."), "AGENTS.md", "codex").read_bytes()
            self.assertNotIn(b"\r", committed, "committed rendition must be LF-normalized")

    @covers("REQ-0.0.37-22-07")
    def test_commit_emits_rendition_committed_event(self) -> None:
        """A successful commit emits a rendition_committed event with attestor + fingerprint."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self._runner.invoke(main, _commit_args())
            events = [
                json.loads(line)
                for line in Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            committed = [e for e in events if e.get("event") == "rendition_committed"]
            self.assertEqual(len(committed), 1, f"expected 1 rendition_committed, got {events}")
            self.assertEqual(committed[0]["attestor"], "g0")
            self.assertIn("corpus_fingerprint", committed[0])

    @covers("REQ-0.0.37-22-07")
    def test_commit_fails_closed_on_empty_attestor(self) -> None:
        """Empty --attestor → exit 1, no rendition and no sidecar written (Gate 5 fail-closed)."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args(attestor=""))
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse(rendition_path(Path("."), "AGENTS.md", "codex").exists())
            self.assertFalse(fingerprint_path(Path("."), "AGENTS.md", "codex").exists())

    @covers("REQ-0.0.37-22-07")
    def test_commit_fails_closed_on_empty_attestation_text(self) -> None:
        """Empty --attestation-text → exit 1, nothing written."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args(text=""))
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse(rendition_path(Path("."), "AGENTS.md", "codex").exists())

    @covers("REQ-0.0.37-22-07")
    def test_commit_fails_closed_on_absent_candidate(self) -> None:
        """No staged candidate → exit 1, nothing written."""
        with self._runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            Path(".gzkit", "corpus").mkdir()
            append_entry(Path("."), "AGENTS.md", _entry("e1"))
            result = self._runner.invoke(main, _commit_args())
            self.assertNotEqual(result.exit_code, 0)
            self.assertFalse(rendition_path(Path("."), "AGENTS.md", "codex").exists())


if __name__ == "__main__":
    unittest.main()
