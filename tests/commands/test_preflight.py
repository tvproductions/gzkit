import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestPreflightCommand(unittest.TestCase):
    """Tests for the gz preflight command."""

    def test_clean_state_exits_zero(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("clean", result.output.lower())

    def test_detects_stale_pipeline_marker(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            stale_time = (datetime.now(UTC) - timedelta(hours=5)).isoformat()
            marker = {
                "obpi_id": "OBPI-0.1.0-01",
                "updated_at": stale_time,
            }
            (plans_dir / ".pipeline-active-OBPI-0.1.0-01.json").write_text(
                json.dumps(marker), encoding="utf-8"
            )
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("OBPI-0.1.0-01", result.output)
            self.assertIn("marker", result.output.lower())

    def test_detects_expired_lock(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            locks_dir = Path(".gzkit/locks/obpi")
            locks_dir.mkdir(parents=True, exist_ok=True)
            expired_time = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
            lock = {
                "obpi_id": "OBPI-0.2.0-01",
                "claimed_at": expired_time,
                "ttl_minutes": 120,
                "agent": "claude-code",
                "pid": 0,
                "session_id": "test",
                "branch": "main",
            }
            (locks_dir / "OBPI-0.2.0-01.lock.json").write_text(json.dumps(lock), encoding="utf-8")
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("OBPI-0.2.0-01", result.output)
            self.assertIn("lock", result.output.lower())

    def test_detects_orphan_receipt(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            receipt = {
                "obpi_id": "OBPI-0.3.0-01",
                "verdict": "PASS",
                "timestamp": "2026-03-01T12:00:00Z",
            }
            (plans_dir / ".plan-audit-receipt-OBPI-0.3.0-01.json").write_text(
                json.dumps(receipt), encoding="utf-8"
            )
            # No matching plan file or marker — receipt is orphaned
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("OBPI-0.3.0-01", result.output)
            self.assertIn("receipt", result.output.lower())

    def test_apply_removes_stale_artifacts(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            stale_time = (datetime.now(UTC) - timedelta(hours=5)).isoformat()
            marker_path = plans_dir / ".pipeline-active-OBPI-0.1.0-01.json"
            marker_path.write_text(
                json.dumps({"obpi_id": "OBPI-0.1.0-01", "updated_at": stale_time}),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(marker_path.exists())

    def test_apply_removes_orphan_receipt(self) -> None:
        """GHI #139: orphan plan-audit receipts are deleted by --apply."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            plans_dir = Path(".claude/plans")
            plans_dir.mkdir(parents=True, exist_ok=True)
            receipt_path = plans_dir / ".plan-audit-receipt-OBPI-0.3.0-01.json"
            receipt_path.write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-0.3.0-01",
                        "verdict": "PASS",
                        "timestamp": "2026-03-01T12:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(receipt_path.exists())

    def test_apply_removes_expired_lock(self) -> None:
        """GHI #139: expired OBPI locks are deleted by --apply."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            locks_dir = Path(".gzkit/locks/obpi")
            locks_dir.mkdir(parents=True, exist_ok=True)
            expired_time = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
            lock_path = locks_dir / "OBPI-0.2.0-01.lock.json"
            lock_path.write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-0.2.0-01",
                        "claimed_at": expired_time,
                        "ttl_minutes": 120,
                        "agent": "claude-code",
                        "pid": 0,
                        "session_id": "test",
                        "branch": "main",
                    }
                ),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(lock_path.exists())

    def test_json_output(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight", "--json"])
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.output)
            self.assertIn("stale_markers", data)
            self.assertIn("orphan_receipts", data)
            self.assertIn("expired_locks", data)

    def test_no_issues_with_apply_exits_zero(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
