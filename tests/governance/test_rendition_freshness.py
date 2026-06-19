"""Freshness gate tests — OBPI-0.0.37-22 (REQ-0.0.37-22-03).

The gate proves a committed rendition still derives from the current corpus by
comparing a corpus CONTENT-fingerprint (frozen at commit time in the provenance
sidecar) against the corpus's current fingerprint. This replaces the prior
mtime tautology (repudiated 2026-06-16: "compares st_mtime not content").

Staging (OBPI-0.0.41 warn→fail precedent): the live gate runs in WARN mode
(``_FRESHNESS_FAIL_CLOSED = False``) so ``gz check`` stays green while the corpus
is enriched and the real renditions are re-seeded; the fail-closed semantics are
proven now via ``fail_closed=True`` and go live when Increment 2 flips the flag.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    save_fingerprint,
    save_rendition,
)
from gzkit.governance.trust_audits.rendition_freshness import validate_rendition_freshness
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


class TestRenditionFreshnessWarnStaging(_TempProjectMixin):
    """Warn mode (the live Increment-1 default): drift never reds gz check."""

    @covers("REQ-0.0.37-22-03")
    def test_warn_mode_returns_no_errors_on_drift(self) -> None:
        """Default (warn) mode returns [] even on real drift — gz check stays green."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        self._commit("AGENTS.md", "claude", corpus)
        self._seed_corpus("AGENTS.md", "mutated")
        with contextlib.redirect_stderr(io.StringIO()):
            errors = validate_rendition_freshness(self.root)  # default = warn
        self.assertEqual(errors, [])

    @covers("REQ-0.0.37-22-03")
    def test_warn_mode_does_not_mutate_ledger(self) -> None:
        """Warn mode emits no ledger event (no per-check drift spam during staging)."""
        corpus = self._seed_corpus("AGENTS.md", "original")
        self._commit("AGENTS.md", "claude", corpus)
        self._seed_corpus("AGENTS.md", "mutated")
        with contextlib.redirect_stderr(io.StringIO()):
            validate_rendition_freshness(self.root)
        drift = [e for e in self._ledger_events() if e.get("event") == "composition_drift_detected"]
        self.assertEqual(drift, [])

    @covers("REQ-0.0.37-22-03")
    def test_warn_mode_prints_recovery_hint_to_stderr(self) -> None:
        """Warn mode surfaces the recompose hint on stderr (honest, non-blocking)."""
        corpus = self._seed_corpus("AGENTS.md", "x")
        save_rendition(self.root, "AGENTS.md", "claude", b"no sidecar\n")
        del corpus
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            validate_rendition_freshness(self.root)
        self.assertIn("compose", stderr.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
