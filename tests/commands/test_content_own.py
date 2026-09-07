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
from tests.commands.common import CliRunner

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


if __name__ == "__main__":
    unittest.main()
