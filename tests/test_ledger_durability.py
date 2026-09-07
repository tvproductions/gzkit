"""``Ledger.append`` does not return until the row is durable (GHI #952).

``flush`` pushes the Python buffer to the OS; only ``fsync`` pushes the OS page
cache to the device. Before this repair ``append`` did the first and not the
second, so a power loss could keep an already-fsynced subject — an ownership
declaration, say — together with the deletion of its recovery journal, while
losing the buffered ledger row that witnessed it. That is the inverse of the
ordering a witness needs, and it belonged to every event producer in the repo
rather than to the path that surfaced it.

The assertions here are on the SYSCALLS the append actually issues, observed
against the ledger's own inode. A test that asserted "the row is on disk"
afterwards would pass on the broken tree too — the page cache serves the read.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gzkit.ledger as ledger_module
from gzkit.ledger import Ledger, LedgerEvent


def _event(artifact_id: str) -> LedgerEvent:
    return LedgerEvent(event="adr_created", id=artifact_id, ts="2026-01-01T00:00:00+00:00")


def _ids_on_disk(path: Path) -> list[str]:
    """Every id the FILE carries, parsed independently of the reader under test."""
    return [
        json.loads(line)["id"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class _FsyncSpy:
    """Record which inodes ``os.fsync`` was called on, and optionally fail."""

    def __init__(self, fail: OSError | None = None) -> None:
        self.inodes: list[int] = []
        self._real = os.fsync
        self._fail = fail

    def __call__(self, fd: int) -> None:
        with contextlib.suppress(OSError):  # pragma: no cover - defensive
            self.inodes.append(os.fstat(fd).st_ino)
        if self._fail is not None:
            raise self._fail
        self._real(fd)


class TestAppendIsDurableBeforeItReturns(unittest.TestCase):
    """The whole point of the method: returning is a durability claim."""

    def _ledger(self, tmp: str, *, precreate: bool) -> Path:
        path = Path(tmp) / ".gzkit" / "ledger.jsonl"
        if precreate:
            path.parent.mkdir(parents=True)
            path.write_text("", encoding="utf-8")
        return path

    def test_the_rows_bytes_reach_the_device_before_append_returns(self) -> None:
        """The binding guarantee — a row reported as appended survives power loss."""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ledger(tmp, precreate=True)
            spy = _FsyncSpy()

            with mock.patch.object(os, "fsync", spy):
                Ledger(path).append(_event("ADR-0.1.0-x"))

            self.assertIn(path.stat().st_ino, spy.inodes)

    def test_a_new_ledgers_directory_entry_is_committed(self) -> None:
        """Bytes fsynced into a file a crash never names are still lost.

        ``touch`` makes the file visible, not durable. Without this barrier the
        first append could report a durable row and lose the whole file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ledger(tmp, precreate=False)
            spy = _FsyncSpy()

            with mock.patch.object(os, "fsync", spy):
                Ledger(path).append(_event("ADR-0.1.0-x"))

            self.assertIn(path.parent.stat().st_ino, spy.inodes)
            self.assertIn(path.stat().st_ino, spy.inodes)

    def test_the_entry_is_committed_once_per_instance_not_once_per_row(self) -> None:
        """The barrier belongs to CREATION, not to each row — on a sound premise.

        This assertion previously read "an EXISTING ledger is not re-committed",
        and that premise was the durability bypass: a file left behind by a
        failed or interrupted creation exists exactly like a committed one, so
        skipping the barrier for it reported rows durable on an uncommitted
        entry. What licenses skipping is not that the file is there — it is that
        THIS INSTANCE established the barrier itself and the file has not gone
        away since. So the saving is measured across two appends on ONE
        instance, where that premise actually holds, and never inferred from a
        file a different run left behind.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ledger(tmp, precreate=True)
            ledger = Ledger(path)
            parent_inode = path.parent.stat().st_ino

            first = _FsyncSpy()
            with mock.patch.object(os, "fsync", first):
                ledger.append(_event("ADR-0.1.0-x"))

            second = _FsyncSpy()
            with mock.patch.object(os, "fsync", second):
                ledger.append(_event("ADR-0.2.0-y"))

            self.assertIn(parent_inode, first.inodes)
            self.assertNotIn(parent_inode, second.inodes)
            # The row's own barrier is still paid every time; only the entry's
            # is amortised.
            self.assertIn(path.stat().st_ino, second.inodes)

    def test_a_ledger_that_disappeared_is_re_created_and_re_committed(self) -> None:
        """Committed-once is true of a file, not of a path.

        The instance flag alone would let a deleted-and-recreated ledger inherit
        a durability claim that belonged to a file that no longer exists — so
        the guard requires the flag AND the file, and this is the arm that makes
        the second half of that conjunction load-bearing.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ledger(tmp, precreate=True)
            ledger = Ledger(path)
            parent_inode = path.parent.stat().st_ino

            ledger.append(_event("ADR-0.1.0-x"))
            path.unlink()

            spy = _FsyncSpy()
            with mock.patch.object(os, "fsync", spy):
                ledger.append(_event("ADR-0.2.0-y"))

            self.assertIn(parent_inode, spy.inodes)


class TestAFailedBarrierRefusesRatherThanReporting(unittest.TestCase):
    """Failure behavior: a durability claim that cannot be made must not be made."""

    def test_a_failing_fsync_raises_and_leaves_no_row_behind(self) -> None:
        """The row must not survive a barrier that failed.

        Keeping it would be the defect one level down: a row on disk that
        `append` never established as durable, with the caller told nothing.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text("", encoding="utf-8")
            spy = _FsyncSpy(fail=OSError("device barrier failed"))

            with (
                mock.patch.object(os, "fsync", spy),
                self.assertRaises(OSError),
            ):
                Ledger(path).append(_event("ADR-0.1.0-x"))

            self.assertEqual(path.read_text(encoding="utf-8"), "")

    def test_a_failing_directory_barrier_refuses_to_create(self) -> None:
        """Propagated, never swallowed — a swallowed barrier reports a claim nobody can check."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".gzkit" / "ledger.jsonl"
            refusal = OSError("directory sync unavailable")

            with (
                mock.patch.object(ledger_module, "commit_directory_entry", side_effect=refusal),
                self.assertRaises(OSError),
            ):
                Ledger(path).append(_event("ADR-0.1.0-x"))


class TestExistenceIsNotEvidenceOfDurability(unittest.TestCase):
    """GHI #952 reopened — a file left by a failed creation was read as a durable one.

    ``create`` touches before it commits, so a raised barrier leaves the file
    visible with its entry uncommitted. ``append`` gated the barrier on
    ``self.path.exists()``, so the NEXT attempt read that residue as proof the
    creation had been made durable, skipped the barrier, and reported its row
    durable on an entry a crash could still take.

    The reported sequence, measured before the repair: attempt 1 refused with
    the file left behind; attempt 2 on a FRESH instance SUCCEEDED; the barrier
    call count stayed at 1.

    The same state arises with no exception at all — a crash between ``touch``
    and the barrier — which is why the repair is to stop inferring durability
    from existence rather than to tidy up the failure path.
    """

    class _CountingBarrier:
        """A directory barrier that fails until it is told to stop."""

        def __init__(self, *, failures: int) -> None:
            self.calls = 0
            self._remaining = failures
            self._real = ledger_module.commit_directory_entry

        def __call__(self, directory: Path) -> None:
            self.calls += 1
            if self._remaining > 0:
                self._remaining -= 1
                raise OSError("directory sync unavailable")
            self._real(directory)

    def _fresh_ledger_path(self, tmp: str) -> Path:
        return Path(tmp) / ".gzkit" / "ledger.jsonl"

    def test_a_second_attempt_on_a_fresh_instance_still_refuses(self) -> None:
        """The reported bypass, asserted at the outcome that mattered.

        A fresh instance is the realistic shape: each `gz` command builds its
        own ``Ledger``, so "the next attempt" is almost never the same object.
        """
        barrier = self._CountingBarrier(failures=99)
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(ledger_module, "commit_directory_entry", barrier),
        ):
            path = self._fresh_ledger_path(tmp)

            with self.assertRaises(OSError):
                Ledger(path).append(_event("ADR-0.1.0-first"))
            self.assertTrue(path.exists(), "the failed creation leaves the file — that is the trap")

            with self.assertRaises(OSError):
                Ledger(path).append(_event("ADR-0.2.0-second"))

            self.assertEqual(path.read_text(encoding="utf-8"), "")

    def test_a_second_attempt_on_the_SAME_instance_still_refuses(self) -> None:
        """The flag must be set by a SUCCESSFUL creation, never by an attempted one.

        The fresh-instance arm above cannot see this: a fresh instance starts
        with the flag clear either way. Setting it before `create` returns would
        let one instance refuse, mark the entry committed, and then report the
        very next row durable — the original bypass rebuilt inside a single
        object.
        """
        barrier = self._CountingBarrier(failures=99)
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(ledger_module, "commit_directory_entry", barrier),
        ):
            path = self._fresh_ledger_path(tmp)
            ledger = Ledger(path)

            with self.assertRaises(OSError):
                ledger.append(_event("ADR-0.1.0-first"))
            with self.assertRaises(OSError):
                ledger.append(_event("ADR-0.2.0-second"))

            self.assertEqual(barrier.calls, 2)
            self.assertEqual(path.read_text(encoding="utf-8"), "")

    def test_the_barrier_is_retried_on_every_attempt_while_it_is_unavailable(self) -> None:
        """Refusing is not enough — the barrier must actually be re-attempted.

        A repair that cached the failure would also refuse forever, and would
        never recover when the barrier came back. The growing call count is what
        separates the two.
        """
        barrier = self._CountingBarrier(failures=99)
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(ledger_module, "commit_directory_entry", barrier),
        ):
            path = self._fresh_ledger_path(tmp)
            for _ in range(3):
                with self.assertRaises(OSError):
                    Ledger(path).append(_event("ADR-0.1.0-x"))

            self.assertEqual(barrier.calls, 3)

    def test_a_file_whose_entry_was_never_committed_is_not_trusted(self) -> None:
        """The crash path, where no exception was ever raised to catch.

        This fixture is byte-identical to what a process killed between ``touch``
        and the barrier leaves. Unlink-on-failure — the obvious repair for the
        reported sequence — does not reach it, which is why the inference itself
        had to go.
        """
        barrier = self._CountingBarrier(failures=0)
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(ledger_module, "commit_directory_entry", barrier),
        ):
            path = self._fresh_ledger_path(tmp)
            path.parent.mkdir(parents=True)
            path.touch()  # exactly the residue of an interrupted creation

            Ledger(path).append(_event("ADR-0.1.0-x"))

            self.assertEqual(barrier.calls, 1)

    def test_append_succeeds_once_the_barrier_becomes_available(self) -> None:
        """Refusal must be a hold, not a wedge."""
        barrier = self._CountingBarrier(failures=2)
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(ledger_module, "commit_directory_entry", barrier),
        ):
            path = self._fresh_ledger_path(tmp)
            for _ in range(2):
                with self.assertRaises(OSError):
                    Ledger(path).append(_event("ADR-0.1.0-held"))

            Ledger(path).append(_event("ADR-0.2.0-recovered"))

            self.assertEqual(_ids_on_disk(path), ["ADR-0.2.0-recovered"])
            self.assertEqual(barrier.calls, 3)

    def test_rows_already_stored_survive_a_refused_append(self) -> None:
        """A refusal must cost nothing that was already committed.

        The refusal now happens INSIDE the lock and before the write, so this
        also pins that the new ordering did not put existing history at risk.
        """
        barrier = self._CountingBarrier(failures=99)
        with tempfile.TemporaryDirectory() as tmp:
            path = self._fresh_ledger_path(tmp)
            path.parent.mkdir(parents=True)
            Ledger(path).append(_event("ADR-0.1.0-committed"))
            before = path.read_text(encoding="utf-8")

            with (
                mock.patch.object(ledger_module, "commit_directory_entry", barrier),
                self.assertRaises(OSError),
            ):
                Ledger(path).append(_event("ADR-0.2.0-refused"))

            self.assertEqual(path.read_text(encoding="utf-8"), before)
            self.assertEqual(_ids_on_disk(path), ["ADR-0.1.0-committed"])


class TestTheBarrierRunsInsideTheTransaction(unittest.TestCase):
    """The durability repair must not undo the transaction boundary (GHI #953)."""

    def test_the_row_is_made_durable_before_the_lock_is_released(self) -> None:
        """Releasing first would let a sibling writer observe an uncommitted commit.

        The two repairs are one contract: `append` returns only after the row is
        both serialized against other writers AND on the device.
        """
        order: list[str] = []
        real_lock = ledger_module.exclusive_file_lock
        real_fsync = os.fsync

        @contextlib.contextmanager
        def recording_lock(target: Path):
            order.append("lock-acquired")
            with real_lock(target):
                yield
            order.append("lock-released")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text("", encoding="utf-8")
            file_inode = path.stat().st_ino
            parent_inode = path.parent.stat().st_ino

            def recording_fsync(fd: int) -> None:
                inode = os.fstat(fd).st_ino
                if inode == file_inode:
                    order.append("row-durable")
                elif inode == parent_inode:
                    order.append("entry-durable")
                real_fsync(fd)

            with (
                mock.patch.object(ledger_module, "exclusive_file_lock", recording_lock),
                mock.patch.object(os, "fsync", recording_fsync),
            ):
                Ledger(path).append(_event("ADR-0.1.0-x"))

        # Both barriers, named rather than counted: a bare "fsync" label passed
        # while the entry's barrier was missing entirely, which is the bypass.
        self.assertEqual(
            order,
            ["lock-acquired", "entry-durable", "row-durable", "lock-released"],
        )


if __name__ == "__main__":  # pragma: no cover - unittest entry point
    unittest.main()
