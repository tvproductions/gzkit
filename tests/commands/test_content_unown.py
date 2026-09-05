"""gz content unown command tests — attested ratchet-raise path (OBPI-0.35.0-04 Task 3).

Un-owning a section is the ONE move that raises the decrease-only unowned-byte
ratchet (`src/gzkit/content/ownership.py::record_unowned_total` refuses every
other attempt to raise it). ADR-0.35.0 § Decision item 3 names an undefined
reversal path as "the one agents invent" -- this command is the governed,
attested exception: the same corpus-attestation shape as `gz content retire`
(REQ-0.35.0-04-04), gating the one legitimate raise (REQ-0.35.0-04-05).
"""

from __future__ import annotations

import ast
import contextlib
import errno
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
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
    declaration_path,
    exclusive_declaration_lock,
    load_declaration,
    measure_section_spans,
    sections_digest,
    write_bytes_atomically,
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


def _write_surface(text: str) -> None:
    """Write the byte-measured surface as BYTES, never through text mode.

    `write_text` opens with `newline=None`, which translates every `\n` to
    `os.linesep` -- so on Windows the file gains a byte per line while
    `measure_section_spans` still measures the untranslated in-memory string,
    and every floor derived here undercounts the file it describes. 23 tests in
    this module failed that way the first time Windows could run them (GHI
    #958, unblocked by GHI #955).

    The production reader is already hardened against the same asymmetry:
    `_surface_digest` decodes raw bytes rather than using `read_text`, "because
    the floor this digest protects is a count of PHYSICAL BYTES" (Step-4b
    round-8 finding 2). A fixture must produce the bytes that reader measures.
    """
    _write_named_surface("Doc.md", text)


def _write_named_surface(name: str, text: str) -> None:
    """Write a byte-measured surface under an arbitrary name, as BYTES.

    Same contract as `_write_surface`, which delegates here: a surface whose
    physical bytes an ownership floor counts is never written through text
    mode. Named surfaces exist because the identity guard needs a SECOND file
    to point at -- a request naming a surface that is not the declaration's
    declared surface, and not the same file either.
    """
    Path(name).write_bytes(text.encode("utf-8"))


def _same_file_alias(surface: str) -> str | None:
    """A SECOND on-disk spelling naming the same surface file AND declaration.

    The round-9 high finding is reproduced by a case-variant spelling on a
    case-insensitive filesystem, where `Doc.md` and `doc.md` are one file.
    macOS and Windows ship that filesystem; Linux CI does not -- so the
    case-variant is used where the filesystem supplies it and an equivalent
    symlink pair is built where it does not, rather than leaving the
    regression unwitnessed on a supported platform. Returns None only when
    neither is available.

    Raises rather than returning for an already-lower-case *surface*: the
    alias would then BE *surface*, and a witness test asserting "the recorded
    identity is `Doc.md`" would collapse into asserting that it equals the
    spelling it was passed -- true on the unfixed tree too. That is the
    silently-vacuous fixture shape this OBPI has produced nine times, so it
    fails loudly instead of skipping quietly.
    """
    alias = surface.lower()
    if alias == surface:
        msg = f"{surface!r} is already lower-case: no distinct alias spelling exists"
        raise ValueError(msg)
    alias_path = Path(alias)
    if alias_path.exists() and alias_path.samefile(surface):
        return alias
    declaration = declaration_path(Path("."), surface)
    try:
        alias_path.symlink_to(surface)
        declaration.with_name(f"{alias}.json").symlink_to(declaration.name)
    except (OSError, NotImplementedError):
        return None
    return alias


def _seed_surface() -> None:
    _write_surface(_SURFACE_TEXT)


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

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
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
        with self._runner.isolated_filesystem():
            self._seed()
            # THE FAULT IS ROUTED BY DESTINATION, NEVER BY A CALL COUNT. This
            # fixture used to fail the SECOND directory fsync of the run, on the
            # premise that the retained source was the first and the declaration
            # followed. A call count is a selector that silently RETARGETS
            # whenever the number of prior directory syncs changes: adding the
            # removal-side journal-absence boundary moved the injected fault
            # onto the retained-source write, so the run died before the journal
            # was ever created and the test reported the journal as "removed"
            # when nothing had removed it. `_failing_directory_barrier_after_replace`
            # routes on the destination of the most recent `os.replace`, so it
            # names the window this test is about -- the declaration's post-swap
            # barrier -- and cannot drift onto another write.
            #
            # The journal's OWN post-rename barrier is a different window with a
            # different honest prose, covered by
            # `TestContentUnownJournalFailureProseIsHonest`.
            with _failing_directory_barrier_after_replace("Doc.md.json") as probe:
                result = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertGreater(
                probe.attempts,
                0,
                "the declaration's post-swap barrier must be the window under test; "
                "a run that never reached it proves nothing about this branch",
            )

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
            _write_surface(_SURFACE_TEXT.replace("alpha body", "alpha body " + ("x" * 400)))
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


class TestContentUnownReadsTheSurfaceInsideTheLock(unittest.TestCase):
    """Step-4b round-6 findings 3, 4 and 6 — the critical section must own the READ.

    The declaration was already re-read inside `exclusive_declaration_lock`
    ("any value read before acquiring is stale by construction"), but the
    SURFACE was not: it was read once at the top of the handler and that
    snapshot was then used for span arithmetic, replay validation and the
    committed declaration. The lock excludes other `gz` processes; it excludes
    no editor at all, so an ordinary save in that window made the command
    witness a span the surface no longer had.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-05")
    def test_a_surface_edited_on_lock_entry_is_refused_not_committed_stale(self) -> None:
        """Would break if the surface snapshot were taken before the lock.

        Round-6 finding 3, `[high]`. An editor grows the target section between
        the handler's read and the lock. Measured on the unfixed tree:
        `command_exit=0` with a success line claiming the floor rose 26 -> 83,
        `journal_exists=False`, and a declaration the canonical loader then
        REJECTED because the summed span (484) exceeded the witnessed floor.

        The assertion is exit 0 with the floor of the GROWN surface, and that
        strictness is what makes this test witness THIS guard rather than its
        backstop. An earlier draft accepted "either it succeeds correctly or it
        refuses"; that draft SURVIVED reverting the read to outside the lock,
        because `_refuse_surface_changed_under_us` then refused and the
        permissive branch accepted the refusal. A test that accepts both
        outcomes of the fix it names witnesses neither -- the round-6 finding-5
        shape, reproduced in this OBPI's own new test and caught by mutating
        the guard, never by the suite going green.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            real_lock = exclusive_declaration_lock
            grown = _SURFACE_TEXT.replace(
                "alpha body line two\n",
                "alpha body line two\n" + "alpha body grown by an editor\n" * 12,
            )

            @contextlib.contextmanager
            def grow_surface_on_entry(path):
                # The edit lands AFTER the handler's read and BEFORE the body of
                # the critical section runs -- exactly the window an editor save
                # occupies. Nothing here touches `.gzkit/`.
                with real_lock(path) as handle:
                    _write_surface(grown)
                    yield handle

            with patch(
                "gzkit.commands.content.unown.exclusive_declaration_lock",
                grow_surface_on_entry,
            ):
                result = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(
                result.exit_code,
                0,
                "an edit landing BEFORE the read must be MEASURED, not refused: "
                f"the read is inside the lock. {result.output}",
            )
            spans = measure_section_spans(grown)
            expected = spans["beta-section"] + spans["alpha-section"]
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(
                declaration["unowned_byte_floor"],
                expected,
                "a successful raise must witness the span the surface actually has",
            )
            self.assertNotEqual(
                declaration["unowned_byte_floor"],
                _SEED_FLOOR + measure_section_spans(_SURFACE_TEXT)["alpha-section"],
                "witnessing the PRE-edit span is the defect this test exists for",
            )
            # The canonical loader is the arbiter: exit 0 must mean loadable.
            load_declaration(_DECLARATION_PATH, grown, Path("."))

    @covers("REQ-0.35.0-04-05")
    def test_a_non_utf8_surface_is_refused_in_governed_prose_not_a_traceback(self) -> None:
        """Would break if the surface read caught only OSError.

        Round-6 finding 6, `[low]`. `read_text` raises `UnicodeDecodeError` --
        a `ValueError`, NOT an `OSError` -- so ordinary encoding corruption
        escaped the three-part fail-closed prose and surfaced as
        `Unexpected error: 'utf-8' codec can't decode byte 0xff...`. The
        declaration was left unchanged, so this is prose quality, not
        corruption; the governed path must still explain itself.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            Path("Doc.md").write_bytes(b"# Doc\n\xff\xfe not utf-8\n")

            result = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertNotIn("Unexpected error", result.output)
            self.assertIn("Why forbidden:", result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(declaration["unowned_byte_floor"], _SEED_FLOOR)

    @covers("REQ-0.35.0-04-05")
    def test_a_surface_edited_after_measurement_is_refused_before_either_store(self) -> None:
        """Would break if `_refuse_surface_changed_under_us` were deleted.

        Reading the surface inside the lock closes the lock-ENTRY window; it
        does not close the window between the measurement and the journal
        write, because the lock excludes `gz` processes and an editor is not
        one. This injects the save at `_mint_event_id` -- after the span has
        been measured and the new floor computed, before anything is written --
        which is the residue the read-inside-the-lock fix leaves behind.

        The sibling test above CANNOT witness this guard: its edit lands before
        the read, so the command measures the grown surface and is correct with
        no re-check at all. Two windows, two guards, two tests.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            grown = _SURFACE_TEXT.replace(
                "alpha body line two\n",
                "alpha body line two\n" + "alpha body grown by an editor\n" * 12,
            )
            real_mint = unown_module._mint_event_id

            def grow_surface_then_mint(record, parent_event_id):
                _write_surface(grown)
                return real_mint(record, parent_event_id)

            with patch.object(unown_module, "_mint_event_id", grow_surface_then_mint):
                result = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("changed while un-owning", result.output)
            self.assertIn("Why forbidden:", result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(
                declaration["unowned_byte_floor"],
                _SEED_FLOOR,
                "neither store may be touched when the surface moved under us",
            )
            self.assertEqual(
                [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"],
                [],
            )
            self.assertFalse(
                (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                "the refusal precedes the journal write, so no residue is left",
            )


class TestContentUnownJournalFailureProseIsHonest(unittest.TestCase):
    """Step-4b round-6 finding 4 — the journal branch inherited a false premise."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_a_post_rename_journal_fsync_failure_does_not_claim_nothing_written(self) -> None:
        """Would break if the journal handler kept its unconditional "Nothing written."

        Round-6 finding 4, `[medium]`. `write_declaration_atomically` syncs the
        parent DIRECTORY after `os.replace`, so an `OSError` from that sync
        means the journal file may ALREADY be on disk. The declaration branch
        learned this at round 3 and tells the truth; the journal branch kept
        asserting "Nothing written." The stores really are unchanged here --
        the lie is about the JOURNAL, and a false account of the failure
        boundary is what sent round-3's operator down the wrong recovery.

        The fault is targeted at the directory sync that follows the JOURNAL's
        own rename, identified by the destination of the preceding
        `os.replace`. It used to fail the FIRST directory sync of the run, which
        was the journal's -- until the transaction gained an earlier write, the
        retained source snapshot (§ Recovery Protocol state E), and "first"
        silently became a different file. A positional injector names the wrong
        subject the moment the sequence around it changes.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with _failing_directory_barrier_after_replace("Doc.md.json.journal"):
                result = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertNotIn(
                "Nothing written",
                result.output,
                "the journal rename may already have landed when its directory "
                "sync failed; the command must not assert a premise it cannot know",
            )
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(
                declaration["unowned_byte_floor"],
                _SEED_FLOOR,
                "the declaration and ledger genuinely ARE unchanged on this branch",
            )
            self.assertEqual(
                [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"],
                [],
            )


class TestContentUnownBindsTheSurfaceToTheTransaction(unittest.TestCase):
    """Step-4b round 7 — a scalar re-read is not a transaction binding.

    Round 6 fixed the lock-entry window by reading the surface inside the lock,
    and added `_refuse_surface_changed_under_us` before the journal write. Round
    7's *Weakest point* named that fix as the defect: "the mutable surface is
    not transactionally version-bound to the declaration, journal, and witness;
    both new failures arise because a scalar re-read is being used as a
    substitute for that missing binding." Same root as round 6, third surfacing
    -- so the operator ruled the design rather than another guard being added.

    The binding: the surface digest is journalled with the transition, and it is
    re-verified after the declaration and the witness are durable but BEFORE the
    journal is cleared. A disagreement retains the journal and refuses to report
    clean success.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    _GROWN = _SURFACE_TEXT.replace(
        "alpha body line two\n",
        "alpha body line two\n" + "alpha body grown by an editor\n" * 12,
    )

    @covers("REQ-0.35.0-04-05")
    def test_an_edit_between_the_check_and_the_commit_is_not_reported_as_success(self) -> None:
        """Would break if the post-durability digest re-verification were deleted.

        Round-7 finding 1, `[high]`, at unown.py:802-803 as it then stood: the
        surface was checked and then committed SEPARATELY, so an ordinary editor
        write landing between the two produced `exit=0` with success prose
        claiming `26 to 83 (+57 B)`, `stored_floor=83`, `live_unowned_span=653`,
        `journal_exists=False`, and then `post_success_load=REJECTED`. The
        command reported success AND destroyed the recovery state AND left a
        declaration its own canonical loader rejects.

        The edit is injected at `_commit_transition` itself -- after every
        pre-flight check has passed, which is precisely the window a check-then-
        act guard cannot cover.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            real_commit = unown_module._commit_transition

            def edit_then_commit(*args, **kwargs):
                _write_surface(self._GROWN)
                return real_commit(*args, **kwargs)

            with patch.object(unown_module, "_commit_transition", edit_then_commit):
                result = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                result.exit_code,
                0,
                "the command must not report clean success when the surface moved "
                f"inside the transaction. {result.output}",
            )
            self.assertIn("Why forbidden:", result.output)
            self.assertTrue(
                (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                "recovery state must be RETAINED when the surface moved: the "
                "journal is the only record able to complete or reconcile it",
            )

    @covers("REQ-0.35.0-04-05")
    def test_an_unchanged_surface_still_completes_cleanly(self) -> None:
        """The false-positive arm: binding must not refuse a legitimate raise.

        Round 7 corroborated that "unchanged input succeeded"; this pins it, so a
        future tightening of the binding cannot silently convert every ordinary
        un-owning into a refusal. A guard with no false-positive test is a guard
        that can be made infinitely strict without any test objecting.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            result = _unown(self._runner, attestor="g0", reason="legitimate raise")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            spans = measure_section_spans(_SURFACE_TEXT)
            self.assertEqual(
                declaration["unowned_byte_floor"],
                spans["beta-section"] + spans["alpha-section"],
            )
            load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path("."))
            self.assertFalse((_DECLARATION_PATH.parent / "Doc.md.json.journal").exists())

    @covers("REQ-0.35.0-04-02")
    def test_replay_refuses_when_a_section_was_renamed_under_the_landed_map(self) -> None:
        """Would break if the already-landed branch checked only the scalar span.

        Round-7 finding 2, `[high]`. After an injected ledger-append failure left
        the declaration and the journal, renaming a section through an ordinary
        surface edit and retrying gave `retry_exit=0`, "Completed the interrupted
        un-owning", one witness and `journal_exists=False` -- then the canonical
        reload REJECTED the undeclared `renamed-section`.

        The cause is that `live_unowned_span` sums only ids PRESENT in the landed
        map, so a renamed section contributes nothing and the span check passes
        while the declaration no longer covers the surface. A scalar cannot
        witness coverage, for the same reason it could not witness the map at
        round 4 or the direction at round 5.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            real_append = unown_module._append_event_once

            def fail_append(root, target, record):
                raise OSError(5, "injected ledger append failure")

            with patch.object(unown_module, "_append_event_once", fail_append):
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 2, msg=first.output)
            self.assertTrue((_DECLARATION_PATH.parent / "Doc.md.json.journal").exists())

            # A journal carrying NO `surface_digest` -- the shape written by any
            # run predating the round-8 binding. `_refuse_clean_success_on_a_moved_
            # surface` returns early on those, so the coverage check below is the
            # ONLY thing standing between a legacy journal and a completion the
            # loader rejects. Without this, the digest guard masks the coverage
            # guard and this test survives deleting the check it names (measured:
            # `section_id_coverage SURVIVED` after round 8 landed).
            journal = _DECLARATION_PATH.parent / "Doc.md.json.journal"
            legacy = json.loads(journal.read_text(encoding="utf-8"))
            legacy.pop("surface_digest", None)
            journal.write_text(json.dumps(legacy, indent=2) + "\n", encoding="utf-8")

            # An ordinary editor rename, not an attack: no .gzkit/ access.
            _write_surface(_SURFACE_TEXT.replace("## Beta Section", "## Renamed Section"))

            self.assertIs(unown_module._append_event_once, real_append)
            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                retry.exit_code,
                0,
                f"recovery must not complete into a state the loader rejects. {retry.output}",
            )
            self.assertTrue(
                (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                "the journal must be RETAINED so the transition stays completable "
                "once the rename is reconciled",
            )


class TestContentUnownRound8(unittest.TestCase):
    """Step-4b round 8 — the binding must cover EVERY finalization path.

    Round 7's design ruling ("bind the surface into the transaction") was
    implemented on the fresh-commit path only. Round 8 found that replay clears
    the journal without ever calling the guard (`post_digest_guard_calls=0`),
    that the digest hashes NEWLINE-NORMALIZED text rather than the bytes whose
    span is governed, and that recovering a different pending section leaves a
    refusal claiming "nothing written" after a witness has landed.
    """

    _GROWN = _SURFACE_TEXT.replace(
        "alpha body line two\n",
        "alpha body line two\n" + "grown by an editor\n" * 12,
    )

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _interrupt_at_append(self):
        """Seed, then fail the ledger append: declaration landed, journal kept."""
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

        def fail(root, target, record):
            raise OSError(5, "injected ledger append failure")

        with patch.object(unown_module, "_append_event_once", fail):
            first = _unown(self._runner, attestor="g0", reason="probe")
        self.assertEqual(first.exit_code, 2, msg=first.output)
        self.assertTrue((_DECLARATION_PATH.parent / "Doc.md.json.journal").exists())

    @covers("REQ-0.35.0-04-05")
    def test_replay_finalization_also_verifies_the_journalled_surface(self) -> None:
        """Would break if replay cleared the journal without the digest guard.

        Round-8 finding 1, `[high]`. `_replay_pending_transition` validated the
        captured surface, appended, and unlinked without ever calling
        `_refuse_clean_success_on_a_moved_surface` -- observed `exit=0
        surface_after=edited-during-ledger-append event_appended=True
        journal_exists=False post_digest_guard_calls=0` with clean-success
        prose. The binding covered one of two finalization paths.

        The edit lands DURING the replay append, after every coherence check has
        already passed against the unmoved surface. That is why a coherence
        check cannot substitute for the digest guard: the checks were correct
        when they ran.
        """
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()
            real_append = unown_module._append_event_once

            def edit_then_append(root, target, record):
                _write_surface(self._GROWN)
                return real_append(root, target, record)

            with patch.object(unown_module, "_append_event_once", edit_then_append):
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                retry.exit_code,
                0,
                "replay must not report clean recovery after the journalled "
                f"surface changed. {retry.output}",
            )
            self.assertTrue(
                (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                "recovery state must survive so the transition stays reconcilable",
            )

    @covers("REQ-0.35.0-04-05")
    def test_replay_of_an_unmoved_surface_still_completes(self) -> None:
        """False-positive arm: the replay guard must not break ordinary recovery."""
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 0, msg=retry.output)
            self.assertFalse((_DECLARATION_PATH.parent / "Doc.md.json.journal").exists())
            self.assertEqual(
                len([e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]),
                1,
                "recovery completes the transition exactly once",
            )
            load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path("."))

    @covers("REQ-0.35.0-04-05")
    def test_the_digest_binds_raw_bytes_not_newline_normalized_text(self) -> None:
        """Would break if the digest were computed from `read_text` output.

        Round-8 finding 2, `[high]`. `Path.read_text` applies universal-newline
        translation, so CRLF collapses to LF before hashing: observed
        `raw_lengths=25,29 decoded_equal=True digests_equal=True
        measured_totals=25,25`. A line-ending conversion changes the physical
        byte spans the floor governs WITHOUT firing the binding, so the recorded
        floor silently undercounts the file. Not exotic on a project whose
        `.claude/rules/cross-platform.md` treats Windows as co-equal -- an
        editor there produces it by saving.

        Asserted on the DIGEST itself, so it pins the binding contract rather
        than one caller's use of it.
        """
        with self._runner.isolated_filesystem():
            lf = "# Doc Title\npreamble\n## Alpha Section\nbody\n"
            crlf = lf.replace("\n", "\r\n")
            Path("lf.md").write_bytes(lf.encode("utf-8"))
            Path("crlf.md").write_bytes(crlf.encode("utf-8"))
            self.assertNotEqual(
                Path("lf.md").stat().st_size,
                Path("crlf.md").stat().st_size,
                "fixture sanity: the two files differ in physical bytes",
            )

            self.assertNotEqual(
                unown_module._surface_digest(Path("lf.md").read_bytes()),
                unown_module._surface_digest(Path("crlf.md").read_bytes()),
                "the digest governs the BYTES whose span is measured; a "
                "line-ending conversion changes those bytes and must change it",
            )

    @covers("REQ-0.35.0-04-05")
    def test_the_read_path_feeds_raw_bytes_to_the_digest(self) -> None:
        """Would break if `_read_surface_or_exit` hashed `read_text` output.

        The sibling test above pins `_surface_digest`'s own contract by calling
        it with bytes, and that is NOT enough: it SURVIVED a mutation that made
        the read path hash newline-normalized text, because it never exercises
        the read path at all. A helper can be perfectly correct while nothing
        routes real input through it.

        This test therefore asserts on `_read_surface_or_exit` — the seam where
        raw bytes must actually reach the digest — and on the decoded text
        retaining its carriage returns, since the spans measured from that text
        must agree with the bytes hashed beside it.
        """
        with self._runner.isolated_filesystem():
            lf = "# Doc Title\npreamble\n## Alpha Section\nbody\n"
            crlf = lf.replace("\n", "\r\n")
            Path("lf.md").write_bytes(lf.encode("utf-8"))
            Path("crlf.md").write_bytes(crlf.encode("utf-8"))

            lf_text, lf_digest, lf_raw = unown_module._read_surface_or_exit(Path("lf.md"), "lf.md")
            crlf_text, crlf_digest, crlf_raw = unown_module._read_surface_or_exit(
                Path("crlf.md"), "crlf.md"
            )
            self.assertEqual(
                (lf_raw, crlf_raw),
                (Path("lf.md").read_bytes(), Path("crlf.md").read_bytes()),
                "the raw bytes handed back are what state E retains as recovery "
                "material; a re-encoded copy would not be the measured bytes",
            )

            self.assertNotEqual(
                lf_digest,
                crlf_digest,
                "the read path must hash the surface's RAW bytes; `read_text` "
                "normalizes CRLF to LF and would make these agree",
            )
            self.assertIn("\r", crlf_text, "the decoded text must not be newline-translated")
            self.assertEqual(
                len(crlf_text.encode("utf-8")),
                Path("crlf.md").stat().st_size,
                "the text measured must round-trip to the bytes hashed, or the "
                "floor governs a different quantity than the digest protects",
            )

    @covers("REQ-0.35.0-04-02")
    def test_recovering_a_different_section_never_claims_nothing_written(self) -> None:
        """Would break if recovery fell through into the refusal paths.

        Round-8 finding 3, `[medium]`. The handler returned after recovery only
        when the recovered section equalled the requested one; otherwise it
        completed the pending transition, appended its witness, deleted its
        journal, and continued into the unknown-section refusal, whose prose
        says "nothing written". Observed `exit=1 event_appended=True
        journal_exists=False`. Operators and automation received an account
        contradicting the durable state change.
        """
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()

            second = _unown(self._runner, section="does-not-exist", attestor="g0", reason="probe")

            # FIXTURE SANITY FIRST, then the assertion unconditionally. This was
            # `if landed:` wrapping its only assertion -- always true today, so
            # the conditional protected nothing, but any regression that stopped
            # the replay appending its witness would have made this test pass
            # while asserting NOTHING. That is the vacuity shape this module
            # names nine times, wearing a guard clause.
            landed = [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]
            self.assertEqual(
                len(landed),
                1,
                "fixture sanity: this invocation must have completed the pending "
                f"transition, or there is no durable change to contradict. {second.output}",
            )
            self.assertNotIn(
                "nothing written",
                second.output.lower(),
                "a witness landed during this invocation, so no refusal in it "
                f"may claim the stores were untouched. {second.output}",
            )


#: Text-mode open modes. A mode containing "b" is binary and translates
#: nothing; a read-only mode writes nothing. Only these can newline-translate
#: on the way out.
_TEXT_WRITE_MODE_CHARS = frozenset("wax")

#: Substrings marking a write target as JSON the loader parses rather than
#: bytes a floor is measured against -- `_DECLARATION_PATH`,
#: `self._JOURNAL_PATH`, `journal`, `declaration_path`.
_NON_SURFACE_MARKERS = ("declaration", "journal")


def _string_literals(node: ast.AST) -> list[str]:
    """Every string constant appearing anywhere inside *node*."""
    return [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    ]


def _writes_a_measured_surface(target: ast.expr) -> bool:
    """Decide whether *target* names a surface whose bytes a floor measures.

    Keyed on WHAT IS WRITTEN, never on the expression a path was derived from.
    That distinction is the defect this predicate was rebuilt around: matching
    the whole unparsed expression let `_DECLARATION_PATH.with_name("crlf.md")`
    inherit the `declaration` exemption while writing a SURFACE, and that
    `with_name` shape is in live use in this module.

    The order is load-bearing. A `.md` filename wins over every exemption,
    because the extension is what the artifact IS; the derivation is only how
    it was reached. Suffixes are matched, never substrings, so
    `"Other.md.json"` reads as the JSON declaration it is.
    """
    literals = _string_literals(target)
    if any(literal.endswith(".md") for literal in literals):
        return True
    if any(literal.endswith(".json") for literal in literals):
        return False
    unparsed = ast.unparse(target).lower()
    if any(marker in unparsed for marker in _NON_SURFACE_MARKERS):
        return False
    if "surface" in unparsed:
        return True
    # A bare `Path(...)` construction carrying no JSON or declaration signal is
    # a surface by default: the canonical seeding writer is `Path(name)`, and
    # an allowlist of known spellings is exactly what stopped covering it.
    return isinstance(target, ast.Call) and ast.unparse(target).startswith("Path(")


def _is_text_mode_open(node: ast.Call) -> bool:
    """Decide whether *node* is an `open`/`Path.open` in a text WRITE mode.

    `open(p, "w").write(...)` and `p.open("w").write(...)` apply the identical
    `newline=None` translation `write_text` does, and neither is an attribute
    call named `write_text` -- so a guard keyed on that one spelling is blind
    to ordinary Python no author would recognise as opting out of it.

    The OPEN is the checked site, not the `.write` that follows: the mode is
    where translation is configured, and checking it needs no dataflow to
    follow the handle. An explicit `newline=""` disables translation and is the
    legitimate escape `.claude/rules/cross-platform.md` already names.
    """
    func = node.func
    is_open = (isinstance(func, ast.Name) and func.id == "open") or (
        isinstance(func, ast.Attribute) and func.attr == "open"
    )
    if not is_open:
        return False
    if any(kw.arg == "newline" for kw in node.keywords):
        return False
    modes = [kw.value for kw in node.keywords if kw.arg == "mode"]
    if isinstance(func, ast.Name):
        modes += node.args[1:2]
    else:
        modes += node.args[:1]
    for mode in modes:
        if not isinstance(mode, ast.Constant) or not isinstance(mode.value, str):
            continue
        if "b" not in mode.value and _TEXT_WRITE_MODE_CHARS & set(mode.value):
            return True
    return False


def _text_mode_surface_writes(tree: ast.AST, label: str) -> list[str]:
    """Report every text-mode write to a byte-measured surface in *tree*.

    A module-level function rather than a method so each rule can be exercised
    against synthetic snippets. A scanner whose only input is the repository it
    scans is green whenever it is blind, which is precisely how the previous
    allowlist matcher passed while covering none of the writes it named.

    Takes an ALREADY-PARSED tree rather than source text, so the `ast.parse`
    stays visible in the caller. That is not cosmetic: it is the signal
    `gz validate --tautological-test-audit` reads to tell a static-analysis
    fence from a test echoing back a file it wrote itself
    (`_reads_project_source`). An earlier extraction moved the parse in here and
    the caller was flagged as a tautology the same day.
    """
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "write_text":
            target, shape = func.value, "write_text"
        elif _is_text_mode_open(node):
            target = node.args[0] if isinstance(func, ast.Name) else func.value
            shape = "open(...)"
        else:
            continue
        if _writes_a_measured_surface(target):
            offenders.append(f"{label}:{node.lineno}  {ast.unparse(target)} via {shape}")
    return offenders


class TestSurfaceFixturesWriteBytes(unittest.TestCase):
    """No fixture may seed the byte-measured surface through text mode.

    The ownership floor is a count of PHYSICAL BYTES. `Path.write_text` opens
    with `newline=None` and translates every `\n` to `os.linesep`, so a fixture
    using it produces a file one byte per line longer on Windows than the
    in-memory string every floor in these tests is derived from. 23 tests here
    failed exactly that way the first time Windows could run this module (GHI
    #958) -- and they had been wrong on Windows for as long as they had
    existed, silent only because GHI #955's import error stopped the module
    loading at all.

    This is asserted STRUCTURALLY rather than behaviourally on purpose: the
    defect is invisible on POSIX, where `os.linesep` is already `\n`, so no
    assertion that runs here can observe it. A test that cannot fail on the
    machine running it is worth nothing; a test that reads the source can.
    """

    #: Roots searched for fixture modules that seed a byte-measured surface.
    _FIXTURE_ROOTS = (
        Path(__file__).parent.parent,
        Path(__file__).parent.parent.parent / "features",
    )

    #: The function whose per-section byte spans an ownership floor is the sum
    #: of. A module that seeds a surface those spans are measured against has
    #: to name it, so it is the derived membership signal for the roster.
    _SPAN_MEASURE = "measure_section_spans"

    def _surface_seeding_modules(self) -> list[Path]:
        """Derive the roster; never enumerate it.

        A hand-maintained tuple of module paths is the same rot as a
        hand-maintained allowlist of write targets, one level up: a third
        fixture module seeding a surface is silently unscanned, and nothing
        tells anyone. Membership is instead the module naming
        `measure_section_spans`, so enrolment happens by writing the fixture.
        """
        modules: list[Path] = []
        for root in self._FIXTURE_ROOTS:
            for candidate in sorted(root.rglob("*.py")):
                if self._SPAN_MEASURE in candidate.read_text(encoding="utf-8"):
                    modules.append(candidate)
        return modules

    def test_the_roster_is_derived_and_covers_the_known_seeding_modules(self) -> None:
        """Would break if the roster stopped finding a real fixture module."""
        names = {module.name for module in self._surface_seeding_modules()}
        self.assertIn("test_content_unown.py", names)
        self.assertIn("content_unown_steps.py", names)

    def test_no_surface_fixture_writes_through_text_mode(self) -> None:
        """Every surface write goes through `write_bytes`, never `write_text`."""
        offenders: list[str] = []
        for module in self._surface_seeding_modules():
            tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
            offenders += _text_mode_surface_writes(tree, module.name)
        self.assertEqual(
            offenders,
            [],
            "A byte-measured surface is written through text-mode newline "
            "translation:\n  " + "\n  ".join(offenders) + "\n\n"
            "Use `write_bytes(text.encode('utf-8'))`. The production reader "
            "decodes raw bytes deliberately (`_surface_digest`, Step-4b round-8 "
            "finding 2) because the floor counts physical bytes; a fixture must "
            "produce the bytes that reader measures.",
        )


class TestSurfaceWriteScanner(unittest.TestCase):
    """The scanner's own rules, exercised against synthetic source.

    Every arm below is a shape that WAS invisible. The allowlist matcher this
    replaced reported `Ran 1 test ... OK` while every surface write in its own
    module went through text mode -- a scanner tested only against the tree it
    scans is green exactly when it is blind, so its rules are pinned here
    against source it cannot silently stop matching.
    """

    def _offenders(self, source: str) -> list[str]:
        return _text_mode_surface_writes(ast.parse(source, filename="snippet.py"), "snippet.py")

    def test_a_md_target_is_flagged_however_it_was_derived(self) -> None:
        """Would break if the exemption were read off the derived expression.

        The live hole: `_DECLARATION_PATH.with_name(...)` carries the
        `declaration` marker while naming a surface.
        """
        self.assertTrue(self._offenders('Path("lf.md").write_text(t)'))
        self.assertTrue(
            self._offenders('_DECLARATION_PATH.with_name("crlf.md").write_text(t)'),
            "a `.md` filename must win over the derivation it was reached by",
        )

    def test_a_json_target_is_exempt_even_when_the_name_contains_md(self) -> None:
        """`Other.md.json` is the declaration it is; suffixes, not substrings."""
        self.assertEqual(
            self._offenders('_DECLARATION_PATH.with_name("Other.md.json").write_text(t)'), []
        )
        self.assertEqual(self._offenders("_DECLARATION_PATH.write_text(t)"), [])
        self.assertEqual(self._offenders("journal.write_text(t)"), [])
        self.assertEqual(self._offenders("self._JOURNAL_PATH.write_text(t)"), [])

    def test_a_surface_named_or_path_constructed_target_is_flagged(self) -> None:
        """The two shapes the previous allowlist enumerated, now derived.

        `Path(name)` is the canonical seeding writer -- the exact site the
        allowlist stopped covering when it was extracted into a helper.
        """
        self.assertTrue(self._offenders("surface_path.write_text(t)"))
        self.assertTrue(self._offenders("Path(surface).write_text(t)"))
        self.assertTrue(self._offenders("Path(name).write_text(t)"))

    def test_open_in_a_text_write_mode_is_flagged_in_both_spellings(self) -> None:
        """`open(...)`/`.open(...)` translate identically and were invisible."""
        self.assertTrue(self._offenders('open("x.md", "w").write(t)'))
        self.assertTrue(self._offenders('Path(name).open("w").write(t)'))
        self.assertTrue(self._offenders('open("x.md", mode="a").write(t)'))

    def test_binary_newline_safe_and_read_opens_are_not_flagged(self) -> None:
        """The false-positive arm: none of these can newline-translate."""
        self.assertEqual(self._offenders('open("x.md", "wb").write(b)'), [])
        self.assertEqual(self._offenders('open("x.md", "w", newline="").write(t)'), [])
        self.assertEqual(self._offenders('open("x.md").read()'), [])
        self.assertEqual(self._offenders('Path("x.md").read_text()'), [])
        self.assertEqual(self._offenders('Path("x.md").write_bytes(b)'), [])


class TestContentUnownRound9(unittest.TestCase):
    """Step-4b round 9 — ONE surface identity and ONE surface read per transaction.

    Round 9 refuted this OBPI on one high and one medium finding that share a
    root: surface identity and surface bytes were re-derived at each call site
    instead of resolved once and carried. The high finding recorded the
    CALLER'S spelling in the ledger witness while the declaration kept its own,
    so a reload the command's own loader performs then rejected the declaration
    the command had just reported success for -- with the journal, the only
    recovery state, already deleted. The medium finding re-read the surface
    through `Path.read_text` in the pre-commit recheck while the transaction
    had measured it through `bytes.decode`, so for any CRLF surface the two
    could never agree and an unchanged file always looked changed.

    Round 8 fixed the initial read and the final digest; round 9 found the
    pre-commit recheck. Patching site three invites site four, so the identity
    and the bytes are each resolved ONCE at transaction entry and carried
    through journal, declaration, witness and prose.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _invoke(self, surface: str, *, section: str = "alpha-section"):
        return self._runner.invoke(
            main,
            [
                "content",
                "unown",
                surface,
                "--section",
                section,
                "--attestor",
                "g0",
                "--reason",
                "probe",
            ],
        )

    @covers("REQ-0.35.0-04-05")
    def test_a_second_spelling_of_the_surface_witnesses_the_declared_identity(self) -> None:
        """Would break if the witness carried the caller's spelling.

        Round-9 finding 1, `[high]`. On a case-insensitive filesystem
        `AGENTS.md` and `agents.md` are the same file; the command copied the
        declaration's surface unchanged but recorded the CLI argument in the
        witness. Observed `surface_samefile True declaration_samefile True
        PARSED_CLI exit 0 appended 1 journal False reload REJECTED`, the reload
        reporting "declares surface 'AGENTS.md' ... but that event witnesses
        surface 'agents.md'". Only the CLI argument changed and nothing was
        forged: the command destroyed its recovery state while reporting
        success for a declaration its own loader then refused.

        `OwnershipDeclaration.surface` is the authoritative identity, so the
        assertion is that the witness carries THAT string -- not merely that
        the command exited 0, which it already did while wrong.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            alias = _same_file_alias("Doc.md")
            if alias is None:
                self.skipTest("no case-insensitive filesystem and no symlink support")

            result = self._invoke(alias)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            witnessed = [
                event["surface"]
                for event in _ledger_events()
                if event["event"] == "section_ownership_unowned"
            ]
            self.assertEqual(
                witnessed,
                ["Doc.md"],
                "the witness must carry the declaration's declared surface "
                f"identity, never the caller's spelling {alias!r}",
            )
            # The canonical loader is the arbiter: exit 0 must mean loadable.
            load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path("."))

    @covers("REQ-0.35.0-04-02")
    def test_a_request_naming_a_different_file_than_the_declaration_is_refused(self) -> None:
        """Would break if identity canonicalization accepted any spelling.

        The other arm of the same guard. `Other.md` is a real, separate file
        whose ownership declaration declares the identity `Doc.md` -- the two
        spellings are NOT one file, so there is nothing to canonicalize to and
        proceeding would witness a floor for one surface against the bytes of
        another. Refusal has to land BEFORE the journal write, because the
        journal is the recovery record: a refusal after it is a residue an
        operator must reconcile by hand.

        Asserted on the durable stores rather than on the exit code alone --
        an exit-code-only assertion would survive a refusal that had already
        journalled, which is the state round 8 finding 3 named.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            _write_named_surface("Other.md", _SURFACE_TEXT)
            foreign_declaration = _DECLARATION_PATH.with_name("Other.md.json")
            foreign_declaration.write_bytes(_DECLARATION_PATH.read_bytes())
            before_declaration = _DECLARATION_PATH.read_bytes()
            before_foreign = foreign_declaration.read_bytes()
            before_events = len(_ledger_events())

            result = self._invoke("Other.md")

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            # Pinned to the check under test. "Why forbidden:" matches ANY
            # governed refusal, and the durable-store assertions below are
            # satisfied by any pre-write refusal -- so an earlier check
            # refusing first would leave this test green with its own guard
            # gone. Four fixtures in this module were false guards that way.
            self.assertIn(
                "does not resolve to the identity its ownership declaration declares",
                result.output,
                f"refused, but NOT by the check under test. {result.output}",
            )
            self.assertIn("are different files", result.output)
            self.assertEqual(
                _DECLARATION_PATH.read_bytes(),
                before_declaration,
                "the declared surface's own declaration must be byte-unchanged",
            )
            self.assertEqual(
                foreign_declaration.read_bytes(),
                before_foreign,
                "the requested surface's declaration must be byte-unchanged",
            )
            self.assertEqual(
                len(_ledger_events()),
                before_events,
                "no witness may be appended for a surface identity that does not resolve",
            )
            self.assertEqual(
                sorted(
                    path.name
                    for path in _DECLARATION_PATH.parent.iterdir()
                    if path.name.endswith(".journal")
                ),
                [],
                "the refusal must precede the journal write, so no residue is left",
            )

    #: The same surface, saved by an editor that writes CRLF line endings.
    _CRLF_SURFACE_TEXT = _SURFACE_TEXT.replace("\n", "\r\n")

    @covers("REQ-0.35.0-04-05")
    def test_an_unchanged_crlf_surface_completes(self) -> None:
        """Would break if the pre-commit recheck re-read through `read_text`.

        Round-9 finding 2, `[medium]`. `_read_surface_or_exit` decodes
        `read_bytes()` with NO newline translation, so the measured text keeps
        its carriage returns; `_refuse_surface_changed_under_us` re-read the
        same file through `read_text`, which applies universal-newline
        translation. For any CRLF surface those two can never be equal, so an
        UNCHANGED valid surface always looked changed. Observed `CRLF raw_bytes
        129 measured_bytes 129 roundtrips True initial_load ACCEPTED` then
        `exit 1 writes [] appended 0 journal False`, against an LF control that
        succeeded 26 -> 83.

        `.claude/rules/cross-platform.md` makes Windows co-equal, and an editor
        there produces CRLF by saving -- so this is the ordinary path on a
        supported platform, not an exotic input. The recheck must compare the
        same quantity the transaction governs: the raw bytes.
        """
        with self._runner.isolated_filesystem():
            _write_surface(self._CRLF_SURFACE_TEXT)
            spans = measure_section_spans(self._CRLF_SURFACE_TEXT)
            _seed_declaration(alpha="corpus-owned", floor=spans["beta-section"])

            result = self._invoke("Doc.md")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            self.assertEqual(declaration["sections"]["alpha-section"], "unowned")
            self.assertEqual(
                declaration["unowned_byte_floor"],
                spans["beta-section"] + spans["alpha-section"],
                "the floor must rise by the section's PHYSICAL byte span, "
                "carriage returns included",
            )
            self.assertFalse(
                (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                "a clean completion clears its journal",
            )
            load_declaration(_DECLARATION_PATH, self._CRLF_SURFACE_TEXT, Path("."))

    @covers("REQ-0.35.0-04-05")
    def test_a_line_ending_conversion_between_measurement_and_commit_is_refused(self) -> None:
        """Would break if the recheck compared newline-translated TEXT.

        The strengthening arm of round-9 finding 2. A line-ending conversion
        leaves the visible text identical while changing every physical byte
        span the floor counts, so a text comparison cannot see it -- not
        because it was written carelessly, but structurally: `read_text`
        normalizes exactly the bytes that changed.

        Both directions are asserted in ONE test on purpose. `CRLF -> LF` is
        refused on the unfixed tree too, but for the wrong reason -- that tree
        refuses every CRLF surface, converted or not (see the sibling control
        test above) -- so on its own it would witness nothing. `LF -> CRLF` is
        the discriminating direction: on the unfixed tree the recheck PASSES it
        and the transition lands, leaving the post-witness binding to refuse a
        transaction that is already durable.

        The assertion is therefore exit 1 with both stores untouched, never
        merely "non-zero": exit 2 means the journal, the declaration and the
        witness all landed and an operator must now reconcile by hand. The
        whole point of a pre-commit recheck is that nothing was written.
        """
        conversions = (
            ("LF -> CRLF", _SURFACE_TEXT, self._CRLF_SURFACE_TEXT),
            ("CRLF -> LF", self._CRLF_SURFACE_TEXT, _SURFACE_TEXT),
        )
        for label, measured, converted in conversions:
            with self.subTest(conversion=label), self._runner.isolated_filesystem():
                spans = measure_section_spans(measured)
                _write_surface(measured)
                _seed_declaration(alpha="corpus-owned", floor=spans["beta-section"])
                real_mint = unown_module._mint_event_id

                def convert_then_mint(
                    record, parent_event_id, _converted=converted, _mint=real_mint
                ):
                    # Lands AFTER the span is measured and the new floor
                    # computed, BEFORE anything is written -- the window the
                    # pre-commit recheck exists to close.
                    _write_surface(_converted)
                    return _mint(record, parent_event_id)

                with patch.object(unown_module, "_mint_event_id", convert_then_mint):
                    result = self._invoke("Doc.md")

                self.assertEqual(
                    result.exit_code,
                    1,
                    "the recheck must refuse BEFORE either store is touched; "
                    f"exit 2 means the transition already landed. {result.output}",
                )
                self.assertIn("changed while un-owning", result.output)
                declaration = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
                self.assertEqual(declaration["sections"]["alpha-section"], "corpus-owned")
                self.assertEqual(declaration["unowned_byte_floor"], spans["beta-section"])
                self.assertEqual(
                    [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"],
                    [],
                )
                self.assertFalse(
                    (_DECLARATION_PATH.parent / "Doc.md.json.journal").exists(),
                    "the refusal precedes the journal write, so no residue is left",
                )

    @covers("REQ-0.35.0-04-02")
    def test_a_journal_naming_a_second_spelling_of_the_surface_is_refused(self) -> None:
        """Would break if replay trusted the journal's own `surface` field.

        The replay arm of round-9 finding 1. Resolving the identity at
        transaction entry stops the CALLER's spelling reaching durable state;
        it does not stop the JOURNAL's, because `record["surface"]` is what
        `_checked_landed_snapshot` and `_append_event_once` read. On a
        case-insensitive
        filesystem, `.gzkit/ownership/doc.md.json` and `Doc.md.json` are one
        file, so a journal naming `doc.md` passes every existing check --
        prior floor, parent pointer, measured span, eligibility and the derived
        successor -- and lands a witness the declaration's own loader then
        rejects, exactly as the CLI-argument path did.

        Every OTHER field is genuinely self-consistent: the event id re-mints
        from this record's own content, the parent matches the live chain
        pointer, and `declaration_json` is the successor a correct replay would
        derive. Only an identity check can catch it, so the assertion pins the
        identity defect rather than "some refusal happened" -- four fixtures in
        this module were false guards for exactly that reason.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]
            record = {
                "surface": "doc.md",
                "section": "alpha-section",
                "prior_unowned_byte_floor": _SEED_FLOOR,
                "new_unowned_byte_floor": _SEED_FLOOR + span,
                "attestor": "g0",
                "reason": "probe",
                "ts": "2026-09-04T00:00:00+00:00",
                "parent_event_id": on_disk["floor_event_id"],
                "declaration_json": "{}",
                "event_id": "placeholder",
            }
            record["event_id"] = _mint_event_id(record, record["parent_event_id"])
            predecessor = OwnershipDeclaration(**on_disk)
            successor = predecessor.model_copy(
                update={
                    "sections": {**predecessor.sections, "alpha-section": "unowned"},
                    "unowned_byte_floor": record["new_unowned_byte_floor"],
                    "floor_event_id": record["event_id"],
                }
            )
            record["declaration_json"] = successor.model_dump_json(indent=2) + "\n"
            journal = _DECLARATION_PATH.parent / "Doc.md.json.journal"
            journal.write_text(json.dumps(record), encoding="utf-8")
            before_declaration = _DECLARATION_PATH.read_bytes()
            before_events = len(_ledger_events())

            result = self._invoke("Doc.md")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn(
                "is not this transaction's target",
                result.output,
                f"refused, but NOT by the check under test. {result.output}",
            )
            self.assertEqual(
                _DECLARATION_PATH.read_bytes(),
                before_declaration,
                "the identity check must precede the declaration write",
            )
            self.assertEqual(
                len(_ledger_events()),
                before_events,
                "no witness may carry a surface identity no declaration declares",
            )
            self.assertTrue(
                journal.exists(),
                "a refused journal is RETAINED -- it is the only recovery record",
            )

    @covers("REQ-0.35.0-04-02")
    def test_an_identity_swapped_between_resolution_and_the_lock_is_refused(self) -> None:
        """DEFENCE IN DEPTH — not evidence of an in-scope defect.

        Reproducing this requires WRITING `.gzkit/` mid-run -- a hand-edited
        declaration plus a minted `section_ownership_genesis` row so the
        swapped state loads at all. The brief's § Threat Model places an actor
        with `.gzkit/` write access OUTSIDE the boundary as an accepted,
        disclosed residual, so this fixture must never be cited as an in-scope
        blocker.

        It injects at a DIFFERENT seam from its fresh-path sibling -- lock
        acquisition rather than the first statement inside the lock -- and both
        are retained because they are two windows, not one. The expectation for
        both is deterministic refusal with no transaction write after the
        injected mismatch.

        The identity is resolved BEFORE `exclusive_declaration_lock`, and it
        has to be: the lock path itself derives from it. But this module's own
        rule is that "any value read before acquiring is stale by
        construction", and the resolved identity was the one pre-lock value
        never re-checked. `record["surface"]` carried the pre-lock string into
        the journal and the witness while `declaration.model_copy` carried
        `declaration.surface` from the IN-LOCK load, and nothing compared them.

        The failure shape is the round-9 high finding verbatim -- witness
        surface != declaration surface, exit 0, journal deleted, declaration
        rejected by its own loader -- reached through a different door.

        The swapped-in declaration is COHERENT, not merely edited: a real
        `section_ownership_genesis` witnessing the second spelling at the same
        floor is emitted first, so `load_declaration` accepts it. Without that
        the loader's own witness cross-check would refuse the run and the test
        would pass while witnessing nothing -- the vacuity shape this OBPI has
        produced nine times.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            swapped_id = f"section-ownership-genesis-doc.md-{_SEED_FLOOR}"
            emit_section_ownership_genesis(
                Path("."),
                swapped_id,
                "doc.md",
                sections_digest(on_disk["sections"]),
                _SEED_FLOOR,
            )
            swapped = {**on_disk, "surface": "doc.md", "floor_event_id": swapped_id}
            # Sanity: the swapped-in state is one the canonical loader ACCEPTS,
            # so any refusal below comes from the guard and not from the loader.
            _DECLARATION_PATH.write_text(json.dumps(swapped), encoding="utf-8")
            load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path("."))
            _DECLARATION_PATH.write_text(json.dumps(on_disk), encoding="utf-8")

            real_lock = exclusive_declaration_lock

            @contextlib.contextmanager
            def swap_identity_on_entry(path):
                # Lands AFTER the identity is resolved and BEFORE the body of
                # the critical section runs -- the window an external writer
                # occupies, and the reason a pre-lock value is stale.
                with real_lock(path) as handle:
                    _DECLARATION_PATH.write_text(json.dumps(swapped), encoding="utf-8")
                    yield handle

            with patch(
                "gzkit.commands.content.unown.exclusive_declaration_lock",
                swap_identity_on_entry,
            ):
                result = self._invoke("Doc.md")

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn(
                "the loaded declaration declares identity",
                result.output,
                f"refused, but NOT by the check under test. {result.output}",
            )
            self.assertEqual(
                [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"],
                [],
                "no witness may name an identity the consumed snapshot does not carry",
            )
            self.assertFalse(
                self._JOURNAL.exists(),
                "the refusal precedes the journal write, so no residue is left",
            )

    @covers("REQ-0.35.0-04-02")
    def test_a_request_naming_a_surface_that_does_not_exist_says_so(self) -> None:
        """Would break if a missing file were reported as a different file.

        `_is_same_file` fails closed on a path it cannot stat, so a request
        naming a surface that simply is not there took the "different files"
        arm: `'Missing.md' and 'Doc.md' are different files`, which is false --
        they are not two files. This refusal fires before the surface is ever
        read, so it is the FIRST thing the operator sees, and it sent them
        looking for a collision instead of a missing file.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            orphan = _DECLARATION_PATH.with_name("Missing.md.json")
            orphan.write_bytes(_DECLARATION_PATH.read_bytes())
            self.assertFalse(Path("Missing.md").exists(), "fixture sanity")

            result = self._invoke("Missing.md")

            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("does not exist", result.output)
            self.assertNotIn(
                "are different files",
                result.output,
                "a surface that is absent is not a surface that differs",
            )
            self.assertIn("gz content unown Doc.md", result.output)

    # No `@covers`: this asserts OPERATOR PROSE, whose subject is the brief's
    # Requirement 9 (three-part recovery prose) -- and Requirement 9 has no
    # Acceptance-Criteria REQ id to bind to. REQ-0.35.0-04-02 is the
    # decrease-only ratchet, which this test does not assert, so carrying it
    # would be a proof-channel binding to the wrong subject (ADR-0.0.59).
    # Inventing a REQ to host it is not this task's business; it stays
    # deliberately uncovered rather than falsely covered.
    def test_the_next_step_never_prescribes_editing_the_declaration(self) -> None:
        """Would break if the refusal offered a declaration hand-edit.

        The draft next-step read "...or repair the declaration so it declares
        <requested>". That instruction cannot be carried out: the floor's
        witness is in an APPEND-ONLY ledger naming the old identity, so a
        declaration edited to declare the requested spelling is one
        `load_declaration` fails closed on at `event_surface !=
        declared_surface`. It is also the silent hand-edit of the declaration
        this command exists to stand between the operator and.

        Asserted POSITIVELY, on the whole next-step line. `assertNotIn` on one
        phrasing tests the absence of a single spelling of an unbounded
        prohibition -- it stays green for every re-wording of the same bad
        advice. `_refuse_surface_identity` emits exactly two next-step
        variants, so pinning the line is bounded and durable.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            _write_named_surface("Other.md", _SURFACE_TEXT)
            _DECLARATION_PATH.with_name("Other.md.json").write_bytes(_DECLARATION_PATH.read_bytes())

            result = self._invoke("Other.md")

            # output-contract: the next-step LINE is the behaviour under test --
            # this asserts what the operator is told to do, so the rendered form
            # IS the contract (`.gzkit/rules/tests.md` § Output-form fixture
            # carve-out).
            self.assertNotEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(
                result.output.rstrip("\n").splitlines()[-1],
                "  Retry with `gz content unown Doc.md --section alpha-section "
                '--attestor "<your name>" --reason "<why>"`.',
                "the next step is the canonical retry and nothing else",
            )

    # No `@covers`: this asserts a PRIVATE HELPER's exception posture at the
    # seam, not a REQ's subject. REQ-0.35.0-04-02 is the decrease-only ratchet.
    # The posture matters BECAUSE it keeps an unresolved identity out of the
    # witness, but the test does not exercise the ratchet, so binding it there
    # would bind the proof channel to a subject it never asserts (ADR-0.0.59).
    def test_an_unreadable_existing_declaration_fails_closed_not_open(self) -> None:
        """Would break if `_declared_surface` swallowed OSError like ValueError.

        It returned None for BOTH, and None means "fall through to the governed
        paths" -- which hands the caller's raw spelling onward as the resolved
        identity, the exact value this path exists to keep out of durable
        state. That is only safe when the loader's own read will refuse
        deterministically too. A missing file and malformed JSON are such
        states; an OSError on a file that EXISTS is not, because it is
        transient and the loader's later read may succeed where this one
        failed. `_is_same_file` already fails closed, and the two must not
        disagree about posture.

        Asserted at the seam rather than through the CLI on purpose: through
        the CLI both postures exit 1 here, because the loader happens to fail
        on the same unreadable file -- so a command-level assertion would pass
        either way and witness nothing.

        The read failure is INJECTED rather than produced by `chmod`, so the
        posture is witnessed on every supported platform. A chmod-based version
        skips on Windows and under root, which is where a fail-open/fail-closed
        disagreement would go unnoticed longest.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            self.assertTrue(_DECLARATION_PATH.exists(), "fixture sanity: the file EXISTS")
            with (
                patch.object(Path, "read_text", side_effect=OSError(13, "injected")),
                self.assertRaises(OSError),
            ):
                unown_module._declared_surface(_DECLARATION_PATH)

            # The deterministic states still fall through, so the governed
            # paths keep naming them with better prose than this guard can.
            self.assertIsNone(
                unown_module._declared_surface(_DECLARATION_PATH.with_name("Absent.md.json")),
                "an ABSENT declaration is deterministic: the loader refuses it",
            )
            _DECLARATION_PATH.write_text("{ not json", encoding="utf-8")
            self.assertIsNone(
                unown_module._declared_surface(_DECLARATION_PATH),
                "MALFORMED content is deterministic: the loader refuses it",
            )

    @covers("REQ-0.35.0-04-05")
    def test_a_snapshot_identity_mismatch_on_the_fresh_path_is_refused(self) -> None:
        """DEFENCE IN DEPTH — not evidence of an in-scope defect.

        Reproducing this requires WRITING `.gzkit/` mid-run: it hand-edits the
        ownership declaration and mints a `section_ownership_genesis` ledger
        row so the swapped state loads at all. The brief's § Threat Model
        places an actor with `.gzkit/` write access OUTSIDE the boundary as an
        accepted, disclosed residual, so nothing here is an in-scope blocker
        and this fixture must never be cited as one.

        What it DOES pin is the fresh path's half of the fixed-target
        contract: the declaration snapshot actually consumed is validated
        against the transaction target, and a mismatch REFUSES before any
        transaction write. The command must never adopt a second identity
        while holding the first one's lock -- that move is what turned a
        hand-edit into a durable witness naming a surface the declaration on
        disk does not carry.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            alias = _same_file_alias("Doc.md")
            if alias is None:
                self.skipTest("no case-insensitive filesystem and no symlink support")
            swapped = self._coherent_identity_swap(alias)
            before_events = len(_ledger_events())
            # Lands AFTER the target is resolved and BEFORE the snapshot is
            # loaded. The two spellings alias ONE file, so the swapped state is
            # coherent and the run reaches the snapshot check rather than being
            # refused for an unrelated reason.
            with self._swap_declaration_inside_the_lock(swapped):
                result = self._invoke("Doc.md")

            self._assert_refused_without_transaction_writes(
                result, before_events, swapped, "loaded declaration", exit_code=1
            )

    @covers("REQ-0.35.0-04-02")
    def test_a_snapshot_identity_mismatch_on_the_unlanded_recovery_branch_is_refused(self) -> None:
        """DEFENCE IN DEPTH — hand-authored journal plus hand-edited declaration.

        Same threat-model boundary as its fresh-path sibling: the reproduction
        writes `.gzkit/` directly, which the brief accepts as a disclosed
        residual. It pins the NOT-YET-LANDED recovery branch's half of the
        fixed-target contract.

        The journal names the target, so the journal-identity check passes and
        cannot mask this one. The predecessor ON DISK names something else, and
        the successor the branch derives from that predecessor inherits it --
        so completing would write a declaration under the target's path
        declaring a foreign identity, with a witness naming the target.
        """
        with self._runner.isolated_filesystem():
            prior_floor, span = self._seed_for_journal()
            record = self._journal_record(prior_floor, span)
            foreign = {
                **json.loads(_DECLARATION_PATH.read_text(encoding="utf-8")),
                "surface": "Other.md",
            }
            record["declaration_json"] = self._derived_successor(foreign, record)
            self._JOURNAL.write_text(json.dumps(record), encoding="utf-8")
            before_events = len(_ledger_events())

            # Injected AFTER the target is resolved, so entry resolution sees
            # the legitimate declaration and fixes the target to 'Doc.md'.
            # Swapping it beforehand is refused at entry as a different-file
            # request -- a real guard, but not the one under test, and a
            # fixture that trips it witnesses nothing here.
            with self._swap_declaration_inside_the_lock(foreign):
                result = self._invoke("Doc.md")

            self._assert_refused_without_transaction_writes(
                result, before_events, foreign, "on-disk predecessor", exit_code=2
            )
            self.assertTrue(self._JOURNAL.exists(), "recovery state must survive a refusal")

    @covers("REQ-0.35.0-04-02")
    def test_a_snapshot_identity_mismatch_on_the_landed_recovery_branch_is_refused(self) -> None:
        """DEFENCE IN DEPTH — hand-edited declaration after a real interruption.

        Same threat-model boundary. This is the ALREADY-LANDED branch: the
        declaration write survived and the ledger append did not, so the
        journal is retained and a retry resumes at the append. That resume must
        stay possible -- the sibling false-positive test below proves it does --
        but it may not witness a declaration whose identity is not the
        target's.

        The declaration write here happened BEFORE the mismatch was injected,
        so "no transaction writes" means no ledger row and a retained journal,
        with the landed declaration byte-unchanged from the state under test.
        """
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()
            landed = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            foreign = {**landed, "surface": "Other.md"}
            before_events = len(_ledger_events())

            # Injected after the target is resolved, for the same reason as the
            # unlanded sibling: a pre-run swap is refused at entry instead.
            with self._swap_declaration_inside_the_lock(foreign):
                result = self._invoke("Doc.md")

            self._assert_refused_without_transaction_writes(
                result, before_events, foreign, "landed declaration", exit_code=2
            )
            self.assertTrue(
                self._JOURNAL.exists(),
                "the journal is the only record able to finish this transition",
            )

    @covers("REQ-0.35.0-04-05")
    def test_an_interrupted_append_still_resumes_when_the_identity_agrees(self) -> None:
        """False-positive arm: the snapshot check must not break recovery.

        The fixed-target contract is required to PRESERVE recovery's ability to
        finish a declaration whose ledger witness has not yet landed. A check
        that refused every already-landed replay would satisfy all three
        refusal tests above and destroy the feature, so the resume path is
        asserted positively here rather than assumed.
        """
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()
            landed_floor = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))[
                "unowned_byte_floor"
            ]

            result = self._invoke("Doc.md")

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertFalse(self._JOURNAL.exists(), "a completed recovery clears its journal")
            witnessed = [
                event for event in _ledger_events() if event["event"] == "section_ownership_unowned"
            ]
            self.assertEqual(len(witnessed), 1, "the transition is witnessed exactly once")
            self.assertEqual(witnessed[0]["surface"], "Doc.md")
            self.assertEqual(witnessed[0]["new_unowned_byte_floor"], landed_floor)
            load_declaration(_DECLARATION_PATH, _SURFACE_TEXT, Path("."))

    @covers("REQ-0.35.0-04-02")
    def test_an_unreadable_declaration_during_replay_says_so(self) -> None:
        """Would break if a read failure were collapsed into an empty dict.

        `on_disk = {}` on `except (OSError, ValueError)` turned an
        existing-but-unreadable declaration into an IDENTITY mismatch: the
        operator was told "the on-disk predecessor declares identity None",
        and the next step -- re-run the same command -- does not address a
        permission flip or a failing disk. It also disagreed with
        `_declared_surface`, which deliberately re-raises `OSError` on a file
        that exists. The two postures now agree and the real condition is
        reported.

        An ABSENT declaration still falls through as `{}`: that is a real state
        the journal must be proven against, not a failure to observe one.
        """
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()
            before_events = len(_ledger_events())
            real_read = unown_module._read_surface_or_exit
            real_read_text = Path.read_text

            def deny_declaration(self_path, *args, **kwargs):
                if self_path.name == _DECLARATION_PATH.name:
                    raise OSError(13, "injected read failure")
                return real_read_text(self_path, *args, **kwargs)

            def install_then_read(surface_path, surface):
                # Installed AFTER entry resolution, which legitimately reads the
                # declaration and would otherwise refuse before the replay ran.
                out = real_read(surface_path, surface)
                patcher = patch.object(Path, "read_text", deny_declaration)
                patcher.start()
                self.addCleanup(patcher.stop)
                return out

            with patch.object(unown_module, "_read_surface_or_exit", install_then_read):
                result = self._invoke("Doc.md")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn("cannot read the ownership declaration", result.output)
            self.assertNotIn(
                "declares identity",
                result.output,
                "a read failure is not an identity mismatch, and its recovery differs",
            )
            self.assertIn("The journal is RETAINED", result.output)
            self.assertTrue(self._JOURNAL.exists())
            self.assertEqual(len(_ledger_events()), before_events)

    def test_the_forged_journal_next_step_never_prescribes_a_hand_edit(self) -> None:
        """Would break if the journal refusal told the operator to hand-edit.

        # output-contract: the next-step prose IS the behaviour under test.

        This next step read "Inspect {journal} against the ledger, reconcile the
        declaration by hand, then delete the journal and retry" while the ledger
        refusal 400 lines away said "The recovery is the retry below, never a
        hand-edit of the declaration". Two next steps in one file giving
        opposite instructions for the same residue -- and this one is reachable
        with NO `.gzkit/` access: an interrupted write leaves a truncated
        journal, which trips the shape check and exits through exactly here.

        Not `@covers`-bound: its subject is the brief's Requirement 9 (recovery
        prose), which has no Acceptance-Criteria REQ id.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            # A journal truncated by an interrupted write -- no `.gzkit/` write
            # access required to produce this in the field.
            self._JOURNAL.write_text('{"surface": "Doc.md", "sect', encoding="utf-8")

            result = self._invoke("Doc.md")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertNotIn(
                "by hand",
                result.output,
                "the governed recovery is a retry, never a hand-edit of the "
                f"declaration this command exists to protect. {result.output}",
            )
            self.assertIn("gz validate --ledger", result.output)

    # ---- fixtures shared by the identity-mismatch tests above --------------

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"

    def _coherent_identity_swap(self, alias: str) -> dict:
        """A declaration declaring *alias* that `load_declaration` ACCEPTS.

        Minting the matching genesis row is what makes the swapped state
        coherent, and it is also exactly why this fixture sits outside the
        threat boundary: it needs ledger write access.
        """
        on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
        swapped_id = f"section-ownership-genesis-{alias}-{_SEED_FLOOR}"
        emit_section_ownership_genesis(
            Path("."), swapped_id, alias, sections_digest(on_disk["sections"]), _SEED_FLOOR
        )
        return {**on_disk, "surface": alias, "floor_event_id": swapped_id}

    @contextlib.contextmanager
    def _swap_declaration_inside_the_lock(self, replacement: dict):
        """Replace the declaration AFTER the target is fixed, before it is consumed.

        `_read_surface_or_exit` is the first statement inside the critical
        section, so a swap here lands after entry resolution and the lock and
        before both the replay path and the fresh load -- the one window where
        the snapshot a branch actually consumes can differ from the target.
        """
        real_read = unown_module._read_surface_or_exit

        def swap_then_read(surface_path, surface):
            _DECLARATION_PATH.write_text(json.dumps(replacement), encoding="utf-8")
            return real_read(surface_path, surface)

        with patch.object(unown_module, "_read_surface_or_exit", swap_then_read):
            yield

    def _seed_for_journal(self) -> tuple[int, int]:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        return _SEED_FLOOR, measure_section_spans(_SURFACE_TEXT)["alpha-section"]

    def _journal_record(self, prior_floor: int, span: int) -> dict:
        """A journal naming the TARGET, self-consistent in every other field."""
        on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
        record = {
            "surface": "Doc.md",
            "section": "alpha-section",
            "prior_unowned_byte_floor": prior_floor,
            "new_unowned_byte_floor": prior_floor + span,
            "attestor": "g0",
            "reason": "probe",
            "ts": "2026-09-04T00:00:00+00:00",
            "parent_event_id": on_disk["floor_event_id"],
            "declaration_json": "{}",
            "event_id": "placeholder",
        }
        record["event_id"] = _mint_event_id(record, record["parent_event_id"])
        return record

    def _derived_successor(self, predecessor_raw: dict, record: dict) -> str:
        """The successor a CORRECT replay derives from *predecessor_raw*.

        Built the way production builds it, so only the identity disagrees --
        a placeholder would fail the declaration_json check instead and mask
        the check under test.
        """
        predecessor = OwnershipDeclaration(**predecessor_raw)
        successor = predecessor.model_copy(
            update={
                "sections": {**predecessor.sections, record["section"]: "unowned"},
                "unowned_byte_floor": record["new_unowned_byte_floor"],
                "floor_event_id": record["event_id"],
            }
        )
        return successor.model_dump_json(indent=2) + "\n"

    def _interrupt_at_append(self) -> None:
        """Land the declaration, fail the ledger append, retain the journal."""
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

        def fail(*args, **kwargs):
            raise OSError(5, "injected ledger append failure")

        with patch.object(unown_module, "_append_event_once", fail):
            first = self._invoke("Doc.md")
        self.assertEqual(first.exit_code, 2, msg=first.output)
        self.assertTrue(self._JOURNAL.exists(), "fixture sanity: the journal is retained")

    def _assert_refused_without_transaction_writes(
        self, result, before_events: int, expected_declaration: dict, phase: str, exit_code: int
    ) -> None:
        """Refused deterministically, with no transaction write after the swap.

        *phase* pins WHICH snapshot check refused. Four checks share one
        refusal function and therefore one prose shape, so an unpinned
        assertion is satisfied by any of them -- and a sibling check catching
        the case leaves a deleted guard green. Measured: the landed-branch
        case was caught by the witness-site check, so this test passed with its
        own guard removed until the phases were made distinguishable.
        """
        # `_refuse_foreign_declaration_snapshot` encodes `exit_code = 2 if
        # journal_retained else 1`, and the same flag chooses the residue prose
        # (`_ENTRY_SWEEP_CAVEAT` vs "The journal is RETAINED at ..."). A bare
        # `assertNotEqual(..., 0)` leaves that contract unpinned: flipping the
        # flag at any call site changes the operator's account of what survived
        # and all three tests stay green. Pinned per site, as
        # `test_a_line_ending_conversion_between_measurement_and_commit_is_refused`
        # pins exit 1 for the same reason.
        #
        # The exit-1 branch is pinned on the part of that caveat this refusal
        # ESTABLISHES. It stopped being "Nothing written." because this branch
        # sits below the entry boundary sweep, which may have unlinked a file
        # one statement earlier -- see `TestEntryBoundarySweepIsNotClaimedAway`.
        self.assertEqual(result.exit_code, exit_code, msg=result.output)
        self.assertIn(
            "no declaration byte changed and no witness was appended"
            if exit_code == 1
            else "The journal is RETAINED at",
            result.output,
            "the residue prose must agree with the exit code the same flag chose",
        )
        self.assertIn("Why forbidden:", result.output)
        self.assertIn(
            f"the {phase} declares identity",
            result.output,
            f"refused, but NOT by the check under test ({phase}). {result.output}",
        )
        # Compare through the PRODUCTION model, not raw `json.loads` equality.
        # Both sides are validated by `OwnershipDeclaration`, so this asserts the
        # refusal left a declaration that still SATISFIES THE SCHEMA as well as
        # being unchanged — raw dict equality says only that two dicts match and
        # would accept a shape the model rejects.
        #
        # Deliberately NOT `load_declaration`: the defence-in-depth callers here
        # hand-edit the declaration to a foreign identity after a real
        # interruption, so its `floor_event_id` resolves to no ledger event by
        # construction and the canonical loader fails closed on it — correctly.
        # Loadability is not the property this helper is about; non-mutation is.
        self.assertEqual(
            OwnershipDeclaration.model_validate(
                json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            ).model_dump(mode="json"),
            OwnershipDeclaration.model_validate(expected_declaration).model_dump(mode="json"),
            "no transaction write may land on a declaration whose identity "
            "is not the transaction target's",
        )
        self.assertEqual(
            len(_ledger_events()),
            before_events,
            "no witness may be appended for an identity the snapshot does not carry",
        )


class TestWitnessSourceIsTheFixedDestination(unittest.TestCase):
    """The witness is derived from a CHECKED snapshot at the FIXED destination.

    `_checked_landed_snapshot` is the last place a payload field used to route
    a filesystem read: the declaration path was re-derived from
    `record["surface"]`, so the write destination and the later read
    destination were chosen through different values. It now reads
    `target.declaration_path` and validates that snapshot to BE the transition
    the witness is about to describe.

    Exercised at the seam. On the replay path the landed-state gate refuses
    first, and on the fresh path reaching this check requires a write landing
    between the declaration write and the ledger append -- so a command-level
    fixture would witness a sibling guard, which is exactly the vacuity this
    module keeps producing.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _target_and_record(self) -> tuple[object, dict]:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        target = unown_module._resolve_target_or_exit(Path("."), "Doc.md", "alpha-section")
        landed = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
        record = {
            "surface": "Doc.md",
            "section": "alpha-section",
            "new_unowned_byte_floor": landed["unowned_byte_floor"],
            "event_id": landed["floor_event_id"],
            "declaration_json": json.dumps(landed),
        }
        return target, record

    @covers("REQ-0.35.0-04-05")
    def test_a_coherent_landed_snapshot_yields_its_map(self) -> None:
        """False-positive arm: the ordinary witness path must still work."""
        with self._runner.isolated_filesystem():
            target, record = self._target_and_record()

            sections = unown_module._checked_landed_snapshot(target, record)

            self.assertEqual(sections, json.loads(record["declaration_json"])["sections"])

    @covers("REQ-0.35.0-04-02")
    def test_a_foreign_identity_at_the_destination_is_refused(self) -> None:
        """Would break if the witness were derived from an unchecked read."""
        with self._runner.isolated_filesystem():
            target, record = self._target_and_record()
            landed = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            _DECLARATION_PATH.write_text(
                json.dumps({**landed, "surface": "Other.md"}), encoding="utf-8"
            )

            with self.assertRaises(SystemExit) as raised:
                unown_module._checked_landed_snapshot(target, record)

            self.assertEqual(raised.exception.code, 2)

    @covers("REQ-0.35.0-04-02")
    def test_a_destination_that_is_not_the_expected_transition_is_refused(self) -> None:
        """Would break if the snapshot were read but never validated.

        A digest taken from an unchecked read describes whatever happens to be
        at the destination -- not the transition the witness claims.
        """
        with self._runner.isolated_filesystem():
            target, record = self._target_and_record()
            landed = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            _DECLARATION_PATH.write_text(
                json.dumps({**landed, "unowned_byte_floor": landed["unowned_byte_floor"] + 99}),
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as raised:
                unown_module._checked_landed_snapshot(target, record)

            self.assertEqual(raised.exception.code, 2)


class _BarrierProbe:
    """Mutable observation of the injected directory-barrier fault.

    A typed object rather than a dict because the two fields have different
    types and one of them is the assertion subject: `attempts` answers "did the
    retry ATTEMPT the barrier", which is a different question from "did it
    refuse" and the one round-10 finding 1 turns on.
    """

    def __init__(self) -> None:
        self.last_replace: str | None = None
        self.attempts: int = 0


@contextlib.contextmanager
def _failing_directory_barrier_after_replace(target_name: str = "Doc.md.json"):
    """Fail the parent-directory fsync that follows *target_name*'s swap.

    `write_declaration_atomically` fsyncs the file, renames it into place, and
    only THEN syncs the parent directory -- so an error from that last step
    means the swap already landed and its durability barrier did not. That is
    § Recovery Protocol state B, and it is the ONE window this injector opens.

    The trigger is the destination of the most recent `os.replace`, never a
    call count: the transaction writes a source snapshot and a journal through
    the same atomic writer, so counting directory syncs would move the injected
    fault whenever the number of prior writes changed. Yields the mutable state
    so a test can assert the barrier was ATTEMPTED -- "the retry refused" is
    also true of a retry that never tried.
    """
    probe = _BarrierProbe()
    real_fsync = os.fsync
    real_replace = os.replace

    def spy_replace(src, dst, *args, **kwargs):
        outcome = real_replace(src, dst, *args, **kwargs)
        probe.last_replace = Path(dst).name
        return outcome

    def barrier(fd: int):
        if stat.S_ISDIR(os.fstat(fd).st_mode) and probe.last_replace == target_name:
            probe.attempts += 1
            msg = "persistent directory fsync failure"
            raise OSError(5, msg)
        return real_fsync(fd)

    with (
        patch("os.replace", side_effect=spy_replace),
        patch("gzkit.content.ownership.os.fsync", side_effect=barrier),
    ):
        yield probe


class TestRecoveryProtocolStateB(unittest.TestCase):
    """§ Recovery Protocol state B -- declaration replaced, durability UNCONFIRMED.

    Step-4b round-10 finding 1, `[high]`. `write_declaration_atomically`
    renames and THEN syncs the parent directory, so EVERY write in
    `_commit_transition` has a window where the swap landed but its barrier did
    not. Landed recovery read ONE signal -- the declaration already carries the
    journalled `floor_event_id` -- and inferred a state that signal does not
    establish: it skipped the atomic writer entirely, appended the witness,
    deleted the journal and reported success, never retrying the failed
    barrier. Measured by the adversary:

        REAL_WRITER first_exit 2 directory_fsync_attempts 2
        REAL_WRITER retry_exit 0 fsync_calls 0 witnesses 1 journal False

    States B and C are INDISTINGUISHABLE by inspection -- that is the defect,
    not an accident of the probe -- so recovery must re-establish the barrier
    on every landed replay rather than deciding which of the two it is in.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _seed(self) -> int:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        return measure_section_spans(_SURFACE_TEXT)["alpha-section"]

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-05")
    def test_landed_recovery_retries_the_barrier_and_refuses_while_it_fails(self) -> None:
        """Would break if landed recovery witnessed a declaration whose
        durability barrier it never re-attempted.

        The demonstration the operator required: repeated failure, then
        successful recovery from ONLY the material the implementation retained.
        The test restores nothing and holds no copy of anything -- every retry
        is the same command against the state the previous one left.
        """
        with self._runner.isolated_filesystem():
            span = self._seed()

            with _failing_directory_barrier_after_replace() as first_state:
                first = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(first.exit_code, 2, msg=first.output)
            self.assertGreaterEqual(first_state.attempts, 1)
            landed = json.loads(_DECLARATION_PATH.read_bytes().decode("utf-8"))
            self.assertEqual(
                landed["unowned_byte_floor"],
                _SEED_FLOOR + span,
                "state B is reached only when the swap ALREADY landed -- a probe "
                "that left the predecessor on disk would be exercising state A",
            )
            self.assertTrue(self._JOURNAL.exists())
            self.assertEqual(self._witnesses(), [])

            with _failing_directory_barrier_after_replace() as retry_state:
                retry = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertGreaterEqual(
                retry_state.attempts,
                1,
                "landed recovery must RE-ATTEMPT the durability barrier; a retry "
                "that never touches the writer cannot re-establish it",
            )
            self.assertEqual(
                retry.exit_code,
                2,
                f"a persistent barrier failure must keep refusing: {retry.output}",
            )
            self.assertEqual(
                self._witnesses(),
                [],
                "no witness may be appended while the declaration's durability "
                "is still unconfirmed",
            )
            self.assertTrue(
                self._JOURNAL.exists(),
                "recovery state must be RETAINED across a persistent barrier failure",
            )

            healed = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertEqual(healed.exit_code, 0, msg=healed.output)
            self.assertEqual(len(self._witnesses()), 1)
            self.assertFalse(self._JOURNAL.exists())
            reloaded = load_declaration(
                _DECLARATION_PATH, Path("Doc.md").read_bytes().decode("utf-8"), Path(".")
            )
            self.assertEqual(reloaded.sections["alpha-section"], "unowned")
            self.assertEqual(reloaded.unowned_byte_floor, _SEED_FLOOR + span)

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-05")
    def test_the_state_b_refusal_names_the_state_it_was_derived_from(self) -> None:
        """Would break if the refusal advised an action derived from one signal.

        # output-contract: the recovery instruction IS the behaviour under test.

        § Recovery Protocol binding constraint 4: every operator instruction in
        this module names the enumerated interruption state it was derived
        from. A refusal that merely says "retry" leaves the operator unable to
        tell whether anything landed.
        """
        with self._runner.isolated_filesystem():
            self._seed()
            with _failing_directory_barrier_after_replace():
                _unown(self._runner, attestor="g0", reason="moving to prose doc")
            with _failing_directory_barrier_after_replace():
                retry = _unown(self._runner, attestor="g0", reason="moving to prose doc")

            self.assertIn("state B", retry.output)
            self.assertIn("Why forbidden:", retry.output)
            self.assertIn("RETAINED", retry.output)
            self.assertNotIn(
                "Nothing written",
                retry.output,
                "the declaration already carries the new floor on this path",
            )


class TestRecoveryProtocolStateE(unittest.TestCase):
    """§ Recovery Protocol state E -- the source CHANGED since measurement.

    Step-4b round-10 finding 2, `[high]`. Recovery needs the exact bytes the
    interrupted run measured, and the journal retained only their DIGEST -- so
    an ordinary editor replacing the uncommitted text left the transition
    permanently uncompletable AND blocked every other section of the same
    surface:

        UNBACKED requested alpha-section exit 2 / doc-title exit 2 /
        alpha-section exit 2

    Restoring the exact old bytes was the only way out, and those bytes were an
    UNDISCLOSED prerequisite -- the governed path had discarded them. The
    measured bytes are now retained beside the journal as immutable recovery
    material, and the refusal extracts them to a side path and names the
    reconciliation. The operator ruled the "second copy of canon" objection
    unsound: the journal already copies the serialized successor declaration,
    and retained recovery material is historical evidence, never canon.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"
    _EXTRACTED = Path("Doc.md.unowning-recovery")

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _interrupt_at_append(self) -> int:
        """Seed, then fail the ledger append: declaration landed, journal kept."""
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]

        def fail(root, target, record):
            raise OSError(5, "injected ledger append failure")

        with patch.object(unown_module, "_append_event_once", fail):
            first = _unown(self._runner, attestor="g0", reason="probe")
        self.assertEqual(first.exit_code, 2, msg=first.output)
        self.assertTrue(self._JOURNAL.exists())
        return span

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    @covers("REQ-0.35.0-04-05")
    def test_a_changed_source_recovers_from_retained_material_alone(self) -> None:
        """Would break if the journal retained a digest but not the bytes.

        THE DEMONSTRATION THE OPERATOR REQUIRED, and the reason it is written
        this way: this test holds NO copy of the original surface. It never
        reads `_SURFACE_TEXT` after seeding and never stashes the bytes it is
        about to overwrite. The ONLY source the restoration draws from is the
        material the implementation itself retained -- a test that kept its own
        copy would prove nothing about recoverability, because the operator has
        no such copy.
        """
        with self._runner.isolated_filesystem():
            span = self._interrupt_at_append()
            surface = Path("Doc.md")

            self.assertTrue(
                self._SNAPSHOT.exists(),
                "the measured source bytes must be retained as recovery material; "
                "a digest names the bytes recovery needs but cannot supply them",
            )
            journalled_digest = json.loads(self._JOURNAL.read_bytes().decode("utf-8"))[
                "surface_digest"
            ]

            # An ordinary editor replaces the uncommitted text. No `.gzkit/`
            # access, no adversary -- and from here on the ORIGINAL bytes exist
            # nowhere the test can reach except the implementation's own store.
            surface.write_bytes(
                surface.read_bytes().replace(b"beta body\n", b"beta body, revised by hand\n")
            )
            edited = surface.read_bytes()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 2, msg=retry.output)
            self.assertIn("state E", retry.output)
            self.assertTrue(
                self._EXTRACTED.exists(),
                "state E must EXTRACT the retained bytes to a side path the "
                "operator can diff and restore from",
            )
            self.assertIn(self._EXTRACTED.as_posix(), retry.output)
            self.assertEqual(
                unown_module._surface_digest(self._EXTRACTED.read_bytes()),
                journalled_digest,
                "the extracted bytes must BE the measured ones -- an extraction "
                "that cannot reproduce the journalled digest recovers nothing",
            )
            self.assertEqual(
                surface.read_bytes(),
                edited,
                "the refusal must NEVER rewrite the source surface; the operator's "
                "newer edit is preserved",
            )

            # A different section is blocked too, and says so in the same terms.
            other = _unown(self._runner, section="doc-title", attestor="g0", reason="probe")
            self.assertEqual(other.exit_code, 2, msg=other.output)
            self.assertTrue(self._JOURNAL.exists())
            self.assertEqual(self._witnesses(), [])

            # RECONCILE exactly as the prose instructs: step 1 saves the newer
            # edit to a path OUTSIDE the repository -- a surface is a tracked
            # Layer-1 file and `git add -A` before `gz check` would otherwise
            # stage a full copy of it -- then step 3 restores the measured
            # bytes FROM THE EXTRACTED SIDE PATH.
            self.assertIn("to a path OUTSIDE this repository", retry.output)
            outside = Path(tempfile.mkdtemp())
            self.addCleanup(shutil.rmtree, outside, True)
            saved = outside / "Doc.md.saved"
            saved.write_bytes(surface.read_bytes())
            surface.write_bytes(self._EXTRACTED.read_bytes())

            completed = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(completed.exit_code, 0, msg=completed.output)
            self.assertEqual(len(self._witnesses()), 1)
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(
                self._SNAPSHOT.exists(),
                "recovery material is cleared with the journal it belongs to",
            )
            self.assertFalse(
                self._EXTRACTED.exists(),
                "the extracted copy is cleared with it -- a stale copy of "
                "superseded canon beside the surface is its own hazard",
            )
            reloaded = load_declaration(
                _DECLARATION_PATH, surface.read_bytes().decode("utf-8"), Path(".")
            )
            self.assertEqual(reloaded.sections["alpha-section"], "unowned")
            self.assertEqual(reloaded.unowned_byte_floor, _SEED_FLOOR + span)
            self.assertEqual(
                saved.read_bytes(),
                edited,
                "the newer edit survived the whole recovery, unmodified, at the "
                "path step 1 of the printed sequence told the operator to use",
            )

    @covers("REQ-0.35.0-04-05")
    def test_the_state_e_refusal_names_the_state_and_the_reconciliation(self) -> None:
        """Would break if the instruction were derived from one signal.

        § Recovery Protocol binding constraint 4. A digest mismatch alone says
        "something differs"; it does not tell the operator that their own edit
        is safe, where the measured bytes are, or what completes the pending
        move. The refusal names the state, both retained paths, and the steps.
        """
        # output-contract: the recovery instruction IS the behaviour under test.
        with self._runner.isolated_filesystem():
            self._interrupt_at_append()
            surface = Path("Doc.md")
            surface.write_bytes(surface.read_bytes() + b"an editor appended this\n")

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertIn("state E", retry.output)
            self.assertIn("Why forbidden:", retry.output)
            self.assertIn(self._SNAPSHOT.as_posix(), retry.output)
            self.assertIn(self._EXTRACTED.as_posix(), retry.output)
            self.assertIn("RETAINED", retry.output)
            self.assertNotIn(
                "Nothing written",
                retry.output,
                "the declaration already carries the new floor on this path",
            )
            # OPERATOR RULING POINT 2 (2026-09-05). The retired step 5 read
            # "re-apply your saved edit and, if it changed a section's span,
            # record it through `gz content unown` again" -- executed verbatim
            # it leaves the loader rejecting the surface (measured: floor 83,
            # summed unowned span 443) and the named remedy exiting 1 at its
            # own initial load. Operator verbatim: "Do not instruct users to
            # reapply an oversized edit and then invoke a command whose initial
            # loader rejects it."
            self.assertNotIn("re-apply your saved edit", retry.output)
            self.assertIn("RE-APPLYING IT IS A SEPARATE DECISION", retry.output)
            self.assertIn("to a path OUTSIDE this repository", retry.output)


class TestForgedJournalAdviceIsStateDerived(unittest.TestCase):
    """The journal refusal may not instruct a deletion derived from ONE signal.

    § Recovery Protocol binding constraint 3. `_refuse_forged_journal` told the
    operator that if the ledger carries no `section_ownership_unowned` event
    for the transition, "the raise never completed: delete the journal and
    re-run." That is FALSE. States B and C both have an ABSENT witness with the
    declaration ALREADY replaced -- the very states the round-10 finding is
    about -- so an operator following it destroys the only record able to
    complete the transition, on the strength of a signal that does not
    establish what it was read to establish.

    The correction is not a softer sentence. Every branch of the instruction is
    derived from the ENUMERATED state and names it, and the state is settled
    from BOTH signals together: the declaration's `floor_event_id` and whether
    the ledger carries the journal's `event_id`.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _refusal(self) -> str:
        """A `_refuse_forged_journal` exit, reached with NO `.gzkit/` write access.

        An interrupted write leaves a truncated journal, which trips the shape
        check and exits through the shared refusal -- the same prose every
        other forged-journal branch prints, so asserting on it here binds all
        of them.
        """
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        self._JOURNAL.write_bytes(b'{"surface": "Doc.md", "sect')
        result = _unown(self._runner, attestor="g0", reason="probe")
        self.assertEqual(result.exit_code, 2, msg=result.output)
        return result.output

    @covers("REQ-0.35.0-04-02")
    def test_an_absent_witness_never_licenses_deleting_the_journal(self) -> None:
        """Would break if the refusal restored its one-signal deletion advice.

        # output-contract: the next-step prose IS the behaviour under test.
        """
        with self._runner.isolated_filesystem():
            output = self._refusal()

            self.assertNotIn(
                "delete the journal and re-run",
                output,
                "the retired instruction: an absent ledger witness does not "
                "prove the declaration is unchanged -- states B and C share "
                "that shape with the declaration already replaced, and the "
                "journal is the only record able to complete them",
            )
            self.assertNotIn(
                "the raise never completed",
                output,
                "a missing witness cannot establish that nothing landed",
            )
            self.assertIn(
                "Do NOT delete the journal",
                output,
                "dropping the false instruction is only half the correction; "
                "the operator who already believes it needs the prohibition",
            )
            self.assertTrue(
                self._JOURNAL.exists(),
                "the refusal itself must retain the recovery record it is "
                "telling the operator not to destroy",
            )

    @covers("REQ-0.35.0-04-02")
    def test_the_advice_is_derived_from_the_enumerated_states(self) -> None:
        """Would break if the refusal named a next step without its state.

        # output-contract: the next-step prose IS the behaviour under test.
        """
        with self._runner.isolated_filesystem():
            output = self._refusal()

            # Presence ANYWHERE in the prose is not the property. The
            # property is that EVERY BRANCH of the instruction names the state
            # it came from -- a label loose in a closing sentence leaves a
            # branch unlabelled while a substring check reads green, which is
            # the silently-vacuous shape this OBPI has produced nine times.
            # Measured: deleting "state A, " from the first branch SURVIVED an
            # `assertIn("state A", output)`, because the closing sentence still
            # said it.
            branches = [
                line.strip() for line in output.splitlines() if line.strip().startswith("- ")
            ]
            self.assertEqual(
                len(branches), 3, f"three enumerated branches were expected: {branches}"
            )
            named: set[str] = set()
            for branch in branches:
                match = re.match(r"- state ([A-E])\b", branch)
                self.assertIsNotNone(match, f"a branch that does not name its state: {branch!r}")
                named.update(re.findall(r"state ([A-E])\b", branch))
            self.assertEqual(
                named,
                {"A", "B", "C", "D", "E"},
                "every state an absent-witness inspection can be in must be named "
                "on a branch of its own instruction, AND NO OTHER LABEL MAY APPEAR: "
                "the subset form this replaces surrendered the second half, so a "
                "stray 'state F' or a mislabelled branch read green. E belongs "
                "because it is orthogonal to A-D and D's branch carries it; the "
                f"assertion below is what pins WHERE: {branches}",
            )
            # D SETTLES THE STORES AND SAYS NOTHING ABOUT THE SOURCE. The D
            # branch used to read "the transition completed. Re-run the same
            # command to clear the journal" -- an action with no source axis,
            # so an operator whose editor touched the surface after the witness
            # landed was promised a clear-up and met a refusal instead. E is
            # ORTHOGONAL to A-D, which is why it may appear here and nowhere
            # else in the enumeration.
            d_branch = next(branch for branch in branches if branch.startswith("- state D"))
            self.assertIn(
                "state E",
                d_branch,
                "D's triage branch must carry the orthogonal source axis: a "
                f"witness settles the transition, never the surface: {d_branch!r}",
            )
            self.assertIn("floor_event_id", output)
            self.assertIn("event_id", output)
            self.assertIn(_DECLARATION_PATH.as_posix(), output)
            self.assertIn("gz validate --ledger", output)
            self.assertIn(
                "INDISTINGUISHABLE",
                output,
                "B and C cannot be told apart from disk, so prose that tells "
                "the operator which one they are in would be lying",
            )
            self.assertNotIn(
                "by hand",
                output,
                "the governed recovery is a retry, never a hand-edit",
            )


class TestRecoveryProtocolStateA(unittest.TestCase):
    """§ Recovery Protocol state A -- journal persisted, declaration untouched.

    The UNLANDED replay branch, and the second of the two branches the
    demonstration obligation covers. Its sibling
    `TestRecoveryProtocolStateB` covers the landed one; a demonstration on one
    branch says nothing about the other, which is precisely the round-8
    finding-1 asymmetry -- a binding implemented on the fresh path and left off
    its twin.

    The unlanded branch already re-applied the transition through the atomic
    writer, so it was never the site of round-10 finding 1. What is asserted
    here is that it stayed that way, and that the recovery material this OBPI
    now retains survives repeated failure on this branch too rather than only
    on the landed one.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    @contextlib.contextmanager
    def _declaration_replace_fails(self):
        """Fail the declaration's atomic swap; every other write lands.

        The swap is the only step that can make new contents visible, so
        failing it -- rather than the durability barrier that follows it --
        is what holds the declaration at its PREDECESSOR and puts the run in
        state A rather than state B.
        """
        real_replace = os.replace

        def refuse(src, dst, *args, **kwargs):
            if Path(dst).name == "Doc.md.json":
                msg = "injected declaration swap failure"
                raise OSError(5, msg)
            return real_replace(src, dst, *args, **kwargs)

        with patch("os.replace", side_effect=refuse):
            yield

    @covers("REQ-0.35.0-04-02")
    def test_the_unlanded_branch_refuses_repeatedly_then_recovers(self) -> None:
        """Would break if a repeated unlanded failure lost its recovery state.

        Repeated failure, then successful recovery from ONLY what the
        implementation retained: this test holds no copy of the declaration,
        the journal or the surface, and restores nothing. Every run is the same
        command against the state the previous one left.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            span = measure_section_spans(_SURFACE_TEXT)["alpha-section"]
            predecessor = _DECLARATION_PATH.read_bytes()

            with self._declaration_replace_fails():
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 2, msg=first.output)
            self.assertEqual(
                _DECLARATION_PATH.read_bytes(),
                predecessor,
                "state A requires the declaration to be UNTOUCHED -- a probe "
                "that let the swap land would be exercising state B instead",
            )
            self.assertTrue(self._JOURNAL.exists(), "the pending transition is journalled")
            self.assertTrue(
                self._SNAPSHOT.exists(),
                "the measured source is retained before the journal that names its digest exists",
            )

            with self._declaration_replace_fails():
                second = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(
                second.exit_code,
                2,
                f"the unlanded branch must keep refusing while it cannot write: {second.output}",
            )
            self.assertEqual(self._witnesses(), [])
            self.assertTrue(
                self._JOURNAL.exists(),
                "a refused unlanded replay retains the journal",
            )
            self.assertTrue(
                self._SNAPSHOT.exists(),
                "and retains the measured source beside it -- recovery material "
                "must survive on BOTH branches, not only the landed one",
            )

            third = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(third.exit_code, 0, msg=third.output)
            self.assertEqual(len(self._witnesses()), 1)
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())
            reloaded = load_declaration(
                _DECLARATION_PATH, Path("Doc.md").read_bytes().decode("utf-8"), Path(".")
            )
            self.assertEqual(reloaded.sections["alpha-section"], "unowned")
            self.assertEqual(
                reloaded.unowned_byte_floor,
                _SEED_FLOOR + span,
                "the floor rises exactly once across three invocations",
            )

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_state_a_recovery_writes_through_the_durable_writer(self) -> None:
        """Would break if the unlanded branch stopped syncing what it wrote.

        The landed branch had to GAIN a durability re-establishment (round-10
        finding 1). This branch has always had one, because it re-applies the
        derived successor through `write_declaration_atomically`. Asserting it
        keeps the two branches from drifting apart again in the other
        direction: a barrier failure here must refuse, exactly as it does
        there.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with self._declaration_replace_fails():
                _unown(self._runner, attestor="g0", reason="probe")

            with _failing_directory_barrier_after_replace() as state:
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertGreaterEqual(
                state.attempts,
                1,
                "the unlanded replay must write through the durable writer",
            )
            self.assertEqual(retry.exit_code, 2, msg=retry.output)
            self.assertEqual(self._witnesses(), [])
            self.assertTrue(self._JOURNAL.exists())


class TestRecoveryProtocolStateD(unittest.TestCase):
    """§ Recovery Protocol state D -- the witness is PRESENT; clear the journal.

    State D is what makes the landed branch's durability re-establishment a
    STATE-DERIVED action rather than a blanket one. A witness in the ledger can
    only exist if the declaration write and its barrier both returned success,
    so re-asserting durability there would be work derived from no state at all.

    D's retry action is NOT "clear the journal only". The § Recovery Protocol
    table's D row now qualifies that phrase, and the sibling test in this class
    asserts exit 2 in D: the source axis is orthogonal, so a witnessed
    transition over a changed source is the D+E pair, and cleanup is its own
    obligation that a failed removal leaves outstanding.

    Reached by an interruption between the ledger append and the journal
    unlink: an ordinary crash window, no `.gzkit/` write access required.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"

    def setUp(self) -> None:
        self._runner = CliRunner()

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_a_witnessed_transition_only_clears_its_journal(self) -> None:
        """Would break if recovery re-wrote a declaration a witness already proves.

        The barrier is held FAILING for the whole retry. A run that re-asserted
        durability regardless of state would touch the writer and refuse -- so
        exit 0 with zero barrier attempts is the observation that the action
        was chosen from the ledger signal, not applied blindly.
        """
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 0, msg=first.output)
            witnesses = [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]
            self.assertEqual(len(witnesses), 1)
            self.assertTrue(
                self._JOURNAL.exists(),
                "state D requires a WITNESSED transition whose journal survived; "
                "without the retained journal the retry would find nothing pending",
            )

            with _failing_directory_barrier_after_replace() as state:
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 0, msg=retry.output)
            self.assertEqual(
                state.attempts,
                0,
                "a witnessed transition needs no durability re-establishment: "
                "the witness could not exist unless the barrier had succeeded",
            )
            self.assertEqual(
                len([e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]),
                1,
                "the witness is appended exactly once across both runs",
            )
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())

    @covers("REQ-0.35.0-04-05")
    def test_the_clear_only_run_does_not_claim_the_raise_an_earlier_run_made(self) -> None:
        """Would break if a run that wrote nothing reported itself as the one that raised.

        THE FAILURE PATH ALREADY CARRIES THIS HONESTY AND THE SUCCESS PATH DID
        NOT. `_refuse_clean_success_on_a_moved_surface` takes `committed_now`
        precisely so it can say "was witnessed by an earlier run" instead of
        claiming authorship -- and it exists because that distinction is the one
        the operator needs. In state D over an unchanged surface this run
        appends nothing (`_append_event_once` finds the existing row) and writes
        nothing (both the coherence gate and the durability re-establishment are
        skipped); it only clears. "Completed the interrupted un-owning ...
        Unowned-byte floor rose from 26 to 83" describes a DIFFERENT run.
        """
        # output-contract: the completion sentence IS the behaviour under test.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 0, msg=first.output)
            ledger_before = _ledger_events()
            declaration_before = _DECLARATION_PATH.read_bytes()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 0, msg=retry.output)
            self.assertEqual(
                _ledger_events(),
                ledger_before,
                "state D appends nothing -- that is what makes the claim false",
            )
            self.assertEqual(
                _DECLARATION_PATH.read_bytes(),
                declaration_before,
                "state D writes no declaration either",
            )
            self.assertNotIn(
                "Completed the interrupted un-owning",
                retry.output,
                "this run completed nothing: it found the transition already "
                "witnessed and cleared the recovery material",
            )
            self.assertIn(
                "wrote no declaration and appended no ledger event",
                retry.output,
                "the run must say what it actually did",
            )
            self.assertIn(
                "an EARLIER run committed and witnessed",
                retry.output,
                "the raise is attributed to the run that made it, exactly as "
                "`_refuse_clean_success_on_a_moved_surface` attributes it",
            )
            self.assertIn(
                f"from {_SEED_FLOOR} to",
                retry.output,
                "the floor values stay reported -- what changes is whose run made the move",
            )

    @covers("REQ-0.35.0-04-02")
    def test_a_changed_source_is_reported_as_the_pair_never_as_bare_state_e(self) -> None:
        """Would break if D were reported as bare E, or E folded into bare D.

        E is ORTHOGONAL to A-D, and this test fences BOTH ways it has been got
        wrong. Reading the digest first made an ordinary crash between the
        ledger append and the journal unlink, followed by an ordinary editor
        save, refuse in state E's terms -- whose prose is FALSE here, because
        it says completing "would witness a span the surface no longer has"
        while in D `_append_event_once` finds the existing id and appends
        nothing at all. The correction then over-swung and let D SWALLOW E
        (Step-4b round-11 finding 1), which is what the operator rejected on
        2026-09-05: *"Establishing one does not discharge the others."*

        The truthful report is the PAIR -- stores in D, source in E -- with the
        witness preserved unduplicated and every recovery obligation named for
        what it actually is.
        """
        # output-contract: naming BOTH states in the refusal IS the behaviour.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 0, msg=first.output)
            self.assertTrue(self._JOURNAL.exists())

            # An ordinary editor save, after the transition already completed.
            surface = Path("Doc.md")
            surface.write_bytes(surface.read_bytes() + b"an editor appended this\n")
            edited = surface.read_bytes()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 2, msg=retry.output)
            self.assertIn("state D", retry.output)
            self.assertIn("state E", retry.output)
            self.assertIn("transition witnessed; source reconciliation pending", retry.output)
            self.assertNotIn(
                "would witness a span the surface no longer has",
                retry.output,
                "bare state-E prose is FALSE in D: the witness is already in the "
                "ledger, so this run witnesses nothing at all",
            )
            self.assertEqual(
                len([e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]),
                1,
                "the witness is PRESERVED, never duplicated -- `_append_event_once`'s "
                "existing-row arm proves the present row describes THIS transition",
            )
            self.assertEqual(
                surface.read_bytes(),
                edited,
                "the refusal must NEVER rewrite the surface; the operator's edit is theirs",
            )
            self.assertTrue(self._JOURNAL.exists())
            self.assertTrue(self._SNAPSHOT.exists())


def _sidecar_names_the_producers_write(name: str) -> dict[str, str]:
    """Ask the REAL producers what they name their sidecars beside a file called *name*.

    `write_bytes_atomically` stages through `tempfile.NamedTemporaryFile` and
    `exclusive_file_lock` opens `<name>.lock`; both spellings live in
    `gzkit.content.ownership` and `gzkit.file_lock`, not here. Transcribing them
    into a test makes the test agree with its author rather than with the code,
    so a producer that changed its staging shape would leave the ignore-rule
    witness green while the real tree went dirty.

    Run in a scratch directory so nothing is written near the repository: only
    the NAMES are carried back, and the caller transplants them beside the real
    target. `git check-ignore` matches on path text, so the files need not exist.
    """
    staged: list[str] = []
    real_replace = Path.replace

    def spy(self: Path, target):
        staged.append(self.name)
        return real_replace(self, target)

    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / name
        with patch.object(Path, "replace", spy):
            write_bytes_atomically(probe, b"probe")
        with exclusive_declaration_lock(probe):
            pass
        residents = {entry.name for entry in Path(tmp).iterdir()} - {name}
    if len(staged) != 1 or len(residents) != 1:
        msg = f"the producers wrote an unexpected sidecar set: {staged=} {residents=}"
        raise AssertionError(msg)
    return {"staging": staged[0], "lock": residents.pop()}


class TestRecoveryArtifactsAreIgnored(unittest.TestCase):
    """Every artifact the raise-path writes must be ignored by real `git`.

    `.gzkit/ownership/` IS tracked -- the declaration is the coverage claim
    gating the ratchet -- so a sidecar that git can see dirties the tree on
    every un-owning. `AGENTS.md` § Execution Rules mandates `git add -A` BEFORE
    `gz check`, so an unignored artifact is STAGED, not merely noticed.

    EVERY PATH IS DERIVED FROM ITS PRODUCER, never transcribed: the four the
    transaction names come from `_target_for`, and the two sidecars come from
    running `write_bytes_atomically` and `exclusive_declaration_lock` and
    observing what they write. A hand-written name agrees with whatever its
    author believed and cannot catch a producer/consumer divergence, which is
    exactly the miss this roster made: the EXTRACT's staging twin -- the
    artifact family the `.*.unowning-recovery.*.tmp` rule was authored for --
    was absent, so deleting that rule broke no test.

    And the check is `git check-ignore` -- real git against the real repository
    -- because "the string appears in `.gitignore`" is a presence check, and
    the glob `.gzkit/ownership/**/*.journal` LOOKS like it covers
    `<surface>.json.journal.source` while matching nothing of the sort.
    """

    _REPO_ROOT = Path(__file__).resolve().parents[2]

    def _artifacts(self) -> dict[str, Path]:
        target = unown_module._target_for(self._REPO_ROOT, "AGENTS.md")
        declaration = target.declaration_path
        extract = target.recovery_extract_path
        declaration_sidecars = _sidecar_names_the_producers_write(declaration.name)
        extract_sidecars = _sidecar_names_the_producers_write(extract.name)
        return {
            "lock": declaration.with_name(declaration_sidecars["lock"]),
            "declaration staging": declaration.with_name(declaration_sidecars["staging"]),
            "journal": target.journal_path,
            "retained source": target.journal_source_path,
            "state-E extract": extract,
            "state-E extract staging": extract.with_name(extract_sidecars["staging"]),
        }

    def test_git_ignores_every_artifact_the_raise_path_writes(self) -> None:
        """Would break if a write-discipline artifact could be committed.

        The state-E extract is the sharpest case: it is written OUTSIDE
        `.gzkit/`, beside the surface at the repository root, so for the real
        declaration it is `AGENTS.md.unowning-recovery` -- a full copy of
        Layer-1 canon sitting in the tracked root, produced by ordinary CLI use
        with no special access.
        """
        unignored = []
        for label, path in self._artifacts().items():
            completed = subprocess.run(
                ["git", "check-ignore", "--quiet", path.as_posix()],
                cwd=self._REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if completed.returncode != 0:
                unignored.append(f"{label}: {path.relative_to(self._REPO_ROOT).as_posix()}")
        self.assertEqual(
            unignored,
            [],
            "every artifact `gz content unown` writes must be ignored by name; "
            f"git does not ignore: {unignored}",
        )


class TestMovedSurfaceRefusalNamesItsStateAndPaths(unittest.TestCase):
    """The finalization refusal is the one instruction that named neither.

    `_refuse_clean_success_on_a_moved_surface` told the operator to "restore
    the surface to the state that was measured" without saying WHERE those
    bytes are -- while its sibling `_refuse_source_changed_since_measurement`
    reaches the same retained material, extracts it, and prints both paths. It
    was also the last operator instruction in the module not to name the
    enumerated state it was derived from.

    The state here is the pair: the stores are in D -- the declaration carries
    the new floor and the ledger carries its witness, both durable -- and the
    SOURCE is in E. That is exactly the orthogonality the plan's five-row table
    obscured by presenting E as a fifth alternative.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"
    _EXTRACTED = Path("Doc.md.unowning-recovery")

    _GROWN = _SURFACE_TEXT.replace(
        "alpha body line two\n",
        "alpha body line two\n" + "alpha body grown by an editor\n" * 12,
    )

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _edit_inside_the_transaction(self):
        """Reproduce round-7's window: an editor save after the pre-flight check."""
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        real_commit = unown_module._commit_transition

        def edit_then_commit(*args, **kwargs):
            _write_surface(self._GROWN)
            return real_commit(*args, **kwargs)

        with patch.object(unown_module, "_commit_transition", edit_then_commit):
            return _unown(self._runner, attestor="g0", reason="probe")

    @covers("REQ-0.35.0-04-05")
    def test_the_refusal_names_the_state_and_the_retained_bytes(self) -> None:
        """Would break if the instruction named a restore without its source."""
        # output-contract: the recovery instruction IS the behaviour under test.
        with self._runner.isolated_filesystem():
            result = self._edit_inside_the_transaction()

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn("state D", result.output)
            self.assertIn("state E", result.output)
            self.assertIn(self._SNAPSHOT.as_posix(), result.output)
            self.assertIn(self._EXTRACTED.as_posix(), result.output)
            self.assertTrue(
                self._EXTRACTED.exists(),
                "an instruction to restore measured bytes must hand them over, "
                "not describe a file the operator has to go find",
            )
            self.assertEqual(
                unown_module._surface_digest(self._EXTRACTED.read_bytes()),
                json.loads(self._JOURNAL.read_bytes().decode("utf-8"))["surface_digest"],
                "the extracted bytes must reproduce the journalled digest",
            )
            # THE RESTORE SCRIPT BELONGS HERE (operator ruling 2026-09-05).
            # An earlier design withheld it on the reasoning that D has nothing
            # left to complete, so a re-run alone would suffice -- and Step-4b
            # round 11 showed where that leads: the re-run cleared every
            # recovery artifact and exited 0 over a surface whose live span
            # exceeded the floor. Reconciliation is a SEPARATE obligation from
            # the witness, so the operator is handed the material and the
            # order that discharges it.
            self.assertIn(
                "restore the measured bytes over",
                result.output,
                "the source is unreconciled, so the restore script is exactly "
                "what this operator needs -- withholding it was round-11's defect",
            )
            self.assertIn(
                "transition witnessed; source reconciliation pending",
                result.output,
                "the three obligations are reported separately, never collapsed",
            )
            self.assertNotIn(
                "completes the pending transition",
                result.output,
                "the transition already completed; the re-run only clears up",
            )

    @covers("REQ-0.35.0-04-05")
    def test_the_promised_next_step_actually_reaches_a_loadable_state(self) -> None:
        """Would break if the printed promise could not be kept.

        The refusal leaves the stores in D with a changed source. Its printed
        next step is a promise, and this test executes it rather than reading
        it: restore the measured bytes from the extract the refusal handed
        over, re-run, and the recovery material is gone with the declaration
        loading cleanly. Before the round-11 correction the printed promise was
        "re-running clears the journal and nothing else" -- which the re-run
        kept, while leaving a declaration its own loader rejects.
        """
        with self._runner.isolated_filesystem():
            refusal = self._edit_inside_the_transaction()
            self.assertTrue(self._JOURNAL.exists())
            self.assertIn(self._EXTRACTED.as_posix(), refusal.output)

            surface = Path("Doc.md")
            surface.write_bytes(self._EXTRACTED.read_bytes())
            rerun = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(rerun.exit_code, 0, msg=rerun.output)
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())
            self.assertFalse(self._EXTRACTED.exists())
            self.assertEqual(
                len([e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]),
                1,
                "the completed transition is witnessed exactly once",
            )
            load_declaration(_DECLARATION_PATH, surface.read_bytes().decode("utf-8"), Path("."))


class TestRecoveryProtocolStateDPlusE(unittest.TestCase):
    """D and E are THREE OBLIGATIONS, and establishing one discharges none of the others.

    Step-4b round-11 finding 1, `[high]`. A prior correction resolved "E
    shadows D" by making D SWALLOW E: the replay probed the ledger first and,
    on a present witness, skipped the source binding entirely, cleared the
    journal, its retained source and the extract, and exited 0 -- while the
    declaration's floor was exceeded by the live span, so `load_declaration`
    rejected the surface and the advertised re-run could not repair it (its own
    initial load rejects the exceeded floor). Measured: `D+E retry_exit 0 floor
    83 span 102 journal False snapshot False extract False`, then
    `advertised_raise alpha-section exit 1`.

    Operator ruling 2026-09-05, verbatim: *"Reject 'D beats E.' Keep three
    obligations separate: the transition is durably witnessed; the source is
    reconciled; recovery cleanup is complete. Establishing one does not
    discharge the others."*

    Reached through ORDINARY CLI use with an editor save during the
    transaction -- no `.gzkit/` write access anywhere in the reproduction.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"
    _EXTRACTED = Path("Doc.md.unowning-recovery")

    _GROWN = _SURFACE_TEXT.replace(
        "alpha body line two\n",
        "alpha body line two\n" + "alpha body grown by an editor\n" * 12,
    )

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _reach_d_plus_e(self):
        """Commit the transition with an editor save landing inside it.

        The stores end in state D -- declaration and witness both durable --
        and the SOURCE ends in state E, carrying bytes the journalled floor was
        never measured against.
        """
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        real_commit = unown_module._commit_transition

        def edit_then_commit(*args, **kwargs):
            _write_surface(self._GROWN)
            return real_commit(*args, **kwargs)

        with patch.object(unown_module, "_commit_transition", edit_then_commit):
            first = _unown(self._runner, attestor="g0", reason="probe")
        self.assertEqual(first.exit_code, 2, msg=first.output)
        return first

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    @covers("REQ-0.35.0-04-05")
    def test_a_witnessed_transition_with_a_changed_source_is_not_clean_success(self) -> None:
        """Would break if a durable witness were read as discharging reconciliation.

        The three obligations are asserted SEPARATELY, because that is the
        ruling: the witness is durable (one row, unduplicated), the source is
        NOT reconciled (non-zero exit naming that), and cleanup is NOT complete
        (every piece of retained recovery material still on disk).
        """
        # output-contract: the separately-named obligations ARE the behaviour.
        with self._runner.isolated_filesystem():
            self._reach_d_plus_e()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                retry.exit_code,
                0,
                "a witnessed transition over an unreconciled source is not a "
                f"clean success: {retry.output}",
            )
            self.assertIn("transition witnessed; source reconciliation pending", retry.output)
            self.assertTrue(
                self._JOURNAL.exists(),
                "the journal is the only record able to name what the floor was "
                "measured against; it is retained while reconciliation is pending",
            )
            self.assertTrue(
                self._SNAPSHOT.exists(),
                "the retained measured bytes ARE the reconciliation material -- "
                "clearing them removes the only route back",
            )
            self.assertTrue(
                self._EXTRACTED.exists(),
                "the extract is what the operator diffs and restores from",
            )

    @covers("REQ-0.35.0-04-05")
    def test_the_refusal_never_rewrites_the_operators_newer_bytes(self) -> None:
        """Would break if reconciliation were performed FOR the operator.

        Restoring the measured bytes over the surface is the one move that
        would discharge E without asking -- and it would silently destroy work
        the command has no claim on. The recovery is HANDED OVER, never
        performed: the retained bytes go to a side path beside the surface and
        the surface itself is left exactly as the operator last wrote it.
        """
        with self._runner.isolated_filesystem():
            self._reach_d_plus_e()
            surface = Path("Doc.md")
            edited = surface.read_bytes()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 2, msg=retry.output)
            self.assertEqual(
                surface.read_bytes(),
                edited,
                "the operator's newer bytes are byte-identical after the refusal",
            )
            self.assertEqual(
                unown_module._surface_digest(self._EXTRACTED.read_bytes()),
                json.loads(self._JOURNAL.read_bytes().decode("utf-8"))["surface_digest"],
                "the extract holds the MEASURED bytes, not the operator's newer ones",
            )

    @covers("REQ-0.35.0-04-05")
    def test_repeated_retries_never_erode_the_recovery_material(self) -> None:
        """Would break if the SECOND retry behaved differently from the first.

        THE OPERATOR'S DEMONSTRATION OBLIGATION. Round-11's defect was exactly
        a retry that behaved differently from the invocation before it: the
        first run refused and the next cleared every artifact and exited 0. A
        single retry says nothing about the second, so this drives three and
        asserts the full set each time -- non-success, ONE witness, the
        operator's newer bytes byte-identical, and every piece of recovery
        material still on disk and still reproducing the journalled digest.
        """
        # output-contract: every retry must keep naming the pending obligation.
        with self._runner.isolated_filesystem():
            self._reach_d_plus_e()
            surface = Path("Doc.md")
            edited = surface.read_bytes()
            journalled = json.loads(self._JOURNAL.read_bytes().decode("utf-8"))["surface_digest"]

            for attempt in range(1, 4):
                retry = _unown(self._runner, attestor="g0", reason="probe")

                self.assertNotEqual(
                    retry.exit_code, 0, f"retry {attempt} reported clean success: {retry.output}"
                )
                self.assertIn(
                    "transition witnessed; source reconciliation pending",
                    retry.output,
                    f"retry {attempt} stopped naming the outstanding obligation",
                )
                self.assertEqual(
                    len(self._witnesses()), 1, f"retry {attempt} duplicated the witness"
                )
                self.assertEqual(
                    surface.read_bytes(), edited, f"retry {attempt} rewrote the operator's bytes"
                )
                self.assertTrue(self._JOURNAL.exists(), f"retry {attempt} destroyed the journal")
                self.assertTrue(self._SNAPSHOT.exists(), f"retry {attempt} destroyed the source")
                self.assertEqual(
                    unown_module._surface_digest(self._EXTRACTED.read_bytes()),
                    journalled,
                    f"retry {attempt} left an extract that is not the measured bytes",
                )

            # Only reconciliation ends it -- and then exactly once.
            surface.write_bytes(self._EXTRACTED.read_bytes())
            completed = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(completed.exit_code, 0, msg=completed.output)
            self.assertEqual(len(self._witnesses()), 1)
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())
            self.assertFalse(self._EXTRACTED.exists())

    @covers("REQ-0.35.0-04-05")
    def test_executing_the_printed_sequence_verbatim_reaches_a_loadable_state(self) -> None:
        """Would break if the printed recovery sequence could not be executed.

        OPERATOR RULING POINT 2 (2026-09-05), verbatim: *"Do not instruct users
        to reapply an oversized edit and then invoke a command whose initial
        loader rejects it."* The retired step 5 said exactly that, and an
        operator following it verbatim ended where they started -- the surface
        oversized against the recorded floor, `load_declaration` refusing it,
        and the named remedy `gz content unown` refusing at its own initial
        load.

        This test EXECUTES the sequence rather than reading it. It asserts on
        the canonical loader, not on prose: the reproduced failure is proven
        REAL by a rejecting load before recovery, the printed steps are then
        performed in order, and the same loader must ACCEPT afterwards with the
        operator's saved edit intact at the path step 1 named.
        """
        # output-contract: the printed sequence is executed, so it IS the contract.
        with self._runner.isolated_filesystem():
            self._reach_d_plus_e()
            surface = Path("Doc.md")
            oversized = surface.read_bytes()

            retry = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(retry.exit_code, 2, msg=retry.output)

            # THE FAILURE IS REAL: the floor the transition witnessed is
            # exceeded by the live span, exactly as round 11 measured
            # (`floor 83 span 102`), so the surface does not load at all.
            with self.assertRaises(OwnershipLoadError):
                load_declaration(_DECLARATION_PATH, oversized.decode("utf-8"), Path("."))

            # The retired instruction is GONE, and its shape with it.
            self.assertNotIn("re-apply your saved edit", retry.output)
            self.assertIn("RE-APPLYING IT IS A SEPARATE DECISION", retry.output)

            # STEP 1 -- save the current work to a path OUTSIDE the repository.
            self.assertIn("to a path OUTSIDE this repository", retry.output)
            outside = Path(tempfile.mkdtemp())
            self.addCleanup(shutil.rmtree, outside, True)
            saved = outside / "Doc.md.saved"
            saved.write_bytes(surface.read_bytes())
            self.assertFalse(
                saved.resolve().is_relative_to(Path.cwd().resolve()),
                "step 1 sends the operator's copy outside the tree, so `git add -A` "
                "cannot stage a full copy of a Layer-1 surface",
            )

            # STEP 2 -- diff it against the extract the refusal named. An
            # observation; what it needs is that BOTH files exist and differ.
            self.assertIn(self._EXTRACTED.as_posix(), retry.output)
            self.assertNotEqual(self._EXTRACTED.read_bytes(), saved.read_bytes())

            # STEP 3 -- restore the measured bytes over the surface.
            self.assertIn("restore the measured bytes over", retry.output)
            surface.write_bytes(self._EXTRACTED.read_bytes())

            # STEP 4 -- re-run the same command.
            completed = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(completed.exit_code, 0, msg=completed.output)

            # THE SEQUENCE ENDS AT A STATE THE CANONICAL LOADER ACCEPTS.
            reloaded = load_declaration(
                _DECLARATION_PATH, surface.read_bytes().decode("utf-8"), Path(".")
            )
            self.assertEqual(reloaded.sections["alpha-section"], "unowned")
            self.assertEqual(len(self._witnesses()), 1)
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())
            self.assertFalse(self._EXTRACTED.exists())

            # AND THE OPERATOR'S NEWER EDIT SURVIVED, where step 1 put it.
            self.assertEqual(
                saved.read_bytes(),
                oversized,
                "the edit the operator saved in step 1 is untouched by the recovery",
            )


@contextlib.contextmanager
def _failing_unlink(*names: str):
    """Fail `Path.unlink` for the named files; delegate every other removal.

    The failure is INJECTED rather than produced by `chmod`, matching the
    posture the unreadable-declaration fixture already uses: a read-only parent
    directory is a POSIX construction, and a storage fault on a removal is not
    a platform-specific event. Injection witnesses the behaviour on every
    supported platform instead of skipping the regression on Windows.
    """
    real_unlink = Path.unlink

    def unlink(self, missing_ok: bool = False):
        # Only an EXISTING file faults. A removal aimed at a file that is not
        # there is the expected-absence outcome cleanup treats as discharged,
        # and injecting a fault into it would fabricate a state the filesystem
        # never produces -- it also fires on the sweep that runs before any
        # write, which is the wrong invocation entirely.
        if self.name in names and self.exists():
            raise OSError(5, "injected removal failure")
        return real_unlink(self, missing_ok=missing_ok)

    with patch.object(Path, "unlink", unlink):
        yield


class TestRecoveryCleanupIsItsOwnObligation(unittest.TestCase):
    """Cleanup is the THIRD obligation, and an attempted unlink does not establish it.

    Operator ruling 2026-09-05, verbatim: *"Make cleanup recoverable. A
    journal-removal failure must preserve dependent recovery material and
    report the storage fault. Account for interruption between deletions,
    including their durability barriers. Retries must handle residual
    artifacts even when the journal is already absent."*

    Step-4b round-11 finding 2 measured the collapse: every removal sat under
    one `contextlib.suppress(OSError)`, so a failed journal unlink was
    indistinguishable from a completed one -- `journal_unlink_failed exit 0
    journal True snapshot False diagnostic_mentions_IO_fault False`. The
    journal survived while the material it gates was destroyed, and every
    later run recovered the same uncleared transition without ever naming the
    fault.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"
    _EXTRACTED = Path("Doc.md.unowning-recovery")

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    def _reach_state_d(self):
        """Witness the transition, then keep its journal: § Recovery Protocol state D."""
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
            first = _unown(self._runner, attestor="g0", reason="probe")
        self.assertEqual(first.exit_code, 0, msg=first.output)
        self.assertTrue(self._JOURNAL.exists())
        self.assertTrue(self._SNAPSHOT.exists())
        return first

    @covers("REQ-0.35.0-04-02")
    def test_a_failed_journal_removal_retains_its_dependents_and_reports_the_fault(
        self,
    ) -> None:
        """Would break if a failed unlink were suppressed as a completed one.

        The journal is what gates replay, so its dependents may never outlive
        it in the wrong direction: deleting the retained source while the
        journal survives leaves every later run recovering a transition whose
        reconciliation material is gone.
        """
        # output-contract: naming the storage fault IS the behaviour under test.
        with self._runner.isolated_filesystem():
            self._reach_state_d()

            with _failing_unlink("Doc.md.json.journal"):
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                retry.exit_code,
                0,
                f"a cleanup that did not happen is not a clean success: {retry.output}",
            )
            self.assertIn("recovery cleanup pending", retry.output.lower())
            self.assertIn("injected removal failure", retry.output)
            self.assertIn(
                "holding the file open",
                retry.output,
                "on Windows -- co-equal per `.claude/rules/cross-platform.md` -- "
                "`unlink` raises PermissionError while another process holds the "
                "file open, and the extract is the file `_reconciliation_sequence` "
                "step 2 tells the operator to open in a diff tool. A remedy list "
                "naming only permissions, disk space and read-only mounts sends "
                "them to check three conditions that are all fine",
            )
            self.assertTrue(self._JOURNAL.exists())
            self.assertTrue(
                self._SNAPSHOT.exists(),
                "the journal gates replay, so a journal that could not be removed "
                "keeps its dependent recovery material alive",
            )
            self.assertEqual(len(self._witnesses()), 1)

    @covers("REQ-0.35.0-04-02")
    def test_a_retry_sweeps_residue_left_after_the_journal_is_already_gone(self) -> None:
        """Would break if replay returned early on an absent journal.

        The deletions are not one atomic act: a crash between them -- or a
        removal that fails on the second file -- leaves recovery material with
        no journal to gate it. Nothing then reads that residue and nothing
        removes it, so it accumulates beside tracked Layer-1 files forever.
        """
        # output-contract: the already-unowned refusal identifies the run that swept.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with _failing_unlink("Doc.md.json.journal.source"):
                first = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(first.exit_code, 0, msg=first.output)
            self.assertFalse(
                self._JOURNAL.exists(),
                "the journal is removed first and its removal succeeded here",
            )
            self.assertTrue(
                self._SNAPSHOT.exists(),
                f"the dependent removal is what failed: {first.output}",
            )

            # An ordinary later invocation. It refuses for its own reason --
            # alpha-section is already unowned -- so nothing on the completion
            # path can be what clears the residue.
            later = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(later.exit_code, 1, msg=later.output)
            self.assertIn("already 'unowned'", later.output)
            self.assertFalse(
                self._SNAPSHOT.exists(),
                "a retry sweeps residual recovery material even when the journal "
                "it belonged to is already absent",
            )

    @covers("REQ-0.35.0-04-05")
    def test_an_interrupted_extraction_leaves_staging_residue_that_is_swept(self) -> None:
        """Would break if only the FINAL extract name were cleaned up.

        `write_bytes_atomically` stages `.<name>.<random>.tmp` in the target's
        directory before renaming, so an interrupted extraction leaves a copy
        of the measured source beside the surface under a name the final
        cleanup never mentions. Round 11 measured `EXTRACT_CRASH exit 99
        residue ['.doc.md.unowning-recovery.3.tmp'] RESIDUE_IS_MEASURED_SOURCE
        True`, retained across a successful recovery.
        """
        # output-contract: the failed-extraction next step IS the behaviour under test.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            def fail(root, target, record):
                raise OSError(5, "injected ledger append failure")

            with patch.object(unown_module, "_append_event_once", fail):
                interrupted = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(interrupted.exit_code, 2, msg=interrupted.output)

            surface = Path("Doc.md")
            surface.write_bytes(surface.read_bytes() + b"an editor appended this\n")

            # THE REAL WRITER NAMES THE RESIDUE. This used to fabricate
            # `.<name>.7.tmp`, a name chosen by the same author who wrote
            # `_staging_residue`'s glob -- so the test agreed with the consumer
            # by construction and could not fail if the PRODUCER's staging name
            # diverged from it. The interruption is now injected at
            # `staging.replace` inside `write_bytes_atomically`, so the file
            # left behind is the one the writer itself chose to name.
            with _crash_at_replace(self._EXTRACTED.name):
                refusal = _unown(self._runner, attestor="g0", reason="probe")

            staged = sorted(Path().glob(f".{self._EXTRACTED.name}.*.tmp"))
            self.assertEqual(
                len(staged),
                1,
                f"the real writer must leave exactly one staging file: {staged}",
            )
            residue = staged[0]
            self.assertRegex(
                residue.name,
                rf"^\.{re.escape(self._EXTRACTED.name)}\..+\.tmp$",
                "the producer stages beside its target as `.<name>.<unique>.tmp`; "
                "this is the shape `_staging_residue` must keep agreeing with",
            )
            self.assertEqual(refusal.exit_code, 2, msg=refusal.output)
            self.assertEqual(
                unown_module._surface_digest(residue.read_bytes()),
                json.loads(self._JOURNAL.read_bytes().decode("utf-8"))["surface_digest"],
                "the residue holds the MEASURED source bytes -- it is recovery "
                "material wearing a name nothing cleans up",
            )
            self.assertFalse(
                self._EXTRACTED.exists(),
                "the extraction did not complete, so no final extract exists",
            )
            self.assertNotIn(
                "diff that copy against",
                refusal.output,
                "an extraction that failed may not hand the operator a numbered "
                "sequence naming a path that does not exist",
            )

            # Reconcile from the retained source the refusal named, then re-run.
            self.assertIn(self._SNAPSHOT.as_posix(), refusal.output)
            surface.write_bytes(self._SNAPSHOT.read_bytes())
            completed = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(completed.exit_code, 0, msg=completed.output)
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())
            self.assertFalse(
                residue.exists(),
                "the staging half of the extraction-file family is cleaned up with "
                "the final half; a copy of the measured source may not survive the "
                "transition it belonged to",
            )


class TestRemoveIfPresentClassifiesAbsence(unittest.TestCase):
    """A target that is definitionally NOT THERE is a discharged obligation.

    `_remove_if_present` treats `FileNotFoundError` as the one outcome meaning
    "already gone" and escalates every other `OSError` to a storage-fault
    refusal. `NotADirectoryError` -- raised when a parent path component has
    been replaced by a FILE -- says the target cannot exist under that path at
    all, which is the same discharged state, reported by a different errno. An
    escalation there sends the operator to check disk space and mount health
    for a file the filesystem is telling them is not there.
    """

    @covers("REQ-0.35.0-04-02")
    def test_a_non_directory_parent_is_an_absence_never_a_storage_fault(self) -> None:
        """Would break if an errno meaning 'cannot exist' were reported as a fault."""

        def unlink(self: Path, missing_ok: bool = False):
            raise NotADirectoryError(20, "Not a directory")

        with patch.object(Path, "unlink", unlink):
            outcome = unown_module._remove_if_present(Path("a-file") / "child")

        self.assertIsNone(
            outcome,
            "a parent component that is a file makes the target definitionally "
            f"absent, which is the obligation already discharged: {outcome!r}",
        )


@contextlib.contextmanager
def _crash_at_replace(doomed: str):
    """Interrupt the REAL atomic writer at `staging.replace`, cleanup included.

    The residue must be produced by `write_bytes_atomically` itself, never
    hand-placed: a fabricated `.<name>.7.tmp` is chosen by the same author who
    reads `_staging_residue`'s glob, so a test built on one cannot fail when the
    producer's staging name and the consumer's pattern diverge -- which is the
    only divergence that matters here.

    The staging cleanup is faulted alongside the rename because that is the
    compound condition which actually leaves residue on disk: `os.replace`
    failing on its own is followed by `staging.unlink()` under
    `contextlib.suppress(OSError)`, and a directory that has gone read-only
    fails both.
    """
    real_replace = Path.replace
    real_unlink = Path.unlink

    def replace(self: Path, target):
        if Path(target).name == doomed:
            raise OSError(5, "injected write interruption")
        return real_replace(self, target)

    def unlink(self: Path, missing_ok: bool = False):
        if self.name.startswith(f".{doomed}.") and self.name.endswith(".tmp"):
            raise OSError(5, "injected staging cleanup failure")
        return real_unlink(self, missing_ok=missing_ok)

    with patch.object(Path, "replace", replace), patch.object(Path, "unlink", unlink):
        yield


class TestOrphanResidueSweepReportsOnlyWhatItObserved(unittest.TestCase):
    """A FRESH run that finds only orphan residue has completed NOTHING.

    Reached by a crash during `_commit_transition`'s FIRST
    `write_bytes_atomically` -- the retention of the measured source, which
    happens before the journal naming its digest exists. What survives is a
    staging file holding a complete copy of the measured source, with no
    journal, no declaration change and no ledger witness. § Recovery Protocol
    has no state for it, because nothing was un-owned.

    The refusal reached from that sweep asserted all three of "the un-owning of
    <surface> is complete", "exactly two are discharged -- transition
    witnessed; source reconciled" and "§ Recovery Protocol state D with cleanup
    outstanding" -- then contradicted itself, saying the journal "keeps gating
    every un-owning" one sentence after saying it was "already gone". Each is a
    premise the run cannot know, which is the class this module already
    corrected once: `_refuse_forged_journal`'s docstring says verbatim that it
    dropped its own "nothing written" clause because *"a premise it cannot know
    is the defect, whichever direction it points."*

    THE EXIT CODE IS ASSERTED, because the question is settled. It was open
    when this test was authored -- refuse on unrelated orphan residue, or sweep
    best-effort and continue -- and the operator ruling of 2026-09-05 answered
    it: *"failed removal of unrelated orphan residue may warn and permit fresh
    work"*. Leaving the code unpinned after that would let the path silently
    revert to refusing while every prose assertion here still passed.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT_NAME = "Doc.md.json.journal.source"

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-02")
    def test_the_orphan_warning_claims_no_transition_no_witness_and_no_state_d(self) -> None:
        """Would break if a sweep asserted a completion the run never observed."""
        # output-contract: what the report may CLAIM is the behaviour under test.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            declaration_before = _DECLARATION_PATH.read_bytes()
            ledger_before = _ledger_events()

            with _crash_at_replace(self._SNAPSHOT_NAME):
                crashed = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(crashed.exit_code, 2, msg=crashed.output)

            residue = sorted(_DECLARATION_PATH.parent.glob(f".{self._SNAPSHOT_NAME}.*.tmp"))
            self.assertEqual(
                len(residue), 1, f"the crash must leave REAL staging residue: {residue}"
            )
            self.assertEqual(
                residue[0].read_bytes(),
                Path("Doc.md").read_bytes(),
                "the residue is a complete copy of the measured source bytes",
            )
            self.assertFalse(self._JOURNAL.exists(), "the journal write was never reached")
            self.assertEqual(
                _DECLARATION_PATH.read_bytes(),
                declaration_before,
                "nothing was un-owned: the declaration is byte-unchanged",
            )
            self.assertEqual(_ledger_events(), ledger_before, "no witness exists")

            with _failing_unlink(residue[0].name):
                swept = _unown(self._runner, attestor="g0", reason="probe")

            for claim in (
                "is complete",
                "exactly two are discharged",
                "transition witnessed; source reconciled",
                "state D",
                "the journal keeps gating",
                "the next run sweeps it",
                "the transition itself is sound",
            ):
                self.assertNotIn(
                    claim,
                    swept.output,
                    f"nothing in this run establishes {claim!r}: no journal, no "
                    "declaration change, no witness",
                )
            self.assertIn(
                "no journal",
                swept.output.lower(),
                "an orphan sweep reports what it observed -- the journal's ABSENCE "
                "is the whole of what it knows",
            )
            self.assertIn(
                residue[0].as_posix(),
                swept.output,
                "the operator cannot act on material the report does not name",
            )
            self.assertEqual(
                swept.exit_code,
                0,
                "an EARLIER run's residue does not make THIS run fail (operator "
                f"ruling 2026-09-05): {swept.output}",
            )


class TestStagingResidueGlobIsLiteral(unittest.TestCase):
    """A surface's FILENAME is data to the sweep's glob, never a pattern.

    `_staging_residue` interpolates the target's name into a `glob` pattern, so
    a filename carrying `[`, `]`, `*` or `?` -- all legal on every supported
    platform -- becomes a character class or a wildcard. The sweep then looks
    for a name no producer ever writes and silently finds nothing, while what
    it missed is a COMPLETE COPY of the measured source bytes sitting beside a
    tracked surface. This sweep is the only thing that removes it.

    The decoy is what makes the assertion sharp: an unescaped `a[1].md` pattern
    does not merely fail to match its own residue, it MATCHES A DIFFERENT FILE
    (`a1.md`'s), so an unescaped sweep would delete a stranger's residue and
    keep its own.
    """

    @covers("REQ-0.35.0-04-05")
    def test_a_metacharacter_in_the_surface_name_is_matched_literally(self) -> None:
        """Would break if a surface filename were interpolated into a glob unescaped."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a[1].md.unowning-recovery"
            residue = target.with_name(f".{target.name}.7.tmp")
            residue.write_bytes(b"the measured source bytes")
            decoy = target.with_name(".a1.md.unowning-recovery.7.tmp")
            decoy.write_bytes(b"a different surface's residue")

            self.assertEqual(
                unown_module._staging_residue(target),
                [residue],
                "the sweep must find ITS OWN staging residue and nobody else's; "
                "an unescaped name turns `[1]` into a character class",
            )


class TestJournalStorageFaultIsNotForgery(unittest.TestCase):
    """A journal that cannot be READ is a storage fault, never evidence of forgery.

    `_journal_record_or_refuse` caught `(OSError, ValueError)` on one read and
    routed both to `_refuse_forged_journal`, whose prose is forgery-class: it
    says the journal "cannot be proven to continue the live on-disk
    predecessor" and sends the operator to compare `floor_event_id` against the
    ledger. A permission flip or an EIO on an EXISTING journal is neither
    unreadable-because-forged nor malformed -- its remedy is restoring read
    access and re-running, and that sentence appeared nowhere.

    Its sibling `_on_disk_declaration_or_refuse` already draws exactly this
    line for the declaration, and says why: an `OSError` on a file that EXISTS
    is transient, not a statement about its contents.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-02")
    def test_an_unreadable_existing_journal_names_the_storage_fault(self) -> None:
        """Would break if a storage fault were reported as a forged journal.

        The read failure is INJECTED rather than produced by `chmod`, so the
        posture is witnessed on every supported platform.
        """
        # output-contract: the remedy the prose names IS the behaviour under test.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            def fail(root, target, record):
                raise OSError(5, "injected ledger append failure")

            with patch.object(unown_module, "_append_event_once", fail):
                interrupted = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(interrupted.exit_code, 2, msg=interrupted.output)

            real_read_text = Path.read_text

            def read_text(self, *args, **kwargs):
                if self.name == "Doc.md.json.journal":
                    raise OSError(13, "injected journal read failure")
                return real_read_text(self, *args, **kwargs)

            with patch.object(Path, "read_text", read_text):
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 2, msg=retry.output)
            self.assertIn("injected journal read failure", retry.output)
            self.assertNotIn(
                "unreadable or malformed",
                retry.output,
                "a journal that could not be READ has not been shown to be "
                "malformed; the forgery prose asserts a premise this run cannot "
                "hold, and sends the operator to a state comparison instead of "
                "to the fault",
            )
            self.assertIn(
                "Restore read access",
                retry.output,
                "the remedy for a storage fault is restoring read access and "
                "re-running -- named nowhere by the forgery refusal",
            )
            self.assertTrue(self._JOURNAL.exists())

    @covers("REQ-0.35.0-04-02")
    def test_a_malformed_journal_is_still_refused_as_forged(self) -> None:
        """Would break if the storage-fault arm swallowed the forgery arm too.

        The distinction cuts both ways: content that does not parse IS a claim
        about the journal's contents, and it keeps the refusal that enumerates
        the interruption states.
        """
        # output-contract: the forgery refusal's own prose is the sibling contract.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            self._JOURNAL.parent.mkdir(parents=True, exist_ok=True)
            self._JOURNAL.write_text("{not json at all", encoding="utf-8")

            result = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(result.exit_code, 2, msg=result.output)
            self.assertIn("unreadable or malformed", result.output)
            self.assertTrue(self._JOURNAL.exists())


class TestLegacyJournalStillObservesTheLiveSurface(unittest.TestCase):
    """A journal predating the `surface_digest` binding is not an unguarded one.

    Both digest bindings return early on a journal carrying no
    `surface_digest`: `_refuse_source_changed_since_measurement` cannot speak
    about a surface the journal never versioned, and
    `_refuse_clean_success_on_a_moved_surface` cannot either. Their docstrings
    say the downstream coherence guards still can -- and on the settled
    (state D) path they did NOT, because the `settled` short-circuit skips
    `_refuse_incoherent_landed_state` as well. The section-id coverage check
    and the span-versus-floor check therefore never ran, and recovery cleared
    every artifact and exited 0 having observed the live surface through no
    check at all.

    The existing legacy-journal coverage exercises the UNSETTLED path, where
    the coherence gate runs regardless -- so the asymmetry was invisible.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _reach_state_d_with_a_legacy_journal(self) -> None:
        """Witness the transition, keep the journal, then strip its digest.

        Stripping is legitimate rather than adversarial: `_mint_event_id`
        digests the transition's identity, floors, attestation and parent --
        never `surface_digest` -- so a journal written before the round-7
        binding re-mints its own id exactly like this one and reaches every
        check below unchanged.
        """
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
            first = _unown(self._runner, attestor="g0", reason="probe")
        self.assertEqual(first.exit_code, 0, msg=first.output)
        record = json.loads(self._JOURNAL.read_bytes().decode("utf-8"))
        del record["surface_digest"]
        self._JOURNAL.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    @covers("REQ-0.35.0-04-02")
    def test_a_restructured_surface_is_still_refused_under_a_legacy_journal(self) -> None:
        """Would break if state D cleared up without observing the live surface.

        A section RENAMED by an ordinary editor leaves the declaration no
        longer covering the surface -- the exact condition round-7 finding 2
        added the coverage check for. With no `surface_digest` to bind against,
        that check is the ONLY thing standing between this state and a clean
        exit that destroys the recovery material.
        """
        # output-contract: the coverage refusal's own words identify the guard.
        with self._runner.isolated_filesystem():
            self._reach_state_d_with_a_legacy_journal()
            surface = Path("Doc.md")
            surface.write_bytes(surface.read_bytes().replace(b"## Beta Section", b"## Gamma Bit"))

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                retry.exit_code,
                0,
                "a declaration that no longer covers its surface may not be "
                f"reported as a clean recovery: {retry.output}",
            )
            self.assertIn("does not cover the surface", retry.output)
            self.assertTrue(
                self._JOURNAL.exists(),
                "a refusal RETAINS the recovery material -- the transition stays "
                "completable once the surface is reconciled",
            )
            self.assertTrue(self._SNAPSHOT.exists())

    @covers("REQ-0.35.0-04-02")
    def test_an_unchanged_surface_under_a_legacy_journal_still_clears_up(self) -> None:
        """Would break if the added guard refused a state it has no quarrel with.

        The fence must not become a blanket refusal: a legacy journal over an
        unchanged surface is state D with nothing wrong, and it still completes
        and clears every artifact.
        """
        with self._runner.isolated_filesystem():
            self._reach_state_d_with_a_legacy_journal()

            retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(retry.exit_code, 0, msg=retry.output)
            self.assertEqual(
                len([e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]),
                1,
                "the witness is preserved, never duplicated",
            )
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())


class _StandaloneBarrierProbe:
    """Mutable observation of the injected standalone directory-barrier fault.

    A typed object rather than a dict because `last_op` routes the injection
    while `attempts` is the assertion subject: "the run refused" is also true
    of a run that never attempted the barrier at all, which is exactly the
    state this fixture exists to distinguish.
    """

    def __init__(self) -> None:
        self.last_op: str | None = None
        self.attempts: int = 0


@contextlib.contextmanager
def _failing_standalone_directory_barrier(code: int = errno.EIO):
    """Fail a directory fsync that is NOT the tail of an atomic write.

    *code* is the injected errno, because the errno is what separates a
    TRANSIENT fault a retry can clear from a filesystem that cannot fsync a
    directory AT ALL. Defaulting it to `EIO` keeps the transient case the
    fixture's ordinary use.

    `write_bytes_atomically` fsyncs the file, renames it, and only THEN syncs
    the parent directory -- so every WRITE-side barrier is immediately preceded
    by its own `os.replace`. A directory fsync reached with no replace before
    it is therefore a STANDALONE barrier and nothing else: the removal-side
    boundary that commits an unlink's directory entry.

    Routing on the last filesystem operation rather than on a call count is
    what keeps the injected fault pinned to that one window: the transaction
    writes a source snapshot, a journal and a declaration through the same
    atomic writer, so counting directory syncs would move the fault whenever
    the number of prior writes changed.
    """
    probe = _StandaloneBarrierProbe()
    real_fsync = os.fsync
    real_replace = os.replace
    real_unlink = Path.unlink

    def spy_replace(src, dst, *args, **kwargs):
        outcome = real_replace(src, dst, *args, **kwargs)
        probe.last_op = "replace"
        return outcome

    def spy_unlink(self: Path, missing_ok: bool = False):
        outcome = real_unlink(self, missing_ok=missing_ok)
        probe.last_op = "unlink"
        return outcome

    def barrier(fd: int):
        if stat.S_ISDIR(os.fstat(fd).st_mode) and probe.last_op != "replace":
            probe.attempts += 1
            msg = "injected standalone directory barrier failure"
            raise OSError(code, msg)
        return real_fsync(fd)

    with (
        patch("os.replace", side_effect=spy_replace),
        patch.object(Path, "unlink", spy_unlink),
        patch("gzkit.content.ownership.os.fsync", side_effect=barrier),
    ):
        yield probe


class TestJournalAbsenceIsMadeDurableBeforeDependentsMove(unittest.TestCase):
    """The journal's ABSENCE is durable before any dependent is deleted or reused.

    Operator ruling 2026-09-05, verbatim: *"Establish durable journal absence
    before deleting or reusing dependent recovery files, including when the
    journal is already absent on entry. Failure to establish that boundary
    preserves the files and exits non-zero."*

    The invariant relied upon is CROSS-FILE ORDERING -- *"a journal that
    survives keeps all of its material"* -- not one removal's own durability.
    A directory-entry removal is not committed until the parent directory is
    fsynced, so with no barrier between the journal's unlink and its
    dependents' unlinks nothing forbids the dependents' entries being committed
    while the journal's is not. That inversion is JOURNAL BACK, RETAINED SOURCE
    GONE: Step-4b round-11 finding 2 restated by the filesystem instead of by
    the code, and aggravated because the artifacts span two directories --
    journal and journal source under `.gzkit/ownership/`, the extract beside
    the surface.

    THE INVARIANT IS POSIX-ONLY, AND SAYING SO IS PART OF STATING IT. Windows
    has no directory handle to sync, so `commit_directory_entry` is a no-op
    there BY CONSTRUCTION and the ordering rests on statement order alone --
    which is why these tests skip off POSIX rather than assert an attempt that
    the platform never makes. A cross-platform claim would be false on a third
    of the supported platforms (`.claude/rules/cross-platform.md`).
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"
    _EXTRACT = Path("Doc.md.unowning-recovery")

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_a_failed_barrier_on_entry_preserves_the_orphan_and_refuses(self) -> None:
        """Would break if an entry with no journal deleted or REUSED a dependent.

        `_commit_transition` writes the retained source at the very start of a
        fresh transaction, so an entry that finds no journal both DELETES the
        old dependents and REUSES one of their paths. Both moves rest on the
        journal being durably absent, and on this path nothing ever removed a
        journal -- so the boundary has to be established rather than inherited.
        """
        # output-contract: the refusal names the barrier as what failed.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            self._EXTRACT.write_bytes(b"orphan recovery material\n")
            declaration_before = _DECLARATION_PATH.read_bytes()

            with _failing_standalone_directory_barrier() as probe:
                refused = _unown(self._runner, attestor="g0", reason="probe")

            self.assertGreater(probe.attempts, 0, "the boundary must be ATTEMPTED, not assumed")
            self.assertNotEqual(
                refused.exit_code,
                0,
                f"an unestablished durability boundary is not a clean run: {refused.output}",
            )
            self.assertTrue(
                self._EXTRACT.exists(),
                "a failed boundary preserves the dependent recovery files",
            )
            self.assertFalse(
                self._SNAPSHOT.exists(),
                "no dependent recovery path may be REUSED before the boundary holds",
            )
            self.assertFalse(self._JOURNAL.exists())
            self.assertEqual(_DECLARATION_PATH.read_bytes(), declaration_before)
            self.assertEqual(self._witnesses(), [])
            self.assertIn("durab", refused.output.lower())

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_a_failed_barrier_after_the_journal_removal_preserves_its_dependents(self) -> None:
        """Would break if dependents were unlinked while the journal's absence was unconfirmed.

        The unlink makes the journal INVISIBLE; the barrier is what makes it
        GONE. Between the two, a crash can leave the journal's directory entry
        intact while the dependents' removals commit -- a surviving journal
        whose retained source no longer exists, which every later run then
        replays and cannot reconcile.
        """
        # output-contract: the refusal names the barrier as what failed.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 0, msg=first.output)
            self.assertTrue(self._SNAPSHOT.exists())

            with _failing_standalone_directory_barrier() as probe:
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertGreater(probe.attempts, 0, "the boundary must be ATTEMPTED, not assumed")
            self.assertNotEqual(
                retry.exit_code,
                0,
                f"an unestablished durability boundary is not a clean run: {retry.output}",
            )
            self.assertTrue(
                self._SNAPSHOT.exists(),
                "the dependent recovery material outlives an unconfirmed journal removal",
            )
            self.assertIn("durab", retry.output.lower())
            self.assertEqual(len(self._witnesses()), 1)


class TestOrphanResidueWarnsAndPermitsFreshWork(unittest.TestCase):
    """Unrelated orphan residue that cannot be removed WARNS; it does not refuse.

    Operator ruling 2026-09-05, verbatim: *"After that boundary is established,
    failed removal of unrelated orphan residue may warn and permit fresh work.
    Normal declaration validation and persistence of the new transaction's
    recovery snapshot remain mandatory."* And: *"Keep orphan warnings distinct
    through finalization; do not reclassify the same old leftover as a failure
    of the new transaction's cleanup."*

    The distinction the ruling draws is between a fault this run CAUSED and a
    leftover it merely FOUND. Reporting the second as the first is the mirror
    of the false-premise defect `_warn_orphan_residue_pending` already
    corrected: a report may assert only what its own run established.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"
    _EXTRACT = Path("Doc.md.unowning-recovery")

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    def _seed_with_an_unremovable_orphan(self) -> None:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        self._EXTRACT.write_bytes(b"orphan recovery material\n")

    @covers("REQ-0.35.0-04-05")
    def test_a_failed_orphan_removal_still_persists_the_new_recovery_snapshot(self) -> None:
        """Would break if a warning bought a shortcut past the retained-source write.

        The warning concerns material an EARLIER run left behind. It says
        nothing about this transaction, which still owes § Recovery Protocol
        state E its measured source -- a fresh journal on disk without the
        bytes it names is the state round-10 finding 2 measured as
        unrecoverable.
        """
        # output-contract: the warning naming the un-removed orphan is the behaviour.
        with self._runner.isolated_filesystem():
            self._seed_with_an_unremovable_orphan()

            with (
                patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None),
                _failing_unlink(self._EXTRACT.name),
            ):
                fresh = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(fresh.exit_code, 0, msg=fresh.output)
            self.assertIn(self._EXTRACT.as_posix(), fresh.output)
            self.assertIn("injected removal failure", fresh.output)
            self.assertIn("warning", fresh.output.lower())
            self.assertTrue(
                self._SNAPSHOT.exists(),
                "the fresh transaction still retains its own measured source",
            )
            self.assertEqual(
                self._SNAPSHOT.read_bytes(),
                Path("Doc.md").read_bytes(),
                "the retained snapshot is the bytes this transition measured",
            )
            self.assertEqual(len(self._witnesses()), 1)

    @covers("REQ-0.35.0-04-05")
    def test_a_warning_never_skips_declaration_validation(self) -> None:
        """Would break if the warn path short-circuited `_load_declaration_or_exit`.

        A declaration whose `floor_event_id` resolves to no ledger event is
        exactly what the loader exists to refuse. Permitting fresh work after a
        warning must mean the ordinary path resumes, never that it is skipped.
        """
        # output-contract: which refusal the run reaches is the behaviour under test.
        with self._runner.isolated_filesystem():
            self._seed_with_an_unremovable_orphan()
            raw = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            raw["floor_event_id"] = "section-ownership-genesis-Doc.md-unwitnessed"
            _DECLARATION_PATH.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

            with _failing_unlink(self._EXTRACT.name):
                refused = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(refused.exit_code, 1, msg=refused.output)
            self.assertIn("resolves to no event", refused.output)
            self.assertIn(
                self._EXTRACT.as_posix(),
                refused.output,
                "the orphan warning is still reported alongside the refusal",
            )
            self.assertEqual(self._witnesses(), [])

    @covers("REQ-0.35.0-04-02")
    def test_an_orphan_warned_on_entry_is_not_this_transactions_cleanup_failure(self) -> None:
        """Would break if finalization reclassified the same leftover as this run's fault.

        The post-completion sweep attempts the same removal and meets the same
        storage condition. Reporting it there makes the new transaction answer
        for a fault it did not cause -- and turns a completed, witnessed
        un-owning into a non-zero exit on the strength of an old leftover.
        """
        # output-contract: what finalization may CLAIM is the behaviour under test.
        with self._runner.isolated_filesystem():
            self._seed_with_an_unremovable_orphan()

            with _failing_unlink(self._EXTRACT.name):
                fresh = _unown(self._runner, attestor="g0", reason="probe")

            self.assertEqual(
                fresh.exit_code,
                0,
                f"an old leftover is not a failure of the new transaction: {fresh.output}",
            )
            self.assertNotIn("recovery cleanup pending", fresh.output.lower())
            self.assertNotIn("could not be cleared", fresh.output)
            self.assertFalse(
                self._JOURNAL.exists(),
                "this transaction's own recovery material was cleared normally",
            )
            self.assertFalse(self._SNAPSHOT.exists())
            self.assertEqual(len(self._witnesses()), 1)

    @covers("REQ-0.35.0-04-02")
    def test_this_transactions_own_cleanup_failure_is_still_non_success(self) -> None:
        """Would break if the carried warning suppressed the current run's own fault.

        The retained source at `<surface>.json.journal.source` is REUSED by
        every fresh transaction, so a removal failure there at finalization is
        this run's material and this run's fault -- even when an unrelated
        orphan was warned about on the same invocation. A carried warning that
        swallowed it would be a blanket suppression wearing the ruling's name.
        """
        # output-contract: naming the storage fault IS the behaviour under test.
        with self._runner.isolated_filesystem():
            self._seed_with_an_unremovable_orphan()

            with _failing_unlink(self._EXTRACT.name, self._SNAPSHOT.name):
                fresh = _unown(self._runner, attestor="g0", reason="probe")

            self.assertNotEqual(
                fresh.exit_code,
                0,
                f"a cleanup that did not happen is not a clean success: {fresh.output}",
            )
            self.assertIn("recovery cleanup pending", fresh.output.lower())
            self.assertIn(self._SNAPSHOT.as_posix(), fresh.output)
            self.assertTrue(self._SNAPSHOT.exists())
            self.assertEqual(len(self._witnesses()), 1)


class TestEntryBoundarySweepIsNotClaimedAway(unittest.TestCase):
    """A refusal reached AFTER the entry sweep may not claim nothing was touched.

    `_establish_recovery_boundary` runs inside the lock, before the declaration
    is even loaded, and on a journal-absent entry it UNLINKS every dependent
    that outlived the missing journal. Four refusals sit downstream of it --
    unknown section, already-unowned section, an unreadable declaration and a
    foreign declaration snapshot -- and each printed a bare "nothing written".

    That is the false-premise class this module already polices itself on:
    `_refuse_forged_journal`'s docstring says verbatim that it dropped its own
    "nothing written" clause because *"a premise it cannot know is the defect,
    whichever direction it points."* Here the premise is not merely unknowable,
    it is FALSE whenever the sweep found anything -- the operator is told the
    run was inert by the same message that follows a real deletion.

    What the refusals may still say is the part they establish: no declaration
    byte changed and no witness was appended.
    """

    _EXTRACT = Path("Doc.md.unowning-recovery")
    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _seed_with_an_orphan_the_sweep_will_remove(self) -> None:
        _seed_surface()
        _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
        self._EXTRACT.write_bytes(b"orphan recovery material\n")

    def _assert_swept_then_refused(self, result, declaration_before: bytes) -> None:
        # The swept path is DERIVED from the production target rather than read
        # off this class's constant, so the assertion cannot drift from the path
        # the sweep actually clears — the same producer-derived discipline the
        # ignore-roster test needed after a hand-written name let a rule go
        # unwitnessed.
        swept = unown_module._target_for(Path.cwd(), "Doc.md").recovery_extract_path
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertFalse(
            swept.exists(),
            "the entry boundary sweep removes the orphan before this refusal is reached",
        )
        self.assertNotIn(
            "nothing written",
            result.output.lower(),
            "the sweep deleted a file one statement earlier: an inert-run claim is "
            f"false here, not merely unproven -- {result.output}",
        )
        self.assertIn(
            "entry boundary",
            result.output.lower(),
            "the refusal names what may already have been removed rather than denying it happened",
        )
        self.assertEqual(
            _DECLARATION_PATH.read_bytes(),
            declaration_before,
            "what the refusal MAY still claim: no declaration byte changed",
        )

    @covers("REQ-0.35.0-04-05")
    def test_the_unknown_section_refusal_does_not_deny_the_sweep_that_preceded_it(self) -> None:
        """Would break if an inert-run claim survived a sweep that deleted a file."""
        # output-contract: what the refusal may CLAIM is the behaviour under test.
        with self._runner.isolated_filesystem():
            self._seed_with_an_orphan_the_sweep_will_remove()
            declaration_before = _DECLARATION_PATH.read_bytes()
            ledger_before = _ledger_events()

            refused = _unown(self._runner, section="no-such-section", attestor="g0", reason="p")

            self._assert_swept_then_refused(refused, declaration_before)
            self.assertEqual(_ledger_events(), ledger_before, "no witness was appended")

    @covers("REQ-0.35.0-04-05")
    def test_the_already_unowned_refusal_does_not_deny_the_sweep_that_preceded_it(self) -> None:
        """Would break if the second downstream refusal kept the claim the first dropped.

        Both refusals sit below the same sweep, so repairing one and leaving the
        other is the round-8 finding-1 asymmetry: the operator meets whichever
        message their invocation happens to reach.
        """
        # output-contract: what the refusal may CLAIM is the behaviour under test.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="unowned")
            self._EXTRACT.write_bytes(b"orphan recovery material\n")
            declaration_before = _DECLARATION_PATH.read_bytes()

            refused = _unown(self._runner, attestor="g0", reason="probe")

            self._assert_swept_then_refused(refused, declaration_before)


class TestAnUnavailableBarrierIsDisclosedNotRefusedForever(unittest.TestCase):
    """A barrier the filesystem CANNOT provide is disclosed; it is not a refusal.

    `commit_directory_entry` is already a no-op on Windows, where there is no
    directory handle to sync -- the barrier is unavailable BY CONSTRUCTION and
    the command runs. A POSIX export that answers `fsync` on a directory with
    `EINVAL` is the same disposition arriving through an errno instead of
    through `os.name`, and treating it as a fault made EVERY invocation exit 2,
    including a first-ever run with no journal and nothing to sweep.

    The remedy prose is what makes that unrecoverable rather than merely
    strict: it told the operator to fix *"an export (NFS, a network share) that
    cannot fsync a directory"* and re-run, which is not a condition a re-run --
    or the operator -- can clear. A remedy naming a fault its own retry cannot
    reach is a promise the command does not keep.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _witnesses(self) -> list[dict]:
        return [e for e in _ledger_events() if e["event"] == "section_ownership_unowned"]

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_a_filesystem_that_cannot_fsync_a_directory_still_un_owns_and_says_so(self) -> None:
        """Would break if an unavailable barrier bricked the command on that filesystem."""
        # output-contract: the disclosure accompanying the completed run is the behaviour.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with _failing_standalone_directory_barrier(errno.EINVAL) as probe:
                run = _unown(self._runner, attestor="g0", reason="probe")

            self.assertGreater(probe.attempts, 0, "the boundary must be ATTEMPTED, not assumed")
            self.assertEqual(
                run.exit_code,
                0,
                "a barrier this filesystem cannot provide is the Windows disposition "
                f"reached by errno; refusing it forever bricks the raise-path: {run.output}",
            )
            self.assertEqual(len(self._witnesses()), 1, "the un-owning landed")
            self.assertFalse(self._JOURNAL.exists())
            self.assertFalse(self._SNAPSHOT.exists())
            self.assertIn("cannot fsync", run.output.lower())
            self.assertIn(
                "warning",
                run.output.lower(),
                "an ordering guarantee this run could not establish is DISCLOSED, "
                "never passed over in silence",
            )

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_a_transient_barrier_fault_still_refuses_and_offers_a_reachable_remedy(self) -> None:
        """Would break if the unavailable-barrier path swallowed a fixable fault too.

        `EIO` is a failing disk, not a filesystem without the operation. The
        boundary is genuinely unestablished, everything downstream rests on it,
        and a retry after the disk is replaced DOES clear it -- so this stays a
        refusal, and its remedy names only conditions a retry can reach.
        """
        # output-contract: which remedies the refusal offers is the behaviour under test.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)

            with _failing_standalone_directory_barrier(errno.EIO) as probe:
                refused = _unown(self._runner, attestor="g0", reason="probe")

            self.assertGreater(probe.attempts, 0)
            self.assertEqual(refused.exit_code, 2, msg=refused.output)
            self.assertEqual(self._witnesses(), [])
            self.assertNotIn(
                "cannot fsync a directory",
                refused.output,
                "a remedy the operator cannot apply, on a path whose only advice is "
                f"to re-run, is a promise the command does not keep: {refused.output}",
            )


class TestRetryProseMatchesWhatTheRetryDoes(unittest.TestCase):
    """A refusal describes the retry the command will actually perform.

    `_refuse_unbarriered_journal_removal` fires after the journal's `unlink`
    succeeded and its barrier did not, and it promised *"each retry re-attempts
    the removal and the barrier together"*. On that retry the journal is
    already gone, so `_establish_recovery_boundary` takes the journal-ABSENT
    branch: the barrier is re-attempted, the removal is not, and a persistent
    fault surfaces through `_refuse_unbarriered_orphan_boundary` -- a different
    refusal with different prose. The operator is told to expect one message
    and shown another.
    """

    _JOURNAL = _DECLARATION_PATH.parent / "Doc.md.json.journal"
    _SNAPSHOT = _DECLARATION_PATH.parent / "Doc.md.json.journal.source"

    def setUp(self) -> None:
        self._runner = CliRunner()

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_the_unbarriered_removal_refusal_does_not_promise_a_second_removal(self) -> None:
        """Would break if the refusal promised a retry step the next run cannot take."""
        # output-contract: what the refusal promises about the retry is the behaviour.
        with self._runner.isolated_filesystem():
            _seed_surface()
            _seed_declaration(alpha="corpus-owned", floor=_SEED_FLOOR)
            with patch.object(unown_module, "_clear_recovery_state", lambda target, **_: None):
                first = _unown(self._runner, attestor="g0", reason="probe")
            self.assertEqual(first.exit_code, 0, msg=first.output)

            with _failing_standalone_directory_barrier() as probe:
                retry = _unown(self._runner, attestor="g0", reason="probe")

            self.assertGreater(probe.attempts, 0)
            self.assertEqual(retry.exit_code, 2, msg=retry.output)
            self.assertFalse(
                self._JOURNAL.exists(),
                "the unlink SUCCEEDED -- only its barrier did not, which is why a "
                "later run has no removal left to re-attempt",
            )
            self.assertNotIn(
                "re-attempts the removal and the barrier together",
                retry.output,
                "the journal is already unlinked, so the next run re-attempts the "
                f"barrier ALONE, through a different refusal: {retry.output}",
            )


if __name__ == "__main__":
    unittest.main()
