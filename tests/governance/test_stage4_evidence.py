"""Tests for tool-generated, fail-closed Stage-4 evidence (GHI #643).

The Stage-4 acceptance evidence must be derived from observables the agent cannot
author. These tests pin: Demo extraction, the assert-shaped-demo keystone (a demo that
exits non-zero on a bad state produces a blocker), receipt resolution, and the
fail-closed validator (no packet → blocked; bad demo → blocked).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.stage4_evidence import (
    EvidencePacket,
    _counts_from_covers_summary,
    extract_demo_commands,
    generate_evidence_packet,
    load_packet,
    validate_stage4_evidence,
    write_packet,
)


class TestCoversCountsSummary(unittest.TestCase):
    def test_uncovered_count_is_behavior_only_not_total(self) -> None:
        # A SUPPORT-carrying OBPI: 2 REQs lack a covering test (both proven
        # SUPPORT), but 0 BEHAVIOR REQs are uncovered. The attestability blocker
        # must use behavior_uncovered_reqs — SUPPORT/STRUCTURAL-FENCE REQs are
        # proven by ledger+validator, never a @covers test (ADR-0.0.59), so
        # counting them as "uncovered by a test" is a false blocker (GHI #683).
        payload = {
            "summary": {
                "total_reqs": 9,
                "covered_reqs": 7,
                "uncovered_reqs": 2,
                "behavior_uncovered_reqs": 0,
            }
        }
        self.assertEqual(_counts_from_covers_summary(payload), (9, 0))

    def test_behavior_uncovered_is_a_real_blocker(self) -> None:
        # A genuinely uncovered BEHAVIOR REQ must still surface as uncovered.
        payload = {"summary": {"total_reqs": 4, "uncovered_reqs": 3, "behavior_uncovered_reqs": 1}}
        self.assertEqual(_counts_from_covers_summary(payload), (4, 1))


def _brief(tmp: Path, demo_body: str | None) -> Path:
    """Write a minimal brief; demo_body is the inside of the ## Demo fenced block."""
    text = "# Brief\n\n## Objective\n\nx\n"
    if demo_body is not None:
        text += f"\n## Demo\n\n```bash\n{demo_body}\n```\n"
    path = tmp / "brief.md"
    path.write_text(text, encoding="utf-8")
    return path


class TestExtractDemoCommands(unittest.TestCase):
    def test_extracts_noncomment_lines(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, "# a comment\necho hello\necho world\n")
            self.assertEqual(extract_demo_commands(brief), ["echo hello", "echo world"])

    def test_no_demo_section_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, None)
            self.assertEqual(extract_demo_commands(brief), [])

    def test_stops_at_next_h2(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            path = tmp / "b.md"
            path.write_text(
                "## Demo\n\n```bash\necho one\n```\n\n"
                "## Acceptance Criteria\n\n```bash\necho two\n```\n",
                encoding="utf-8",
            )
            self.assertEqual(extract_demo_commands(path), ["echo one"])


class TestGenerateBlockers(unittest.TestCase):
    def test_no_demo_is_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, None)
            packet = generate_evidence_packet(tmp, brief, "OBPI-x")
            self.assertFalse(packet.attestable)
            self.assertTrue(any("No ## Demo" in b for b in packet.blockers))

    def test_demo_nonzero_exit_is_a_blocker(self) -> None:
        # Assert-shaped demo that fails (exit 1) → keystone: this is what catches a lie.
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, 'python3 -c "raise SystemExit(1)"')
            packet = generate_evidence_packet(tmp, brief, "OBPI-x")
            self.assertFalse(packet.attestable)
            self.assertTrue(any("Demo exited 1" in b for b in packet.blockers))

    def test_missing_receipts_are_blockers(self) -> None:
        # Temp project has no artifacts/receipts/ → every canonical receipt missing.
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, 'python3 -c "raise SystemExit(0)"')
            packet = generate_evidence_packet(tmp, brief, "OBPI-x")
            self.assertFalse(packet.attestable)
            self.assertTrue(any("No ARB receipt" in b for b in packet.blockers))


class TestPacketRoundTrip(unittest.TestCase):
    def test_write_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            packet = EvidencePacket(
                obpi_id="OBPI-x",
                generated_at="2026-06-24T00:00:00+00:00",
                demos=[],
                receipts=[],
                covers_total=0,
                covers_uncovered=0,
                attestable=False,
                blockers=["x"],
            )
            write_packet(tmp, packet)
            loaded = load_packet(tmp, "OBPI-x")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.obpi_id, "OBPI-x")
            self.assertEqual(loaded.blockers, ["x"])

    def test_load_absent_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            self.assertIsNone(load_packet(Path(t), "OBPI-nope"))


class TestValidateFailClosed(unittest.TestCase):
    def test_no_packet_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, 'python3 -c "raise SystemExit(0)"')
            errors = validate_stage4_evidence(tmp, brief, "OBPI-x")
            self.assertTrue(
                any("No tool-generated evidence packet" in e.message for e in errors),
                [e.message for e in errors],
            )

    def test_bad_demo_is_fail_closed_even_with_packet(self) -> None:
        # A green packet on disk must NOT rescue a live-failing demo — validate re-runs it.
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, 'python3 -c "raise SystemExit(1)"')
            fabricated = EvidencePacket(
                obpi_id="OBPI-x",
                generated_at="2026-06-24T00:00:00+00:00",
                demos=[],
                receipts=[],
                covers_total=0,
                covers_uncovered=0,
                attestable=True,  # fabricated green
                blockers=[],
            )
            write_packet(tmp, fabricated)
            errors = validate_stage4_evidence(tmp, brief, "OBPI-x")
            # The live re-run sees exit 1 → fail-closed regardless of the packet's claim.
            self.assertTrue(
                any("Demo exited 1" in e.message for e in errors),
                [e.message for e in errors],
            )


if __name__ == "__main__":
    unittest.main()
