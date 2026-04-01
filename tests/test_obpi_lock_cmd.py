"""Tests for OBPI lock management CLI commands."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.obpi_lock_cmd import (
    _current_branch,
    _lock_dir,
    _lock_path,
    _resolve_agent,
    obpi_lock_claim_cmd,
    obpi_lock_release_cmd,
    obpi_lock_status_cmd,
)


class TestHelpers(unittest.TestCase):
    """Test helper functions."""

    def test_lock_dir_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _lock_dir(root)
            self.assertTrue(result.is_dir())
            self.assertEqual(result, root / ".gzkit" / "locks" / "obpi")

    def test_lock_path_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _lock_path(root, "OBPI-0.1.0-01")
            self.assertEqual(result.name, "OBPI-0.1.0-01.lock.json")

    def test_resolve_agent_claude_code(self):
        with patch.dict("os.environ", {"CLAUDE_CODE": "1"}, clear=False):
            self.assertEqual(_resolve_agent(), "claude-code")

    def test_resolve_agent_codex(self):
        with patch.dict("os.environ", {"CODEX_SANDBOX": "1"}, clear=False):
            self.assertEqual(_resolve_agent(), "codex")

    def test_resolve_agent_unknown(self):
        env = {
            k: v
            for k, v in __import__("os").environ.items()
            if k not in ("CLAUDE_CODE", "CODEX_SANDBOX")
        }
        with patch.dict("os.environ", env, clear=True):
            agent = _resolve_agent()
            self.assertTrue(agent.startswith("unknown-"))

    def test_current_branch_returns_string(self):
        branch = _current_branch()
        self.assertIsInstance(branch, str)
        self.assertTrue(len(branch) > 0)


class TestLockClaim(unittest.TestCase):
    """Test obpi_lock_claim_cmd."""

    def _setup_project(self, tmp: str) -> Path:
        root = Path(tmp)
        config_path = root / ".gzkit.json"
        config_path.write_text('{"project_name": "test", "mode": "full"}', encoding="utf-8")
        return root

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_claim_creates_lock_file(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            obpi_lock_claim_cmd(obpi_id="OBPI-0.1.0-01", ttl_minutes=120, as_json=False)

            lock_file = root / ".gzkit" / "locks" / "obpi" / "OBPI-0.1.0-01.lock.json"
            self.assertTrue(lock_file.exists())
            data = json.loads(lock_file.read_text(encoding="utf-8"))
            self.assertEqual(data["obpi_id"], "OBPI-0.1.0-01")
            self.assertEqual(data["ttl_minutes"], 120)

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_claim_json_output(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            with patch("builtins.print") as mock_print:
                obpi_lock_claim_cmd(obpi_id="OBPI-0.1.0-01", ttl_minutes=60, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "claimed")
                self.assertEqual(output["lock"]["obpi_id"], "OBPI-0.1.0-01")
                self.assertEqual(output["lock"]["ttl_minutes"], 60)

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_claim_same_agent_overwrites(self, mock_init, mock_root):
        """Same agent can re-claim its own lock."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            obpi_lock_claim_cmd(obpi_id="OBPI-0.1.0-01", ttl_minutes=120, as_json=False)
            # Second claim by same agent should succeed (overwrite)
            obpi_lock_claim_cmd(obpi_id="OBPI-0.1.0-01", ttl_minutes=240, as_json=False)

            lock_file = root / ".gzkit" / "locks" / "obpi" / "OBPI-0.1.0-01.lock.json"
            data = json.loads(lock_file.read_text(encoding="utf-8"))
            self.assertEqual(data["ttl_minutes"], 240)


class TestLockRelease(unittest.TestCase):
    """Test obpi_lock_release_cmd."""

    def _setup_project(self, tmp: str) -> Path:
        root = Path(tmp)
        config_path = root / ".gzkit.json"
        config_path.write_text('{"project_name": "test", "mode": "full"}', encoding="utf-8")
        return root

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_release_removes_lock(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            # Create lock first
            lock_dir = root / ".gzkit" / "locks" / "obpi"
            lock_dir.mkdir(parents=True, exist_ok=True)
            lock_file = lock_dir / "OBPI-0.1.0-01.lock.json"
            lock_file.write_text('{"obpi_id": "OBPI-0.1.0-01"}', encoding="utf-8")

            obpi_lock_release_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)
            self.assertFalse(lock_file.exists())

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_release_not_found(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            # Should not raise, just report not found
            obpi_lock_release_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_release_json_output(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            lock_dir = root / ".gzkit" / "locks" / "obpi"
            lock_dir.mkdir(parents=True, exist_ok=True)
            lock_file = lock_dir / "OBPI-0.1.0-01.lock.json"
            lock_file.write_text('{"obpi_id": "OBPI-0.1.0-01"}', encoding="utf-8")

            with patch("builtins.print") as mock_print:
                obpi_lock_release_cmd(obpi_id="OBPI-0.1.0-01", as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "released")

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_release_not_found_json(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            with patch("builtins.print") as mock_print:
                obpi_lock_release_cmd(obpi_id="OBPI-0.1.0-01", as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["status"], "not_found")


class TestLockStatus(unittest.TestCase):
    """Test obpi_lock_status_cmd."""

    def _setup_project(self, tmp: str) -> Path:
        root = Path(tmp)
        config_path = root / ".gzkit.json"
        config_path.write_text('{"project_name": "test", "mode": "full"}', encoding="utf-8")
        return root

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_status_no_locks(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            # Should not raise
            obpi_lock_status_cmd(adr_id=None, as_json=False)

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_status_json_empty(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            with patch("builtins.print") as mock_print:
                obpi_lock_status_cmd(adr_id=None, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["locks"], [])
                self.assertEqual(output["count"], 0)

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_status_shows_existing_lock(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            lock_dir = root / ".gzkit" / "locks" / "obpi"
            lock_dir.mkdir(parents=True, exist_ok=True)
            from datetime import UTC, datetime

            lock_data = {
                "obpi_id": "OBPI-0.1.0-01",
                "agent": "claude-code",
                "pid": 12345,
                "session_id": "test-session",
                "claimed_at": datetime.now(UTC).isoformat(),
                "branch": "main",
                "ttl_minutes": 120,
            }
            lock_file = lock_dir / "OBPI-0.1.0-01.lock.json"
            lock_file.write_text(json.dumps(lock_data), encoding="utf-8")

            with patch("builtins.print") as mock_print:
                obpi_lock_status_cmd(adr_id=None, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["count"], 1)
                self.assertEqual(output["locks"][0]["obpi_id"], "OBPI-0.1.0-01")
                self.assertFalse(output["locks"][0]["expired"])

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_status_filter_by_adr(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            lock_dir = root / ".gzkit" / "locks" / "obpi"
            lock_dir.mkdir(parents=True, exist_ok=True)
            from datetime import UTC, datetime

            for obpi_id in ["OBPI-0.1.0-01", "OBPI-0.2.0-01"]:
                lock_data = {
                    "obpi_id": obpi_id,
                    "agent": "claude-code",
                    "pid": 12345,
                    "session_id": "test",
                    "claimed_at": datetime.now(UTC).isoformat(),
                    "branch": "main",
                    "ttl_minutes": 120,
                }
                lock_file = lock_dir / f"{obpi_id}.lock.json"
                lock_file.write_text(json.dumps(lock_data), encoding="utf-8")

            with patch("builtins.print") as mock_print:
                obpi_lock_status_cmd(adr_id="ADR-0.1.0", as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["count"], 1)
                self.assertEqual(output["locks"][0]["obpi_id"], "OBPI-0.1.0-01")

    @patch("gzkit.commands.common.get_project_root")
    @patch("gzkit.commands.common.ensure_initialized")
    def test_status_expired_lock(self, mock_init, mock_root):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._setup_project(tmp)
            mock_root.return_value = root

            lock_dir = root / ".gzkit" / "locks" / "obpi"
            lock_dir.mkdir(parents=True, exist_ok=True)
            from datetime import UTC, datetime, timedelta

            expired_time = (datetime.now(UTC) - timedelta(minutes=200)).isoformat()
            lock_data = {
                "obpi_id": "OBPI-0.1.0-01",
                "agent": "claude-code",
                "pid": 12345,
                "session_id": "test",
                "claimed_at": expired_time,
                "branch": "main",
                "ttl_minutes": 120,
            }
            lock_file = lock_dir / "OBPI-0.1.0-01.lock.json"
            lock_file.write_text(json.dumps(lock_data), encoding="utf-8")

            with patch("builtins.print") as mock_print:
                obpi_lock_status_cmd(adr_id=None, as_json=True)
                output = json.loads(mock_print.call_args[0][0])
                self.assertEqual(output["count"], 1)
                self.assertTrue(output["locks"][0]["expired"])


if __name__ == "__main__":
    unittest.main()
