"""Tests for correction_mining — OBPI-0.0.70-02 session-correction mining.

The miner reads Claude Code session transcripts (ground truth) and emits
proposal records for operator-correction patterns that recur across
sessions — the corrections Behavior Rule 11 self-reporting misses. Tests
pin the REQ semantics: clustering threshold, fail-soft parsing, PII
scrubbing, content-hash idempotency, and the read-only/--dry-run fences.

All fixtures are tempfile-backed per .gzkit/rules/tests.md. Records are
plain dicts by design: ADR-0.0.70 Boundary Invariant 3 pins the miner
stdlib-only, which overrides the Pydantic default for this module.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.insights.correction_mining import (
    _cluster_key,
    main,
    mine_corrections,
    scrub,
    write_proposals,
)
from gzkit.traceability import covers


def _entry(kind: str, text: str) -> dict:
    if kind == "assistant":
        return {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": text}]},
        }
    return {"type": "user", "message": {"content": text}}


def _write_session(directory: Path, name: str, user_texts: list[str]) -> None:
    """Write a transcript where each user text follows an assistant turn."""
    lines: list[dict] = []
    for text in user_texts:
        lines.append(_entry("assistant", "I made some changes."))
        lines.append(_entry("user", text))
    path = directory / f"{name}.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(json.dumps(line) + "\n")


class TestClustering(unittest.TestCase):
    """REQ-0.0.70-02-01 / REQ-0.0.70-02-02: threshold-gated clustering."""

    @covers("REQ-0.0.70-02-01")
    def test_pattern_recurring_across_three_sessions_emits_one_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            correction = "never edit the vendor mirrors directly"
            for n in range(3):
                _write_session(root, f"session-{n}", [correction])
            proposals = mine_corrections(root)
            self.assertEqual(len(proposals), 1)
            record = proposals[0]
            self.assertEqual(record["recurrence_count"], 3)
            self.assertEqual(len(record["session_ids"]), 3)
            self.assertTrue(record["cluster_key"])
            self.assertLessEqual(len(record["quote"].splitlines()), 1)

    @covers("REQ-0.0.70-02-02")
    def test_pattern_below_threshold_emits_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_session(root, "session-0", ["wrong, use the ledger instead"])
            _write_session(root, "session-1", ["wrong, use the ledger instead"])
            self.assertEqual(mine_corrections(root), [])

    @covers("REQ-0.0.70-02-02")
    def test_non_corrective_messages_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(4):
                _write_session(root, f"session-{n}", ["please add a feature for parsing"])
            self.assertEqual(mine_corrections(root), [])


class TestRealTranscriptShape(unittest.TestCase):
    """REQ-0.0.70-02-01: the parser handles the real transcript interleaving.

    Real Claude Code transcripts interleave `attachment`/`system`/`ai-title`
    entries between the assistant turn and the operator's reply, inject
    harness-authored user messages (`isMeta: true`, sidechains, `<tag>`-leading
    caveats), and carry tool results as user-typed entries. A correction is an
    operator message arriving after assistant activity — interleaved harness
    noise must not break the adjacency, and injected messages must not count.
    Pinned against observed shapes from 280 real transcripts (2026-06-12).
    """

    @covers("REQ-0.0.70-02-01")
    def test_interleaved_noise_does_not_break_adjacency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(3):
                lines = [
                    _entry("assistant", "I made some changes."),
                    {"type": "attachment", "payload": "irrelevant"},
                    {"type": "system", "content": "hook output"},
                    _entry("user", "wrong, the ledger is the source of truth"),
                ]
                path = root / f"session-{n}.jsonl"
                with path.open("w", encoding="utf-8") as fh:
                    for line in lines:
                        fh.write(json.dumps(line) + "\n")
            proposals = mine_corrections(root)
            self.assertEqual(len(proposals), 1)
            self.assertEqual(proposals[0]["recurrence_count"], 3)

    @covers("REQ-0.0.70-02-01")
    def test_meta_sidechain_and_tag_injected_messages_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(3):
                meta = _entry("user", "don't treat this as operator text")
                meta["isMeta"] = True
                side = _entry("user", "don't treat this as operator text")
                side["isSidechain"] = True
                caveat = _entry(
                    "user", "<local-command-caveat>don't count tags</local-command-caveat>"
                )
                lines = [
                    _entry("assistant", "I made some changes."),
                    meta,
                    _entry("assistant", "More changes."),
                    side,
                    _entry("assistant", "Even more."),
                    caveat,
                ]
                path = root / f"session-{n}.jsonl"
                with path.open("w", encoding="utf-8") as fh:
                    for line in lines:
                        fh.write(json.dumps(line) + "\n")
            self.assertEqual(mine_corrections(root), [])


class TestFailSoft(unittest.TestCase):
    """REQ-0.0.70-02-03: malformed input yields zero proposals, never raises."""

    @covers("REQ-0.0.70-02-03")
    def test_absent_directory_yields_zero_proposals(self):
        self.assertEqual(mine_corrections(Path("/nonexistent/gzkit-mining-test")), [])

    @covers("REQ-0.0.70-02-03")
    def test_malformed_jsonl_yields_zero_proposals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.jsonl").write_text("not json at all\n{broken", encoding="utf-8")
            (root / "empty.jsonl").write_text("", encoding="utf-8")
            self.assertEqual(mine_corrections(root), [])

    @covers("REQ-0.0.70-02-03")
    def test_non_utf8_transcript_fails_soft(self):
        """A non-UTF-8 transcript MUST yield zero proposals, never raise.

        UnicodeDecodeError subclasses ValueError (not OSError); a fail-soft
        fence that only catches OSError lets it escape the miner, violating
        REQ-02-03 ('never an exception escaping the miner').
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "binary.jsonl").write_bytes(b"\xff\xfe not valid utf-8 \x00\x81")
            self.assertEqual(mine_corrections(root), [])


class TestScrubbing(unittest.TestCase):
    """REQ-0.0.70-02-04: operator-PII rule binds every emitted record."""

    @covers("REQ-0.0.70-02-04")
    def test_email_addresses_are_scrubbed_from_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            correction = "no, never put someone@example.com in artifacts"
            for n in range(3):
                _write_session(root, f"session-{n}", [correction])
            proposals = mine_corrections(root)
            self.assertEqual(len(proposals), 1)
            self.assertNotIn("someone@example.com", proposals[0]["quote"])
            self.assertIn("[email-scrubbed]", proposals[0]["quote"])

    @covers("REQ-0.0.70-02-04")
    def test_scrub_caps_quote_to_one_line(self):
        scrubbed = scrub("no, do it right\nand here is a second line")
        self.assertEqual(len(scrubbed.splitlines()), 1)

    @covers("REQ-0.0.70-02-04")
    def test_cluster_key_scrubs_operator_email(self):
        """The git-tracked cluster_key field (and the proposal hash built from
        it) MUST NOT carry an operator email local-part.

        The operator-PII rule binds EVERY emitted record, not just the quote
        field (ADR-0.0.70 Boundary Invariant 2). _cluster_key tokenizes raw
        text, so an unscrubbed email leaks its local-part as a word token.
        """
        key = _cluster_key("no, email me at 2949663+ahuimanu@users.noreply.github.com about this")
        self.assertNotIn("ahuimanu", key)
        self.assertNotIn("gmail", key)

    @covers("REQ-0.0.70-02-04")
    def test_emitted_record_cluster_key_is_pii_free(self):
        """End-to-end: a clustered correction carrying an email emits a record
        whose cluster_key field is free of the operator address."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            correction = "no, stop emailing 2949663+ahuimanu@users.noreply.github.com in commits"
            for n in range(3):
                _write_session(root, f"session-{n}", [correction])
            proposals = mine_corrections(root)
            self.assertEqual(len(proposals), 1)
            self.assertNotIn("ahuimanu", proposals[0]["cluster_key"])


class TestIdempotency(unittest.TestCase):
    """REQ-0.0.70-02-05: re-runs never duplicate proposal records."""

    @covers("REQ-0.0.70-02-05")
    def test_second_write_over_unchanged_transcripts_adds_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcripts = root / "transcripts"
            transcripts.mkdir()
            proofs = root / "proofs"
            for n in range(3):
                _write_session(transcripts, f"session-{n}", ["stop, that breaks the gate"])
            first = write_proposals(mine_corrections(transcripts), proofs)
            second = write_proposals(mine_corrections(transcripts), proofs)
            self.assertEqual(len(first), 1)
            self.assertEqual(second, [])
            self.assertEqual(len(list(proofs.glob("proposal-*.json"))), 1)


class TestDryRun(unittest.TestCase):
    """REQ-0.0.70-02-08: --dry-run prints the summary and writes nothing."""

    @covers("REQ-0.0.70-02-08")
    def test_dry_run_writes_nothing_anywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcripts = root / "transcripts"
            transcripts.mkdir()
            proofs = root / "proofs"
            for n in range(3):
                _write_session(transcripts, f"session-{n}", ["actually, revert that change"])
            stdout = io.StringIO()
            with patch.object(sys, "stdout", stdout):
                exit_code = main(
                    [
                        "--dry-run",
                        "--transcripts-dir",
                        str(transcripts),
                        "--proofs-dir",
                        str(proofs),
                    ]
                )
            self.assertEqual(exit_code, 0)
            self.assertIn("1 cluster", stdout.getvalue())
            self.assertFalse(proofs.exists())


if __name__ == "__main__":
    unittest.main()
