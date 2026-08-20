"""gz content commit command tests — OBPI-0.0.37-22 (REQ-0.0.37-22-07 BEHAVIOR).

REQ-derived: the governed candidate→committed promotion seam. ``gz content commit``
promotes the staged candidate to the durable committed rendition AND freezes the
corpus content-fingerprint in a provenance sidecar, under operator attestation
(corpus attestation: ``--attestor`` / ``--attestation-text`` fail-closed on empty --
 NOT Gate 5, which names OBPI/ADR completion only; GHI #822). It is the
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
        """Empty --attestor → exit 1; no rendition, no sidecar (corpus attestation fail-closed)."""
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


class TestCommitAttestationGranularity(unittest.TestCase):
    """`commit` gates the CORPUS DELTA, never the re-render (GHI #821).

    Operator ruling 2026-08-17, verbatim: *"a rerender of unhanged canon doesn't
    require my attestation"* (spelling preserved). The discriminator is
    ``corpus_fingerprint()`` — already computed at every commit, previously read
    for freshness but never for this. These tests assert the RULING, not the
    branch: each one names which of the four dispositions it pins, so a future
    change to how the exemption is detected cannot quietly change WHAT is exempt.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _commit_unattested(self) -> object:
        return self._runner.invoke(main, ["content", "commit", "AGENTS.md", "--consumer", "codex"])

    def test_first_commit_still_requires_attestation(self) -> None:
        """No prior sidecar → canon is unproven, not unchanged → still fail-closed.

        The absence of a sidecar is NOT evidence that canon is unchanged; it is
        absence of evidence either way. Reading it as an exemption would make the
        very first commit of every consumer the one unattested one.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._commit_unattested()
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertFalse(fingerprint_path(Path("."), "AGENTS.md", "codex").exists())

    def test_recommit_of_unchanged_canon_needs_no_attestation(self) -> None:
        """Corpus fingerprint unmoved since the committed sidecar → exempt, exit 0."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self.assertEqual(self._runner.invoke(main, _commit_args()).exit_code, 0)

            # Re-render the SAME canon: rewrite the candidate, commit with no attestation.
            candidate_path(Path("."), "AGENTS.md", "codex").write_text(
                _CANDIDATE_TEXT + "\ntrimmed tail\n", encoding="utf-8"
            )
            result = self._commit_unattested()
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_exempt_recommit_carries_the_standing_attestation_forward(self) -> None:
        """The exempt path inherits the prior attestor rather than blanking it.

        Canon did not move, so the operator's standing attestation still describes
        this corpus. Writing an empty attestor would record that nobody attested
        a corpus somebody did attest — losing provenance to express an exemption.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self._runner.invoke(main, _commit_args(attestor="g0", text="attest completed"))
            candidate_path(Path("."), "AGENTS.md", "codex").write_text(
                _CANDIDATE_TEXT + "\ntrimmed tail\n", encoding="utf-8"
            )
            self.assertEqual(self._commit_unattested().exit_code, 0)

            prov = load_fingerprint(Path("."), "AGENTS.md", "codex")
            assert prov is not None
            self.assertEqual(prov.attestor, "g0")
            self.assertEqual(prov.attestation_text, "attest completed")

    def test_recommit_after_canon_moved_is_fail_closed_again(self) -> None:
        """A corpus delta re-arms the gate — this is the arm that must NOT relax.

        Distinguishes the ruling from "commit never needs attestation": appending
        one entry moves the fingerprint, and the standing attestation no longer
        describes the corpus being committed.
        """
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self.assertEqual(self._runner.invoke(main, _commit_args()).exit_code, 0)

            append_entry(Path("."), "AGENTS.md", _entry("e3", text="new canon"))
            result = self._commit_unattested()
            self.assertNotEqual(result.exit_code, 0, msg=result.output)

    def test_explicit_attestation_still_honored_on_the_exempt_path(self) -> None:
        """Exempt means "not required", never "not accepted" — a supplied attestor wins."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            self._runner.invoke(main, _commit_args(attestor="first", text="first words"))
            candidate_path(Path("."), "AGENTS.md", "codex").write_text(
                _CANDIDATE_TEXT + "\nagain\n", encoding="utf-8"
            )
            result = self._runner.invoke(main, _commit_args(attestor="second", text="second words"))
            self.assertEqual(result.exit_code, 0, msg=result.output)

            prov = load_fingerprint(Path("."), "AGENTS.md", "codex")
            assert prov is not None
            self.assertEqual(prov.attestor, "second")


class TestCommitNamesThePlaybackWriter(unittest.TestCase):
    """`commit` writes the RENDITION only; it must say so and name the next writer.

    The pipeline is corpus -> compose -> commit -> playback, and the stages have
    different writers: this seam writes `.gzkit/renditions/<surface>/<consumer>.md`
    and never the played-back surface itself. A session that stops here has a
    rendered contract still showing the PRIOR canon while the ledger records a
    committed rendition — the half-applied state `gz validate --invariant-coherence`
    exists to catch, which only bites if someone runs it.

    Observed 2026-08-20: a canon repair reached this seam and reported three
    success lines with no next step. Asserting the SEMANTIC (a governed next step
    naming the playback writer) rather than the sentence, per DO IT RIGHT #6 and
    the three-part bar in `.claude/rules/guardrail-feedback-prose.md`.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_success_output_names_the_playback_writer(self) -> None:
        """A successful commit names the runnable command that writes the surface."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            result = self._runner.invoke(main, _commit_args())
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(
                "gz agent sync control-surfaces",
                result.output,
                "commit must name the playback writer; without it the rendered "
                "surface silently keeps the prior canon",
            )

    def test_success_output_states_the_rendition_only_scope(self) -> None:
        """The prose says what was written and which gate stays red until playback."""
        with self._runner.isolated_filesystem():
            _seed_corpus_and_candidate()
            output = self._runner.invoke(main, _commit_args()).output
            self.assertIn("rendition", output, "must state that only the rendition was written")
            self.assertIn(
                "--invariant-coherence",
                output,
                "must name the gate that stays red until playback runs, so the "
                "operator can tell a finished change from a half-applied one",
            )


if __name__ == "__main__":
    unittest.main()
