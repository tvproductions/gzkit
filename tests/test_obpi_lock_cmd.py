"""Tests for OBPI lock management — data layer, events, and CLI commands."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from pydantic import ValidationError
from rich.console import Console

from gzkit.commands.obpi_lock import (
    obpi_lock_check_cmd,
    obpi_lock_claim_cmd,
    obpi_lock_list_cmd,
    obpi_lock_release_cmd,
)
from gzkit.ledger_events import obpi_lock_claimed_event, obpi_lock_released_event
from gzkit.lock_manager import (
    LockData,
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
# Shared quiet console — suppresses Rich output during command tests
# ---------------------------------------------------------------------------

_quiet_console = Console(file=StringIO())


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


def _expired_iso(minutes_ago: int = 200) -> str:
    return (datetime.now(UTC) - timedelta(minutes=minutes_ago)).isoformat()


# ---------------------------------------------------------------------------
# 1. TestLockDataModel
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestLockDataModel(unittest.TestCase):
    """Unit tests for the LockData Pydantic model."""

    @covers("REQ-0.0.14-01-01")
    def test_valid_lock_data(self):
        lock = _make_lock()
        self.assertEqual(lock.obpi_id, "OBPI-0.0.14-01")
        self.assertEqual(lock.agent, "claude-code")
        self.assertEqual(lock.ttl_minutes, 120)

    def test_rejects_extra_fields(self):
        with self.assertRaises(ValidationError):
            LockData(
                obpi_id="OBPI-0.0.14-01",
                agent="claude-code",
                pid=1,
                session_id="s",
                claimed_at=datetime.now(UTC).isoformat(),
                branch="main",
                ttl_minutes=120,
                unknown_extra_field="bad",
            )

    @covers("REQ-0.0.14-01-08")
    def test_is_expired_true(self):
        lock = _make_lock(claimed_at=_expired_iso(200), ttl_minutes=120)
        self.assertTrue(lock.is_expired)

    @covers("REQ-0.0.14-01-08")
    def test_is_expired_false(self):
        lock = _make_lock(claimed_at=datetime.now(UTC).isoformat(), ttl_minutes=120)
        self.assertFalse(lock.is_expired)

    def test_elapsed_minutes(self):
        target_elapsed = 30
        claimed_at = (datetime.now(UTC) - timedelta(minutes=target_elapsed)).isoformat()
        lock = _make_lock(claimed_at=claimed_at, ttl_minutes=120)
        # Allow 1-minute window for execution time
        self.assertAlmostEqual(lock.elapsed_minutes, target_elapsed, delta=1.0)


# ---------------------------------------------------------------------------
# 2. TestLockManagerIO
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestLockManagerIO(unittest.TestCase):
    """Filesystem I/O operations in lock_manager."""

    def test_read_lock_returns_none_for_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = read_lock(root, "OBPI-0.0.14-01")
            self.assertIsNone(result)

    def test_read_lock_returns_none_for_corrupt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = lock_path(root, "OBPI-0.0.14-01")
            path.write_text("not valid json {{{{", encoding="utf-8")
            result = read_lock(root, "OBPI-0.0.14-01")
            self.assertIsNone(result)

    @covers("REQ-0.0.14-01-01")
    def test_write_lock_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = _make_lock()
            written = write_lock(root, lock)
            self.assertTrue(written.exists())
            data = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(data["obpi_id"], "OBPI-0.0.14-01")
            self.assertEqual(data["agent"], "claude-code")
            self.assertEqual(data["ttl_minutes"], 120)

    def test_write_lock_excludes_computed_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = _make_lock()
            written = write_lock(root, lock)
            data = json.loads(written.read_text(encoding="utf-8"))
            self.assertNotIn("is_expired", data)
            self.assertNotIn("elapsed_minutes", data)

    @covers("REQ-0.0.14-01-03")
    def test_delete_lock_removes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = _make_lock()
            write_lock(root, lock)
            result = delete_lock(root, "OBPI-0.0.14-01")
            self.assertTrue(result)
            self.assertFalse(lock_path(root, "OBPI-0.0.14-01").exists())

    def test_delete_lock_returns_false_for_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = delete_lock(root, "OBPI-0.0.14-01")
            self.assertFalse(result)

    @covers("REQ-0.0.14-01-08")
    def test_reap_expired_locks_removes_expired(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expired_lock = _make_lock(
                obpi_id="OBPI-0.0.14-01",
                claimed_at=_expired_iso(200),
                ttl_minutes=120,
            )
            write_lock(root, expired_lock)
            reaped = reap_expired_locks(root)
            self.assertEqual(len(reaped), 1)
            self.assertEqual(reaped[0].obpi_id, "OBPI-0.0.14-01")
            self.assertFalse(lock_path(root, "OBPI-0.0.14-01").exists())

    @covers("REQ-0.0.14-01-08")
    def test_reap_expired_locks_preserves_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_lock = _make_lock(
                obpi_id="OBPI-0.0.14-02",
                claimed_at=datetime.now(UTC).isoformat(),
                ttl_minutes=120,
            )
            write_lock(root, active_lock)
            reaped = reap_expired_locks(root)
            self.assertEqual(len(reaped), 0)
            self.assertTrue(lock_path(root, "OBPI-0.0.14-02").exists())

    def test_list_locks_filters_by_adr(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_lock(root, _make_lock(obpi_id="OBPI-0.0.14-01"))
            write_lock(root, _make_lock(obpi_id="OBPI-0.1.0-01"))
            results = list_locks(root, adr_filter="ADR-0.0.14")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].obpi_id, "OBPI-0.0.14-01")

    def test_resolve_agent_override(self):
        result = resolve_agent(agent_override="my-custom-agent")
        self.assertEqual(result, "my-custom-agent")

    def test_resolve_agent_claude_code_env(self):
        with patch.dict("os.environ", {"CLAUDE_CODE": "1"}, clear=False):
            result = resolve_agent()
            self.assertEqual(result, "claude-code")


# ---------------------------------------------------------------------------
# 3. TestLedgerLockEvents
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.14-01")
class TestLedgerLockEvents(unittest.TestCase):
    """Event factory tests for OBPI lock ledger events."""

    @covers("REQ-0.0.14-01-01")
    def test_obpi_lock_claimed_event_structure(self):
        event = obpi_lock_claimed_event(
            obpi_id="OBPI-0.0.14-01",
            agent="claude-code",
            ttl_minutes=120,
            branch="main",
            session_id="sess-abc",
        )
        self.assertEqual(event.event, "obpi_lock_claimed")
        self.assertEqual(event.id, "OBPI-0.0.14-01")
        self.assertEqual(event.extra["agent"], "claude-code")
        self.assertEqual(event.extra["ttl_minutes"], 120)
        self.assertEqual(event.extra["branch"], "main")
        self.assertEqual(event.extra["session_id"], "sess-abc")

    @covers("REQ-0.0.14-01-03")
    def test_obpi_lock_released_event_structure(self):
        event = obpi_lock_released_event(
            obpi_id="OBPI-0.0.14-01",
            agent="claude-code",
            force=True,
        )
        self.assertEqual(event.event, "obpi_lock_released")
        self.assertEqual(event.id, "OBPI-0.0.14-01")
        self.assertEqual(event.extra["agent"], "claude-code")
        self.assertTrue(event.extra["force"])


# ---------------------------------------------------------------------------
# Shared setup helper for command-level tests
# ---------------------------------------------------------------------------


def _setup_project(tmp: str) -> Path:
    root = Path(tmp)
    config_path = root / ".gzkit.json"
    config_data = {
        "project_name": "test",
        "mode": "lite",
        "paths": {"ledger": ".gzkit/ledger.jsonl"},
    }
    config_path.write_text(json.dumps(config_data), encoding="utf-8")
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text("", encoding="utf-8")
    return root


def _mock_config(ledger_rel: str = ".gzkit/ledger.jsonl") -> MagicMock:
    mock_config = MagicMock()
    mock_config.paths.ledger = ledger_rel
    return mock_config


# ---------------------------------------------------------------------------
# 4. TestLockClaim
# ---------------------------------------------------------------------------


@patch("gzkit.commands.obpi_lock.console", _quiet_console)
@covers("OBPI-0.0.14-01")
class TestLockClaim(unittest.TestCase):
    """Command-level tests for obpi_lock_claim_cmd."""

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-01")
    def test_claim_creates_lock_file(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            obpi_lock_claim_cmd(obpi_id="OBPI-0.0.14-01", ttl_minutes=120, as_json=False)

            lf = root / ".gzkit" / "locks" / "obpi" / "OBPI-0.0.14-01.lock.json"
            self.assertTrue(lf.exists())
            data = json.loads(lf.read_text(encoding="utf-8"))
            self.assertEqual(data["obpi_id"], "OBPI-0.0.14-01")
            self.assertEqual(data["ttl_minutes"], 120)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-01")
    def test_claim_emits_ledger_event(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            obpi_lock_claim_cmd(obpi_id="OBPI-0.0.14-01", ttl_minutes=120, as_json=False)

            ledger_path = root / ".gzkit" / "ledger.jsonl"
            raw_lines = ledger_path.read_text(encoding="utf-8").splitlines()
            lines = [ln for ln in raw_lines if ln.strip()]
            self.assertGreater(len(lines), 0)
            event = json.loads(lines[-1])
            self.assertEqual(event["event"], "obpi_lock_claimed")
            self.assertEqual(event["id"], "OBPI-0.0.14-01")

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-07")
    def test_claim_json_output(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            with patch("builtins.print") as mock_print:
                obpi_lock_claim_cmd(obpi_id="OBPI-0.0.14-01", ttl_minutes=60, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "claimed")
                self.assertEqual(output["lock"]["obpi_id"], "OBPI-0.0.14-01")
                self.assertEqual(output["lock"]["ttl_minutes"], 60)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    def test_claim_same_agent_overwrites(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            agent = resolve_agent()
            obpi_lock_claim_cmd(
                obpi_id="OBPI-0.0.14-01", ttl_minutes=120, as_json=False, agent=agent
            )
            obpi_lock_claim_cmd(
                obpi_id="OBPI-0.0.14-01", ttl_minutes=240, as_json=False, agent=agent
            )

            lf = root / ".gzkit" / "locks" / "obpi" / "OBPI-0.0.14-01.lock.json"
            data = json.loads(lf.read_text(encoding="utf-8"))
            self.assertEqual(data["ttl_minutes"], 240)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-02")
    def test_claim_exits_1_on_conflict(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            # Pre-place a lock from a different agent
            existing = _make_lock(
                obpi_id="OBPI-0.0.14-01",
                agent="other-agent",
                claimed_at=datetime.now(UTC).isoformat(),
                ttl_minutes=120,
            )
            write_lock(root, existing)

            with self.assertRaises(SystemExit) as ctx:
                obpi_lock_claim_cmd(
                    obpi_id="OBPI-0.0.14-01",
                    ttl_minutes=60,
                    as_json=False,
                    agent="claude-code",
                )
            self.assertEqual(ctx.exception.code, 1)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    def test_claim_with_agent_flag(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            obpi_lock_claim_cmd(
                obpi_id="OBPI-0.0.14-01",
                ttl_minutes=60,
                as_json=False,
                agent="custom-agent",
            )

            lf = root / ".gzkit" / "locks" / "obpi" / "OBPI-0.0.14-01.lock.json"
            data = json.loads(lf.read_text(encoding="utf-8"))
            self.assertEqual(data["agent"], "custom-agent")


# ---------------------------------------------------------------------------
# 5. TestLockRelease
# ---------------------------------------------------------------------------


@patch("gzkit.commands.obpi_lock.console", _quiet_console)
@covers("OBPI-0.0.14-01")
class TestLockRelease(unittest.TestCase):
    """Command-level tests for obpi_lock_release_cmd."""

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-03")
    def test_release_removes_lock(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            lock = _make_lock(obpi_id="OBPI-0.0.14-01", agent="claude-code")
            write_lock(root, lock)

            obpi_lock_release_cmd(obpi_id="OBPI-0.0.14-01", as_json=False, agent="claude-code")
            self.assertFalse(lock_path(root, "OBPI-0.0.14-01").exists())

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-03")
    def test_release_emits_ledger_event(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            lock = _make_lock(obpi_id="OBPI-0.0.14-01", agent="claude-code")
            write_lock(root, lock)

            obpi_lock_release_cmd(obpi_id="OBPI-0.0.14-01", as_json=False, agent="claude-code")

            ledger_path = root / ".gzkit" / "ledger.jsonl"
            raw_lines = ledger_path.read_text(encoding="utf-8").splitlines()
            lines = [ln for ln in raw_lines if ln.strip()]
            self.assertGreater(len(lines), 0)
            event = json.loads(lines[-1])
            self.assertEqual(event["event"], "obpi_lock_released")
            self.assertEqual(event["id"], "OBPI-0.0.14-01")

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    def test_release_not_found(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            # Should not raise — just a no-op
            obpi_lock_release_cmd(obpi_id="OBPI-0.0.14-01", as_json=False)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-07")
    def test_release_json_output(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            lock = _make_lock(obpi_id="OBPI-0.0.14-01", agent="claude-code")
            write_lock(root, lock)

            with patch("builtins.print") as mock_print:
                obpi_lock_release_cmd(obpi_id="OBPI-0.0.14-01", as_json=True, agent="claude-code")
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "released")
                self.assertEqual(output["obpi_id"], "OBPI-0.0.14-01")

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-04")
    def test_release_validates_ownership(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            lock = _make_lock(obpi_id="OBPI-0.0.14-01", agent="owner-agent")
            write_lock(root, lock)

            with self.assertRaises(SystemExit) as ctx:
                obpi_lock_release_cmd(obpi_id="OBPI-0.0.14-01", as_json=False, agent="other-agent")
            self.assertEqual(ctx.exception.code, 1)
            # Lock should still exist
            self.assertTrue(lock_path(root, "OBPI-0.0.14-01").exists())

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-04")
    def test_release_force_bypasses_ownership(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            lock = _make_lock(obpi_id="OBPI-0.0.14-01", agent="owner-agent")
            write_lock(root, lock)

            obpi_lock_release_cmd(
                obpi_id="OBPI-0.0.14-01",
                as_json=False,
                force=True,
                agent="different-agent",
            )
            self.assertFalse(lock_path(root, "OBPI-0.0.14-01").exists())


# ---------------------------------------------------------------------------
# 6. TestLockCheck
# ---------------------------------------------------------------------------


@patch("gzkit.commands.obpi_lock.console", _quiet_console)
@covers("OBPI-0.0.14-01")
class TestLockCheck(unittest.TestCase):
    """Command-level tests for obpi_lock_check_cmd."""

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-05")
    def test_check_exits_0_when_held(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            write_lock(root, _make_lock(obpi_id="OBPI-0.0.14-01"))

            # Should return normally (exit 0) — no exception
            try:
                obpi_lock_check_cmd(obpi_id="OBPI-0.0.14-01", as_json=False)
            except SystemExit as exc:
                self.fail(f"check_cmd raised SystemExit({exc.code}) for a held lock")

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-05")
    def test_check_exits_1_when_free(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            with self.assertRaises(SystemExit) as ctx:
                obpi_lock_check_cmd(obpi_id="OBPI-0.0.14-01", as_json=False)
            self.assertEqual(ctx.exception.code, 1)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-05")
    def test_check_exits_1_when_expired(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            expired = _make_lock(
                obpi_id="OBPI-0.0.14-01",
                claimed_at=_expired_iso(200),
                ttl_minutes=120,
            )
            write_lock(root, expired)

            with self.assertRaises(SystemExit) as ctx:
                obpi_lock_check_cmd(obpi_id="OBPI-0.0.14-01", as_json=False)
            self.assertEqual(ctx.exception.code, 1)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-07")
    def test_check_json_held(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            write_lock(root, _make_lock(obpi_id="OBPI-0.0.14-01", ttl_minutes=120))

            with patch("builtins.print") as mock_print:
                obpi_lock_check_cmd(obpi_id="OBPI-0.0.14-01", as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "held")
                self.assertIn("elapsed_minutes", output)
                self.assertIn("remaining_minutes", output)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-07")
    def test_check_json_free(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            with patch("builtins.print") as mock_print:
                with self.assertRaises(SystemExit):
                    obpi_lock_check_cmd(obpi_id="OBPI-0.0.14-01", as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "free")
                self.assertEqual(output["obpi_id"], "OBPI-0.0.14-01")


# ---------------------------------------------------------------------------
# 7. TestLockList
# ---------------------------------------------------------------------------


@patch("gzkit.commands.obpi_lock.console", _quiet_console)
@covers("OBPI-0.0.14-01")
class TestLockList(unittest.TestCase):
    """Command-level tests for obpi_lock_list_cmd."""

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-06")
    @covers("REQ-0.0.14-01-07")
    def test_list_empty(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            # Ensure lock dir exists but is empty
            lock_dir(root)

            with patch("builtins.print") as mock_print:
                obpi_lock_list_cmd(adr_id=None, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["locks"], [])
                self.assertEqual(output["count"], 0)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-06")
    @covers("REQ-0.0.14-01-08")
    def test_list_reaps_expired_before_listing(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            expired = _make_lock(
                obpi_id="OBPI-0.0.14-01",
                claimed_at=_expired_iso(200),
                ttl_minutes=120,
            )
            write_lock(root, expired)

            with patch("builtins.print") as mock_print:
                obpi_lock_list_cmd(adr_id=None, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                # Expired lock must NOT appear in active locks
                active_ids = [lk["obpi_id"] for lk in output["locks"]]
                self.assertNotIn("OBPI-0.0.14-01", active_ids)
                # It should appear in reaped
                reaped_ids = [lk["obpi_id"] for lk in output["reaped"]]
                self.assertIn("OBPI-0.0.14-01", reaped_ids)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-06")
    @covers("REQ-0.0.14-01-07")
    def test_list_json_output(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            write_lock(root, _make_lock(obpi_id="OBPI-0.0.14-01"))
            write_lock(root, _make_lock(obpi_id="OBPI-0.0.14-02"))

            with patch("builtins.print") as mock_print:
                obpi_lock_list_cmd(adr_id=None, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["count"], 2)
                self.assertIn("locks", output)
                self.assertIn("reaped", output)

    @patch("gzkit.commands.obpi_lock.get_project_root")
    @patch("gzkit.commands.obpi_lock.ensure_initialized")
    @covers("REQ-0.0.14-01-06")
    def test_list_filters_by_adr(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = _setup_project(tmp)
            mock_root.return_value = root
            mock_init.return_value = _mock_config()

            write_lock(root, _make_lock(obpi_id="OBPI-0.0.14-01"))
            write_lock(root, _make_lock(obpi_id="OBPI-0.1.0-01"))

            with patch("builtins.print") as mock_print:
                obpi_lock_list_cmd(adr_id="ADR-0.0.14", as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["count"], 1)
                self.assertEqual(output["locks"][0]["obpi_id"], "OBPI-0.0.14-01")


if __name__ == "__main__":
    unittest.main()
