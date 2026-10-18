import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.cli import main
from gzkit.pipeline_markers import STALE_MARKER_HOURS
from tests.commands.common import CliRunner, _quick_init, hostile_console, parse_json_document


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
            stale_time = (datetime.now(UTC) - timedelta(hours=STALE_MARKER_HOURS + 1)).isoformat()
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
        """An expired orphan session lock is an issue; a work lock is not (never evict).

        Re-seated 2026-10-18 onto the one lock still reaped, the ``mx-session``
        lock of a closed hangar: an expired work lock is booked and stays held
        (operator ruling, worked example 6 of attested-req-subject-retirement.md;
        covered in test_preflight_expired_leases.py).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            locks_dir = Path(".gzkit/locks/obpi")
            locks_dir.mkdir(parents=True, exist_ok=True)
            expired_time = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
            lock = {
                "obpi_id": "mx-session",
                "claimed_at": expired_time,
                "ttl_minutes": 120,
                "agent": "claude-code",
                "pid": 0,
                "session_id": "test",
                "branch": "main",
            }
            (locks_dir / "mx-session.lock.json").write_text(json.dumps(lock), encoding="utf-8")
            result = runner.invoke(main, ["preflight"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("mx-session", result.output)
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
            stale_time = (datetime.now(UTC) - timedelta(hours=STALE_MARKER_HOURS + 1)).isoformat()
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
        """GHI #139: an expired orphan session lock is deleted by --apply.

        Re-seated 2026-10-18 from a work lock, which is now booked and kept held.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            locks_dir = Path(".gzkit/locks/obpi")
            locks_dir.mkdir(parents=True, exist_ok=True)
            expired_time = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
            lock_path = locks_dir / "mx-session.lock.json"
            lock_path.write_text(
                json.dumps(
                    {
                        "obpi_id": "mx-session",
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

    def test_apply_reaps_expired_lock_with_audit_trail(self) -> None:
        """Defect 4: --apply routes expired-lock cleanup through the canonical
        token-block reaper, not a silent unlink. The surrender MUST leave an
        ``obpi_lock_released`` ledger event and an ``abandoned_by_reaper``
        register entry (token-block-discipline.md § Sub-Invariant 3). Re-seated
        2026-10-18 onto the orphan session lock, the one lock still reaped."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            locks_dir = Path(".gzkit/locks/obpi")
            locks_dir.mkdir(parents=True, exist_ok=True)
            expired_time = (datetime.now(UTC) - timedelta(hours=30)).isoformat()
            lock_path = locks_dir / "mx-session.lock.json"
            lock_path.write_text(
                json.dumps(
                    {
                        "obpi_id": "mx-session",
                        "claimed_at": expired_time,
                        "ttl_minutes": 1440,
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
            # The lock is surrendered (file gone) ...
            self.assertFalse(lock_path.exists())
            # ... but never silently: a release event is in the ledger ...
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("obpi_lock_released", ledger_text)
            self.assertIn("mx-session", ledger_text)
            # ... and a reaping register entry exists on disk.
            register_entries = list(Path(".gzkit/locks/exchange").glob("*mx-session*reaped*.md"))
            self.assertTrue(
                register_entries,
                "reaping must write an abandoned_by_reaper register entry",
            )

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

    def test_json_output_survives_a_hostile_console(self) -> None:
        """GHI #1010: `--json` stdout is the document, never console-rendered text."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            with hostile_console():
                result = runner.invoke(main, ["preflight", "--json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            data = parse_json_document(self, result.output)
            self.assertEqual(data["stale_markers"], [])

    def test_no_issues_with_apply_exits_zero(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            result = runner.invoke(main, ["preflight", "--apply"])
            self.assertEqual(result.exit_code, 0)
