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

import gzkit.commands.content.unown as unown_module
from gzkit.cli.main import main
from gzkit.commands.content.unown import _mint_event_id, content_unown_cmd
from gzkit.content.ownership import (
    OwnershipDeclaration,
    OwnershipLoadError,
    load_declaration,
    measure_section_spans,
    sections_digest,
)
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.ledger import Ledger, LedgerEvent
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

# A day-one declaration is witnessed by a real `section_ownership_genesis`
# ledger event, never by self-coherence: a null `floor_event_id` is fail-closed
# (REQ-0.35.0-04-02), because a floor that merely agrees with its own summed
# span is exactly what an attacker recomputes after a hand edit. The seed floor
# is derived from measure_section_spans, never hardcoded, so it stays coherent
# regardless of _SURFACE_TEXT's exact byte layout. With the default
# alpha="corpus-owned", beta-section is the only section 'unowned' at seed time.
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
    # Mint the genesis witness FIRST and embed its id, because the emitter's
    # contract is caller-minted ids: Layer-1 (the declaration) and Layer-2 (the
    # ledger) must agree on which event proves the day-one floor.
    genesis_event_id = f"section-ownership-genesis-Doc.md-{floor}"
    _DECLARATION_PATH.write_text(
        json.dumps(
            {
                "surface": "Doc.md",
                "sections": sections,
                "unowned_byte_floor": floor,
                "measured_at": "2026-09-02T00:00:00Z",
                "floor_event_id": genesis_event_id,
            }
        ),
        encoding="utf-8",
    )
    emit_section_ownership_genesis(
        Path("."), genesis_event_id, "Doc.md", sections_digest(sections), floor
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

    @covers("REQ-0.35.0-04-05")
    def test_a_post_swap_durability_failure_keeps_the_journal_and_says_so(self) -> None:
        """Would break if an ambiguous declaration-write error cleared the journal.

        Step-4b round-3 finding 3, and a regression introduced by this OBPI's own
        round-2 finding-4 repair. The parent-directory fsync barrier runs AFTER
        `os.replace` has swapped the file, so an `OSError` from it means the
        declaration may ALREADY carry the new floor while no ledger witness
        exists. The handler used to treat every such error as pre-commit: it
        deleted the journal and printed "Nothing written" and "the declaration is
        byte-unchanged". Both were false, the transition became uncompletable,
        and `load_declaration` rejected the declaration permanently.

        The failure is injected on the DIRECTORY fsync specifically -- the file
        descriptor is synced before the swap, the directory after it, so failing
        only the second reproduces the post-swap window and nothing else. This is
        a plain `EIO`: no adversary, just failing media or an NFS mount.
        """
        import stat as _stat

        with self._runner.isolated_filesystem():
            self._seed()
            real_fsync = os.fsync
            # `write_declaration_atomically` writes the JOURNAL first and the
            # DECLARATION second, and both sync the same parent directory. Fail
            # only the second directory sync, so the journal lands intact and the
            # fault is isolated to the post-swap window on the declaration --
            # failing the first would merely test the journalling branch, where
            # "Nothing written" is entirely true.
            directory_syncs = 0

            def fail_second_directory_fsync(fd: int) -> None:
                nonlocal directory_syncs
                if _stat.S_ISDIR(os.fstat(fd).st_mode):
                    directory_syncs += 1
                    if directory_syncs >= 2:
                        raise OSError(5, "Input/output error")
                    return None
                return real_fsync(fd)

            fail_directory_fsync = fail_second_directory_fsync

            with patch("gzkit.content.ownership.os.fsync", side_effect=fail_directory_fsync):
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            residue = [p.name for p in _DECLARATION_PATH.parent.iterdir()]
            self.assertIn(
                "Doc.md.json.journal",
                residue,
                "the journal is the ONLY record able to complete a transition whose "
                "declaration may already have landed; it must survive",
            )
            self.assertNotIn(
                "Nothing written",
                result.output,
                "the command must not claim nothing happened when the atomic swap "
                "may already have changed the declaration",
            )
            self.assertNotIn(
                "byte-unchanged",
                result.output,
                "the command must not assert a premise it cannot know after the swap",
            )

    @covers("REQ-0.35.0-04-02")
    def test_replay_refuses_to_complete_into_a_state_the_loader_would_reject(self) -> None:
        """Would break if the already-landed replay branch skipped validation.

        Step-4b round-3 finding 4. Every predecessor/span/eligibility check lives
        inside the branch where the on-disk `floor_event_id` differs from the
        journal's event. When the declaration write already landed and only the
        ledger append failed, replay reached the append and the journal unlink
        having validated nothing. Growing the newly-unowned section before the
        retry then produced `retry_exit=0` with the journal consumed and a
        declaration the canonical loader rejects -- recovery reporting success
        while destroying the record that could have recovered it.
        """
        with self._runner.isolated_filesystem():
            self._seed()
            real_append = Ledger.append

            def refuse_append(self_ledger, event):  # noqa: ANN001, ANN202
                msg = "ledger unavailable"
                raise OSError(msg)

            with patch.object(Ledger, "append", refuse_append):
                first = _unown(self._runner, attestor="g0", reason="moving to prose doc")
            self.assertEqual(first.exit_code, 2, msg=first.output)
            self.assertTrue((_DECLARATION_PATH.parent / "Doc.md.json.journal").exists())

            # The surface GROWS before the retry: the section that was un-owned
            # is now far larger, so the floor the journal would complete into no
            # longer covers the live unowned span.
            Path("Doc.md").write_text(
                _SURFACE_TEXT.replace("alpha body", "alpha body " + ("x" * 400)),
                encoding="utf-8",
            )
            Ledger.append = real_append

            retry = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertNotEqual(
                retry.exit_code,
                0,
                msg=f"replay must refuse a state the loader would reject: {retry.output}",
            )
            self.assertTrue(
                (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                "a refused replay must RETAIN the journal so the transition stays "
                "completable once the surface is reconciled",
            )

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
            # No STAGING file may survive -- a rolled-back write leaves no
            # half-serialized temp behind. The JOURNAL is a different artifact
            # and is deliberately retained (Step-4b round-3 finding 3): the
            # declaration write is no longer provably all-or-nothing, because
            # the parent-directory durability barrier runs AFTER `os.replace`.
            # An OSError therefore cannot distinguish "never landed" from
            # "landed but not yet durable", and deleting the journal on that
            # ambiguity destroyed the only record able to complete the
            # transition. Retaining it is safe in both directions: replay
            # re-validates every field against the declaration actually on disk.
            self.assertEqual(
                [name for name in residue if name.endswith(".tmp")],
                [],
                f"a rolled-back transaction leaves no staging file: {residue}",
            )
            self.assertIn(
                "Doc.md.json.journal",
                residue,
                "the journal must be RETAINED after an ambiguous declaration-write "
                "failure -- it is the only record that can complete the transition",
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


class TestContentUnownReplayJournalValidation(unittest.TestCase):
    """Step-4b adversary finding 2: a forged journal must never author an
    arbitrary declaration write or floor raise.

    `_replay_pending_transition` is CRASH-RECOVERY STATE ONLY -- it may
    complete a transition proven to continue the live on-disk predecessor and
    the real measured section spans, never invent a new one. Every case here
    hand-authors `.gzkit/ownership/Doc.md.json.journal` the way the reported
    adversary run did (accepted with exit 0, floor raised 26 -> 1025, blank
    provenance) and asserts the replay path now refuses it instead.
    """

    _JOURNAL_PATH = Path(".gzkit") / "ownership" / "Doc.md.json.journal"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _seed(self) -> tuple[int, int]:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]
        return _SEED_FLOOR, span

    def _on_disk_parent(self) -> str | None:
        """The chain pointer actually on disk, for forging an otherwise-valid journal.

        A forged journal must be wrong in EXACTLY ONE field -- the one its test
        names. Hardcoding `parent_event_id=self._on_disk_parent()` was correct only while the
        day-one declaration carried a null `floor_event_id`; now that genesis is
        witnessed by a real ledger event, a null parent is itself a second
        defect, and the parent-mismatch check fires FIRST and masks the check
        under test. Reading the live pointer keeps each test a guard for its own
        check rather than an alias for this one.
        """
        return json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))["floor_event_id"]

    def _base_record(
        self,
        *,
        prior_floor: int,
        new_floor: int,
        parent_event_id: str | None,
        section: str = "alpha-section",
    ) -> dict:
        return {
            "surface": "Doc.md",
            "section": section,
            "prior_unowned_byte_floor": prior_floor,
            "new_unowned_byte_floor": new_floor,
            "attestor": "g0",
            "reason": "moving to prose doc",
            "ts": "2026-09-02T00:00:00+00:00",
            "parent_event_id": parent_event_id,
            "declaration_json": "{}",
            # Placeholder -- callers overwrite with a genuinely re-minted id
            # unless the test is specifically exercising a non-re-minting id.
            "event_id": "not-a-real-event-id",
        }

    def _derive_declaration_json(self, *, section: str, new_floor: int, event_id: str) -> str:
        """Build the JSON a CORRECT replay would derive for this transition.

        Mirrors `_replay_pending_transition`'s own derivation exactly: read
        the live on-disk predecessor, flip `section` to 'unowned', set the
        new floor and event id. Tests use this to build a forged journal's
        `declaration_json` so that ONLY the field under test disagrees with
        a genuine transition -- never a confound like a bare `"{}"`
        placeholder, which fails the declaration_json-equality check
        regardless of whether the check the test actually names still
        exists (the check that check fires LAST, so a wrong-on-its-face
        placeholder masks every earlier check being deleted).
        """
        on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
        predecessor = OwnershipDeclaration(**on_disk)
        new_sections = dict(predecessor.sections)
        new_sections[section] = "unowned"
        successor = predecessor.model_copy(
            update={
                "sections": new_sections,
                "unowned_byte_floor": new_floor,
                "floor_event_id": event_id,
            }
        )
        return successor.model_dump_json(indent=2) + "\n"

    def _write_journal(self, record: dict) -> None:
        self._JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._JOURNAL_PATH.write_text(json.dumps(record), encoding="utf-8")

    def _assert_refused_and_untouched(
        self, *, exit_code: int = 2, req: str = "REQ-0.35.0-04-02", defect: str | None = None
    ):
        """Assert the journal was refused, and — when *defect* is given — that
        it was refused BY THE CHECK UNDER TEST rather than by any other.

        Asserting only "some refusal happened" is what made four of these
        tests false guards: every check exits 2, prints "Why forbidden:" and
        cites the same REQ, so deleting the check a test names left a
        DIFFERENT check to satisfy the assertions and the test stayed green.
        *defect* pins the specific message, so the test fails when its own
        check is removed — which is the only thing that makes it a guard.
        """
        before_bytes = _DECLARATION_PATH.read_bytes()
        before_ledger = len(_ledger_events())

        result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

        self.assertEqual(result.exit_code, exit_code, msg=result.output)
        self.assertEqual(
            _DECLARATION_PATH.read_bytes(),
            before_bytes,
            "a refused journal must leave the declaration byte-unchanged",
        )
        self.assertEqual(
            len(_ledger_events()),
            before_ledger,
            "a refused journal must emit no ledger event",
        )
        self.assertIn("Why forbidden:", result.output)
        self.assertIn(req, result.output)
        self.assertNotIn("Traceback", result.output)
        self.assertNotIn("Unexpected error", result.output)
        if defect is not None:
            self.assertIn(
                defect,
                result.output,
                f"refused, but NOT by the check under test: expected {defect!r}",
            )
        return result

    @covers("REQ-0.35.0-04-02")
    def test_event_id_that_does_not_re_mint_is_refused(self) -> None:
        """Would break if replay trusted a journal's claimed `event_id`
        without re-deriving it from the journal's own content -- exactly the
        adversary's forged journal, accepted with exit 0 in the reported
        finding.

        Every OTHER field is genuinely self-consistent (real prior floor,
        real parent, real span, a correctly-DERIVED `declaration_json` keyed
        to the placeholder event_id) so only the re-mint check can catch
        this.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed()
            record = self._base_record(
                prior_floor=prior_floor,
                new_floor=prior_floor + span,
                parent_event_id=self._on_disk_parent(),
            )
            # event_id is left as the placeholder, which does not re-mint.
            record["declaration_json"] = self._derive_declaration_json(
                section=record["section"],
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            self._write_journal(record)
            self._assert_refused_and_untouched(
                defect="does not re-mint from the journal's own content"
            )

    @covers("REQ-0.35.0-04-02")
    def test_mismatched_prior_floor_is_refused(self) -> None:
        """Would break if replay never checked that the journal starts from
        the declaration currently on disk.

        `event_id` genuinely re-mints from the record's own (forged) content,
        `parent_event_id` genuinely matches the on-disk chain pointer, and
        `declaration_json` is correctly DERIVED for this forged transition --
        only the prior-floor check can catch this.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed()
            forged_prior = prior_floor + 999
            record = self._base_record(
                prior_floor=forged_prior,
                new_floor=forged_prior + span,
                parent_event_id=self._on_disk_parent(),
            )
            record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
            record["declaration_json"] = self._derive_declaration_json(
                section=record["section"],
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            self._write_journal(record)
            self._assert_refused_and_untouched(defect="does not match the floor currently on disk")

    @covers("REQ-0.35.0-04-02")
    def test_mismatched_parent_event_id_is_refused(self) -> None:
        """Would break if replay never checked the journal's chain pointer
        against the declaration's actual `floor_event_id`.

        Every other field is genuinely self-consistent -- only the
        parent-pointer check can catch this.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed()
            forged_parent = "section-ownership-unowned-Doc.md-beta-section-deadbeefdeadbeef"
            record = self._base_record(
                prior_floor=prior_floor,
                new_floor=prior_floor + span,
                parent_event_id=forged_parent,
            )
            record["event_id"] = unown_module._mint_event_id(record, forged_parent)
            record["declaration_json"] = self._derive_declaration_json(
                section=record["section"],
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            self._write_journal(record)
            self._assert_refused_and_untouched(defect="does not match the on-disk floor_event_id")

    @covers("REQ-0.35.0-04-02")
    def test_arbitrary_floor_jump_disconnected_from_measured_span_is_refused(self) -> None:
        """Reproduces the adversary's exact forgery: an unvalidated floor
        raise disconnected from any real section span.

        `event_id` genuinely re-mints from the record's own content,
        `prior_unowned_byte_floor`/`parent_event_id` genuinely match the
        declaration on disk, and `declaration_json` is correctly DERIVED for
        this forged transition -- only the real-measured-span check can
        catch this.
        """
        with self._runner.isolated_filesystem():
            prior_floor, _span = self._seed()
            forged_new_floor = prior_floor + 999
            record = self._base_record(
                prior_floor=prior_floor,
                new_floor=forged_new_floor,
                parent_event_id=self._on_disk_parent(),
            )
            record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
            record["declaration_json"] = self._derive_declaration_json(
                section=record["section"],
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            self._write_journal(record)
            self._assert_refused_and_untouched(
                defect="does not equal the on-disk floor plus section"
            )

    @covers("REQ-0.35.0-04-05")
    def test_already_unowned_section_named_in_journal_is_refused(self) -> None:
        """CRITICAL (Step-4b adversary finding 2, round 2): a journal naming
        a section that is ALREADY 'unowned' on the on-disk predecessor must
        be refused, even when every other field is genuinely self-consistent.

        Would break if replay never checked section eligibility the way the
        live command path does (`current != "corpus-owned"` at
        unown.py:508-516): flipping an already-'unowned' section to
        'unowned' is a no-op on `sections`, so the derived successor JSON
        matches the journal's claim regardless of a real, correctly-derived
        `declaration_json` -- the floor would be durably inflated a SECOND
        time for one section, witnessed by a genuine ledger event recording
        a flip that never happened, on a ratchet the ordinary path can never
        lower back down.
        """
        with self._runner.isolated_filesystem():
            prior_floor, _alpha_span = self._seed()
            beta_span = measure_section_spans(_SURFACE_TEXT)["beta-section"]
            record = self._base_record(
                section="beta-section",
                prior_floor=prior_floor,
                new_floor=prior_floor + beta_span,
                parent_event_id=self._on_disk_parent(),
            )
            record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
            record["declaration_json"] = self._derive_declaration_json(
                section="beta-section",
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            self._write_journal(record)
            self._assert_refused_and_untouched(defect="not 'corpus-owned'")

    @covers("REQ-0.35.0-04-02")
    def test_declaration_json_disagreeing_with_derived_successor_is_refused(self) -> None:
        """Would break if replay trusted `declaration_json` verbatim instead
        of deriving the successor from the on-disk predecessor and comparing.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed()
            record = self._base_record(
                prior_floor=prior_floor,
                new_floor=prior_floor + span,
                parent_event_id=self._on_disk_parent(),
            )
            record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
            record["declaration_json"] = json.dumps(
                {
                    "surface": "Doc.md",
                    "sections": {
                        "doc-title": "corpus-owned",
                        "alpha-section": "unowned",
                        "beta-section": "unowned",
                    },
                    "unowned_byte_floor": prior_floor + span,
                    "measured_at": "2026-09-02T00:00:00Z",
                    "floor_event_id": record["event_id"],
                }
            )
            self._write_journal(record)
            self._assert_refused_and_untouched()

    @covers("REQ-0.35.0-04-04")
    def test_blank_attestor_in_journal_is_refused_same_shape_as_command_path(self) -> None:
        """The replay path takes the SAME fail-closed shape as the command
        path for a blank attestor/reason (REQ-0.35.0-04-04).

        Every other field -- including a correctly-DERIVED `declaration_json`
        -- is genuinely self-consistent, so only the blank-attestation check
        can catch this.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed()
            record = self._base_record(
                prior_floor=prior_floor,
                new_floor=prior_floor + span,
                parent_event_id=self._on_disk_parent(),
            )
            record["attestor"] = "   "
            record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
            record["declaration_json"] = self._derive_declaration_json(
                section=record["section"],
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            self._write_journal(record)
            self._assert_refused_and_untouched(exit_code=1, req="REQ-0.35.0-04-04")

    @covers("REQ-0.35.0-04-02")
    def test_field_complete_journal_missing_ts_is_refused_not_a_keyerror(self) -> None:
        """Would break if `_JOURNAL_FIELDS` omitted `ts` while
        `_append_event_once` still read `record["ts"]` -- a field-complete
        journal missing only `ts` would die on a raw `KeyError` instead of
        the governed three-part refusal.

        Asserts the EXACT defect phrase production emits for a missing `ts`
        field, never a bare substring like `"ts"` -- that substring occurs
        inside `_refuse_forged_journal`'s own boilerplate ("...completed
        from **its** journal...") and would pass vacuously on every refusal
        regardless of whether `ts` is actually checked.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed()
            record = self._base_record(
                prior_floor=prior_floor,
                new_floor=prior_floor + span,
                parent_event_id=self._on_disk_parent(),
            )
            record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
            record["declaration_json"] = self._derive_declaration_json(
                section=record["section"],
                new_floor=record["new_unowned_byte_floor"],
                event_id=record["event_id"],
            )
            del record["ts"]
            self._write_journal(record)
            result = self._assert_refused_and_untouched()
            self.assertIn(self._JOURNAL_PATH.as_posix(), result.output)
            self.assertIn("missing required field(s) ts", result.output)


class TestAlreadyLandedReplayBindsTheLandedMap(unittest.TestCase):
    """Step-4b round-4 finding 2: the already-landed branch witnessed the wrong map.

    When the declaration write LANDED but the ledger append did not, the retry
    takes a branch whose coherence gate checks only the landed FLOOR and the
    live unowned SPAN. Neither reads the section map. Meanwhile
    `_append_event_once` derives the emitted `sections_digest` from the
    JOURNAL's `declaration_json` rather than from the declaration actually on
    disk, and `_mint_event_id` omits the map entirely -- so a journal whose map
    differs from what landed keeps the same event id, passes id recomputation,
    and is witnessed with a digest describing a state that does not exist.

    The adversary observed `journal_unlinked=True`, disk digest
    `380c4e7a3bd5f6c924f9bfba9edef3e0`, ledger digest
    `a21473dc0b8602d21af34bf39f1404ef`, then `post_replay_loader=REJECTED`:
    recovery reporting success, consuming the only record that could have
    recovered it, and leaving a declaration the canonical loader cannot read.
    """

    _JOURNAL_PATH = Path(".gzkit") / "ownership" / "Doc.md.json.journal"

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-05")
    def test_a_journal_map_disagreeing_with_the_landed_declaration_is_refused(self) -> None:
        """Would break if the already-landed branch witnessed the journal's map."""
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]
            new_floor = _SEED_FLOOR + span

            on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            predecessor = OwnershipDeclaration(**on_disk)
            # A GENUINELY re-minted id. A hand-typed one fails the
            # id-recomputation check first and masks the branch under test --
            # the same confound `_derive_declaration_json` exists to avoid.
            event_id = _mint_event_id(
                {
                    "surface": "Doc.md",
                    "section": "alpha-section",
                    "prior_unowned_byte_floor": _SEED_FLOOR,
                    "new_unowned_byte_floor": new_floor,
                    "attestor": "g0",
                    "reason": "moving to prose doc",
                },
                on_disk["floor_event_id"],
            )

            # The declaration that ACTUALLY landed: alpha-section un-owned.
            landed_sections = dict(predecessor.sections)
            landed_sections["alpha-section"] = "unowned"
            landed = predecessor.model_copy(
                update={
                    "sections": landed_sections,
                    "unowned_byte_floor": new_floor,
                    "floor_event_id": event_id,
                }
            )
            _DECLARATION_PATH.write_text(landed.model_dump_json(indent=2) + "\n", encoding="utf-8")

            # The journal claims a DIFFERENT map at the same floor and the same
            # event id -- the one field the id does not cover.
            # `doc-title` is the only section the seed leaves 'corpus-owned',
            # so it is the only flip that actually changes the map. Flipping an
            # already-'unowned' section would leave the maps identical and the
            # test would pass while witnessing nothing.
            self.assertEqual(landed_sections["doc-title"], "corpus-owned")
            forged_sections = dict(landed_sections)
            forged_sections["doc-title"] = "unowned"
            forged = landed.model_copy(update={"sections": forged_sections})
            record = {
                "surface": "Doc.md",
                "section": "alpha-section",
                "prior_unowned_byte_floor": _SEED_FLOOR,
                "new_unowned_byte_floor": new_floor,
                "attestor": "g0",
                "reason": "moving to prose doc",
                "ts": "2026-09-02T00:00:00+00:00",
                "parent_event_id": on_disk["floor_event_id"],
                "declaration_json": forged.model_dump_json(indent=2) + "\n",
                "event_id": event_id,
            }
            self._JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
            self._JOURNAL_PATH.write_text(json.dumps(record), encoding="utf-8")

            result = _unown(
                self._runner,
                attestor="g0",
                reason="moving to prose doc",
            )

            self.assertNotEqual(
                result.exit_code,
                0,
                "a journal whose map disagrees with the landed declaration must fail closed",
            )
            self.assertTrue(
                self._JOURNAL_PATH.exists(),
                "the journal must be RETAINED -- it is the only record that can recover this",
            )
            witnesses = [r for r in _ledger_events() if r.get("id") == event_id]
            self.assertEqual(
                witnesses,
                [],
                "no witness may be appended for a map that never landed",
            )
            # The declaration deliberately does NOT load here: its
            # floor_event_id names an event the ledger never received, which is
            # the interrupted state by construction. That is precisely why the
            # journal must survive -- it is the only thing that can still
            # complete the transition. The defect was completing it WRONG and
            # then destroying that record, leaving `post_replay_loader=REJECTED`
            # with nothing left to recover from.
            self.assertIn("map", (result.output or "").lower())

    @covers("REQ-0.35.0-04-05")
    def test_an_existing_row_wearing_the_same_id_must_match_semantically(self) -> None:
        """Step-4b round-5 `[high]`: idempotence was keyed on the id alone.

        `_append_event_once` returned on the mere EXISTENCE of the id, before
        the landed map was derived or compared -- so round 4's map binding
        guarded the append path and left this one wide open. Observed
        `existing_digest_matches_landed=False`, `ledger_append_count=0`,
        `journal_unlinked=True`, then `post_replay_load=REJECTED`. Idempotence
        must mean "this exact witness is already recorded", never "something
        wears this id".
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]
            new_floor = _SEED_FLOOR + span
            on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            predecessor = OwnershipDeclaration(**on_disk)
            event_id = _mint_event_id(
                {
                    "surface": "Doc.md",
                    "section": "alpha-section",
                    "prior_unowned_byte_floor": _SEED_FLOOR,
                    "new_unowned_byte_floor": new_floor,
                    "attestor": "g0",
                    "reason": "moving to prose doc",
                },
                on_disk["floor_event_id"],
            )
            landed_sections = dict(predecessor.sections)
            landed_sections["alpha-section"] = "unowned"
            landed = predecessor.model_copy(
                update={
                    "sections": landed_sections,
                    "unowned_byte_floor": new_floor,
                    "floor_event_id": event_id,
                }
            )
            _DECLARATION_PATH.write_text(landed.model_dump_json(indent=2) + "\n", encoding="utf-8")

            # A row already wearing this id, but describing a DIFFERENT map.
            wrong = dict(landed_sections)
            wrong["doc-title"] = "unowned"
            Ledger(Path(".gzkit") / "ledger.jsonl").append(
                LedgerEvent(
                    event="section_ownership_unowned",
                    id=event_id,
                    ts="2026-09-02T00:00:00+00:00",
                    extra={
                        "surface": "Doc.md",
                        "section": "alpha-section",
                        "sections_digest": sections_digest(wrong),
                        "prior_unowned_byte_floor": _SEED_FLOOR,
                        "new_unowned_byte_floor": new_floor,
                        "attestor": "g0",
                        "reason": "moving to prose doc",
                    },
                )
            )

            record = {
                "surface": "Doc.md",
                "section": "alpha-section",
                "prior_unowned_byte_floor": _SEED_FLOOR,
                "new_unowned_byte_floor": new_floor,
                "attestor": "g0",
                "reason": "moving to prose doc",
                "ts": "2026-09-02T00:00:00+00:00",
                "parent_event_id": on_disk["floor_event_id"],
                "declaration_json": landed.model_dump_json(indent=2) + "\n",
                "event_id": event_id,
            }
            self._JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
            self._JOURNAL_PATH.write_text(json.dumps(record), encoding="utf-8")

            result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertNotEqual(result.exit_code, 0)
            self.assertTrue(
                self._JOURNAL_PATH.exists(),
                "an id collision must RETAIN the journal, not consume it",
            )
            self.assertIn("sections_digest", (result.output or ""))


if __name__ == "__main__":
    unittest.main()
