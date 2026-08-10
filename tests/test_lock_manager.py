"""Tests for gzkit.lock_manager — lock file I/O and TTL logic."""

from __future__ import annotations

import json
import tempfile
import unittest
import unittest.mock
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from gzkit.exchange_records import exchange_dir
from gzkit.lock_manager import (
    LockData,
    current_branch,
    delete_lock,
    list_locks,
    lock_dir,
    lock_path,
    read_lock,
    reap_expired_locks,
    resolve_agent,
    write_lock,
)


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):
        return obj

    return _identity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _CapturingLedger:
    """Minimal ledger double: captures appended events for assertion.

    ``reap_expired_locks`` only needs a sink with ``append`` (its parameter is
    typed as the structural ``lock_manager._LedgerSink`` Protocol). Using a
    capturing double here — instead of the real ``gzkit.ledger.Ledger`` — keeps
    this module (which also holds OBPI-0.0.41-02 tests) from importing
    ``gzkit.ledger`` and dragging ``ledger.py`` into OBPI-0.0.41-02's
    brief-reconcile neighborhood.
    """

    def __init__(self) -> None:
        self.events: list = []

    def append(self, event: object) -> None:
        self.events.append(event)


def _make_lock(
    obpi_id: str = "OBPI-0.0.14-01",
    agent: str = "claude-code",
    pid: int = 12345,
    session_id: str = "test-session",
    claimed_at: str | None = None,
    branch: str = "main",
    ttl_minutes: int = 120,
) -> LockData:
    if claimed_at is None:
        claimed_at = datetime.now(UTC).isoformat()
    return LockData(
        obpi_id=obpi_id,
        agent=agent,
        pid=pid,
        session_id=session_id,
        claimed_at=claimed_at,
        branch=branch,
        ttl_minutes=ttl_minutes,
    )


# ---------------------------------------------------------------------------
# LockData model
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestLockData(unittest.TestCase):
    """Unit tests for the LockData Pydantic model."""

    @covers("REQ-0.0.14-01-01")
    def test_construction(self):
        lock = _make_lock()
        self.assertEqual(lock.obpi_id, "OBPI-0.0.14-01")
        self.assertEqual(lock.agent, "claude-code")
        self.assertEqual(lock.pid, 12345)

    @covers("REQ-0.0.14-01-08")
    def test_is_expired_false_for_fresh_lock(self):
        lock = _make_lock(ttl_minutes=120)
        self.assertFalse(lock.is_expired)

    @covers("REQ-0.0.14-01-08")
    def test_is_expired_true_for_old_lock(self):
        old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
        lock = _make_lock(claimed_at=old_time, ttl_minutes=120)
        self.assertTrue(lock.is_expired)

    def test_elapsed_minutes_is_positive(self):
        lock = _make_lock()
        self.assertGreaterEqual(lock.elapsed_minutes, 0.0)

    def test_elapsed_minutes_reflects_age(self):
        old_time = (datetime.now(UTC) - timedelta(minutes=30)).isoformat()
        lock = _make_lock(claimed_at=old_time)
        self.assertAlmostEqual(lock.elapsed_minutes, 30.0, delta=1.0)

    def test_extra_fields_forbidden(self):
        with self.assertRaises(ValidationError):
            LockData(
                obpi_id="OBPI-0.0.14-01",
                agent="x",
                pid=1,
                session_id="s",
                claimed_at=datetime.now(UTC).isoformat(),
                branch="main",
                ttl_minutes=60,
                unexpected_field="boom",
            )

    def test_frozen_immutability(self):
        lock = _make_lock()
        with self.assertRaises(ValidationError):
            lock.agent = "modified"  # ty: ignore[invalid-assignment]


# ---------------------------------------------------------------------------
# resolve_agent
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestResolveAgent(unittest.TestCase):
    """Unit tests for resolve_agent()."""

    @covers("REQ-0.0.14-01-01")
    def test_override_returned_verbatim(self):
        self.assertEqual(resolve_agent("my-agent"), "my-agent")

    def test_claudecode_env_stable_identity(self):
        # Claude Code exports CLAUDECODE=1 (no underscore), not CLAUDE_CODE.
        # Stable identity prevents per-invocation PID drift (GHI #484).
        # Strip session-ID vars so the fallback-to-bare-"claude-code" branch fires.
        clean = {
            k: v
            for k, v in __import__("os").environ.items()
            if k not in ("CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID", "CLAUDE_CODE", "CLAUDECODE")
        }
        with patch.dict("os.environ", {**clean, "CLAUDECODE": "1"}, clear=True):
            agent = resolve_agent()
            self.assertEqual(agent, "claude-code")

    def test_claudecode_env_with_session_id(self):
        env = {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "abcd1234efgh5678"}
        with patch.dict("os.environ", env, clear=False):
            agent = resolve_agent()
            self.assertEqual(agent, "claude-code-abcd1234")

    def test_legacy_claude_code_env_still_accepted(self):
        # CLAUDE_CODE (with underscore) is accepted for backwards compatibility.
        with patch.dict("os.environ", {"CLAUDE_CODE": "1"}, clear=False):
            agent = resolve_agent()
            self.assertTrue(agent.startswith("claude-code"))

    def test_codex_env(self):
        clean = {
            k: v
            for k, v in __import__("os").environ.items()
            if k not in ("CLAUDECODE", "CLAUDE_CODE")
        }
        with patch.dict("os.environ", {**clean, "CODEX_SANDBOX": "1"}, clear=True):
            self.assertEqual(resolve_agent(), "codex")

    def test_fallback_unknown(self):
        clean = {
            k: v
            for k, v in __import__("os").environ.items()
            if k not in ("CLAUDECODE", "CLAUDE_CODE", "CODEX_SANDBOX")
        }
        with patch.dict("os.environ", clean, clear=True):
            agent = resolve_agent()
            self.assertTrue(agent.startswith("unknown-"))


# ---------------------------------------------------------------------------
# current_branch
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestCurrentBranch(unittest.TestCase):
    """Unit tests for current_branch()."""

    @covers("REQ-0.0.14-01-01")
    def test_returns_nonempty_string(self):
        branch = current_branch()
        self.assertIsInstance(branch, str)
        self.assertTrue(len(branch) > 0)

    def test_returns_unknown_on_subprocess_error(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            self.assertEqual(current_branch(), "unknown")

    def test_returns_unknown_on_nonzero_exit(self):
        mock_result = unittest.mock.MagicMock()
        mock_result.returncode = 128
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            self.assertEqual(current_branch(), "unknown")

    def test_subprocess_run_uses_errors_replace(self):
        mock_result = unittest.mock.MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            current_branch()
            kwargs = mock_run.call_args.kwargs
            self.assertEqual(
                kwargs.get("errors"),
                "replace",
                "GHI #534: subprocess.run must pass errors='replace' so a git "
                "rev-parse grandchild emitting non-utf8 stdout (e.g. CP1252 on "
                "Windows) does not crash the _readerthread with UnicodeDecodeError.",
            )


# ---------------------------------------------------------------------------
# lock_dir / lock_path
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestLockDirAndPath(unittest.TestCase):
    """Unit tests for lock_dir() and lock_path()."""

    @covers("REQ-0.0.14-01-01")
    def test_lock_dir_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = lock_dir(root)
            self.assertTrue(result.is_dir())
            self.assertEqual(result, root / ".gzkit" / "locks" / "obpi")

    def test_lock_dir_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock_dir(root)
            lock_dir(root)  # second call must not raise

    @covers("REQ-0.0.14-01-01")
    def test_lock_path_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = lock_path(root, "OBPI-0.0.14-01")
            self.assertEqual(path.name, "OBPI-0.0.14-01.lock.json")
            self.assertTrue(path.parent.is_dir())


# ---------------------------------------------------------------------------
# read_lock / write_lock
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestReadWriteLock(unittest.TestCase):
    """Unit tests for read_lock() and write_lock()."""

    @covers("REQ-0.0.14-01-01")
    def test_write_then_read_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = _make_lock()
            written_path = write_lock(root, original)
            self.assertTrue(written_path.is_file())

            recovered = read_lock(root, original.obpi_id)
            self.assertIsNotNone(recovered)
            assert recovered is not None
            self.assertEqual(recovered.obpi_id, original.obpi_id)
            self.assertEqual(recovered.agent, original.agent)
            self.assertEqual(recovered.ttl_minutes, original.ttl_minutes)

    @covers("REQ-0.0.14-01-01")
    def test_write_excludes_computed_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = _make_lock()
            path = write_lock(root, lock)
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("is_expired", raw)
            self.assertNotIn("elapsed_minutes", raw)

    @covers("REQ-0.0.14-01-01")
    def test_read_lock_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(read_lock(root, "OBPI-0.0.14-99"))

    @covers("REQ-0.0.14-01-01")
    def test_read_lock_corrupt_json_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad_path = lock_path(root, "OBPI-0.0.14-01")
            bad_path.write_text("{not valid json", encoding="utf-8")
            self.assertIsNone(read_lock(root, "OBPI-0.0.14-01"))

    @covers("REQ-0.0.41-02-01")
    def test_write_lock_exclusive_creation_raises_on_second_call(self):
        """`write_lock` uses `open(path, 'x')` exclusive-creation mode.

        Closes the check-then-write race in `obpi_lock_claim_cmd` by making the
        second concurrent write fail loudly instead of silently overwriting an
        existing lock. The token-block doctrine names this as the load-bearing
        exclusion property of the lock primitive.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock1 = _make_lock(obpi_id="OBPI-RACE-TEST")
            lock2 = _make_lock(obpi_id="OBPI-RACE-TEST", agent="other-agent")

            path = write_lock(root, lock1)
            self.assertTrue(path.is_file())

            with self.assertRaises(FileExistsError):
                write_lock(root, lock2)

            # The original lock content must remain intact (no partial overwrite).
            recovered = read_lock(root, "OBPI-RACE-TEST")
            self.assertIsNotNone(recovered)
            assert recovered is not None
            self.assertEqual(recovered.agent, "claude-code")  # lock1's agent, not lock2's


# ---------------------------------------------------------------------------
# delete_lock
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestDeleteLock(unittest.TestCase):
    """Unit tests for delete_lock()."""

    @covers("REQ-0.0.14-01-03")
    def test_delete_existing_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock())
            result = delete_lock(root, "OBPI-0.0.14-01")
            self.assertTrue(result)
            self.assertIsNone(read_lock(root, "OBPI-0.0.14-01"))

    @covers("REQ-0.0.14-01-03")
    def test_delete_nonexistent_lock_returns_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = delete_lock(root, "OBPI-0.0.14-99")
            self.assertFalse(result)


# ---------------------------------------------------------------------------
# list_locks
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestListLocks(unittest.TestCase):
    """Unit tests for list_locks()."""

    @covers("REQ-0.0.14-01-06")
    def test_empty_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(list_locks(root), [])

    @covers("REQ-0.0.14-01-06")
    def test_lists_multiple_locks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock("OBPI-0.0.14-01"))
            write_lock(root, _make_lock("OBPI-0.0.14-02"))
            locks = list_locks(root)
            self.assertEqual(len(locks), 2)

    @covers("REQ-0.0.14-01-06")
    def test_adr_filter_matches_correct_obpi(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock("OBPI-0.0.14-01"))
            write_lock(root, _make_lock("OBPI-0.1.0-01"))
            locks = list_locks(root, adr_filter="ADR-0.0.14")
            self.assertEqual(len(locks), 1)
            self.assertEqual(locks[0].obpi_id, "OBPI-0.0.14-01")

    @covers("REQ-0.0.14-01-06")
    def test_adr_filter_matches_full_slug_obpi(self):
        # GHI #622: full-slug obpi_ids must resolve to their parent ADR.
        # rsplit("-", 1) mis-parsed these by stripping only the last slug
        # segment, so a slug-bearing lock silently failed every ADR filter.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock("OBPI-0.0.72-02-handoff-frontmatter-reconcile"))
            write_lock(root, _make_lock("OBPI-0.1.0-01-some-other-slug"))
            locks = list_locks(root, adr_filter="ADR-0.0.72")
            self.assertEqual(len(locks), 1)
            self.assertEqual(locks[0].obpi_id, "OBPI-0.0.72-02-handoff-frontmatter-reconcile")

    @covers("REQ-0.0.14-01-06")
    def test_adr_filter_excludes_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock("OBPI-0.0.14-01"))
            locks = list_locks(root, adr_filter="ADR-9.9.9")
            self.assertEqual(locks, [])

    @covers("REQ-0.0.14-01-06")
    def test_corrupt_files_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock("OBPI-0.0.14-01"))
            # Plant a corrupt file
            bad = lock_dir(root) / "OBPI-0.0.14-bad.lock.json"
            bad.write_text("not json", encoding="utf-8")
            locks = list_locks(root)
            self.assertEqual(len(locks), 1)


# ---------------------------------------------------------------------------
# reap_expired_locks
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestReapExpiredLocks(unittest.TestCase):
    """Unit tests for reap_expired_locks()."""

    @covers("REQ-0.0.14-01-08")
    def test_reaps_expired_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            expired = _make_lock("OBPI-0.0.14-01", claimed_at=old_time, ttl_minutes=120)
            write_lock(root, expired)

            reaped = reap_expired_locks(root)
            self.assertEqual(len(reaped), 1)
            self.assertEqual(reaped[0].obpi_id, "OBPI-0.0.14-01")
            # File should be gone
            self.assertIsNone(read_lock(root, "OBPI-0.0.14-01"))

    @covers("REQ-0.0.14-01-08")
    def test_preserves_active_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock("OBPI-0.0.14-01", ttl_minutes=120))

            reaped = reap_expired_locks(root)
            self.assertEqual(reaped, [])
            self.assertIsNotNone(read_lock(root, "OBPI-0.0.14-01"))

    @covers("REQ-0.0.14-01-08")
    def test_mixed_reaps_only_expired(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            write_lock(root, _make_lock("OBPI-0.0.14-01", claimed_at=old_time, ttl_minutes=120))
            write_lock(root, _make_lock("OBPI-0.0.14-02", ttl_minutes=120))

            reaped = reap_expired_locks(root)
            self.assertEqual(len(reaped), 1)
            self.assertEqual(reaped[0].obpi_id, "OBPI-0.0.14-01")
            self.assertIsNotNone(read_lock(root, "OBPI-0.0.14-02"))

    @covers("REQ-0.0.14-01-08")
    def test_empty_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(reap_expired_locks(root), [])


# ---------------------------------------------------------------------------
# reap_expired_locks — OBPI-0.0.41-03 register-entry + ledger coupling
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.41-03")
class TestReapWritesRegisterEntry(unittest.TestCase):
    """Reaping is as auditable as voluntary release (Sub-Invariant 3)."""

    @covers("REQ-0.0.41-03-02")
    def test_reap_writes_abandoned_by_reaper_handoff(self):
        """Each reaped lock yields an abandoned_by_reaper register entry."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            expired = _make_lock(
                "OBPI-0.0.41-03",
                agent="agent-a",
                claimed_at=old_time,
                ttl_minutes=120,
            )
            write_lock(root, expired)

            reaped = reap_expired_locks(root, reaper_agent="reaper-b")
            self.assertEqual(len(reaped), 1)

            handoffs = list(exchange_dir(root).glob("*.md"))
            self.assertEqual(len(handoffs), 1)
            text = handoffs[0].read_text(encoding="utf-8")
            # Reaping-specific frontmatter (Sub-Invariant 3 step 2)
            self.assertIn("abandoned: true", text)
            self.assertIn("category: reaping", text)
            self.assertIn("abandoned_by: reaper-b", text)
            self.assertIn("abandoned_at:", text)
            self.assertIn("previous_agent: agent-a", text)
            # Sub-Invariant 2 minimum-information fields
            self.assertIn("last_lock_event_timestamp:", text)
            self.assertIn("last_commit_sha:", text)

    @covers("REQ-0.0.41-03-03")
    def test_reap_emits_ledger_event_with_handoff_path(self):
        """A reaped lock emits obpi_lock_released with handoff_path at the entry."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            write_lock(
                root,
                _make_lock("OBPI-0.0.41-03", claimed_at=old_time, ttl_minutes=120),
            )

            sink = _CapturingLedger()
            reaped = reap_expired_locks(root, ledger=sink, reaper_agent="reaper-b")
            self.assertEqual(len(reaped), 1)

            released = [e for e in sink.events if e.event == "obpi_lock_released"]
            self.assertEqual(len(released), 1)
            self.assertIn("handoff_path", released[-1].extra)
            hp = released[-1].extra["handoff_path"]
            self.assertTrue(hp.startswith(".gzkit/locks/exchange/"))
            # handoff_path resolves to the on-disk register entry, not a fabricated string
            self.assertTrue((root / hp).is_file())

    @covers("REQ-0.0.41-03-03")
    def test_reap_without_ledger_still_reaps(self):
        """Backward-compat: reap_expired_locks(root) with no ledger still reaps."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            write_lock(
                root,
                _make_lock("OBPI-0.0.41-03", claimed_at=old_time, ttl_minutes=120),
            )

            reaped = reap_expired_locks(root)
            self.assertEqual(len(reaped), 1)
            self.assertIsNone(read_lock(root, "OBPI-0.0.41-03"))
            # Register entry still written even without a ledger
            self.assertEqual(len(list(exchange_dir(root).glob("*.md"))), 1)


if __name__ == "__main__":
    unittest.main()
