"""gz content own command tests -- the governed `unowned -> corpus-owned` transition (GHI #974).

ADR-0.35.0 § Decision 3 declares a two-directional ownership seam and a
decrease-only ratchet; OBPI-0.35.0-04 shipped the raise direction only. The
lowering move that CHANGES THE MAP -- a section becoming corpus-owned once the
corpus actually carries its content -- had no governed path, so an overgrown
unowned section could never be brought back under its floor except by the
hand-edit the ratchet exists to forbid.

The fixture reproduces that state exactly: a declaration witnessed at one
surface, then the surface grows inside an `unowned` section, so the loader
refuses and `gz content unown` refuses too. Everything here asserts through
the REAL loader (`load_declaration`) and the public CLI.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import gzkit.commands.content.unown as unown_module
from gzkit.cli.main import main
from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.ownership import (
    OwnershipLoadError,
    load_declaration,
    measure_section_spans,
    sections_digest,
)
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.ledger import Ledger
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _isolated_git_env

_SEED_SURFACE_TEXT = (
    "# Doc Title\n"
    "preamble text under the H1\n"
    "## Alpha Section\n"
    "alpha body line one\n"
    "alpha body line two\n"
    "## Beta Section\n"
    "beta body\n"
)

#: The same surface after the two lift pointers of GHI #933 grew an UNOWNED
#: section: a blockquote pointer, an H3 sub-heading (structure, not canon) and
#: a numbered bold claim -- the three line shapes AGENTS.md actually carries.
_GROWN_SURFACE_TEXT = (
    "# Doc Title\n"
    "preamble text under the H1\n"
    "## Alpha Section\n"
    "alpha body line one\n"
    "alpha body line two\n"
    "\n"
    "> See [alpha rationale](docs/alpha.md#why) for the lifted rationale.\n"
    "\n"
    "### Alpha operative claims\n"
    "\n"
    "1. **Alpha claim one.** The detail of claim one.\n"
    "## Beta Section\n"
    "beta body\n"
)

#: Corpus texts covering every content line of the grown alpha section, in the
#: capture convention (leading structural marker stripped, every other byte exact).
_ALPHA_COVERAGE = (
    "alpha body line one",
    "alpha body line two",
    "See [alpha rationale](docs/alpha.md#why) for the lifted rationale.",
    "**Alpha claim one.** The detail of claim one.",
)

_DECLARATION_PATH = Path(".gzkit") / "ownership" / "Doc.md.json"
_CORPUS_PATH = Path(".gzkit") / "corpus" / "Doc.md.jsonl"
_LEDGER_PATH = Path(".gzkit") / "ledger.jsonl"
_JOURNAL_PATH = Path(".gzkit") / "ownership" / "Doc.md.json.journal"
_GENESIS_ID = "section-ownership-genesis-Doc.md-own"


def _write_surface(text: str) -> None:
    """Bytes, never text mode -- the floor counts PHYSICAL bytes (GHI #958)."""
    Path("Doc.md").write_bytes(text.encode("utf-8"))


def _seed_declaration(sections: dict[str, str], *, surface_text: str = _SEED_SURFACE_TEXT) -> int:
    """Declare *sections*, witnessed by a real genesis event at the seed floor."""
    spans = measure_section_spans(surface_text)
    floor = sum(span for sid, span in spans.items() if sections[sid] == "unowned")
    _DECLARATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    _DECLARATION_PATH.write_text(
        json.dumps(
            {
                "surface": "Doc.md",
                "sections": sections,
                "unowned_byte_floor": floor,
                "measured_at": "2026-09-07T00:00:00Z",
                "floor_event_id": _GENESIS_ID,
            }
        ),
        encoding="utf-8",
    )
    emit_section_ownership_genesis(
        Path("."), _GENESIS_ID, "Doc.md", sections_digest(sections), floor
    )
    return floor


def _entry(
    index: int, text: str, *, section: str = "alpha-section", **overrides: object
) -> CorpusEntry:
    base: dict[str, object] = {
        "id": f"corpus-{section}-{index:02d}",
        "surface": "Doc.md",
        "section": section,
        "tier": "invariant",
        "classification": "Judgment",
        "text": text,
        "origin": "test",
        "ts": "2026-09-07T00:00:00Z",
    }
    base.update(overrides)
    return CorpusEntry(**base)


def _seed_corpus(*entries: CorpusEntry) -> None:
    _CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CORPUS_PATH.write_text(Corpus(entries=entries).dumps() + "\n", encoding="utf-8")


def _seed_overgrown_alpha(*, corpus_texts: tuple[str, ...] = _ALPHA_COVERAGE) -> int:
    """The GHI #974 reproduction: declared at the seed surface, then alpha GROWS.

    Returns the seed floor. After this the live unowned span exceeds it, the
    loader refuses, and the section is 'unowned' so `unown` refuses it too.
    """
    _write_surface(_SEED_SURFACE_TEXT)
    floor = _seed_declaration(
        {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
    )
    _write_surface(_GROWN_SURFACE_TEXT)
    _seed_corpus(*(_entry(i, text) for i, text in enumerate(corpus_texts)))
    return floor


def _ledger_events() -> list[dict]:
    if not _LEDGER_PATH.exists():
        return []
    return [
        json.loads(line) for line in _LEDGER_PATH.read_text(encoding="utf-8").splitlines() if line
    ]


def _ownership_events() -> list[dict]:
    return [
        e
        for e in _ledger_events()
        if e.get("event") in {"unowned_ratchet_updated", "section_ownership_unowned"}
    ]


def _own(
    runner: CliRunner,
    *,
    section: str = "alpha-section",
    attestor: str = "g0",
    reason: str = "corpus carries every line",
):
    return runner.invoke(
        main,
        [
            "content",
            "own",
            "Doc.md",
            "--section",
            section,
            "--attestor",
            attestor,
            "--reason",
            reason,
        ],
    )


def _unown(
    runner: CliRunner, *, section: str, attestor: str = "g0", reason: str = "moving to prose doc"
):
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


def _declaration() -> dict:
    return json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))


class TestContentOwnReproducesTheMissingTransition(unittest.TestCase):
    """GHI #974: the overgrown-unowned state has exactly one content-preserving exit."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_the_reproduced_state_is_refused_by_the_loader_and_by_unown(self) -> None:
        """The precondition, asserted so the success tests below prove a transition
        rather than a no-op: before `own`, the real loader refuses the live surface
        and the only existing map verb refuses the section."""
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(_DECLARATION_PATH, _GROWN_SURFACE_TEXT, Path.cwd())
            self.assertIn("exceeds it", str(refused.exception))
            unown = _unown(self._runner, section="alpha-section")
            self.assertEqual(unown.exit_code, 1, msg=unown.output)

    @covers("REQ-0.35.0-04-03")
    def test_owning_a_covered_section_flips_the_map_and_lowers_the_floor(self) -> None:
        with self._runner.isolated_filesystem():
            seed_floor = _seed_overgrown_alpha()
            spans = measure_section_spans(_GROWN_SURFACE_TEXT)

            result = _own(self._runner)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            declaration = _declaration()
            self.assertEqual(declaration["sections"]["alpha-section"], "corpus-owned")
            # THE FLOOR IS THE REMAINING UNOWNED SPAN, MEASURED -- never
            # `prior - span`. Here `prior - live_alpha_span` would sit BELOW
            # beta's real span, a floor the loader refuses on its next read.
            self.assertEqual(declaration["unowned_byte_floor"], spans["beta-section"])
            self.assertLess(seed_floor - spans["alpha-section"], spans["beta-section"])
            self.assertLessEqual(declaration["unowned_byte_floor"], seed_floor)

    @covers("REQ-0.35.0-04-03")
    def test_the_result_reloads_through_the_real_loader(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            result = _own(self._runner)
            self.assertEqual(result.exit_code, 0, msg=result.output)

            reloaded = load_declaration(_DECLARATION_PATH, _GROWN_SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.sections["alpha-section"], "corpus-owned")
            events = _ownership_events()
            self.assertEqual(len(events), 1, msg=events)
            self.assertEqual(events[0]["id"], reloaded.floor_event_id)

    @covers("REQ-0.35.0-04-03")
    def test_the_witness_records_the_map_the_evidence_and_the_attestation(self) -> None:
        with self._runner.isolated_filesystem():
            seed_floor = _seed_overgrown_alpha()
            result = _own(self._runner, reason="every alpha line is in the corpus")
            self.assertEqual(result.exit_code, 0, msg=result.output)

            (event,) = _ownership_events()
            self.assertEqual(event["event"], "unowned_ratchet_updated")
            self.assertEqual(event["surface"], "Doc.md")
            self.assertEqual(event["section"], "alpha-section")
            self.assertEqual(event["prior_unowned_byte_floor"], seed_floor)
            self.assertEqual(event["new_unowned_byte_floor"], _declaration()["unowned_byte_floor"])
            self.assertEqual(event["sections_digest"], sections_digest(_declaration()["sections"]))
            self.assertEqual(event["predecessor_event_id"], _GENESIS_ID)
            self.assertEqual(event["attestor"], "g0")
            self.assertEqual(event["reason"], "every alpha line is in the corpus")
            self.assertEqual(
                sorted(event["covering_entry_ids"]),
                sorted(f"corpus-alpha-section-{i:02d}" for i in range(len(_ALPHA_COVERAGE))),
            )
            self.assertEqual(event["covered_lines"], 4)
            self.assertEqual(event["body_lines"], 4)

    def test_a_shrunken_remainder_lowers_the_floor_to_what_is_measured(self) -> None:
        """Would break if the floor were `prior - span`: after beta SHRANK the
        remaining unowned span is smaller than that arithmetic gives, and the
        ratchet must record what is measured, not what was subtracted."""
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            seed_floor = _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            shrunk = _SEED_SURFACE_TEXT.replace("beta body\n", "b\n")
            _write_surface(shrunk)
            _seed_corpus(_entry(0, "alpha body line one"), _entry(1, "alpha body line two"))
            spans = measure_section_spans(shrunk)

            result = _own(self._runner)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_declaration()["unowned_byte_floor"], spans["beta-section"])
            self.assertLess(spans["beta-section"], seed_floor - spans["alpha-section"])


class TestContentOwnFailsClosed(unittest.TestCase):
    """Every refusal writes nothing: declaration byte-unchanged, no witness."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _assert_nothing_written(self, *, exit_code: int = 1, **own_kwargs):
        """Invoke `own`, assert it refused, and that both stores are untouched.

        The invocation lives INSIDE the helper so the assertion is about what the
        command did, never a bare read of a file the test wrote itself.
        """
        before = _DECLARATION_PATH.read_bytes()
        result = _own(self._runner, **own_kwargs)
        self.assertEqual(result.exit_code, exit_code, msg=result.output)
        self.assertEqual(_DECLARATION_PATH.read_bytes(), before)
        self.assertEqual(_ownership_events(), [])
        self.assertFalse(_JOURNAL_PATH.exists())
        return result

    @covers("REQ-0.35.0-04-04")
    def test_a_blank_attestor_or_reason_is_refused_before_anything_is_read(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            for attestor, reason in (("", "r"), ("   ", "r"), ("g0", ""), ("g0", " \t")):
                with self.subTest(attestor=attestor, reason=reason):
                    self._assert_nothing_written(attestor=attestor, reason=reason)

    def test_an_already_owned_section_is_refused(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            _own(self._runner)
            before = _DECLARATION_PATH.read_bytes()
            events_before = _ownership_events()
            result = _own(self._runner)
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertEqual(_DECLARATION_PATH.read_bytes(), before)
            self.assertEqual(_ownership_events(), events_before)

    def test_an_unknown_section_is_refused(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            self._assert_nothing_written(section="gamma-section")

    def test_one_uncovered_content_line_is_refused_and_named(self) -> None:
        """A section is owned by the corpus only when the corpus carries ALL of it."""
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha(corpus_texts=_ALPHA_COVERAGE[:-1])
            result = self._assert_nothing_written()
            self.assertIn("**Alpha claim one.** The detail of claim one.", result.output)
            self.assertIn("gz content remember", result.output)

    def test_a_single_nominal_entry_does_not_own_a_multi_line_section(self) -> None:
        """The presence check `compute_baseline` performs -- one addressed entry
        makes a section 'owned' -- is exactly what this transition must NOT trust."""
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha(corpus_texts=_ALPHA_COVERAGE[:1])
            self._assert_nothing_written()

    def test_entries_addressed_to_another_section_do_not_count(self) -> None:
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            _write_surface(_GROWN_SURFACE_TEXT)
            _seed_corpus(
                *(_entry(i, text, section="beta-section") for i, text in enumerate(_ALPHA_COVERAGE))
            )
            self._assert_nothing_written()

    def test_a_retired_entry_does_not_count(self) -> None:
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            _write_surface(_GROWN_SURFACE_TEXT)
            entries = [_entry(i, text) for i, text in enumerate(_ALPHA_COVERAGE)]
            tombstone = _entry(99, "", retires=entries[-1].id, id="corpus-alpha-section-tombstone")
            _seed_corpus(*entries, tombstone)
            self._assert_nothing_written()

    @covers("REQ-0.35.0-04-02")
    def test_owning_cannot_raise_the_floor_when_another_unowned_section_grew(self) -> None:
        """Owning alpha lowers the floor by design; if BETA also grew past the
        headroom, the remaining unowned span still exceeds the recorded floor,
        and this ordinary path may never raise it."""
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            grown = _GROWN_SURFACE_TEXT.replace("beta body\n", "beta body " + ("x" * 400) + "\n")
            _write_surface(grown)
            _seed_corpus(*(_entry(i, text) for i, text in enumerate(_ALPHA_COVERAGE)))
            result = self._assert_nothing_written()
            self.assertIn("beta-section", result.output)


class TestContentOwnPreservesUnrelatedState(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_only_the_named_section_moves_and_no_stored_content_changes(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            surface_before = Path("Doc.md").read_bytes()
            corpus_before = _CORPUS_PATH.read_bytes()
            map_before = _declaration()["sections"]

            result = _own(self._runner)

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(Path("Doc.md").read_bytes(), surface_before)
            self.assertEqual(_CORPUS_PATH.read_bytes(), corpus_before)
            after = _declaration()["sections"]
            self.assertEqual(
                {k: v for k, v in after.items() if k != "alpha-section"},
                {k: v for k, v in map_before.items() if k != "alpha-section"},
            )
            self.assertEqual(len(_ownership_events()), 1)
            residue = sorted(
                p.name
                for p in _DECLARATION_PATH.parent.iterdir()
                if p.name not in {"Doc.md.json", "Doc.md.json.lock"}
            )
            self.assertEqual(residue, [], f"a settled transaction leaves no residue: {residue}")


class TestContentOwnIsRecoverable(unittest.TestCase):
    """The transition shares the un-owning journal and its recovery protocol."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    @covers("REQ-0.35.0-04-02")
    def test_a_retry_completes_an_owning_interrupted_at_the_ledger_append(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                interrupted = _own(self._runner)
            self.assertEqual(interrupted.exit_code, 2, msg=interrupted.output)
            self.assertTrue(_JOURNAL_PATH.exists())
            with self.assertRaises(OwnershipLoadError):
                load_declaration(_DECLARATION_PATH, _GROWN_SURFACE_TEXT, Path.cwd())

            retry = _own(self._runner)

            self.assertEqual(retry.exit_code, 0, msg=retry.output)
            healed = load_declaration(_DECLARATION_PATH, _GROWN_SURFACE_TEXT, Path.cwd())
            self.assertEqual(healed.sections["alpha-section"], "corpus-owned")
            (event,) = _ownership_events()
            self.assertEqual(event["id"], healed.floor_event_id)
            self.assertFalse(_JOURNAL_PATH.exists())

    def test_a_retry_completes_an_owning_interrupted_before_the_declaration_landed(self) -> None:
        """State A: the journal exists, the declaration is untouched."""
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            before = _DECLARATION_PATH.read_bytes()
            real_write = unown_module.write_declaration_atomically

            def fail_declaration_only(path: Path, text: str) -> None:
                if path.name == "Doc.md.json":
                    raise OSError("no space left on device")
                real_write(path, text)

            with patch.object(unown_module, "write_declaration_atomically", fail_declaration_only):
                interrupted = _own(self._runner)
            self.assertEqual(interrupted.exit_code, 2, msg=interrupted.output)
            self.assertTrue(_JOURNAL_PATH.exists())
            self.assertEqual(_DECLARATION_PATH.read_bytes(), before)

            retry = _own(self._runner)
            self.assertEqual(retry.exit_code, 0, msg=retry.output)
            self.assertEqual(_declaration()["sections"]["alpha-section"], "corpus-owned")
            self.assertEqual(len(_ownership_events()), 1)

    def test_a_pending_owning_is_refused_until_coverage_is_restored(self) -> None:
        """State A with the corpus moved underneath: a journal may finish a
        transition, never re-decide one. Coverage lost between the journal and
        the retry is refused with the journal RETAINED, and a corpus that covers
        the section again lets the same journal complete."""
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            real_write = unown_module.write_declaration_atomically

            def fail_declaration_only(path: Path, text: str) -> None:
                if path.name == "Doc.md.json":
                    raise OSError("no space left on device")
                real_write(path, text)

            with patch.object(unown_module, "write_declaration_atomically", fail_declaration_only):
                self.assertEqual(_own(self._runner).exit_code, 2)

            entries = [_entry(i, text) for i, text in enumerate(_ALPHA_COVERAGE)]
            _seed_corpus(*entries, _entry(99, "", retires=entries[-1].id, id="tomb-1"))
            refused = _own(self._runner)
            self.assertEqual(refused.exit_code, 2, msg=refused.output)
            self.assertTrue(_JOURNAL_PATH.exists(), "the pending transition must stay completable")
            self.assertEqual(_ownership_events(), [])

            restored = _entry(100, _ALPHA_COVERAGE[-1], id="corpus-alpha-section-restored")
            _seed_corpus(*entries, _entry(99, "", retires=entries[-1].id, id="tomb-1"), restored)
            completed = _own(self._runner)
            self.assertEqual(completed.exit_code, 0, msg=completed.output)
            self.assertEqual(_declaration()["sections"]["alpha-section"], "corpus-owned")

    def test_a_completed_owning_is_never_applied_twice(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                _own(self._runner)
            _own(self._runner)
            third = _own(self._runner)
            self.assertNotEqual(third.exit_code, 0, msg=third.output)
            self.assertEqual(len(_ownership_events()), 1)
            self.assertEqual(
                _declaration()["unowned_byte_floor"],
                measure_section_spans(_GROWN_SURFACE_TEXT)["beta-section"],
            )


class TestOwnAndUnownShareOneJournal(unittest.TestCase):
    """One surface, one pending transition: whichever verb runs next completes it."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_unown_completes_a_pending_owning_and_does_not_start_its_own(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                self.assertEqual(_own(self._runner).exit_code, 2)

            recovered = _unown(self._runner, section="beta-section")

            self.assertEqual(recovered.exit_code, 1, msg=recovered.output)
            self.assertEqual(_declaration()["sections"]["alpha-section"], "corpus-owned")
            self.assertEqual(_declaration()["sections"]["beta-section"], "unowned")
            self.assertFalse(_JOURNAL_PATH.exists())
            (event,) = _ownership_events()
            self.assertEqual(event["event"], "unowned_ratchet_updated")
            self.assertEqual(event["section"], "alpha-section")

            followup = _unown(self._runner, section="doc-title")
            self.assertEqual(followup.exit_code, 0, msg=followup.output)
            self.assertEqual(_declaration()["sections"]["doc-title"], "unowned")
            self.assertEqual(_declaration()["sections"]["alpha-section"], "corpus-owned")

    def test_own_completes_a_pending_unowning_and_does_not_start_its_own(self) -> None:
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            _seed_corpus(_entry(0, "alpha body line one"), _entry(1, "alpha body line two"))
            with patch.object(Ledger, "append", side_effect=OSError("disk full")):
                self.assertEqual(_unown(self._runner, section="doc-title").exit_code, 2)

            recovered = _own(self._runner)

            self.assertEqual(recovered.exit_code, 1, msg=recovered.output)
            self.assertEqual(_declaration()["sections"]["doc-title"], "unowned")
            self.assertEqual(_declaration()["sections"]["alpha-section"], "unowned")
            (event,) = _ownership_events()
            self.assertEqual(event["event"], "section_ownership_unowned")
            reloaded = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.floor_event_id, event["id"])


class TestContentOwnIsSerialized(unittest.TestCase):
    def setUp(self) -> None:
        self._runner = CliRunner()

    def test_a_concurrent_owning_and_unowning_both_land(self) -> None:
        """Forced interleave inside the loaded read, as the un-owning test does:
        a lost update would leave one Layer-2 witness with no Layer-1 state."""
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            _seed_corpus(_entry(0, "alpha body line one"), _entry(1, "alpha body line two"))
            spans = measure_section_spans(_SEED_SURFACE_TEXT)

            from gzkit.commands.content.own import content_own_cmd  # noqa: PLC0415
            from gzkit.commands.content.unown import content_unown_cmd  # noqa: PLC0415

            rendezvous = threading.Barrier(2)
            real_load = unown_module.load_declaration

            def load_then_rendezvous(*args, **kwargs):
                loaded = real_load(*args, **kwargs)
                with contextlib.suppress(threading.BrokenBarrierError, threading.ThreadError):
                    rendezvous.wait(timeout=0.75)
                return loaded

            failures: dict[str, BaseException] = {}

            def own_worker() -> None:
                try:
                    content_own_cmd(
                        surface="Doc.md", section="alpha-section", attestor="g0", reason="own"
                    )
                except BaseException as exc:  # noqa: BLE001 - recorded, then asserted on
                    failures["own"] = exc

            def unown_worker() -> None:
                try:
                    content_unown_cmd(
                        surface="Doc.md", section="doc-title", attestor="g0", reason="unown"
                    )
                except BaseException as exc:  # noqa: BLE001 - recorded, then asserted on
                    failures["unown"] = exc

            with patch.object(unown_module, "load_declaration", load_then_rendezvous):
                threads = [
                    threading.Thread(target=own_worker),
                    threading.Thread(target=unown_worker),
                ]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(timeout=30)

            self.assertEqual(failures, {}, f"neither worker may fail: {failures}")
            declaration = _declaration()
            self.assertEqual(declaration["sections"]["alpha-section"], "corpus-owned")
            self.assertEqual(declaration["sections"]["doc-title"], "unowned")
            self.assertEqual(
                declaration["unowned_byte_floor"], spans["doc-title"] + spans["beta-section"]
            )
            self.assertEqual(len(_ownership_events()), 2)
            reloaded = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.unowned_byte_floor, declaration["unowned_byte_floor"])


class TestContentOwnReplayJournalValidation(unittest.TestCase):
    """A forged OWNING journal must never author an ownership flip or a floor.

    The un-owning twin (`TestContentUnownReplayJournalValidation`) proved the
    replay is CRASH-RECOVERY STATE ONLY for raises; these are the owning
    direction's two guards, each forged to be wrong in exactly ONE field so
    that only the check under test can refuse it.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _forge(self, *, section: str, new_floor: int) -> None:
        """Write an owning journal that is self-consistent except for the field under test."""
        on_disk = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
        record: dict = {
            "transition": "own",
            "surface": "Doc.md",
            "section": section,
            "prior_unowned_byte_floor": on_disk["unowned_byte_floor"],
            "new_unowned_byte_floor": new_floor,
            "attestor": "g0",
            "reason": "forged",
            "ts": "2026-09-07T00:00:00+00:00",
            "parent_event_id": on_disk["floor_event_id"],
            "covering_entry_ids": [f"corpus-alpha-section-{i:02d}" for i in range(4)],
            "covered_lines": 4,
            "body_lines": 4,
            "surface_digest": unown_module._surface_digest(Path("Doc.md").read_bytes()),
        }
        record["event_id"] = unown_module._mint_event_id(record, record["parent_event_id"])
        successor = dict(on_disk)
        successor["sections"] = {**on_disk["sections"], section: "corpus-owned"}
        successor["unowned_byte_floor"] = new_floor
        successor["floor_event_id"] = record["event_id"]
        from gzkit.content.ownership import OwnershipDeclaration  # noqa: PLC0415

        record["declaration_json"] = (
            OwnershipDeclaration(**successor).model_dump_json(indent=2) + "\n"
        )
        _JOURNAL_PATH.write_text(json.dumps(record), encoding="utf-8")

    def _assert_refused_by(self, defect: str) -> None:
        before = _DECLARATION_PATH.read_bytes()
        result = _own(self._runner)
        self.assertEqual(result.exit_code, 2, msg=result.output)
        self.assertIn(
            defect, result.output, f"refused, but NOT by the check under test: {result.output}"
        )
        self.assertEqual(_DECLARATION_PATH.read_bytes(), before)
        self.assertEqual(_ownership_events(), [])
        self.assertTrue(_JOURNAL_PATH.exists(), "a refused journal is RETAINED")

    def test_a_journal_owning_an_already_owned_section_is_refused(self) -> None:
        """Would break if the replay skipped the predecessor-status check: the
        successor map is a no-op, coverage holds and the floor re-measures, so a
        witness would land for a flip that never happened."""
        with self._runner.isolated_filesystem():
            _write_surface(_GROWN_SURFACE_TEXT)
            _seed_declaration(
                {
                    "doc-title": "corpus-owned",
                    "alpha-section": "corpus-owned",
                    "beta-section": "unowned",
                },
                surface_text=_GROWN_SURFACE_TEXT,
            )
            _seed_corpus(*(_entry(i, text) for i, text in enumerate(_ALPHA_COVERAGE)))
            remaining = measure_section_spans(_GROWN_SURFACE_TEXT)["beta-section"]
            self._forge(section="alpha-section", new_floor=remaining)
            self._assert_refused_by("only an unowned section may be owned")

    def test_a_journal_carrying_a_floor_the_surface_does_not_measure_is_refused(self) -> None:
        """Would break if the replay accepted any floor at or below the prior one:
        a floor one byte ABOVE the measured remainder passes the landed-state
        gate (span <= floor) and would be laundered into the chain."""
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha()
            remaining = measure_section_spans(_GROWN_SURFACE_TEXT)["beta-section"]
            self._forge(section="alpha-section", new_floor=remaining + 1)
            self._assert_refused_by("remaining unowned span under the successor map")


def _git(*args: str) -> None:
    """Run one ``git`` against the isolated fixture repository (GHI #977 boundary)."""
    subprocess.run(["git", *args], check=True, capture_output=True, env=_isolated_git_env())


class TestGrowthRefusalPrescribesAUsableRecovery(unittest.TestCase):
    """GHI #976: the loader's growth refusal names the state and a recovery that runs.

    One arithmetic -- the live unowned span above the stored floor -- is produced
    by two states, an unowned section that GREW and a section hand-flipped to
    'unowned', and the recovery differs. The prose used to prescribe
    `gz content unown` for both, which loads the declaration first and so
    refuses in both. Each test drives the refusal, then follows the message's
    own prescription through the real command path to a declaration the
    loader accepts.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _growth_refusal(self, surface_text: str) -> str:
        with self.assertRaises(OwnershipLoadError) as refused:
            load_declaration(_DECLARATION_PATH, surface_text, Path.cwd())
        message = str(refused.exception)
        self.assertIn("exceeds it", message, "fixture sanity: this must be the growth refusal")
        return message

    @covers("REQ-0.35.0-04-02")
    def test_a_grown_unowned_section_is_recovered_by_own_after_capture(self) -> None:
        with self._runner.isolated_filesystem():
            _seed_overgrown_alpha(corpus_texts=())
            message = self._growth_refusal(_GROWN_SURFACE_TEXT)
            spans = measure_section_spans(_GROWN_SURFACE_TEXT)
            # The failing state is described: every unowned section with its
            # LIVE span, so the one that grew is readable off the message.
            self.assertIn(f"'alpha-section' ({spans['alpha-section']} B)", message)
            self.assertIn(f"'beta-section' ({spans['beta-section']} B)", message)
            self.assertIn("gz content own Doc.md --section <id>", message)

            # Following the prescription: `own` states its own precondition --
            # the corpus must carry every content line -- and names the capture.
            uncovered = _own(self._runner)
            self.assertEqual(uncovered.exit_code, 1, msg=uncovered.output)
            self.assertIn("gz content remember Doc.md --section alpha-section", uncovered.output)
            self.assertIn(
                "gz content remember Doc.md --section <id>",
                message,
                "the loader's next step must state the coverage prerequisite `own` enforces",
            )
            _seed_corpus(*(_entry(i, text) for i, text in enumerate(_ALPHA_COVERAGE)))

            owned = _own(self._runner)
            self.assertEqual(owned.exit_code, 0, msg=owned.output)
            reloaded = load_declaration(_DECLARATION_PATH, _GROWN_SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.sections["alpha-section"], "corpus-owned")
            self.assertEqual(reloaded.unowned_byte_floor, spans["beta-section"])

    @covers("REQ-0.35.0-04-02")
    def test_a_grown_unowned_section_is_recovered_by_shrinking_it_back(self) -> None:
        with self._runner.isolated_filesystem():
            floor = _seed_overgrown_alpha(corpus_texts=())
            message = self._growth_refusal(_GROWN_SURFACE_TEXT)
            self.assertIn("shrink it back under the floor", message)

            _write_surface(_SEED_SURFACE_TEXT)

            reloaded = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.sections["alpha-section"], "unowned")
            self.assertEqual(reloaded.unowned_byte_floor, floor)

    @covers("REQ-0.35.0-04-02")
    def test_a_hand_flipped_map_is_recovered_by_restoring_the_tracked_declaration(
        self,
    ) -> None:
        with self._runner.isolated_filesystem():
            _write_surface(_SEED_SURFACE_TEXT)
            floor = _seed_declaration(
                {"doc-title": "corpus-owned", "alpha-section": "unowned", "beta-section": "unowned"}
            )
            _git("init", "-q")
            _git("add", "-A")
            _git(
                "-c",
                "user.name=g0",
                "-c",
                "user.email=g0@users.noreply.github.com",
                "-c",
                "commit.gpgsign=false",
                "commit",
                "-q",
                "-m",
                "witnessed declaration",
            )
            raw = _declaration()
            raw["sections"]["doc-title"] = "unowned"
            _DECLARATION_PATH.write_text(json.dumps(raw), encoding="utf-8")

            message = self._growth_refusal(_SEED_SURFACE_TEXT)
            restore = f"git checkout -- {_DECLARATION_PATH.as_posix()}"
            self.assertIn(restore, message)
            self.assertIn("gz content unown Doc.md --section <id>", message)
            # The claim the message makes about this state: neither verb can
            # act on an edited map, so the prescription must not be a verb.
            self.assertEqual(_unown(self._runner, section="doc-title").exit_code, 1)
            self.assertEqual(_own(self._runner, section="doc-title").exit_code, 1)
            self.assertEqual(_declaration()["sections"]["doc-title"], "unowned")

            _git("checkout", "--", _DECLARATION_PATH.as_posix())

            restored = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(restored.sections["doc-title"], "corpus-owned")
            self.assertEqual(restored.unowned_byte_floor, floor)
            # ...and the un-owning the edit was reaching for lands through the
            # governed verb, under a fresh attested witness.
            result = _unown(self._runner, section="doc-title")
            self.assertEqual(result.exit_code, 0, msg=result.output)
            after = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(after.sections["doc-title"], "unowned")
            spans = measure_section_spans(_SEED_SURFACE_TEXT)
            self.assertEqual(after.unowned_byte_floor, floor + spans["doc-title"])


_CONTRACT_SURFACE_TEXT = (
    "# Test Agent Contract\n"
    "Purpose line.\n"
    "## Behavior Rules\n"
    "- Do the thing.\n"
    "## Prime Directive\n"
    "- Own it.\n"
)


class TestUnownHelpAttributesTheLoweringPath(unittest.TestCase):
    """GHI #976: `unown --help` attributes the decrease-or-equal path to the verb
    that performs it. `gz content remember` captures corpus entries and never
    touches the declaration; `gz content own` is the lowering move. Both halves
    are bound to observed behaviour, never to the help text alone."""

    def setUp(self) -> None:
        self._runner = CliRunner()

    def _normalized_help(self) -> str:
        result = self._runner.invoke(main, ["content", "unown", "--help"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return " ".join(result.output.split())

    def test_help_names_own_as_the_lowering_move_and_own_lowers_the_floor(self) -> None:
        help_text = self._normalized_help()
        self.assertIn("`gz content own`, the ordinary decrease-or-equal path", help_text)
        self.assertNotIn("`gz content remember`'s ordinary path", help_text)
        with self._runner.isolated_filesystem():
            seed_floor = _seed_overgrown_alpha()
            result = _own(self._runner)
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertLess(_declaration()["unowned_byte_floor"], seed_floor)

    def test_help_says_remember_never_touches_the_ratchet_and_it_does_not(self) -> None:
        help_text = self._normalized_help()
        self.assertIn(
            "`gz content remember` captures corpus entries and never touches the ownership "
            "declaration",
            help_text,
        )
        with self._runner.isolated_filesystem():
            Path("AGENTS.md").write_bytes(_CONTRACT_SURFACE_TEXT.encode("utf-8"))
            sections = {
                "test-agent-contract": "corpus-owned",
                "behavior-rules": "unowned",
                "prime-directive": "unowned",
            }
            spans = measure_section_spans(_CONTRACT_SURFACE_TEXT)
            floor = spans["behavior-rules"] + spans["prime-directive"]
            declaration_path = Path(".gzkit") / "ownership" / "AGENTS.md.json"
            declaration_path.parent.mkdir(parents=True, exist_ok=True)
            declaration_path.write_text(
                json.dumps(
                    {
                        "surface": "AGENTS.md",
                        "sections": sections,
                        "unowned_byte_floor": floor,
                        "measured_at": "2026-09-07T00:00:00Z",
                        "floor_event_id": "section-ownership-genesis-AGENTS.md-976",
                    }
                ),
                encoding="utf-8",
            )
            emit_section_ownership_genesis(
                Path("."),
                "section-ownership-genesis-AGENTS.md-976",
                "AGENTS.md",
                sections_digest(sections),
                floor,
            )
            before = declaration_path.read_bytes()

            result = self._runner.invoke(
                main,
                [
                    "content",
                    "remember",
                    "AGENTS.md",
                    "--section",
                    "behavior-rules",
                    "--text",
                    "- Do the thing.",
                    "--tier",
                    "invariant",
                    "--classification",
                    "Judgment",
                    "--origin",
                    "GHI #976",
                ],
            )

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(declaration_path.read_bytes(), before)
            reloaded = load_declaration(declaration_path, _CONTRACT_SURFACE_TEXT, Path.cwd())
            self.assertEqual(reloaded.unowned_byte_floor, floor)
            self.assertEqual(reloaded.sections, sections)


if __name__ == "__main__":
    unittest.main()


class TestDeclarationDamageRefusalsPrescribeConditionalRecovery(unittest.TestCase):
    """GHI #978: declaration-damage refusals name a CONDITIONAL recovery, not a command.

    Eight arms of `load_declaration` refuse a declaration that disagrees with
    the ledger evidence witnessing it. Each used to prescribe either
    `gz content unown` -- which loads the declaration first and so re-raises
    the very refusal that named it -- or a hand-edit of the witnessed artifact.

    Restoring the tracked declaration DOES recover these states, but only when
    the saved copy still agrees with the surviving ledger evidence AND no
    governed transition has run since it was saved. The second precondition was
    load-bearing and invisible to the loader -- restoring over a governed
    transition produced a declaration that LOADED while silently reverting an
    attested transition. GHI #979 made it visible: the loader refuses a witness
    that is not its chain's TIP, so that precondition is now machine-held and
    the prose says so rather than asking the operator to verify it by eye.
    Everything here drives the real loader and the real CLI.
    """

    def setUp(self) -> None:
        self._runner = CliRunner()

    _MAP = {
        "doc-title": "corpus-owned",
        "alpha-section": "corpus-owned",
        "beta-section": "unowned",
    }

    def _seed(self) -> int:
        _write_surface(_SEED_SURFACE_TEXT)
        return _seed_declaration(dict(self._MAP))

    def _seed_without_ownership_events(self) -> None:
        """A declaration whose surface has NO ownership event anywhere in the ledger.

        `_seed_declaration` emits a genesis row; genesis ABSENCE is a different
        state and needs a fixture that never writes one, or the test asserts
        prose against a ledger that would in fact support the restore branch.
        """
        _write_surface(_SEED_SURFACE_TEXT)
        spans = measure_section_spans(_SEED_SURFACE_TEXT)
        floor = sum(span for sid, span in spans.items() if self._MAP[sid] == "unowned")
        _DECLARATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        _DECLARATION_PATH.write_text(
            json.dumps(
                {
                    "surface": "Doc.md",
                    "sections": dict(self._MAP),
                    "unowned_byte_floor": floor,
                    "measured_at": "2026-09-07T00:00:00Z",
                    "floor_event_id": None,
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(_ownership_events(), [], "fixture: no ownership events may exist")

    def _git(self):
        """An initialised repo in the isolated filesystem, returning a runner."""
        env = _isolated_git_env()

        def run(args):
            return subprocess.run(
                ["git", *args],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

        run(["init", "."])
        run(["config", "user.email", "g0@users.noreply.github.com"])
        run(["config", "user.name", "g0"])
        return run

    def _damage(self, **fields: object) -> None:
        raw = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
        raw.update(fields)
        _DECLARATION_PATH.write_text(json.dumps(raw), encoding="utf-8")

    def _refusal(self) -> str:
        with self.assertRaises(OwnershipLoadError) as refused:
            load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
        return str(refused.exception)

    def _assert_conditional_recovery(self, message: str) -> None:
        """The recovery is stated with BOTH preconditions and an honest blocker."""
        self.assertIn("git checkout --", message)
        self.assertIn("agrees with the ownership events", message)
        self.assertIn("no governed ownership transition has run", message)
        self.assertIn("REFUSED naming the chain tip", message)
        self.assertIn("NO governed recovery", message)
        # The circular prescriptions and hand-edits are gone.
        self.assertNotIn("raise the floor again through", message)
        self.assertNotIn("raise it again through", message)
        self.assertNotIn("repoint floor_event_id", message)

    @covers("REQ-0.35.0-04-02")
    def test_a_null_pointer_with_surviving_events_is_recovered_by_restoring(self) -> None:
        """The restore branch is REAL here: the surface's genesis row survives."""
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "witnessed declaration"])
            self._damage(floor_event_id=None)
            message = self._refusal()
            self.assertIn("declares floor_event_id null", message)
            self._assert_conditional_recovery(message)

            run(["checkout", "--", str(_DECLARATION_PATH)])
            restored = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(restored.sections, self._MAP)
            landed = _unown(self._runner, section="alpha-section")
            self.assertEqual(landed.exit_code, 0, msg=landed.output)

    @covers("REQ-0.35.0-04-02")
    def test_an_unresolvable_pointer_no_longer_prescribes_the_verb_that_refuses(self) -> None:
        with self._runner.isolated_filesystem():
            self._seed()
            self._damage(floor_event_id="section-ownership-genesis-Doc.md-absent")
            message = self._refusal()
            self.assertIn("resolves to no event", message)
            self._assert_conditional_recovery(message)

    @covers("REQ-0.35.0-04-02")
    def test_a_floor_witness_mismatch_no_longer_prescribes_a_hand_edit(self) -> None:
        with self._runner.isolated_filesystem():
            floor = self._seed()
            self._damage(unowned_byte_floor=floor + 500)
            message = self._refusal()
            self.assertIn("resolves to a ledger event recording", message)
            self.assertNotIn("set unowned_byte_floor back to", message)
            self._assert_conditional_recovery(message)

    @covers("REQ-0.35.0-04-02")
    def test_an_out_of_enum_value_no_longer_prescribes_editing_the_declaration(self) -> None:
        with self._runner.isolated_filesystem():
            self._seed()
            raw = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            raw["sections"]["alpha-section"] = "partially-owned"
            _DECLARATION_PATH.write_text(json.dumps(raw), encoding="utf-8")
            message = self._refusal()
            self.assertIn("declares ownership value", message)
            self.assertNotIn("is exactly 'corpus-owned' or 'unowned', then retry", message)
            self._assert_conditional_recovery(message)

    @covers("REQ-0.35.0-04-02")
    def test_a_surface_gained_section_names_the_absent_mechanism_not_a_command(self) -> None:
        """No `gz content` verb declares a new section, so the prose must say so."""
        with self._runner.isolated_filesystem():
            self._seed()
            _write_surface(_SEED_SURFACE_TEXT + "## Gamma Section\ngamma body\n")
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(
                    _DECLARATION_PATH,
                    _SEED_SURFACE_TEXT + "## Gamma Section\ngamma body\n",
                    Path.cwd(),
                )
            message = str(refused.exception)
            self.assertIn("has no ownership declaration", message)
            self.assertIn("no `gz content` verb declares a new section", message)
            self.assertIn("stop and escalate", message)
            # It must not invent a command that does not exist.
            self.assertNotIn("gz content declare", message)

    @covers("REQ-0.35.0-04-02")
    def test_a_surface_dropped_section_names_the_absent_mechanism_not_a_command(self) -> None:
        with self._runner.isolated_filesystem():
            self._seed()
            shrunk = (
                "# Doc Title\npreamble text under the H1\n"
                "## Alpha Section\nalpha body line one\nalpha body line two\n"
            )
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(_DECLARATION_PATH, shrunk, Path.cwd())
            message = str(refused.exception)
            self.assertIn("absent from the surface", message)
            self.assertIn("no `gz content` verb removes a declaration entry", message)
            self.assertIn("stop and escalate", message)

    @covers("REQ-0.35.0-04-02")
    def test_genesis_absence_is_not_recovered_by_restoring_the_declaration(self) -> None:
        """The OTHER branch, against a ledger that genuinely carries no genesis.

        The prose names two states behind one null pointer. This fixture is the
        one the restore branch cannot serve: no ownership event exists for the
        surface at all, so restoring the tracked declaration reproduces the
        refusal rather than clearing it, and the missing-mechanism branch is
        the true one.
        """
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed_without_ownership_events()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "declaration with no witness behind it"])

            before = self._refusal()
            self.assertIn("no `gz content` verb mints a genesis event", before)
            self.assertIn("NO governed recovery", before)

            run(["checkout", "--", str(_DECLARATION_PATH)])
            after = self._refusal()
            self.assertEqual(
                before,
                after,
                "restoring cannot serve this state -- the saved copy is unwitnessed too",
            )

    @covers("REQ-0.35.0-04-02")
    def test_restoring_over_a_governed_transition_is_refused_naming_the_chain_tip(
        self,
    ) -> None:
        """GHI #979: the demonstrated silent revert is now a refusal.

        A governed `unown` raises the floor under attestation. Restoring a
        declaration saved BEFORE it used to load, reverting the attested
        transition in the declaration while its event stayed in the ledger with
        nothing pointing at it. The loader now refuses that copy, names the
        attested transition standing after its witness, and the saved copy that
        DOES name the tip still recovers the state -- so the refusal is a
        diagnosis with an executable exit, not a dead end.
        """
        with self._runner.isolated_filesystem():
            run = self._git()
            seed_floor = self._seed()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "declaration witnessed at the seed floor"])

            raised = _unown(self._runner, section="alpha-section")
            self.assertEqual(raised.exit_code, 0, msg=raised.output)
            after = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(after.sections["alpha-section"], "unowned")
            self.assertGreater(after.unowned_byte_floor, seed_floor)
            attested = [
                e for e in _ownership_events() if e.get("event") == "section_ownership_unowned"
            ]
            self.assertEqual(len(attested), 1, "fixture sanity: one attested raise")
            attested_id = attested[0]["id"]
            run(["add", "-A", "-f"])
            run(["commit", "-m", "declaration carries the attested raise"])

            # The trap: restore the copy saved BEFORE the attested transition.
            run(["checkout", "HEAD~1", "--", str(_DECLARATION_PATH)])
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            message = str(refused.exception)
            self.assertIn("not the TIP", message)
            self.assertIn(attested_id, message)
            # The reverted state is named, never adopted.
            self.assertEqual(_declaration()["sections"]["alpha-section"], "corpus-owned")
            self.assertEqual(_declaration()["unowned_byte_floor"], seed_floor)
            self.assertIn(
                attested_id,
                [e["id"] for e in _ownership_events()],
                "the attested raise is still in the ledger",
            )
            # A governed verb refuses on the same reading rather than building on
            # it. 'doc-title' is corpus-owned in this fixture, so the ONLY reason
            # `unown` can refuse it is the loader's chain-head check.
            blocked = _unown(self._runner, section="doc-title")
            self.assertEqual(blocked.exit_code, 1, msg=blocked.output)
            self.assertIn("not the TIP", blocked.output)

            # Recovery arm (a): the saved copy that names the tip.
            run(["checkout", "HEAD", "--", str(_DECLARATION_PATH)])
            recovered = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(recovered.floor_event_id, attested_id)
            self.assertEqual(recovered.sections["alpha-section"], "unowned")
            landed = _unown(self._runner, section="doc-title")
            self.assertEqual(landed.exit_code, 0, msg=landed.output)

    @covers("REQ-0.35.0-04-02")
    def test_restoring_over_a_governed_owning_is_refused_naming_the_chain_tip(self) -> None:
        """The OTHER direction, which moves the floor the way the ratchet forbids.

        Restoring behind a governed `own` puts the floor back UP -- a raise
        reachable only through `gz content unown` (REQ-0.35.0-04-02) -- and
        re-declares a corpus-owned section unowned. The arithmetic is
        self-consistent, so only chain-head identity catches it.
        """
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed()
            _seed_corpus(_entry(0, "beta body", section="beta-section"))
            run(["add", "-A", "-f"])
            run(["commit", "-m", "declaration witnessed at the seed floor"])
            before = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())

            owned = _own(self._runner, section="beta-section")
            self.assertEqual(owned.exit_code, 0, msg=owned.output)
            after = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(after.sections["beta-section"], "corpus-owned")
            self.assertLess(after.unowned_byte_floor, before.unowned_byte_floor)
            witness = after.floor_event_id

            run(["checkout", "HEAD", "--", str(_DECLARATION_PATH)])
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            message = str(refused.exception)
            self.assertIn("not the TIP", message)
            self.assertIn(witness, message)
            # The restored copy would have RAISED the floor with no attested raise.
            self.assertGreater(
                _declaration()["unowned_byte_floor"],
                after.unowned_byte_floor,
                "the restored copy carries the higher, pre-owning floor",
            )

    @covers("REQ-0.35.0-04-02")
    def test_a_non_object_sections_field_states_the_restore_preconditions(self) -> None:
        """Condition 1 had no direct case: a 'sections' field that is not an object."""
        with self._runner.isolated_filesystem():
            self._seed()
            self._damage(sections=["alpha-section", "beta-section"])
            message = self._refusal()
            self.assertIn("non-object 'sections' field", message)
            self.assertNotIn("so 'sections' is a JSON", message)
            self._assert_conditional_recovery(message)

    @covers("REQ-0.35.0-04-02")
    def test_a_non_ownership_event_type_states_the_restore_preconditions(self) -> None:
        """Condition 7 had no direct case: the witness resolves, but to the wrong type."""
        with self._runner.isolated_filesystem():
            self._seed()
            foreign = "task-started-probe"
            # Appended as a raw row into the FIXTURE's ledger: the point is a
            # resolvable id whose event type is outside the ownership roster.
            with _LEDGER_PATH.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "schema": "gzkit.ledger.v1",
                            "event": "task_started",
                            "id": foreign,
                            "ts": "2026-09-07T00:00:00Z",
                        },
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            self._damage(floor_event_id=foreign)
            message = self._refusal()
            self.assertIn("not a recognized section-ownership event", message)
            self._assert_conditional_recovery(message)

    @covers("REQ-0.35.0-04-01")
    def test_a_surface_removed_in_error_is_repaired_by_restoring_the_surface(self) -> None:
        """The damaged artifact is the SURFACE, so the surface is what must be restored.

        Restoring the declaration here repairs nothing -- the declaration is
        already correct, and it is the surface that drifted. The prose must
        name the damaged artifact, and following it must reach a declaration
        the loader accepts and a governed verb can act on.
        """
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "surface and declaration agree"])

            shrunk = "# Doc Title\npreamble text under the H1\n## Alpha Section\nalpha body\n"
            _write_surface(shrunk)
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(_DECLARATION_PATH, shrunk, Path.cwd())
            message = str(refused.exception)
            self.assertIn("absent from the surface", message)
            # The prescription names the SURFACE, not the declaration.
            self.assertIn("git checkout -- Doc.md", message)

            # Restoring the declaration instead changes nothing -- it is not damaged.
            run(["checkout", "--", str(_DECLARATION_PATH)])
            with self.assertRaises(OwnershipLoadError):
                load_declaration(_DECLARATION_PATH, shrunk, Path.cwd())

            # Following the prescription repairs the artifact that actually drifted.
            run(["checkout", "--", "Doc.md"])
            restored = load_declaration(
                _DECLARATION_PATH, Path("Doc.md").read_text(encoding="utf-8"), Path.cwd()
            )
            self.assertEqual(restored.sections, self._MAP)
            landed = _unown(self._runner, section="alpha-section")
            self.assertEqual(landed.exit_code, 0, msg=landed.output)

    @covers("REQ-0.35.0-04-01")
    def test_a_surface_gained_in_error_is_repaired_by_restoring_the_surface(self) -> None:
        """Symmetric: an unintended surface ADDITION is repaired at the surface."""
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "surface and declaration agree"])

            grown = _SEED_SURFACE_TEXT + "## Gamma Section\ngamma body\n"
            _write_surface(grown)
            with self.assertRaises(OwnershipLoadError) as refused:
                load_declaration(_DECLARATION_PATH, grown, Path.cwd())
            message = str(refused.exception)
            self.assertIn("has no ownership declaration", message)
            self.assertIn("git checkout -- Doc.md", message)

            run(["checkout", "--", "Doc.md"])
            restored = load_declaration(
                _DECLARATION_PATH, Path("Doc.md").read_text(encoding="utf-8"), Path.cwd()
            )
            self.assertEqual(restored.sections, self._MAP)

    @covers("REQ-0.35.0-04-01")
    def test_a_truncated_declaration_is_repaired_by_restoring_the_declaration(self) -> None:
        """Cause (c) of the undeclared-section arm: the DECLARATION lost the entry."""
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "surface and declaration agree"])

            raw = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            del raw["sections"]["alpha-section"]
            _DECLARATION_PATH.write_text(json.dumps(raw), encoding="utf-8")
            message = self._refusal()
            self.assertIn("has no ownership declaration", message)
            self.assertIn("git checkout -- .gzkit/ownership/Doc.md.json", message)

            run(["checkout", "--", str(_DECLARATION_PATH)])
            restored = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(restored.sections, self._MAP)

    @covers("REQ-0.35.0-04-01")
    def test_a_stale_declaration_entry_is_repaired_by_restoring_the_declaration(self) -> None:
        """Cause (c) of the absent-section arm: the DECLARATION gained a ghost."""
        with self._runner.isolated_filesystem():
            run = self._git()
            self._seed()
            run(["add", "-A", "-f"])
            run(["commit", "-m", "surface and declaration agree"])

            raw = json.loads(_DECLARATION_PATH.read_text(encoding="utf-8"))
            raw["sections"]["ghost-section"] = "unowned"
            _DECLARATION_PATH.write_text(json.dumps(raw), encoding="utf-8")
            message = self._refusal()
            self.assertIn("absent from the surface", message)
            self.assertIn("git checkout -- .gzkit/ownership/Doc.md.json", message)

            run(["checkout", "--", str(_DECLARATION_PATH)])
            restored = load_declaration(_DECLARATION_PATH, _SEED_SURFACE_TEXT, Path.cwd())
            self.assertEqual(restored.sections, self._MAP)
