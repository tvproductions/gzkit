import json
import sys
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner


def _write_registry(payload: dict[str, object]) -> None:
    registry_path = Path("config/gzkit.chores.json")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class TestChoresCommands(unittest.TestCase):
    """Behavior tests for gz chores commands."""

    def test_chores_list_reads_registry(self) -> None:
        """chores list prints configured chores."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            _write_registry(
                {
                    "schema": "gzkit.chores.v1",
                    "version": 1,
                    "chores": [
                        {
                            "slug": "demo-check",
                            "title": "Demo quality check",
                            "lane": "lite",
                            "description": "demo",
                            "steps": [
                                {
                                    "name": "echo",
                                    "argv": [sys.executable, "-c", "print('ok')"],
                                    "timeout_seconds": 10,
                                }
                            ],
                            "evidence": {"commands": ["uv run gz test"]},
                            "acceptance": {"checks": ["step exits zero"]},
                        }
                    ],
                }
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("demo-check", result.output)

    def test_chores_plan_missing_registry_shows_blockers(self) -> None:
        """chores plan fails closed when registry is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["chores", "plan", "quality-check"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("BLOCKERS", result.output)
            self.assertIn("config/gzkit.chores.json", result.output)

    def test_chores_rejects_shell_string_steps(self) -> None:
        """Registry loader rejects step.command shell strings."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            _write_registry(
                {
                    "schema": "gzkit.chores.v1",
                    "version": 1,
                    "chores": [
                        {
                            "slug": "unsafe-step",
                            "title": "Unsafe step",
                            "lane": "lite",
                            "steps": [{"name": "bad", "command": "echo nope"}],
                            "evidence": {"commands": ["echo nope"]},
                            "acceptance": {"checks": ["no shell strings"]},
                        }
                    ],
                }
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("argv arrays only", result.output)

    def test_chores_run_executes_declared_steps_and_writes_log(self) -> None:
        """chore run executes argv-only steps and appends deterministic log path."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            _write_registry(
                {
                    "schema": "gzkit.chores.v1",
                    "version": 1,
                    "chores": [
                        {
                            "slug": "demo-run",
                            "title": "Demo run",
                            "lane": "lite",
                            "steps": [
                                {
                                    "name": "print-ok",
                                    "argv": [sys.executable, "-c", "print('ok')"],
                                    "timeout_seconds": 10,
                                }
                            ],
                            "evidence": {"commands": ["python -c print"]},
                            "acceptance": {"checks": ["stdout contains ok"]},
                        }
                    ],
                }
            )

            result = runner.invoke(main, ["chores", "run", "demo-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Chore completed", result.output)

            log_path = Path("design/briefs/chores/CHORE-demo-run/logs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            log_content = log_path.read_text(encoding="utf-8")
            self.assertIn("Status: PASS", log_content)
            self.assertIn("[print-ok] stdout:", log_content)

    def test_chores_run_timeout_returns_nonzero(self) -> None:
        """chore run returns non-zero for timed out step and records log."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            _write_registry(
                {
                    "schema": "gzkit.chores.v1",
                    "version": 1,
                    "chores": [
                        {
                            "slug": "slow-run",
                            "title": "Slow run",
                            "lane": "lite",
                            "steps": [
                                {
                                    "name": "sleep",
                                    "argv": [sys.executable, "-c", "import time; time.sleep(2)"],
                                    "timeout_seconds": 1,
                                }
                            ],
                            "evidence": {"commands": ["sleep command"]},
                            "acceptance": {"checks": ["timeout is enforced"]},
                        }
                    ],
                }
            )

            result = runner.invoke(main, ["chores", "run", "slow-run"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("timed out", result.output.lower())

            log_path = Path("design/briefs/chores/CHORE-slow-run/logs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_audit_reports_log_presence(self) -> None:
        """chore audit reports log status per chore."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            _write_registry(
                {
                    "schema": "gzkit.chores.v1",
                    "version": 1,
                    "chores": [
                        {
                            "slug": "auditable",
                            "title": "Auditable chore",
                            "lane": "lite",
                            "steps": [
                                {
                                    "name": "print-ok",
                                    "argv": [sys.executable, "-c", "print('ok')"],
                                    "timeout_seconds": 10,
                                }
                            ],
                            "evidence": {"commands": ["python -c print"]},
                            "acceptance": {"checks": ["stdout contains ok"]},
                        }
                    ],
                }
            )

            run_result = runner.invoke(main, ["chores", "run", "auditable"])
            self.assertEqual(run_result.exit_code, 0)

            audit_result = runner.invoke(main, ["chores", "audit", "--slug", "auditable"])
            self.assertEqual(audit_result.exit_code, 0)
            self.assertIn("auditable", audit_result.output)
            self.assertIn("yes", audit_result.output.lower())
