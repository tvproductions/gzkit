"""``Ledger.append`` is one transaction across writers and across a crash (GHI #953).

Two criticals, both surfaced by the OBPI-0.35.0-04 Step-4b round-6 adversary and
both reproduced against the real ``Ledger.append`` before anything was repaired:

1. **A failed append erased another writer's committed row.** The existence
   check, the length probe, the write and the rollback truncation were four
   unserialized steps over one shared file. Writer A probed the length, writer B
   appended and was told SUCCESS, A failed mid-write and truncated back to its
   own probe — deleting B's row after B's caller had already moved on.
2. **A truncated final row wedged every reader.** ``read_history`` raised
   ``JSONDecodeError`` on the fragment, and since ``latest_event`` reads before
   any write, a crash-recovery retry died before it could reach the intact
   journal that would have restored the witness. Measured worse than reported:
   ``append`` itself then WELDED the new row onto the fragment, corrupting a
   second record.

The assertions are on STORED BYTES and on what a reader replays — never on a
helper's return value. A helper agreeing while the file on disk has lost a
committed row is the whole defect.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from gzkit.ledger import BoundaryRepair, Ledger, LedgerEvent, read_corrected_rows
from gzkit.validate_pkg.ledger_check import validate_ledger

#: How long writer A holds the window open for writer B. Unserialized, B needs
#: microseconds and releases the wait itself; serialized, B cannot run at all
#: until A finishes, so this is the whole cost of the test under the fix.
_INTERLEAVE_WINDOW_SECONDS = 0.5

_SEED = (
    '{"schema":"gzkit.ledger.v1","event":"adr_created","id":"SEED",'
    '"ts":"2026-01-01T00:00:00+00:00"}\n'
)


def _event(artifact_id: str, ts: str) -> LedgerEvent:
    return LedgerEvent(event="adr_created", id=artifact_id, ts=ts)


def _stored_line(artifact_id: str, ts: str) -> str:
    """One record exactly as ``append`` serializes it, WITHOUT its terminator.

    Built from ``LedgerEvent`` rather than hand-written JSON so the fixture
    cannot drift from what the writer actually emits — the claim under test is
    about a record this store really produces, not about a string an author
    thought it produced. ``lane`` is carried because ``adr_created`` requires
    it, which is what lets the coherence test below assert that
    ``validate_ledger`` reports NOTHING against the row the reader was dropping.
    """
    event = LedgerEvent(event="adr_created", id=artifact_id, ts=ts, lane="lite")
    return json.dumps(event.model_dump(), separators=(",", ":"))


def _ids_on_disk(path: Path) -> list[str]:
    """Every id the FILE carries, parsed independently of the reader under test."""
    ids: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            ids.append(json.loads(raw)["id"])
    return ids


class TestConcurrentAppendDoesNotEraseACommittedRow(unittest.TestCase):
    """Critical 1 — the rollback may never truncate another transaction's bytes."""

    def _run_interleaving(self, ledger_path: Path) -> dict[str, str]:
        """Force writer A to fail mid-write while writer B tries to append.

        A's failure is injected at the write itself, which is the only point
        where the rollback can fire. B is released the moment A is inside its
        append, so B reaches the ledger during exactly the window the missing
        lock left open.
        """
        outcomes: dict[str, str] = {}
        a_inside = threading.Event()
        b_done = threading.Event()
        real_open = Path.open

        def failing_open(self: Path, *args: object, **kwargs: object):
            handle = real_open(self, *args, **kwargs)  # ty: ignore[no-matching-overload]
            mode = kwargs.get("mode", args[0] if args else "r")
            if mode == "a" and threading.current_thread().name == "A":
                # A is now past its length probe and about to write. Hold here
                # so B has the whole window the missing lock left open.
                #
                # The wait is BOUNDED because the two outcomes are different
                # shapes, not different timings: unserialized, B finishes in
                # microseconds and releases this immediately; serialized, B is
                # blocked on the lock A holds and can only run once A is done,
                # so the wait must time out for the test to finish at all. A
                # deadlock under the fix is the honest cost of forcing the
                # interleaving the fix prevents.
                a_inside.set()
                b_done.wait(_INTERLEAVE_WINDOW_SECONDS)
                return _FailingWriter(handle)
            return handle

        class _FailingWriter:
            """Writes raise; truncate/flush/close reach the real handle."""

            def __init__(self, inner) -> None:
                self._inner = inner

            def write(self, _text: str) -> int:
                raise OSError("injected partial write")

            def truncate(self, size: int) -> int:
                return self._inner.truncate(size)

            def flush(self) -> None:
                self._inner.flush()

            def __enter__(self):
                return self

            def __exit__(self, *_exc: object) -> bool:
                self._inner.close()
                return False

        def writer_a() -> None:
            try:
                Ledger(ledger_path).append(_event("A-ROW", "2026-01-02T00:00:00+00:00"))
                outcomes["A"] = "success"
            except OSError as exc:
                outcomes["A"] = f"OSError: {exc}"

        def writer_b() -> None:
            a_inside.wait(5)
            try:
                Ledger(ledger_path).append(_event("B-ROW", "2026-01-03T00:00:00+00:00"))
                outcomes["B"] = "success"
            except OSError as exc:
                outcomes["B"] = f"OSError: {exc}"
            finally:
                b_done.set()

        Path.open = failing_open
        try:
            thread_a = threading.Thread(target=writer_a, name="A")
            thread_b = threading.Thread(target=writer_b, name="B")
            thread_a.start()
            thread_b.start()
            thread_a.join(30)
            thread_b.join(30)
        finally:
            Path.open = real_open
        return outcomes

    def test_a_failed_append_leaves_the_other_writers_row_on_disk(self) -> None:
        """B reported success, so B's row must still be there once A rolls back.

        This is the property the missing lock broke, and it is asserted on the
        file rather than on either writer's return: B's caller was told the row
        was durable, and a durability claim that a sibling transaction can undo
        is not a durability claim.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text(_SEED, encoding="utf-8")

            outcomes = self._run_interleaving(path)

            self.assertEqual(outcomes.get("B"), "success")
            self.assertIn("injected partial write", outcomes.get("A", ""))
            self.assertEqual(_ids_on_disk(path), ["SEED", "B-ROW"])

    def test_the_failed_writers_own_row_is_still_rolled_back(self) -> None:
        """Serialization must not cost the rollback GHI #687 established.

        The repair widens the window the rollback runs in; it must not turn a
        failed append into a committed one.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text(_SEED, encoding="utf-8")

            self._run_interleaving(path)

            self.assertNotIn("A-ROW", _ids_on_disk(path))
            self.assertTrue(path.read_text(encoding="utf-8").endswith("\n"))


class TestTrailingFragmentRecovery(unittest.TestCase):
    """Critical 2 — an unterminated final line is residue, and must not wedge the store."""

    def _seeded(self, tmp: str, tail: str) -> Path:
        path = Path(tmp) / "ledger.jsonl"
        path.write_text(_SEED + tail, encoding="utf-8")
        return path

    def test_every_reader_replays_past_an_unterminated_final_line(self) -> None:
        """The strict reader raising here is what stranded crash recovery.

        ``latest_event`` reads BEFORE any write, so a retry died on the fragment
        and never reached the journal holding the witness — and died identically
        on every subsequent retry.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._seeded(tmp, '{"schema":"gzkit.ledger.v1","event":"adr_cre')
            ledger = Ledger(path)

            self.assertEqual([event.id for event in ledger.read_history()], ["SEED"])
            self.assertIsNotNone(ledger.latest_event("SEED"))

    def test_append_discards_the_fragment_instead_of_welding_onto_it(self) -> None:
        """Appending after a crash produced TWO broken rows, not one.

        The new line was concatenated onto the fragment, so the recovery attempt
        corrupted a record that would otherwise have been readable.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._seeded(tmp, '{"schema":"gzkit.ledger.v1","event":"adr_cre')

            Ledger(path).append(_event("RECOVER", "2026-01-04T00:00:00+00:00"))

            self.assertEqual(_ids_on_disk(path), ["SEED", "RECOVER"])

    def test_a_committed_row_is_never_discarded_as_a_fragment(self) -> None:
        """The boundary must be the terminator, not "the last line looks odd".

        Every row ``append`` reports as written carries its newline, so a clean
        file has nothing past the final one and recovery is a no-op.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._seeded(tmp, "")

            self.assertEqual(Ledger(path).restore_record_boundary(), BoundaryRepair("intact", 0))
            self.assertEqual(_ids_on_disk(path), ["SEED"])

    def test_a_file_that_is_entirely_a_fragment_is_emptied_not_half_kept(self) -> None:
        """No newline anywhere means no committed row anywhere."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text('{"schema":"gzkit.ledger', encoding="utf-8")

            repair = Ledger(path).restore_record_boundary()

            self.assertEqual(repair, BoundaryRepair("discarded", 23))
            self.assertEqual(path.read_text(encoding="utf-8"), "")

    def test_recovery_is_reported_rather_than_silent(self) -> None:
        """After the append the fragment is gone and the validator sees nothing.

        ``gz validate --ledger`` reports the fragment as invalid JSON only while
        it exists, so the append that removes it owes the operator the notice —
        otherwise a crash leaves no trace on any surface.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._seeded(tmp, '{"schema":"gzkit.led')
            script = (
                "import sys;"
                "from pathlib import Path;"
                "from gzkit.ledger import Ledger, LedgerEvent;"
                f"Ledger(Path({str(path)!r})).append("
                "LedgerEvent(event='adr_created', id='R',"
                " ts='2026-01-04T00:00:00+00:00'))"
            )
            result = subprocess.run(  # noqa: S603
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                errors="replace",
                check=True,
            )

            self.assertIn("interrupted append", result.stderr)
            self.assertIn("20 byte(s)", result.stderr)

    def test_a_killed_writer_leaves_a_store_the_next_writer_can_use(self) -> None:
        """The adversary's named regression: SIGKILL between partial write and rollback.

        A signal-killed process runs no ``except OSError``, so this is the one
        path that can leave a fragment behind at all. Uses a real subprocess and
        a real kill rather than a hand-written fragment, because the claim is
        about what an interrupted APPEND leaves, not about what a fixture says
        it leaves.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text(_SEED, encoding="utf-8")
            script = (
                "import os, signal;"
                "from pathlib import Path;"
                "from gzkit.ledger import Ledger, LedgerEvent;"
                "import gzkit.ledger as mod;"
                "real = Path.open;\n"
                "def killing(self, *a, **k):\n"
                "    h = real(self, *a, **k)\n"
                "    mode = k.get('mode', a[0] if a else 'r')\n"
                "    if mode == 'a':\n"
                '        h.write(\'{"schema":"gzkit.ledger.v1","eve\')\n'
                "        h.flush()\n"
                "        os.kill(os.getpid(), signal.SIGKILL)\n"
                "    return h\n"
                "Path.open = killing\n"
                f"Ledger(Path({str(path)!r})).append("
                "LedgerEvent(event='adr_created', id='DOOMED',"
                " ts='2026-01-02T00:00:00+00:00'))"
            )
            killed = subprocess.run(  # noqa: S603
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                errors="replace",
                check=False,
            )

            self.assertEqual(killed.returncode, -9)
            self.assertFalse(path.read_text(encoding="utf-8").endswith("\n"))

            Ledger(path).append(_event("AFTER", "2026-01-03T00:00:00+00:00"))

            self.assertEqual(_ids_on_disk(path), ["SEED", "AFTER"])
            self.assertEqual([event.id for event in Ledger(path).read_history()], ["SEED", "AFTER"])


class TestACompleteRecordMissingItsSeparatorIsNotResidue(unittest.TestCase):
    """GHI #953 regression — the writer's convention proved nothing about stored bytes.

    The first cut of the fragment repair read *bytes past the final newline* as
    *an interrupted append*, on the reasoning that ``append`` terminates every
    row it writes. That is true of rows ``append`` wrote and says nothing about
    a file an editor, a ``printf``, a partial restore, or a crash between the
    closing brace and the newline left behind. A complete, schema-valid row
    stored without its separator was therefore invisible to ``read_history``
    and DELETED by the next ``append`` — while ``validate_ledger`` and
    ``read_corrected_rows`` both went on reporting it, so no surface said the
    row had gone.

    The discriminator is now the parse, which is exact for this writer: an
    interrupted write leaves a proper prefix of a serialized JSON object, and no
    proper prefix of a JSON object parses as one.
    """

    def _ledger_containing(self, tmp: str, text: str) -> Path:
        path = Path(tmp) / "ledger.jsonl"
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_lone_complete_record_without_its_newline_survives_append(self) -> None:
        """A one-row file whose only row lacks a terminator loses that row.

        This is the smallest possible instance and the worst: the whole ledger
        was replaced by the row being appended.
        """
        with tempfile.TemporaryDirectory() as tmp:
            stored = _stored_line("ADR-0.1.0-only", "2026-01-01T00:00:00+00:00")
            path = self._ledger_containing(tmp, stored)

            Ledger(path).append(_event("ADR-0.9.0-new", "2026-01-05T00:00:00+00:00"))

            self.assertEqual(_ids_on_disk(path), ["ADR-0.1.0-only", "ADR-0.9.0-new"])

    def test_a_complete_record_without_its_newline_after_earlier_rows_survives_append(
        self,
    ) -> None:
        """The same loss with history in front of it, which is the live shape.

        A real ledger is thousands of rows; the one at risk is whichever was
        written last. Asserting only the single-row file would leave the
        backward scan for the record boundary unexercised.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = _stored_line("ADR-0.1.0-first", "2026-01-01T00:00:00+00:00")
            last = _stored_line("ADR-0.2.0-last", "2026-01-02T00:00:00+00:00")
            path = self._ledger_containing(tmp, f"{first}\n{last}")

            Ledger(path).append(_event("ADR-0.9.0-new", "2026-01-05T00:00:00+00:00"))

            self.assertEqual(
                _ids_on_disk(path),
                ["ADR-0.1.0-first", "ADR-0.2.0-last", "ADR-0.9.0-new"],
            )

    def test_the_file_is_left_parseable_row_by_row_after_append(self) -> None:
        """Every row must stand alone afterwards, terminator included.

        Preserving the row's BYTES while welding the next one onto it would
        satisfy an id census and still corrupt the store, so the check is that
        each line decodes on its own and the file ends on a boundary.
        """
        with tempfile.TemporaryDirectory() as tmp:
            stored = _stored_line("ADR-0.1.0-only", "2026-01-01T00:00:00+00:00")
            path = self._ledger_containing(tmp, stored)

            Ledger(path).append(_event("ADR-0.9.0-new", "2026-01-05T00:00:00+00:00"))

            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            lines = text.splitlines()
            self.assertEqual(len(lines), 2)
            for line in lines:
                self.assertIsInstance(json.loads(line), dict)

    def test_every_reader_agrees_about_a_complete_record_missing_its_newline(
        self,
    ) -> None:
        """The defect was a DISAGREEMENT between readers, and that is what is fixed.

        ``validate_ledger`` and ``read_corrected_rows`` split on lines and saw
        the row; ``read_history`` skipped it. A row the validator reports as
        clean while the strict reader denies it exists is the state that let the
        writer delete it without any surface objecting.
        """
        with tempfile.TemporaryDirectory() as tmp:
            stored = _stored_line("ADR-0.1.0-only", "2026-01-01T00:00:00+00:00")
            path = self._ledger_containing(tmp, stored)

            self.assertEqual(validate_ledger(path), [])
            self.assertEqual([row["id"] for row in read_corrected_rows(path)], ["ADR-0.1.0-only"])
            self.assertEqual(
                [event.id for event in Ledger(path).read_history()],
                ["ADR-0.1.0-only"],
            )

    def test_the_repair_supplies_the_separator_rather_than_dropping_the_row(self) -> None:
        """Named at the repair itself, so the outcome cannot be inferred from a byte count.

        ``discarded`` and ``terminated`` differ in what they do to the file, not
        in how many bytes they looked at — asserting the count alone would pass
        for either.
        """
        with tempfile.TemporaryDirectory() as tmp:
            stored = _stored_line("ADR-0.1.0-only", "2026-01-01T00:00:00+00:00")
            path = self._ledger_containing(tmp, stored)

            repair = Ledger(path).restore_record_boundary()

            self.assertEqual(repair, BoundaryRepair("terminated", len(stored)))
            self.assertEqual(path.read_text(encoding="utf-8"), f"{stored}\n")

    def test_a_truncated_record_is_still_discarded(self) -> None:
        """The control on the repair: preserving everything is the opposite failure.

        A guard that answered "keep it" unconditionally would pass every test
        above. What separates the two cases is the parse, so the fixture here is
        a genuine PREFIX of the same record the sibling tests store whole.
        """
        with tempfile.TemporaryDirectory() as tmp:
            first = _stored_line("ADR-0.1.0-first", "2026-01-01T00:00:00+00:00")
            partial = _stored_line("ADR-0.2.0-last", "2026-01-02T00:00:00+00:00")[:60]
            path = self._ledger_containing(tmp, f"{first}\n{partial}")

            repair = Ledger(path).restore_record_boundary()

            self.assertEqual(repair, BoundaryRepair("discarded", len(partial)))
            self.assertEqual(_ids_on_disk(path), ["ADR-0.1.0-first"])

    def test_no_prefix_of_a_stored_record_can_pass_the_discriminator(self) -> None:
        """The proof the repair rests on, exercised rather than asserted in prose.

        ``append`` writes ``json.dumps(...) + chr(10)``, so an interrupted write
        leaves a proper prefix of a serialized JSON object. The repair keeps a
        trailing segment only when it parses as an object, which is safe exactly
        because no such prefix does. Sweeping every cut point is what makes that
        a measured property of this writer's output rather than a claim about
        JSON in general.
        """
        stored = _stored_line("ADR-0.1.0-swept", "2026-01-01T00:00:00+00:00")

        for cut in range(1, len(stored)):
            with tempfile.TemporaryDirectory() as tmp:
                path = self._ledger_containing(tmp, stored[:cut])
                repair = Ledger(path).restore_record_boundary()
                self.assertEqual(
                    repair.action,
                    "discarded",
                    f"prefix of length {cut} was kept as a complete record",
                )

        with tempfile.TemporaryDirectory() as tmp:
            path = self._ledger_containing(tmp, stored)
            self.assertEqual(Ledger(path).restore_record_boundary().action, "terminated")

    def test_termination_is_reported_rather_than_silent(self) -> None:
        """A file that ended mid-record is evidence, even when nothing is lost.

        Either a run died between the write and its newline, or a writer that is
        not ``append`` touched the system-of-record. Once the separator is
        supplied there is no trace left on any other surface, so the append that
        supplies it owes the operator the notice.
        """
        with tempfile.TemporaryDirectory() as tmp:
            stored = _stored_line("ADR-0.1.0-only", "2026-01-01T00:00:00+00:00")
            path = self._ledger_containing(tmp, stored)
            script = (
                "from pathlib import Path;"
                "from gzkit.ledger import Ledger, LedgerEvent;"
                f"Ledger(Path({str(path)!r})).append("
                "LedgerEvent(event='adr_created', id='R',"
                " ts='2026-01-04T00:00:00+00:00'))"
            )
            result = subprocess.run(  # noqa: S603
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                errors="replace",
                check=True,
            )

            self.assertIn("missing final newline", result.stderr)
            self.assertIn("no row was discarded", result.stderr)


class TestLockSidecarIsNotCommittable(unittest.TestCase):
    """The sidecar sits beside a TRACKED file, so it must be ignored by name."""

    def test_the_sidecar_the_lock_actually_opens_is_gitignored(self) -> None:
        """Named from the primitive's own construction, never transcribed.

        A hand-written name agrees with its author rather than with the code, so
        a lock that moved its sidecar would leave this witness green while every
        governance event dirtied the tree. ``git check-ignore`` matches on path
        text, so nothing needs to exist.
        """
        repo_root = Path(__file__).resolve().parents[1]
        opened: list[str] = []
        real_open = Path.open

        def spy(self: Path, *args: object, **kwargs: object):
            opened.append(self.name)
            return real_open(self, *args, **kwargs)  # ty: ignore[no-matching-overload]

        with tempfile.TemporaryDirectory() as tmp:
            from gzkit.file_lock import exclusive_file_lock

            probe = Path(tmp) / "ledger.jsonl"
            Path.open = spy
            try:
                with exclusive_file_lock(probe):
                    pass
            finally:
                Path.open = real_open

        self.assertEqual(opened, ["ledger.jsonl.lock"])
        result = subprocess.run(  # noqa: S603
            ["git", "check-ignore", "-q", f".gzkit/{opened[0]}"],  # noqa: S607
            cwd=repo_root,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f".gzkit/{opened[0]} is not gitignored")


if __name__ == "__main__":  # pragma: no cover - unittest entry point
    unittest.main()
