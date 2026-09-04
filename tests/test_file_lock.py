"""Cross-platform advisory file lock — the shared primitive (GHI #945).

The subject of these tests is a CLAIM ABOUT COUNT, not about mechanics:
there is exactly ONE cross-platform advisory-lock implementation in this
repository, and every store that needs exclusive access reaches it through
a public name. `corpus_store` and `ownership` both serialize a whole-file
read-modify-write; when they restate the `flock`/`msvcrt.locking` pair
separately the two copies drift, and the drift only manifests under
concurrency, where nothing routine would observe it.

That is why the cross-caller tests below assert MUTUAL EXCLUSION between
two different callers rather than symbol identity. An identity assertion
passes on an alias; only exclusion proves the callers contend for the same
kernel lock on the same sidecar.
"""

from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from gzkit.file_lock import exclusive_file_lock

# Long enough that a released lock is reacquired well inside it, short
# enough that a genuinely-blocked acquirer does not stall the suite.
_ACQUIRE_TIMEOUT = 5.0
# How long to let a contending thread try before concluding it is blocked.
# A false "blocked" verdict here would be a passing test on a broken lock,
# so this is deliberately larger than any uncontended acquisition.
_BLOCKED_DWELL = 0.25


class _Contender:
    """Run `body` in a thread and report whether it got past the lock."""

    def __init__(self, body) -> None:
        self.entered = threading.Event()
        self.release = threading.Event()
        self._body = body
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        with self._body():
            self.entered.set()
            self.release.wait(_ACQUIRE_TIMEOUT)

    def start(self) -> None:
        self._thread.start()

    def join(self) -> None:
        self.release.set()
        self._thread.join(_ACQUIRE_TIMEOUT)


class TestExclusiveFileLock(unittest.TestCase):
    """The primitive's own contract."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        self.target = self.root / "store.jsonl"

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_second_acquirer_waits_until_the_first_releases(self) -> None:
        """Two writers cannot hold the same path at once — the whole point."""
        first = _Contender(lambda: exclusive_file_lock(self.target))
        first.start()
        self.assertTrue(first.entered.wait(_ACQUIRE_TIMEOUT), "first never acquired")

        second = _Contender(lambda: exclusive_file_lock(self.target))
        second.start()
        self.assertFalse(
            second.entered.wait(_BLOCKED_DWELL),
            "second acquirer entered while the first still held the lock",
        )

        first.join()
        self.assertTrue(
            second.entered.wait(_ACQUIRE_TIMEOUT),
            "second acquirer never entered after the first released",
        )
        second.join()

    def test_lock_is_a_sidecar_so_the_target_may_be_replaced_while_held(self) -> None:
        """Locking must not depend on the target's inode.

        Every caller commits by replacing the target path, which gives the new
        file a different inode on POSIX. A lock taken on the target itself would
        protect a file no later writer opens — exclusion that reads as held and
        excludes nobody.
        """
        with exclusive_file_lock(self.target):
            self.assertTrue(self.target.with_name("store.jsonl.lock").exists())
            self.assertFalse(
                self.target.exists(),
                "locking created the target; the sidecar must be a separate file",
            )

    def test_lock_is_released_when_the_guarded_block_raises(self) -> None:
        """A failed write must not wedge the store for every later writer."""
        with self.assertRaises(RuntimeError), exclusive_file_lock(self.target):
            raise RuntimeError("write failed")

        acquired = _Contender(lambda: exclusive_file_lock(self.target))
        acquired.start()
        self.assertTrue(
            acquired.entered.wait(_ACQUIRE_TIMEOUT),
            "lock survived the exception that broke out of its block",
        )
        acquired.join()

    def test_distinct_paths_do_not_contend(self) -> None:
        """Exclusion is per-path; one store must not block an unrelated one."""
        held = _Contender(lambda: exclusive_file_lock(self.target))
        held.start()
        self.assertTrue(held.entered.wait(_ACQUIRE_TIMEOUT))

        other = _Contender(lambda: exclusive_file_lock(self.root / "other.jsonl"))
        other.start()
        self.assertTrue(
            other.entered.wait(_ACQUIRE_TIMEOUT),
            "an unrelated path blocked on this one's lock",
        )
        other.join()
        held.join()


class TestOneImplementationTwoCallers(unittest.TestCase):
    """The count claim: both content stores contend for the SAME lock.

    A second copy of the primitive — or a sidecar named differently — would
    leave each of these tests passing its own exclusion test in isolation
    while the two callers silently stopped excluding each other. That is the
    drift GHI #945 exists to make impossible, so it is asserted directly.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_declaration_lock_contends_with_the_public_primitive(self) -> None:
        """`ownership` reaches the shared lock, not a private restatement."""
        from gzkit.content.ownership import exclusive_declaration_lock

        path = self.root / ".gzkit" / "ownership" / "AGENTS.md.json"
        holder = _Contender(lambda: exclusive_declaration_lock(path))
        holder.start()
        self.assertTrue(holder.entered.wait(_ACQUIRE_TIMEOUT), "declaration lock never acquired")

        rival = _Contender(lambda: exclusive_file_lock(path))
        rival.start()
        self.assertFalse(
            rival.entered.wait(_BLOCKED_DWELL),
            "the declaration lock and the shared primitive did not exclude each other",
        )
        holder.join()
        self.assertTrue(rival.entered.wait(_ACQUIRE_TIMEOUT))
        rival.join()

    def test_corpus_append_contends_with_the_public_primitive(self) -> None:
        """`corpus_store` reaches the shared lock, not a private restatement."""
        from gzkit.content.corpus_store import append_entry, corpus_path
        from gzkit.content.models.corpus import CorpusEntry

        surface = "AGENTS.md"
        path = corpus_path(self.root, surface)
        path.parent.mkdir(parents=True, exist_ok=True)

        holder = _Contender(lambda: exclusive_file_lock(path))
        holder.start()
        self.assertTrue(holder.entered.wait(_ACQUIRE_TIMEOUT))

        appended = threading.Event()

        def _append() -> None:
            append_entry(
                self.root,
                surface,
                CorpusEntry(
                    id="e1",
                    surface=surface,
                    section="s",
                    tier="compressible",
                    classification="Judgment",
                    text="t",
                    origin="cli:test",
                    ts="2026-09-04T00:00:00Z",
                ),
            )
            appended.set()

        writer = threading.Thread(target=_append, daemon=True)
        writer.start()
        self.assertFalse(
            appended.wait(_BLOCKED_DWELL),
            "append_entry committed while the shared primitive held its path",
        )

        holder.join()
        self.assertTrue(appended.wait(_ACQUIRE_TIMEOUT), "append never completed after release")
        writer.join(_ACQUIRE_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
