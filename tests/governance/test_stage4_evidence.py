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


class TestExtractDemoCommandsMultiLine(unittest.TestCase):
    """A command spanning physical lines is ONE command (GHI #965).

    ``generate_evidence_packet`` feeds every returned string to ``_run_demo``, which
    executes it with ``shell=True``. The joiner's contract is therefore exactly "return
    what a human would have pasted into a shell". Splitting at physical line boundaries
    made the tool report NOT-ATTESTABLE for a green state — a false red landing on
    precisely the assert-shaped Demos this module's keystone prescribes.
    """

    def _extract(self, demo_body: str) -> list[str]:
        with tempfile.TemporaryDirectory() as t:
            return extract_demo_commands(_brief(Path(t), demo_body))

    def test_single_quoted_program_is_one_command(self) -> None:
        # The GHI #965 reproduction shape: `uv run python -c '` opens a quote that
        # stays open across the program until a lone closing line.
        body = "uv run python -c '\nimport sys\nraise SystemExit(0)\n'"
        self.assertEqual(self._extract(body), [body])

    def test_double_quoted_program_is_one_command(self) -> None:
        body = 'python3 -c "\nimport sys\nprint(1)\n"'
        self.assertEqual(self._extract(body), [body])

    def test_backslash_continuation_is_one_command(self) -> None:
        body = "echo one \\\n  two \\\n  three"
        self.assertEqual(self._extract(body), [body])

    def test_command_substitution_spanning_lines_is_one_command(self) -> None:
        body = "echo $(\n  printf hi\n)"
        self.assertEqual(self._extract(body), [body])

    def test_backtick_substitution_spanning_lines_is_one_command(self) -> None:
        body = "echo `\nprintf hi\n`"
        self.assertEqual(self._extract(body), [body])

    def test_heredoc_is_one_command(self) -> None:
        body = "python3 - <<'PY'\nimport sys\nraise SystemExit(0)\nPY"
        self.assertEqual(self._extract(body), [body])

    def test_interior_comment_line_is_program_text_not_a_fence_comment(self) -> None:
        # `#` inside a quoted program is Python source. Stripping it as a fence
        # comment silently rewrites the operator's probe into a different program.
        body = "python3 -c '\n# not a fence comment\nraise SystemExit(0)\n'"
        self.assertEqual(self._extract(body), [body])

    def test_interior_blank_line_is_preserved(self) -> None:
        body = "python3 -c '\nimport sys\n\nraise SystemExit(0)\n'"
        self.assertEqual(self._extract(body), [body])

    def test_interior_indentation_is_preserved(self) -> None:
        # Python is whitespace-significant: stripping interior lines changes the
        # program's meaning, not merely its shape.
        body = "python3 -c '\nfor i in (1, 2):\n    print(i)\n'"
        self.assertEqual(self._extract(body), [body])

    def test_escaped_quote_outside_quotes_does_not_open_a_continuation(self) -> None:
        # `\"` outside quotes is an escaped literal, not a quote opener; treating it
        # as one would swallow every following command into a single string.
        body = 'echo \\"\necho after'
        self.assertEqual(self._extract(body), ['echo \\"', "echo after"])

    def test_unterminated_quote_is_returned_not_dropped(self) -> None:
        # Fail-closed: an unclosed quote must still reach the shell so the demo
        # reports a real non-zero exit. Dropping it would turn a malformed Demo
        # into a silent pass — the fabrication class this module exists to stop.
        body = "python3 -c '\nimport sys"
        self.assertEqual(self._extract(body), [body])

    def test_commands_after_a_multiline_command_still_separate(self) -> None:
        body = "python3 -c '\nprint(1)\n'\necho after"
        self.assertEqual(self._extract(body), ["python3 -c '\nprint(1)\n'", "echo after"])

    def test_top_level_comments_and_blanks_are_still_dropped(self) -> None:
        # The pre-existing single-line contract is unchanged by the joiner.
        body = "# a fence comment\n\necho hello\n\n# another\necho world"
        self.assertEqual(self._extract(body), ["echo hello", "echo world"])


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

    def test_multiline_demo_that_passes_is_not_a_blocker(self) -> None:
        # GHI #965's false red: a multi-line assert-shaped probe that exits 0 must
        # produce no Demo blocker. Before the joiner this yielded one blocker per
        # physical line (exit 2 on the opener, 127 on each interior line).
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, "python3 -c '\nimport sys\nraise SystemExit(0)\n'")
            packet = generate_evidence_packet(tmp, brief, "OBPI-x")
            self.assertEqual([b for b in packet.blockers if "Demo exited" in b], [])
            self.assertEqual([d.exit_status for d in packet.demos], [0])

    def test_multiline_demo_that_fails_is_still_a_blocker(self) -> None:
        # The keystone survives the joiner: a multi-line demo asserting a bad state
        # still fails closed. Joining commands must not soften the fail-closed edge.
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            brief = _brief(tmp, "python3 -c '\nimport sys\nraise SystemExit(1)\n'")
            packet = generate_evidence_packet(tmp, brief, "OBPI-x")
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
