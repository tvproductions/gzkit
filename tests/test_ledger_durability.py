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
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gzkit.ledger as ledger_module
from gzkit.ledger import Ledger, LedgerEvent


def _event(artifact_id: str) -> LedgerEvent:
    return LedgerEvent(event="adr_created", id=artifact_id, ts="2026-01-01T00:00:00+00:00")


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

    def test_an_existing_ledger_is_not_re_committed_on_every_append(self) -> None:
        """The directory barrier belongs to CREATION, not to each row.

        Paying it per append would be a real cost on the hot path, and the entry
        is already durable — so this is the boundary between the two guarantees,
        not an optimisation.
        """
        with tempfile.TemporaryDirectory() as tmp:
            path = self._ledger(tmp, precreate=True)
            spy = _FsyncSpy()

            with mock.patch.object(os, "fsync", spy):
                Ledger(path).append(_event("ADR-0.1.0-x"))

            self.assertNotIn(path.parent.stat().st_ino, spy.inodes)


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

        def recording_fsync(fd: int) -> None:
            order.append("fsync")
            real_fsync(fd)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text("", encoding="utf-8")

            with (
                mock.patch.object(ledger_module, "exclusive_file_lock", recording_lock),
                mock.patch.object(os, "fsync", recording_fsync),
            ):
                Ledger(path).append(_event("ADR-0.1.0-x"))

        self.assertEqual(order, ["lock-acquired", "fsync", "lock-released"])


if __name__ == "__main__":  # pragma: no cover - unittest entry point
    unittest.main()
