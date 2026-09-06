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

from gzkit.ledger import Ledger, LedgerEvent

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

            self.assertEqual(Ledger(path).discard_trailing_fragment(), 0)
            self.assertEqual(_ids_on_disk(path), ["SEED"])

    def test_a_file_that_is_entirely_a_fragment_is_emptied_not_half_kept(self) -> None:
        """No newline anywhere means no committed row anywhere."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text('{"schema":"gzkit.ledger', encoding="utf-8")

            discarded = Ledger(path).discard_trailing_fragment()

            self.assertEqual(discarded, 23)
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
