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
    RUN_LOG_KEEP_LINES,
    RUN_LOG_MAX_BYTES,
    RUN_LOG_NAME,
    _cluster_key,
    main,
    mine_corrections,
    scan_corrections,
    scrub,
    write_proposals,
    write_run_log,
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


class TestRunTelemetry(unittest.TestCase):
    """A zero-proposal run must record what it scanned (GHI #614).

    The miner's only output was its positive findings, so `0 cluster(s)` was
    indistinguishable from a miner that had silently decayed — a stale
    `CORRECTIVE_MARKERS` lexicon that no longer matches how the operator phrases
    corrections reports `0 cluster(s)` too. The sibling sensor shipped in the
    same ADR (the Stop hook) writes one telemetry line per block, so its
    catch-rate is observable; the miner had no equivalent negative-signal
    surface. ADR-0.0.70 § Consequences › Negative #3 names this decay class.

    The run log lands in the proofs directory, NOT `.gzkit/sensors/` as the GHI
    proposed: attested Boundary Invariant 2 fences the miner to write only to
    `.gzkit/chores/session-correction-mining/proofs/`.
    """

    def _run(self, texts_per_session: list[list[str]], threshold: int = 3) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n, texts in enumerate(texts_per_session):
                _write_session(root, f"session-{n}", texts)
            return scan_corrections(root, threshold=threshold)

    def test_below_threshold_run_records_the_clusters_it_saw(self) -> None:
        """The discriminator: matched corrections but nothing met the threshold."""
        run = self._run([["stop, that breaks the gate"]], threshold=3)

        self.assertEqual(run["proposals"], [])
        self.assertGreater(
            run["corrections_matched"],
            0,
            "a healthy null result still records that corrections were matched",
        )
        self.assertGreater(run["clusters_total"], 0)
        self.assertEqual(run["threshold"], 3)

    def test_lexicon_miss_records_zero_matches_distinguishing_decay(self) -> None:
        """A decayed lexicon reads differently from a below-threshold run.

        Same empty proposal list; `corrections_matched == 0` is the signal that
        the marker vocabulary matched nothing at all.
        """
        run = self._run([["please proceed with the next increment"]], threshold=3)

        self.assertEqual(run["proposals"], [])
        self.assertEqual(run["corrections_matched"], 0)
        self.assertEqual(run["clusters_total"], 0)

    def test_transcript_and_session_counts_reflect_what_was_scanned(self) -> None:
        run = self._run(
            [["stop, that breaks the gate"], ["stop, that breaks the gate"], []],
            threshold=3,
        )

        self.assertEqual(run["transcripts_scanned"], 3)
        self.assertEqual(
            run["sessions_with_corrections"],
            2,
            "the third transcript carried no correction and must not be counted",
        )

    def test_run_log_records_counts_and_never_operator_text(self) -> None:
        """Boundary Invariant 2's PII arm: the run log is counts and config only."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcripts = root / "transcripts"
            transcripts.mkdir()
            proofs = root / "proofs"
            secret = "stop, that breaks the gate at contractor@example.com"
            _write_session(transcripts, "session-0", [secret])

            run = scan_corrections(transcripts, threshold=3)
            log = write_run_log(run, proofs)

            body = log.read_text(encoding="utf-8")
            record = json.loads(body.splitlines()[-1])
            self.assertEqual(record["proposals_emitted"], 0)
            self.assertEqual(record["threshold"], 3)
            self.assertEqual(record["transcripts_scanned"], 1)
            self.assertTrue(record["ts"])
            self.assertNotIn("breaks the gate", body)
            self.assertNotIn("contractor@example.com", body)

    def test_real_run_writes_the_log_even_with_no_proposals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcripts = root / "transcripts"
            transcripts.mkdir()
            proofs = root / "proofs"
            _write_session(transcripts, "session-0", ["stop, that breaks the gate"])

            stdout = io.StringIO()
            with patch.object(sys, "stdout", stdout):
                exit_code = main(
                    ["--transcripts-dir", str(transcripts), "--proofs-dir", str(proofs)]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(list(proofs.glob("proposal-*.json")), [])
            self.assertTrue(
                (proofs / RUN_LOG_NAME).is_file(),
                "a zero-proposal run must still leave a trace it ran",
            )

    def test_over_cap_run_log_is_rotated_to_the_newest_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proofs = Path(tmp) / "proofs"
            proofs.mkdir()
            log = proofs / RUN_LOG_NAME
            log.write_text("x" * (RUN_LOG_MAX_BYTES + 1) + "\n", encoding="utf-8")

            write_run_log(scan_corrections(Path(tmp) / "absent"), proofs)

            lines = log.read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), RUN_LOG_KEEP_LINES + 1)
            self.assertEqual(json.loads(lines[-1])["transcripts_scanned"], 0)

    def test_mine_corrections_remains_the_proposals_projection(self) -> None:
        """The existing narrow API is the run's proposal list, not a second scan.

        Compared on the content-derived identity fields; ``mined_at`` is wall-clock
        and differs between two invocations by design.
        """

        def identity(proposals: list[dict]) -> list[tuple]:
            return [
                (p["proposal_id"], p["cluster_key"], p["recurrence_count"], tuple(p["session_ids"]))
                for p in proposals
            ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for n in range(3):
                _write_session(root, f"session-{n}", ["stop, that breaks the gate"])

            narrow = identity(mine_corrections(root))
            full = identity(scan_corrections(root)["proposals"])

            self.assertEqual(narrow, full)
            self.assertEqual(len(narrow), 1)


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
