"""gz content unown command tests — attested ratchet-raise path (OBPI-0.35.0-04 Task 3).

Un-owning a section is the ONE move that raises the decrease-only unowned-byte
ratchet (`src/gzkit/content/ownership.py::record_unowned_total` refuses every
other attempt to raise it). ADR-0.35.0 § Decision item 3 names an undefined
reversal path as "the one agents invent" -- this command is the governed,
attested exception: the same corpus-attestation shape as `gz content retire`
(REQ-0.35.0-04-04), gating the one legitimate raise (REQ-0.35.0-04-05).
"""

from __future__ import annotations

import contextlib
import json
import os
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import main
from gzkit.commands.content.unown import content_unown_cmd
from gzkit.content.ownership import (
    OwnershipLoadError,
    load_declaration,
    measure_section_spans,
)
from gzkit.ledger import Ledger
from gzkit.traceability import covers
from tests.commands.common import CliRunner

_SURFACE_TEXT = (
    "# Doc Title\n"
    "preamble text under the H1\n"
    "## Alpha Section\n"
    "alpha body line one\n"
    "alpha body line two\n"
    "## Beta Section\n"
    "beta body\n"
)

_DECLARATION_PATH = Path(".gzkit") / "ownership" / "Doc.md.json"
_LEDGER_PATH = Path(".gzkit") / "ledger.jsonl"

# A genesis declaration (floor_event_id=None) is only load-bearing valid when
# its floor equals the summed span of its own declared-'unowned' sections
# (REQ-0.35.0-04-02) -- derive that sum from measure_section_spans, never
# hardcode it, so the default seed stays coherent regardless of
# _SURFACE_TEXT's exact byte layout. With the default alpha="corpus-owned",
# beta-section is the only section declared 'unowned' at seed time.
_SEED_FLOOR = measure_section_spans(_SURFACE_TEXT)["beta-section"]


def _seed_surface() -> None:
    Path("Doc.md").write_text(_SURFACE_TEXT, encoding="utf-8")


def _seed_declaration(*, alpha: str = "corpus-owned", floor: int | None = None) -> None:
    sections = {
        "doc-title": "corpus-owned",
        "alpha-section": alpha,
        "beta-section": "unowned",
    }
    if floor is None:
        spans = measure_section_spans(_SURFACE_TEXT)
        floor = sum(span for sid, span in spans.items() if sections[sid] == "unowned")
    _DECLARATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DECLARATION_PATH.write_text(
        json.dumps(
            {
                "surface": "Doc.md",
                "sections": sections,
                "unowned_byte_floor": floor,
                "measured_at": "2026-09-02T00:00:00Z",
                "floor_event_id": None,
            }
        ),
        encoding="utf-8",
    )


def _ledger_events() -> list[dict]:
    if not _LEDGER_PATH.exists():
        return []
    return [
        json.loads(line) for line in _LEDGER_PATH.read_text(encoding="utf-8").splitlines() if line
    ]


def _unown(runner: CliRunner, *, section: str = "alpha-section", attestor: str, reason: str):
    return runner.invoke(
        main,
        [
            "content",
            "unown",
            "Doc.md",
            "--section",
            section,
            "--attestor",
            attestor,
            "--reason",
            reason,
        ],
    )


class TestContentUnownFailClosed(unittest.TestCase):
    """REQ-0.35.0-04-04: empty/whitespace attestor or reason -> refuse, nothing written."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _assert_refused_byte_unchanged(
        self, *, section: str = "alpha-section", attestor: str, reason: str
    ) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration()
            before_bytes = _DECLARATION_PATH.read_bytes()
            before_ledger_count = len(_ledger_events())

            result = _unown(self._runner, section=section, attestor=attestor, reason=reason)

            self.assertNotEqual(result.exit_code, 0)
            after_bytes = _DECLARATION_PATH.read_bytes()
            self.assertEqual(
                before_bytes, after_bytes, "declaration must be byte-unchanged on refusal"
            )
            after_ledger_count = len(_ledger_events())
            self.assertEqual(
                before_ledger_count, after_ledger_count, "no ledger event may be emitted"
            )

    @covers("REQ-0.35.0-04-04")
    def test_empty_attestor_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="", reason="a real reason")

    @covers("REQ-0.35.0-04-04")
    def test_whitespace_only_attestor_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="   ", reason="a real reason")

    @covers("REQ-0.35.0-04-04")
    def test_empty_reason_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="g0", reason="")

    @covers("REQ-0.35.0-04-04")
    def test_whitespace_only_reason_is_refused(self) -> None:
        self._assert_refused_byte_unchanged(attestor="g0", reason="   ")

    def test_unknown_section_id_is_refused(self) -> None:
        """An id naming no declared section is refused; nothing written.

        Would break if production stopped checking membership before
        mutating -- e.g. if an unknown id silently no-opped with exit 0, or
        wrote a new section entry instead of refusing.
        """
        self._assert_refused_byte_unchanged(
            section="does-not-exist", attestor="g0", reason="a real reason"
        )

    def test_already_unowned_section_is_refused(self) -> None:
        """A section already 'unowned' has nothing to raise the floor by.

        Would break if production stopped distinguishing 'corpus-owned' from
        other states before mutating -- e.g. if it re-raised the floor for an
        already-unowned section, double-counting its byte span.
        """
        self._assert_refused_byte_unchanged(
            section="beta-section", attestor="g0", reason="a real reason"
        )


class TestContentUnownRaisesTheFloor(unittest.TestCase):
    """REQ-0.35.0-04-05: attested raise-path un-owns a corpus-owned section."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-05")
    def test_section_becomes_unowned_and_floor_rises_by_its_span(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(declaration["sections"]["alpha-section"], "unowned")
            self.assertEqual(declaration["unowned_byte_floor"], _SEED_FLOOR + span)

    @covers("REQ-0.35.0-04-05")
    def test_ledger_event_carries_all_five_required_fields(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            events = [e for e in _ledger_events() if e.get("section") == "alpha-section"]
            self.assertEqual(len(events), 1, msg=_ledger_events())
            event = events[0]
            self.assertEqual(event["section"], "alpha-section")
            self.assertEqual(event["prior_unowned_byte_floor"], _SEED_FLOOR)
            self.assertEqual(event["new_unowned_byte_floor"], _SEED_FLOOR + span)
            self.assertEqual(event["attestor"], "g0")
            self.assertEqual(event["reason"], "moving to prose doc")


class TestContentUnownAttestedRoundTrip(unittest.TestCase):
    """REQ-0.35.0-04-02/-05: a `gz content unown` raise reloads cleanly.

    The chain-validation `load_declaration` now enforces (Stage-2 fix cycle,
    closing the adversary's direct-hand-edit finding) must not reject the
    ONE legitimate raise path it exists to protect -- the declaration
    `gz content unown` writes carries a `floor_event_id` that resolves
    against the very ledger event this same command emits.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-02")
    def test_attested_raise_reloads_cleanly_because_its_chain_resolves(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")
            self.assertEqual(result.exit_code, 0, msg=result.output)

            # The resulting declaration must reload through the SAME
            # fail-closed loader every other caller uses -- no special-cased
            # trust for the command that just wrote it.
            declaration = load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path.cwd())
            self.assertEqual(declaration.sections["alpha-section"], "unowned")
            self.assertIsNotNone(declaration.floor_event_id)


class TestContentUnownPartialFailure(unittest.TestCase):
    """Ledger write fails after the declaration write already succeeded.

    Layer-2 truth gap the command is honest about: exit 2 (not 1) signals
    "half happened" distinctly from every exit-1 refusal above, where the
    declaration is byte-unchanged.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_ledger_append_failure_exits_2_with_declaration_persisted(self) -> None:
        """Would break if production collapsed this branch into the exit-1
        refusal path, or rolled back the already-written declaration instead
        of leaving it (falsely claiming nothing happened when it did), or
        dropped the declaration path from the error message.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(declaration["sections"]["alpha-section"], "unowned")
            self.assertEqual(declaration["unowned_byte_floor"], _SEED_FLOOR + span)
            self.assertIn(_DECLARATION_PATH.as_posix(), result.output)


class TestContentUnownIsSerialized(unittest.TestCase):
    """Two concurrent un-ownings of DIFFERENT sections must BOTH land.

    An unlocked whole-file read-modify-write loses one of them: both runs exit
    0, both emit a `section_ownership_unowned` ledger event, and the surviving
    declaration carries only ONE transition. That residue is worse than a
    refusal -- a Layer-2 event asserts a floor raise that Layer-1 silently
    discarded, on the ONE governed path that may raise the ratchet at all.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-05")
    def test_two_concurrent_unownings_of_different_sections_both_land(self) -> None:
        """Would break if the read-modify-write stopped being serialized, or if
        the second writer kept using a declaration it read before acquiring.

        The interleave is FORCED, not raced: a rendezvous inside the loaded
        read makes both workers observe the pre-transition floor before either
        writes, which is exactly the window the unlocked code lost an update
        in. The rendezvous is time-bounded and its breakage suppressed, so a
        correctly-serialized implementation -- where the second worker cannot
        reach the read until the first has committed -- proceeds rather than
        deadlocking.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            spans = measure_section_spans(_SURFACE_TEXT)
            sections = ("doc-title", "alpha-section")

            import gzkit.commands.content.unown as unown_module  # noqa: PLC0415

            rendezvous = threading.Barrier(len(sections))
            real_load = unown_module.load_declaration

            def load_then_rendezvous(*args, **kwargs):
                loaded = real_load(*args, **kwargs)
                with contextlib.suppress(threading.BrokenBarrierError, threading.ThreadError):
                    rendezvous.wait(timeout=0.75)
                return loaded

            failures: dict[str, BaseException] = {}

            def worker(section: str) -> None:
                try:
                    content_unown_cmd(
                        surface="Doc.md",
                        section=section,
                        attestor="g0",
                        reason=f"concurrent probe for {section}",
                    )
                except BaseException as exc:  # noqa: BLE001 - recorded, then asserted on
                    failures[section] = exc

            with patch.object(unown_module, "load_declaration", load_then_rendezvous):
                threads = [threading.Thread(target=worker, args=(section,)) for section in sections]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=30)

            self.assertEqual(failures, {}, f"neither worker may fail: {failures}")

            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            for section in sections:
                self.assertEqual(
                    declaration["sections"][section],
                    "unowned",
                    f"{section!r} was un-owned and its transition must survive",
                )
            self.assertEqual(
                declaration["unowned_byte_floor"],
                _SEED_FLOOR + spans["doc-title"] + spans["alpha-section"],
                "the floor must rise by BOTH spans -- a lost update shows up here",
            )
            events = [e for e in _ledger_events() if e.get("event") == "section_ownership_unowned"]
            self.assertEqual(
                sorted(e["section"] for e in events),
                sorted(sections),
                "each landed transition is witnessed exactly once",
            )
            # No ledger event may name a floor the declaration never adopted:
            # the surviving chain pointer must resolve, and the loader that
            # enforces that is the same one every other caller uses.
            reloaded = load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.unowned_byte_floor, declaration["unowned_byte_floor"])


class TestContentUnownIsRecoverable(unittest.TestCase):
    """An interrupted un-owning is COMPLETABLE on retry, never merely tolerated.

    The declaration must be written before the ledger witnesses it (a witness
    may never outlive the state it witnesses), and `load_declaration` fails
    closed when a declaration names an event the ledger does not carry. Both
    are deliberate, so recovery has to come from the WRITE side: the pending
    transition is journalled before either store is touched, and a retry
    finishes the interrupted append instead of starting a new transition.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _seed(self) -> int:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        return measure_section_spans(_SURFACE_TEXT)["alpha-section"]

    @covers("REQ-0.35.0-04-02")
    def test_a_retry_completes_a_transition_interrupted_at_the_ledger_append(self) -> None:
        """Would break if the residue of a failed ledger append were left
        unrecoverable -- the pre-fix behaviour, where the declaration named a
        `floor_event_id` for an event that does not exist and every subsequent
        run fail-closed on it, bricking the raise-path.
        """
        with self._runner.isolated_filesystem():
            span = self._seed()

            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                interrupted = _unown(self._runner, attestor="g0", reason="moving to prose doc")
            self.assertEqual(interrupted.exit_code, 2, msg=interrupted.output)

            # The interim state is honestly incoherent, never silently wrong:
            # the loader still fails closed on the unresolvable chain pointer.
            with self.assertRaises(OwnershipLoadError):
                load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path.cwd())

            retry = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(
                retry.exit_code,
                0,
                msg=f"a retry must COMPLETE the interrupted move: {retry.output}",
            )
            healed = load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path.cwd())
            self.assertEqual(healed.sections["alpha-section"], "unowned")
            self.assertEqual(healed.unowned_byte_floor, _SEED_FLOOR + span)
            events = [e for e in _ledger_events() if e.get("section") == "alpha-section"]
            self.assertEqual(len(events), 1, msg=f"exactly one witness: {events}")
            self.assertEqual(
                events[0]["id"],
                healed.floor_event_id,
                "the recovered append must reuse the id the declaration already names",
            )

    @covers("REQ-0.35.0-04-05")
    def test_a_recovered_transition_raises_the_floor_exactly_once(self) -> None:
        """Would break if a retry started a FRESH transition instead of
        finishing the journalled one -- the floor would rise by the section's
        span twice, permanently over-stating unowned bytes on a ratchet that
        cannot be raised back down by any other path.
        """
        with self._runner.isolated_filesystem():
            span = self._seed()

            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                self._unown_once()
            self._unown_once()
            third = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertNotEqual(
                third.exit_code,
                0,
                msg=f"a completed transition has nothing left to do: {third.output}",
            )
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(
                declaration["unowned_byte_floor"],
                _SEED_FLOOR + span,
                "the floor must rise exactly once for one un-owning",
            )
            events = [e for e in _ledger_events() if e.get("section") == "alpha-section"]
            self.assertEqual(len(events), 1, msg=f"exactly one witness: {events}")
            residue = sorted(
                p.name
                for p in _DECLARATION_PATH.parent.iterdir()
                if p.name not in {"Doc.md.json", "Doc.md.json.lock"}
            )
            self.assertEqual(residue, [], f"a settled transaction leaves no residue: {residue}")

    def _unown_once(self):
        return _unown(self._runner, attestor="g0", reason="moving to prose doc")

    @covers("REQ-0.35.0-04-05")
    def test_a_failed_declaration_replace_leaves_no_torn_file_and_no_witness(self) -> None:
        """Would break if the declaration were written with a truncating
        in-place write: a crash mid-write leaves a half-serialized declaration
        that no reader can parse, and the fault is injected at the rename --
        the only step that may make new contents visible.
        """
        with self._runner.isolated_filesystem():
            self._seed()
            before_bytes = _DECLARATION_PATH.read_bytes()
            before_events = _ledger_events()
            real_replace = os.replace

            def refuse_declaration_replace(src, dst, *args, **kwargs):
                if Path(dst).name == "Doc.md.json":
                    msg = "disk full"
                    raise OSError(msg)
                return real_replace(src, dst, *args, **kwargs)

            with patch("os.replace", side_effect=refuse_declaration_replace):
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertEqual(
                _DECLARATION_PATH.read_bytes(),
                before_bytes,
                "a failed declaration write must leave the file byte-unchanged, never torn",
            )
            self.assertEqual(
                _ledger_events(),
                before_events,
                "a witness must never outlive a state that was never adopted",
            )
            residue = sorted(
                p.name
                for p in _DECLARATION_PATH.parent.iterdir()
                if p.name not in {"Doc.md.json", "Doc.md.json.lock"}
            )
            self.assertEqual(
                residue, [], f"a rolled-back transaction leaves no staging or journal: {residue}"
            )


class TestContentUnownFailuresSpeakInProse(unittest.TestCase):
    """Requirement 9: every fail-closed exit names what failed, why it is
    forbidden (citing the binding rule/REQ), and a governed next step.

    A fail-closed exit that omits the `Why forbidden:` clause hands the
    operator a symptom with no rule behind it, which is exactly the state that
    invites a hand-edit of the declaration -- the silent-hand-edit path
    ADR-0.35.0 exists to close. A raw traceback is the same defect, worse.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    _JOURNAL_PATH = Path(".gzkit") / "ownership" / "Doc.md.json.journal"

    @covers("REQ-0.35.0-04-05")
    def test_a_failed_declaration_write_names_the_rule_it_is_forbidden_by(self) -> None:
        """Would break if the declaration-write-failure exit printed only a
        symptom and a next step. Every other fail-closed exit in this command
        -- including the journal write immediately before it and the ledger
        append immediately after -- cites the binding REQ; this one is reached
        with a journal already on disk, so an operator who is not told which
        rule holds is most likely to 'fix' it by deleting that journal, which
        is the one file recovery depends on.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            real_replace = os.replace

            def refuse_declaration_replace(src, dst, *args, **kwargs):
                if Path(dst).name == "Doc.md.json":
                    msg = "disk full"
                    raise OSError(msg)
                return real_replace(src, dst, *args, **kwargs)

            with patch("os.replace", side_effect=refuse_declaration_replace):
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn("Why forbidden:", result.output)
            self.assertIn("REQ-0.35.0-04", result.output)

    @covers("REQ-0.35.0-04-05")
    def test_a_failed_ledger_append_names_the_rule_it_is_forbidden_by(self) -> None:
        """Would break if this exit stated only the partial success.

        This is the LAST fail-closed exit in the command still missing the
        literal `Why forbidden:` clause its exact sibling in
        `_replay_pending_transition` carries -- two paths out of the same
        interrupted transaction, disagreeing on whether the operator is told
        which rule binds. It is also the most dangerous one to leave
        wordless: the declaration on disk now names a `floor_event_id` the
        ledger lacks, so every subsequent `load_declaration` fails closed,
        and an operator handed a bare symptom is most likely to 'fix' that by
        hand-editing the declaration -- the silent-hand-edit path ADR-0.35.0
        exists to close. The partial success must survive the addition: the
        un-owning genuinely DID happen, and prose that implies otherwise
        sends the operator to re-run it.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn("Why forbidden:", result.output)
            self.assertIn("REQ-0.35.0-04", result.output)
            # The partial success stays stated: the declaration really is on
            # disk with the new floor, so this must not read as "nothing
            # happened, run it again".
            self.assertIn("ALREADY HAPPENED", result.output)
            self.assertIn(self._JOURNAL_PATH.as_posix(), result.output)

    @covers("REQ-0.35.0-04-02")
    def test_a_structurally_wrong_journal_is_refused_in_prose_not_a_traceback(self) -> None:
        """Would break if the journal guard covered only unparseable JSON.

        A journal that PARSES but is not the expected record -- truncated to
        `null` by an interrupted write, or an object missing `event_id` --
        reaches the record's key lookups and raises TypeError/KeyError. That
        escapes as a raw traceback past the three-part prose this same
        function already supplies for the unparseable case, and a traceback
        tells the operator nothing about which file to reconcile.
        """
        for label, payload in (
            ("null", "null"),
            ("list", "[]"),
            ("missing-keys", json.dumps({"surface": "Doc.md"})),
        ):
            with self.subTest(journal=label), self._runner.isolated_filesystem():
                _seed_surface()
                _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
                self._JOURNAL_PATH.write_text(payload, encoding="utf-8")

                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

                self.assertEqual(result.exit_code, 2, msg=result.output)
                # A raw TypeError/KeyError escapes the command as an unhandled
                # exception, which the runner reports as exit 1 with an
                # "Unexpected error" line -- never as this command's governed
                # exit 2. Assert the traceback shape is absent explicitly, so
                # the test names the defect it fences rather than relying on
                # the exit code alone to imply it.
                self.assertNotIn("Unexpected error", result.output)
                self.assertNotIn("Traceback", result.output)
                # The same three-part prose the unparseable case already gets.
                self.assertIn(self._JOURNAL_PATH.as_posix(), result.output)
                self.assertIn("Why forbidden:", result.output)
                self.assertIn("REQ-0.35.0-04-02", result.output)


if __name__ == "__main__":
    unittest.main()
