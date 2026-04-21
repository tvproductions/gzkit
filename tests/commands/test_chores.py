import json
import sys
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init

# Forward-slash executable path for shlex.split compatibility on Windows.
_PYTHON = '"' + sys.executable.replace("\\", "/") + '"'


def _write_v2_registry(chores: list[dict[str, object]]) -> None:
    """Write a v2.0 chores registry with the given chore pointers."""
    registry_path = Path("config/gzkit.chores.json")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "specVersion": "2.0",
        "description": "Test chore registry",
        "project": {
            "name": "gzkit",
            "root": ".",
            "choresDir": "ops/chores",
        },
        "lanes": {
            "lite": {"timeoutSeconds": 120},
            "medium": {"timeoutSeconds": 300},
            "heavy": {"timeoutSeconds": 900},
        },
        "chores": chores,
    }
    registry_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_acceptance(chore_path: str, criteria: list[dict[str, object]]) -> None:
    """Write an acceptance.json inside the given chore directory."""
    acceptance_dir = Path(chore_path)
    acceptance_dir.mkdir(parents=True, exist_ok=True)
    acceptance_file = acceptance_dir / "acceptance.json"
    payload = {"criteria": criteria}
    acceptance_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _setup_demo_chore(
    slug: str = "demo-check",
    title: str = "Demo quality check",
    lane: str = "lite",
    chore_path: str = "ops/chores/demo-check",
    command: str | None = None,
    expected: int = 0,
    vendor: str | None = None,
) -> None:
    """Create a complete v2.0 chore (registry pointer + acceptance.json)."""
    cmd = command or f'{_PYTHON} -c "print(42)"'
    pointer: dict[str, object] = {
        "slug": slug,
        "title": title,
        "version": "1.0.0",
        "path": chore_path,
        "lane": lane,
    }
    if vendor is not None:
        pointer["vendor"] = vendor
    _write_v2_registry([pointer])
    _write_acceptance(
        chore_path,
        [
            {
                "type": "exitCodeEquals",
                "command": cmd,
                "expected": expected,
            },
        ],
    )


class TestChoresCommands(unittest.TestCase):
    """Behavior tests for gz chores v2.0 commands."""

    def test_chores_list_reads_registry(self) -> None:
        """chores list prints configured chores from v2.0 registry."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore()

            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("demo-check", result.output)

    def test_chores_plan_missing_registry_shows_blockers(self) -> None:
        """chores plan fails closed when registry is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["chores", "plan", "quality-check"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("BLOCKERS", result.output)
            self.assertIn("config/gzkit.chores.json", result.output)

    def test_chores_rejects_v1_schema(self) -> None:
        """Registry loader rejects v1 schema format."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            registry_path = Path("config/gzkit.chores.json")
            registry_path.parent.mkdir(parents=True, exist_ok=True)
            registry_path.write_text(
                json.dumps(
                    {
                        "schema": "gzkit.chores.v1",
                        "version": 1,
                        "chores": [{"slug": "x", "title": "X", "lane": "lite"}],
                    }
                ),
                encoding="utf-8",
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("specVersion", result.output)

    def test_chores_rejects_shell_operators_in_criteria(self) -> None:
        """Acceptance criteria reject commands with shell operators."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = "ops/chores/shell-test"
            _write_v2_registry(
                [
                    {
                        "slug": "shell-test",
                        "title": "Shell test",
                        "version": "1.0.0",
                        "path": chore_path,
                        "lane": "lite",
                    },
                ]
            )
            _write_acceptance(
                chore_path,
                [
                    {
                        "type": "exitCodeEquals",
                        "command": "echo hello && echo world",
                        "expected": 0,
                    },
                ],
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("shell operators", result.output)

    def test_chores_rejects_missing_acceptance_json(self) -> None:
        """Registry loader fails when acceptance.json is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = "ops/chores/no-acceptance"
            Path(chore_path).mkdir(parents=True, exist_ok=True)
            _write_v2_registry(
                [
                    {
                        "slug": "no-acceptance",
                        "title": "No acceptance",
                        "version": "1.0.0",
                        "path": chore_path,
                        "lane": "lite",
                    },
                ]
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("acceptance.json", result.output)

    def test_chores_run_executes_criteria_and_writes_log(self) -> None:
        """chore run executes acceptance criteria and writes log."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="demo-run",
                chore_path="ops/chores/demo-run",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "run", "demo-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Chore completed", result.output)

            log_path = Path("ops/chores/demo-run/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            log_content = log_path.read_text(encoding="utf-8")
            self.assertIn("Status: PASS", log_content)

    def test_chores_run_timeout_returns_nonzero(self) -> None:
        """chore run returns non-zero for timed out criterion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="slow-run",
                chore_path="ops/chores/slow-run",
                command=f'{_PYTHON} -c "import time; time.sleep(5)"',
            )
            # Patch lane timeout to 1s for test speed
            reg_path = Path("config/gzkit.chores.json")
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
            reg["lanes"]["lite"]["timeoutSeconds"] = 1
            reg_path.write_text(json.dumps(reg), encoding="utf-8")

            result = runner.invoke(main, ["chores", "run", "slow-run"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Timed out", result.output)

            log_path = Path("ops/chores/slow-run/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_run_nonzero_exit_returns_nonzero(self) -> None:
        """chore run fails when criterion exit code doesn't match expected."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="failing-run",
                chore_path="ops/chores/failing-run",
                command=f'{_PYTHON} -c "import sys; sys.exit(3)"',
            )

            result = runner.invoke(main, ["chores", "run", "failing-run"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("criterion failed", result.output)

            log_path = Path("ops/chores/failing-run/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_run_missing_executable(self) -> None:
        """chore run fails closed when criterion executable is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="missing-exe",
                chore_path="ops/chores/missing-exe",
                command="this-executable-should-not-exist-gzkit",
            )

            result = runner.invoke(main, ["chores", "run", "missing-exe"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Missing executable", result.output)

            log_path = Path("ops/chores/missing-exe/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_audit_reports_log_presence(self) -> None:
        """chore audit reports log status per chore."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="auditable",
                chore_path="ops/chores/auditable",
                command=f'{_PYTHON} -c "print(42)"',
            )

            run_result = runner.invoke(main, ["chores", "run", "auditable"])
            self.assertEqual(run_result.exit_code, 0)

            audit_result = runner.invoke(
                main,
                ["chores", "audit", "--slug", "auditable"],
            )
            self.assertEqual(audit_result.exit_code, 0)
            self.assertIn("auditable", audit_result.output)
            self.assertIn("yes", audit_result.output.lower())

    def test_chores_supports_medium_lane(self) -> None:
        """Medium lane chores are accepted by the registry loader."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="medium-chore",
                chore_path="ops/chores/medium-chore",
                lane="medium",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("medium-chore", result.output)
            self.assertIn("medium", result.output)

    def test_chores_vendor_field_parsed_and_displayed(self) -> None:
        """Vendor field is parsed from registry and shown in list output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            Path(".claude").mkdir()
            _setup_demo_chore(
                slug="vendor-chore",
                chore_path="ops/chores/vendor-chore",
                vendor="claude",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("vendor-chore", result.output)
            self.assertIn("claude", result.output)

    def test_chores_vendor_filtered_when_no_harness(self) -> None:
        """Vendor-scoped chores are hidden when harness is not active."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="vendor-chore",
                chore_path="ops/chores/vendor-chore",
                vendor="claude",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertNotIn("vendor-chore", result.output)


class TestChoresFileExistsCriterion(unittest.TestCase):
    """fileExists criterion parses from `path` and evaluates existence (GHI #269)."""

    def _write_file_exists_chore(self, chore_path: str, slug: str, target_path: str) -> None:
        _write_v2_registry(
            [
                {
                    "slug": slug,
                    "title": f"File exists: {target_path}",
                    "version": "1.0.0",
                    "path": chore_path,
                    "lane": "lite",
                }
            ]
        )
        _write_acceptance(
            chore_path,
            [{"type": "fileExists", "path": target_path}],
        )

    def test_fileExists_parses_without_command(self) -> None:
        """acceptance.json with type=fileExists and path parses without requiring command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            self._write_file_exists_chore(
                chore_path="ops/chores/fe-parse",
                slug="fe-parse",
                target_path="README.md",
            )
            # README.md is created by _quick_init, but parse step does not need it.
            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("fe-parse", result.output)

    def test_fileExists_missing_path_reports_blocker(self) -> None:
        """acceptance.json with type=fileExists but no path fails parse with blocker."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = "ops/chores/fe-blocker"
            _write_v2_registry(
                [
                    {
                        "slug": "fe-blocker",
                        "title": "Missing path",
                        "version": "1.0.0",
                        "path": chore_path,
                        "lane": "lite",
                    }
                ]
            )
            _write_acceptance(chore_path, [{"type": "fileExists"}])

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("BLOCKERS", result.output)
            self.assertIn("path", result.output)
            self.assertIn("fileExists", result.output)

    def test_fileExists_run_passes_when_file_present(self) -> None:
        """chore run with fileExists criterion passes when the target file exists."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = "ops/chores/fe-present"
            target = "ops/chores/fe-present/sentinel.txt"
            self._write_file_exists_chore(
                chore_path=chore_path,
                slug="fe-present",
                target_path=target,
            )
            Path(target).write_text("present", encoding="utf-8")

            result = runner.invoke(main, ["chores", "run", "fe-present"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Chore completed", result.output)

            log_path = Path("ops/chores/fe-present/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            log_content = log_path.read_text(encoding="utf-8")
            self.assertIn("Status: PASS", log_content)

    def test_fileExists_run_fails_when_file_missing(self) -> None:
        """chore run with fileExists criterion fails when the target file is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = "ops/chores/fe-missing"
            target = "ops/chores/fe-missing/never-here.txt"
            self._write_file_exists_chore(
                chore_path=chore_path,
                slug="fe-missing",
                target_path=target,
            )

            result = runner.invoke(main, ["chores", "run", "fe-missing"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("file not found", result.output)

            log_path = Path("ops/chores/fe-missing/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))
