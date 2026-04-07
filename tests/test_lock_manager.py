"""Tests for gzkit.lock_manager — lock file I/O and TTL logic."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

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

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
            lock.agent = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# resolve_agent
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestResolveAgent(unittest.TestCase):
    """Unit tests for resolve_agent()."""

    @covers("REQ-0.0.14-01-01")
    def test_override_returned_verbatim(self):
        self.assertEqual(resolve_agent("my-agent"), "my-agent")

    def test_claude_code_env(self):
        with patch.dict("os.environ", {"CLAUDE_CODE": "1"}, clear=False):
            self.assertEqual(resolve_agent(), "claude-code")

    def test_codex_env(self):
        env = {k: v for k, v in __import__("os").environ.items() if k != "CLAUDE_CODE"}
        with patch.dict("os.environ", {**env, "CODEX_SANDBOX": "1"}, clear=True):
            self.assertEqual(resolve_agent(), "codex")

    def test_fallback_unknown(self):
        clean = {
            k: v
            for k, v in __import__("os").environ.items()
            if k not in ("CLAUDE_CODE", "CODEX_SANDBOX")
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


if __name__ == "__main__":
    unittest.main()
