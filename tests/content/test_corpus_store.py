"""Append-only corpus store tests — OBPI-0.0.37-19.

Unit-tier coverage of the store mechanism (where entries live + append-only I/O).
The REQ-level BEHAVIOR proofs (REQ-0.0.37-19-01..04) live in
``tests/commands/test_content_remember.py`` against the command surface; these
assert the lower-level ``corpus_store`` contract the command relies on.
"""

from __future__ import annotations

import tempfile
import threading
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock

from gzkit.content.corpus_store import append_entry, corpus_path, load_corpus
from gzkit.content.models import Corpus, CorpusEntry


def _entry(entry_id: str, *, section: str = "behavior-rules") -> CorpusEntry:
    """Build a conformant CorpusEntry for store round-trip tests."""
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section=section,
        tier="compressible",
        classification="Ambiguous",
        text=f"entry {entry_id}",
        origin="cli:content-remember",
        ts="2026-06-05T00:00:00Z",
    )


class TestCorpusStore(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_corpus_path_is_per_surface_jsonl_under_gzkit_corpus(self) -> None:
        """The store path is .gzkit/corpus/<surface>.jsonl, addressed by surface name."""
        path = corpus_path(self._root, "AGENTS.md")
        self.assertEqual(path, self._root / ".gzkit" / "corpus" / "AGENTS.md.jsonl")

    def test_load_returns_empty_corpus_when_no_file_exists(self) -> None:
        """A surface with no store file loads as an empty corpus, not an error."""
        loaded = load_corpus(self._root, "AGENTS.md")
        self.assertEqual(loaded, Corpus())
        self.assertEqual(len(loaded.entries), 0)

    def test_append_creates_dir_and_file_on_first_use(self) -> None:
        """First append materializes .gzkit/corpus/ and the per-surface file."""
        path = corpus_path(self._root, "AGENTS.md")
        self.assertFalse(path.exists())
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 0)

    def test_append_is_append_only_prior_entries_preserved(self) -> None:
        """A second append preserves the first entry — the store never drops history."""
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        append_entry(self._root, "AGENTS.md", _entry("c2"))
        reloaded = load_corpus(self._root, "AGENTS.md")
        self.assertEqual([e.id for e in reloaded.entries], ["c1", "c2"])

    def test_append_round_trips_all_addressed_fields(self) -> None:
        """A loaded entry carries the exact addressed/provenanced fields that were appended."""
        append_entry(self._root, "AGENTS.md", _entry("c1", section="prime-directive"))
        reloaded = load_corpus(self._root, "AGENTS.md")
        (entry,) = reloaded.entries
        self.assertEqual(entry.id, "c1")
        self.assertEqual(entry.surface, "AGENTS.md")
        self.assertEqual(entry.section, "prime-directive")
        self.assertEqual(entry.tier, "compressible")
        self.assertEqual(entry.classification, "Ambiguous")
        self.assertEqual(entry.origin, "cli:content-remember")

    def test_each_surface_has_an_isolated_store(self) -> None:
        """Appends to one surface do not bleed into another surface's store."""
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        self.assertEqual(len(load_corpus(self._root, "CLAUDE.md").entries), 0)


if __name__ == "__main__":
    unittest.main()


class TestAppendValidatesBeforePersisting(unittest.TestCase):
    """GHI #875 — the WRITE boundary must not persist a state the READ boundary refuses.

    ``Corpus.loads`` validates the tombstone algebra; ``Corpus.append`` does not.
    Before this fix ``append_entry`` wrote through the unvalidated path, so an entry
    whose ``retires`` named an id absent from the log was persisted, returned as live
    content, and rejected only on the next load — leaving an append-only store with
    no delete path in a state that cannot be read at all.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_append_of_an_unresolvable_tombstone_leaves_the_store_readable(self) -> None:
        """An append the load boundary would refuse must not reach disk (Algebra 2)."""
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        path = corpus_path(self._root, "AGENTS.md")
        before = path.read_text(encoding="utf-8")

        orphan = CorpusEntry(
            id="c2",
            surface="AGENTS.md",
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text="retires an id that is not in the log",
            origin="cli:content-remember",
            ts="2026-06-05T00:00:00Z",
            retires="never-appended",
        )

        with self.assertRaises(ValueError):
            append_entry(self._root, "AGENTS.md", orphan)

        self.assertEqual(path.read_text(encoding="utf-8"), before)
        self.assertEqual(len(load_corpus(self._root, "AGENTS.md").entries), 1)


class TestAppendCommitsAtomically(unittest.TestCase):
    """GHI #881 — a failed append must leave the prior corpus byte-identical.

    ``Path.write_text`` opens with ``mode='w'``, truncating before it writes. On the
    append-only corpus — Layer-1 canon with no delete path — a disk-full or
    interrupted write therefore destroyed committed canon, and ``content retire``'s
    handler told the operator "nothing written" while the store lay truncated. The
    store's only mutation of the target must be a single atomic commit step.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_a_failed_commit_leaves_the_store_byte_identical(self) -> None:
        """When the atomic commit step fails, the prior corpus survives intact."""
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        append_entry(self._root, "AGENTS.md", _entry("c2"))
        path = corpus_path(self._root, "AGENTS.md")
        before = path.read_bytes()

        with (
            mock.patch("os.replace", side_effect=OSError("No space left on device")),
            self.assertRaises(OSError),
        ):
            append_entry(self._root, "AGENTS.md", _entry("c3"))

        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(load_corpus(self._root, "AGENTS.md").entries), 2)
        debris = [p.name for p in path.parent.iterdir() if p.name.endswith(".tmp")]
        self.assertEqual(debris, [], f"failed append left staging debris: {debris}")


def _racing_writer(
    root: Path,
    surface: str,
    gate: threading.Barrier,
    failures: list[BaseException],
) -> Callable[[str], None]:
    """Build a thread body that appends one entry the instant every racer is ready.

    A factory rather than a closure defined in the trial loop: a loop-local closure
    captures the NAME of each per-trial list, not its value, so a thread outliving its
    iteration would report into the wrong trial's failure list.
    """

    def writer(name: str) -> None:
        try:
            gate.wait()
            append_entry(root, surface, _entry(name))
        except BaseException as exc:  # noqa: BLE001 - carried to the main thread to assert on
            failures.append(exc)

    return writer


class TestConcurrentAppendsAllLand(unittest.TestCase):
    """GHI #880 — two concurrent appends must both survive; neither may be lost.

    ``append_entry`` is a read-modify-write of the WHOLE file. Without exclusion the
    later writer's snapshot predates the earlier writer's row, so last-writer-wins
    over the entire store: a row that ``append_entry`` RETURNED as appended is absent
    from disk, and the caller proceeds — emitting a ledger event witnessing a corpus
    row that is not there. Reproduced 20/20 at filing.
    """

    TRIALS = 20

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_no_concurrent_append_is_lost_across_repeated_trials(self) -> None:
        """Every row two racing writers report as appended is on disk afterwards."""
        for trial in range(self.TRIALS):
            surface = f"surface-{trial}"
            append_entry(self._root, surface, _entry("seed"))
            gate = threading.Barrier(2)
            failures: list[BaseException] = []
            writer = _racing_writer(self._root, surface, gate, failures)

            threads = [threading.Thread(target=writer, args=(n,)) for n in ("left", "right")]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            self.assertEqual(failures, [], f"trial {trial}: writer raised {failures}")
            landed = {e.id for e in load_corpus(self._root, surface).entries}
            self.assertEqual(
                landed,
                {"seed", "left", "right"},
                f"trial {trial}: a row reported as appended is missing from disk",
            )


def _racing_retirer(
    root: Path,
    surface: str,
    gate: threading.Barrier,
    outcomes: list[BaseException | None],
) -> Callable[[str], None]:
    """Build a thread body that retires the same live entry every racer targets."""

    def retirer(name: str) -> None:
        tombstone = CorpusEntry(
            id=name,
            surface=surface,
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text=f"retire target via {name}",
            origin="cli:content-retire",
            ts="2026-06-05T00:00:00Z",
            retires="target",
        )
        try:
            gate.wait()
            append_entry(root, surface, tombstone)
            outcomes.append(None)
        except BaseException as exc:  # noqa: BLE001 - carried to the main thread to assert on
            outcomes.append(exc)

    return retirer


class TestConcurrentDoubleRetireIsRefused(unittest.TestCase):
    """GHI #880 — the caller-side guards read a snapshot, so the store must refuse.

    ``content_retire_cmd`` takes ONE snapshot and both its guards read it — the
    already-retired refusal and the floor-liveness delta — while ``append_entry``
    re-reads the file. Two processes retiring the same LIVE entry therefore both pass
    guards computed against pre-retirement state. Exclusion alone would not catch it:
    it serializes the writers but each still writes a valid-looking row. What refuses
    the second is Algebra 7 (at most one LIVE tombstone per target) evaluated INSIDE
    the lock, against the corpus the first writer just committed.
    """

    TRIALS = 20

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_exactly_one_of_two_racing_retirements_of_one_entry_lands(self) -> None:
        """Two racers, one live target: one tombstone commits and one is refused."""
        for trial in range(self.TRIALS):
            surface = f"surface-{trial}"
            append_entry(self._root, surface, _entry("target"))
            gate = threading.Barrier(2)
            outcomes: list[BaseException | None] = []
            retirer = _racing_retirer(self._root, surface, gate, outcomes)

            threads = [threading.Thread(target=retirer, args=(n,)) for n in ("t-a", "t-b")]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            landed = [o for o in outcomes if o is None]
            refused = [o for o in outcomes if isinstance(o, ValueError)]
            self.assertEqual(len(landed), 1, f"trial {trial}: expected one commit, got {outcomes}")
            self.assertEqual(
                len(refused), 1, f"trial {trial}: expected one Algebra-7 refusal, got {outcomes}"
            )
            self.assertEqual(len(load_corpus(self._root, surface).entries), 2)


class TestDuplicateIdNeverReachesDisk(unittest.TestCase):
    """GHI #874 — the write boundary refuses an alias, and leaves the store intact.

    Same boundary discipline as ``TestAppendValidatesBeforePersisting`` (GHI #875):
    an append the READ boundary would refuse must never be persisted, because the
    store is append-only and has no delete path to recover through.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        (self._root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_appending_an_existing_id_is_refused_and_changes_nothing(self) -> None:
        append_entry(self._root, "AGENTS.md", _entry("c1"))
        path = corpus_path(self._root, "AGENTS.md")
        before = path.read_text(encoding="utf-8")

        with self.assertRaises(ValueError) as caught:
            append_entry(self._root, "AGENTS.md", _entry("c1", section="prime-directive"))

        self.assertIn("'c1'", str(caught.exception))
        self.assertEqual(path.read_text(encoding="utf-8"), before)
        self.assertEqual(len(load_corpus(self._root, "AGENTS.md").entries), 1)
