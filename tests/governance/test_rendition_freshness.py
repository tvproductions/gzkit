"""Freshness gate tests — OBPI-0.0.37-22 (REQ-0.0.37-22-03), OBPI-0.0.74-09.

The gate proves a committed rendition still derives from the current corpus by
comparing a corpus CONTENT-fingerprint (frozen at commit time in the provenance
sidecar) against the corpus's current fingerprint. This replaces the prior
mtime tautology (repudiated 2026-06-16: "compares st_mtime not content").

Severity resolved through the shared MX checkpoint (OBPI-0.0.74-09): outside
the hangar the gate is fail-closed; inside the hangar it is advisory. Tests use
explicit ``fail_closed=True/False`` to test each mode independently of MX state.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    rendition_fingerprint,
    rendition_path,
    save_fingerprint,
    save_rendition,
)
from gzkit.governance.trust_audits.rendition_freshness import validate_rendition_freshness
from gzkit.mx import marker as _marker
from gzkit.mx.marker import Marker
from gzkit.traceability import covers


class _TempProjectMixin(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _seed_corpus(self, surface: str, *texts: str) -> Corpus:
        """Write a valid corpus JSONL for *surface* and return the Corpus."""
        corpus_dir = self.root / ".gzkit" / "corpus"
        corpus_dir.mkdir(exist_ok=True)
        entries = tuple(
            CorpusEntry(
                id=f"e{i}",
                surface=surface,
                section="behavior-rules",
                tier="compressible",
                classification="Mechanical",
                text=text,
                origin="test",
                ts="2026-06-19T00:00:00+00:00",
            )
            for i, text in enumerate(texts or ("seed entry",))
        )
        corpus = Corpus(entries=entries)
        (corpus_dir / f"{surface}.jsonl").write_text(corpus.dumps() + "\n", encoding="utf-8")
        return corpus

    def _commit(
        self, surface: str, consumer: str, corpus: Corpus, content: bytes = b"rendition body\n"
    ) -> None:
        """Commit a rendition plus a matching provenance sidecar (what gz content commit does)."""
        save_rendition(self.root, surface, consumer, content)
        save_fingerprint(
            self.root,
            surface,
            consumer,
            RenditionProvenance(
                corpus_fingerprint=corpus_fingerprint(corpus),
                corpus_entry_count=len(corpus.entries),
                rendition_fingerprint=rendition_fingerprint(content),
                committed_ts="2026-06-19T00:00:00+00:00",
                attestor="test",
                attestation_text="attest completed",
            ),
        )

    def _corpus_file(self, surface: str) -> Path:
        return self.root / ".gzkit" / "corpus" / f"{surface}.jsonl"

    def _ledger_events(self) -> list[dict]:
        ledger_path = self.root / ".gzkit" / "ledger.jsonl"
        if not ledger_path.exists():
            return []
        return [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]


class TestRenditionFreshnessAgreement(_TempProjectMixin):
    """Gate returns no errors when corpus and rendition agree, or either is absent."""

    @covers("REQ-0.0.37-22-03")
    def test_no_errors_when_corpus_absent(self) -> None:
        """No corpus → no drift possible → no errors (even with a rendition present)."""
        save_rendition(self.root, "AGENTS.md", "claude", b"content")
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])

    @covers("REQ-0.0.37-22-03")
    def test_no_errors_when_rendition_absent(self) -> None:
        """No rendition → nothing to check → no errors (bootstrap)."""
        self._seed_corpus("AGENTS.md")
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])

    @covers("REQ-0.0.37-22-03")
    def test_no_errors_when_fingerprint_matches_corpus(self) -> None:
        """Committed fingerprint equals the corpus fingerprint → agreement → no errors."""
        corpus = self._seed_corpus("AGENTS.md", "alpha", "beta")
        self._commit("AGENTS.md", "claude", corpus)
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])

    @covers("REQ-0.0.37-22-03")
    def test_no_errors_when_both_absent(self) -> None:
        """Neither corpus nor rendition → no errors."""
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])


class TestRenditionFreshnessRegressionLock(_TempProjectMixin):
    """The repudiation regression lock: mtime is irrelevant; only content drives drift."""

    @covers("REQ-0.0.37-22-03")
    def test_mtime_bump_without_content_change_is_not_drift(self) -> None:
        """A pure mtime bump (identical content) is NOT drift — the old mtime gate flagged it."""
        corpus = self._seed_corpus("AGENTS.md", "stable")
        self._commit("AGENTS.md", "claude", corpus)
        # Make the corpus far newer than the rendition WITHOUT changing its content.
        corpus_file = self._corpus_file("AGENTS.md")
        future = corpus_file.stat().st_mtime + 10_000
        os.utime(corpus_file, (future, future))
        self.assertEqual(
            validate_rendition_freshness(self.root, fail_closed=True),
            [],
            "mtime newer but content identical → must NOT be drift",
        )

    @covers("REQ-0.0.37-22-03")
    def test_staged_candidate_file_is_not_treated_as_a_rendition(self) -> None:
        """A `<consumer>.candidate.md` left by compose must not trigger drift (no sidecar)."""
        corpus = self._seed_corpus("AGENTS.md", "stable")
        self._commit("AGENTS.md", "claude", corpus)
        # Simulate a staged candidate sitting beside the committed rendition.
        candidate = self.root / ".gzkit" / "renditions" / "AGENTS.md" / "codex.candidate.md"
        candidate.write_text("# staged candidate\n", encoding="utf-8")
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])

    @covers("REQ-0.0.37-22-03")
    def test_byte_identical_rewrite_is_not_drift(self) -> None:
        """Rewriting the corpus file with byte-identical content (new mtime) is NOT drift."""
        corpus = self._seed_corpus("AGENTS.md", "stable")
        self._commit("AGENTS.md", "claude", corpus)
        corpus_file = self._corpus_file("AGENTS.md")
        # rewrite with byte-identical content (new mtime, same fingerprint)
        corpus_file.write_text(corpus.dumps() + "\n", encoding="utf-8")
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])


class TestRenditionFreshnessDriftClosed(_TempProjectMixin):
    """Fail-closed mode: real content drift and missing provenance exit 3."""

    @covers("REQ-0.0.37-22-03")
    def test_corpus_content_edit_is_drift(self) -> None:
        """A genuine corpus content change makes the frozen fingerprint stale → one error."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        self._commit("AGENTS.md", "claude", corpus)
        self._seed_corpus("AGENTS.md", "original", "appended entry")  # corpus content grows
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(len(errors), 1, f"Expected 1 drift error, got: {errors}")

    @covers("REQ-0.0.37-22-03")
    def test_drift_error_type_is_rendition_freshness(self) -> None:
        """Drift error carries type 'rendition_freshness'."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        self._commit("AGENTS.md", "claude", corpus)
        self._seed_corpus("AGENTS.md", "mutated")
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(errors[0].type, "rendition_freshness")

    @covers("REQ-0.0.37-22-03")
    def test_drift_message_is_three_part_recovery(self) -> None:
        """Drift message names the corpus (what/why) and the compose+commit recovery (next step)."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        self._commit("AGENTS.md", "claude", corpus)
        self._seed_corpus("AGENTS.md", "mutated")
        message = validate_rendition_freshness(self.root, fail_closed=True)[0].message.lower()
        self.assertIn("corpus", message)
        self.assertIn("compose", message)
        self.assertIn("commit", message)

    @covers("REQ-0.0.37-22-03")
    @covers("REQ-0.0.74-09-02")
    def test_missing_sidecar_is_drift(self) -> None:
        """A rendition with no provenance sidecar cannot prove derivation → drift (closed)."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        save_rendition(self.root, "AGENTS.md", "claude", b"hand-placed rendition\n")  # no sidecar
        del corpus
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(len(errors), 1)

    @covers("REQ-0.0.37-22-03")
    def test_drift_emits_composition_drift_detected_event(self) -> None:
        """Fail-closed drift emits exactly one composition_drift_detected ledger event."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        self._commit("AGENTS.md", "claude", corpus)
        self._seed_corpus("AGENTS.md", "mutated")
        validate_rendition_freshness(self.root, fail_closed=True)
        drift = [e for e in self._ledger_events() if e.get("event") == "composition_drift_detected"]
        self.assertEqual(len(drift), 1)

    @covers("REQ-0.0.37-22-03")
    def test_consumers_checked_independently(self) -> None:
        """An agreeing consumer and a stale consumer under one surface are scored independently."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        self._commit("AGENTS.md", "claude", corpus)  # claude agrees
        save_rendition(self.root, "AGENTS.md", "codex", b"codex no sidecar\n")  # codex drifts
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(len(errors), 1, "only codex (missing sidecar) drifts")


class TestRenditionIntegrity(_TempProjectMixin):
    """GHI #694: committed rendition bytes are tamper-evident against a frozen digest.

    The corpus arm proves ``corpus → rendition`` derivation. This arm proves the
    committed bytes are still the bytes an operator attested. ``gz content commit``
    is a byte copy (``commands/content/commit.py``), so a committed rendition whose
    bytes no longer match its frozen ``rendition_fingerprint`` was written outside
    the promotion seam.

    Observed live 2026-07-13: ``claude.md`` was 31,990 B under a sidecar attesting
    ``total 31741B``; every rendition gate passed green because the corpus arm
    compares corpus digests (unchanged by a rendition edit) and the floor arm only
    asserts corpus ⊆ rendition (blind to prose with no corpus entry).
    """

    def test_post_commit_byte_edit_is_drift(self) -> None:
        """A rendition edited after commit no longer matches its frozen digest → drift."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        self._commit("AGENTS.md", "claude", corpus, content=b"attested body\n")
        rendition_path(self.root, "AGENTS.md", "claude").write_bytes(b"tampered body\n")
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(len(errors), 1, f"post-commit byte edit must be drift, got: {errors}")

    def test_integrity_drift_error_type_is_distinct(self) -> None:
        """Byte drift is attributed as 'rendition_integrity', not corpus staleness."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        self._commit("AGENTS.md", "claude", corpus, content=b"attested body\n")
        rendition_path(self.root, "AGENTS.md", "claude").write_bytes(b"tampered body\n")
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(errors[0].type, "rendition_integrity")

    def test_untampered_rendition_is_clean(self) -> None:
        """Committed bytes that still match their frozen digest are not drift."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        self._commit("AGENTS.md", "claude", corpus, content=b"attested body\n")
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=True), [])

    def test_absent_rendition_fingerprint_is_drift(self) -> None:
        """A sidecar with no frozen digest cannot prove integrity → drift, never a skip.

        Treating an absent digest as "nothing to check" would make the gate
        bypassable by deleting one JSON field.
        """
        corpus = self._seed_corpus("AGENTS.md", "x")
        save_rendition(self.root, "AGENTS.md", "claude", b"body\n")
        save_fingerprint(
            self.root,
            "AGENTS.md",
            "claude",
            RenditionProvenance(
                corpus_fingerprint=corpus_fingerprint(corpus),
                corpus_entry_count=len(corpus.entries),
                committed_ts="2026-06-19T00:00:00+00:00",
                attestor="test",
                attestation_text="attest completed",
            ),
        )
        errors = validate_rendition_freshness(self.root, fail_closed=True)
        self.assertEqual(
            len(errors), 1, f"absent rendition_fingerprint must be drift, got: {errors}"
        )

    def test_integrity_message_names_the_attestation_and_recovery(self) -> None:
        """Three-part recovery prose: what drifted, why it is forbidden, the next step."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        self._commit("AGENTS.md", "claude", corpus, content=b"attested body\n")
        rendition_path(self.root, "AGENTS.md", "claude").write_bytes(b"tampered body\n")
        message = validate_rendition_freshness(self.root, fail_closed=True)[0].message.lower()
        self.assertIn("attest", message)
        self.assertIn("commit", message)

    def test_integrity_drift_warns_in_warn_mode(self) -> None:
        """Warn mode reports no errors and mutates no ledger (mirrors the corpus arm)."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        self._commit("AGENTS.md", "claude", corpus, content=b"attested body\n")
        rendition_path(self.root, "AGENTS.md", "claude").write_bytes(b"tampered body\n")
        self.assertEqual(validate_rendition_freshness(self.root, fail_closed=False), [])
        self.assertEqual(self._ledger_events(), [])


class TestCheckpointWiringFreshness(_TempProjectMixin):
    """OBPI-0.0.74-09: the gate resolves severity via the shared MX checkpoint.

    Outside the hangar (no marker): fail-closed by default.
    Inside the hangar (marker present): advisory (warns, no errors).
    """

    @covers("REQ-0.0.74-09-01")
    def test_without_mx_marker_gate_is_fail_closed(self) -> None:
        """No MX marker → default mode is fail-closed (full strength outside the hangar)."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        save_rendition(self.root, "AGENTS.md", "claude", b"no sidecar\n")
        del corpus
        errors = validate_rendition_freshness(self.root)
        self.assertEqual(len(errors), 1, "outside hangar: gate must be fail-closed by default")

    @covers("REQ-0.0.74-09-01")
    def test_with_mx_marker_gate_is_advisory(self) -> None:
        """Active MX marker → default mode is advisory (gates demote inside the hangar)."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        save_rendition(self.root, "AGENTS.md", "claude", b"no sidecar\n")
        del corpus
        _marker.write(Marker(session_id="test-session"), self.root)
        errors = validate_rendition_freshness(self.root)
        self.assertEqual(errors, [], "inside hangar: gate must be advisory by default")


if __name__ == "__main__":
    unittest.main()
