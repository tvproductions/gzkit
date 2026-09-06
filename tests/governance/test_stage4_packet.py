"""Tests for Step-4a packet transcript verification (GHI #942).

Stage 4a is the human's attestation surface, and its pasted command output was
believed on the composing agent's word: an observed packet rendered a `$`-prefixed
transcript whose JSON keys the command never emits, and cited a proof command that
returns nothing. Step 4b re-derives the *claim* from the repository; nothing ever
re-ran the *packet*.

These tests pin the contract a `$` transcript makes — "I ran this and this came
back" — and hold the packet to it: a pasted line the command did not produce is a
blocker, an abridged or re-indented transcript is not, and a transcript that
witnesses nothing is a blocker. They also pin what the verifier must NOT do:
re-run the bare ARB incantations that carry no output claim.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.governance.stage4_packet import (
    extract_citation_commands,
    extract_transcripts,
    verify_packet,
)


def _packet(tmp: Path, body: str) -> Path:
    path = tmp / "packet.md"
    path.write_text(body, encoding="utf-8")
    return path


class TestTranscriptExtraction(unittest.TestCase):
    def test_dollar_prompt_opens_a_transcript_and_following_lines_are_its_claim(self) -> None:
        # The `$` prompt is the claim that this is a transcript. Lines beneath it,
        # up to the next prompt or the fence end, are what the author says came back.
        text = "```\n$ echo one\none\n$ echo two\ntwo\n```\n"
        transcripts = extract_transcripts(text)
        self.assertEqual([t.command for t in transcripts], ["echo one", "echo two"])
        self.assertEqual([t.claimed for t in transcripts], [["one"], ["two"]])

    def test_prose_dollar_outside_a_fence_is_not_a_transcript(self) -> None:
        # Only fenced blocks carry transcripts; a `$` in prose is ordinary text.
        self.assertEqual(extract_transcripts("A shell prompt is $ echo hi in prose.\n"), [])

    def test_multiline_quoted_command_is_one_command_not_a_command_plus_output(self) -> None:
        # GHI #965's class, arriving in this surface: a quoted program spanning
        # physical lines is ONE command. Splitting it would read the program's own
        # body as claimed output and report every interior line as fabricated.
        text = "```\n$ python3 -c '\nprint(1)\n'\n1\n```\n"
        transcripts = extract_transcripts(text)
        self.assertEqual(len(transcripts), 1)
        self.assertEqual(transcripts[0].command, "python3 -c '\nprint(1)\n'")
        self.assertEqual(transcripts[0].claimed, ["1"])


class TestCitationExtraction(unittest.TestCase):
    def test_bare_shell_fence_is_a_citation_never_a_transcript(self) -> None:
        # The template's ARB block cites incantations whose result is backed by a
        # receipt. It claims no output, so it is reported, never re-run — re-running
        # it would spend a full unittest sweep to witness a claim nobody made.
        text = "```bash\n# arb:unittest — full sweep\nuv run gz arb step --name unittest\n```\n"
        self.assertEqual(extract_citation_commands(text), ["uv run gz arb step --name unittest"])
        self.assertEqual(extract_transcripts(text), [])

    def test_a_fence_holding_a_transcript_yields_no_citations(self) -> None:
        # Output lines beneath a prompt are the transcript's claim, never commands.
        text = "```bash\n$ echo hi\nhi\n```\n"
        self.assertEqual(extract_citation_commands(text), [])

    def test_non_shell_fence_is_not_read_as_commands(self) -> None:
        # A pasted JSON or text block is data. Reading its lines as cited commands
        # would fill the operator's surface with noise that witnesses nothing.
        self.assertEqual(extract_citation_commands('```json\n{"a": 1}\n```\n'), [])


class TestFabricatedOutput(unittest.TestCase):
    def test_a_pasted_line_the_command_did_not_produce_is_a_blocker(self) -> None:
        # The observed GHI #942 instance: correct figures rendered inside an
        # invented object shape. The key `obpi_id` is not in the real output.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = (
                "```\n"
                '$ python3 -c \'print("{\\"identifier\\": \\"OBPI-1\\"}")\'\n'
                '{"obpi_id": "OBPI-1"}\n'
                "```\n"
            )
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertFalse(result.verified)
        self.assertTrue(any("did not produce" in b for b in result.blockers))
        self.assertEqual(result.transcripts[0].missing_lines, ['{"obpi_id": "OBPI-1"}'])

    def test_a_faithful_transcript_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            result = verify_packet(tmp, _packet(tmp, "```\n$ echo hello\nhello\n```\n"))
        self.assertTrue(result.verified, result.blockers)
        self.assertEqual(result.blockers, [])

    def test_an_abridged_transcript_is_honest(self) -> None:
        # Showing less than the command produced is legitimate editing. Showing
        # what it did NOT produce is the fabrication direction.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ printf 'a\\nb\\nc\\n'\nb\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertTrue(result.verified, result.blockers)

    def test_reindented_output_still_matches(self) -> None:
        # Real `gz covers --json` nests its summary; a packet quoting the inner
        # object re-indents it. Indentation is presentation, not a claim.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = '```\n$ printf \'  {\\n    "n": 8\\n  }\\n\'\n{\n"n": 8\n}\n```\n'
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertTrue(result.verified, result.blockers)

    def test_ellipsis_is_an_elision_not_a_claim(self) -> None:
        # The escape for output that cannot reproduce — a timestamp, a fresh
        # receipt id: elide it. Pasting an unreproducible line is what fails.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ printf 'a\\nzzz\\nc\\n'\na\n...\nc\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertTrue(result.verified, result.blockers)


class TestHollowTranscript(unittest.TestCase):
    def test_a_transcript_that_witnesses_nothing_is_a_blocker(self) -> None:
        # The second observed instance: a command cited as proof of a REQ that
        # returns nothing when run. The REQ was genuinely true; the evidence
        # offered for it witnessed nothing.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ true\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertFalse(result.verified)
        self.assertTrue(any("witnesses nothing" in b for b in result.blockers))

    def test_a_silent_command_is_honest_when_its_exit_status_is_shown(self) -> None:
        # The authorable form for a silent assert-shaped probe: show the status,
        # which is the information the reader needs and which reproduces.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = '```\n$ true; echo "exit $?"\nexit 0\n```\n'
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertTrue(result.verified, result.blockers)


class TestExitStatus(unittest.TestCase):
    def test_selective_omission_cannot_conceal_a_failure(self) -> None:
        # THE CONCEALMENT VECTOR (operator directive 2026-09-06). Containment
        # alone lets a packet quote only the success lines of a command that
        # failed: every pasted line reproduces, so the packet verifies while the
        # failure it omitted never reaches the operator. Every line below IS in
        # the real output — the lie is the omission, not any single line.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = (
                "```\n"
                "$ python3 -c \"import sys; print('ruff: clean'); "
                "print('FAILED (failures=12)', file=sys.stderr); sys.exit(1)\"\n"
                "ruff: clean\n"
                "```\n"
            )
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertFalse(result.verified)
        self.assertEqual(result.transcripts[0].missing_lines, [])
        self.assertTrue(any("exited 1" in b for b in result.blockers))

    def test_an_honest_red_run_is_authorable_by_showing_the_status(self) -> None:
        # The escape, and the reason the rule above is not a false-block: a
        # packet that WANTS to show a RED run shows the status, which reproduces
        # and puts the failure in front of the operator instead of omitting it.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = (
                "```\n"
                '$ python3 -c \'print("boom"); raise SystemExit(1)\'; echo "exit $?"\n'
                "boom\n"
                "exit 1\n"
                "```\n"
            )
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertTrue(result.verified, result.blockers)

    def test_a_piped_verifier_cannot_report_its_own_green(self) -> None:
        # The adjacent concealment: a trailing filter makes the shell report the
        # FILTER's status, so a failing suite replays as exit 0 and the verifier
        # cannot see the failure at all. Same rule as the Bash hook (GHI #589),
        # via the same predicate — never a second copy of it.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ uv run -m unittest tests.foo | tail -1\nOK\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertFalse(result.verified)
        self.assertTrue(any("exit status" in b for b in result.blockers))

    def test_a_piped_verifier_that_keeps_its_status_is_accepted(self) -> None:
        # pipefail keeps the pipe AND reports the verifier's own status, so the
        # replay observes the real result. The escape must stay open, or authors
        # route around the rule by dropping the pipe and the evidence with it.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ set -o pipefail; echo OK | tail -1\nOK\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertTrue(result.verified, result.blockers)

    def test_a_command_that_cannot_run_is_a_blocker(self) -> None:
        # An unresolvable command produces shell error text, never the pasted claim.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ gz-no-such-verb-ever\nall good\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertFalse(result.verified)

    def test_a_hung_command_is_a_blocker_never_a_hang(self) -> None:
        # The verifier stands between the agent and the operator's attestation.
        # A packet command that never returns must fail the gate, not hold it.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```\n$ sleep 30\ndone\n```\n"
            with mock.patch("gzkit.governance.stage4_packet._COMMAND_TIMEOUT_SECONDS", 1):
                result = verify_packet(tmp, _packet(tmp, body))
        self.assertFalse(result.verified)
        self.assertTrue(any("timed out" in b for b in result.blockers))


class TestPacketLevel(unittest.TestCase):
    def test_citations_are_reported_but_never_run(self) -> None:
        # Surfacing what was cited-but-unverified is the honest report of this
        # check's own reach: the operator sees which claims it did not witness.
        # A citation is not a substitute for a transcript — a packet offering
        # only citations still owes the reader one reproducible witness.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            body = "```bash\nuv run gz arb ruff\n```\n"
            result = verify_packet(tmp, _packet(tmp, body))
        self.assertEqual(result.citations, ["uv run gz arb ruff"])
        self.assertEqual(result.transcripts, [])
        self.assertEqual([b for b in result.blockers if "`$` transcript" not in b], [])

    def test_a_packet_with_no_transcripts_at_all_is_a_blocker(self) -> None:
        # Stage 4a requires "one concrete command + output the reviewer can run".
        # A packet claiming nothing reproducible offers the operator no witness.
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            result = verify_packet(tmp, _packet(tmp, "# Stage 4\n\nAll good.\n"))
        self.assertFalse(result.verified)
        self.assertTrue(any("no `$` transcript" in b for b in result.blockers))
