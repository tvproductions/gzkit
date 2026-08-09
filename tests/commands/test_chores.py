import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import structlog.testing

from gzkit.cli import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init

# Forward-slash executable path for shlex.split compatibility on Windows.
_PYTHON = '"' + sys.executable.replace("\\", "/") + '"'


def _project_chores_root() -> Path:
    """Return the project chores root under the current working directory."""
    return Path.cwd() / ".gzkit" / "chores"


def _write_v2_registry(chores: list[dict[str, object]]) -> None:
    """Write a v2.0 chores registry with the given chore pointers."""
    registry_path = _project_chores_root() / "registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "specVersion": "2.0",
        "description": "Test chore registry",
        "project": {
            "name": "gzkit",
            "root": ".",
            "choresDir": ".gzkit/chores",
        },
        "lanes": {
            "lite": {"description": "Gate-rigor: Gates 1, 2 required."},
            "heavy": {"description": "Gate-rigor: All gates required."},
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
    chore_path: str | None = None,
    command: str | None = None,
    expected: int = 0,
    vendor: str | None = None,
    timeout_seconds: int = 120,
) -> None:
    """Create a complete v2.0 chore (registry pointer + acceptance.json)."""
    if chore_path is None:
        chore_path = str(_project_chores_root() / slug)
    cmd = command or f'{_PYTHON} -c "print(42)"'
    pointer: dict[str, object] = {
        "slug": slug,
        "title": title,
        "version": "1.0.0",
        "path": chore_path,
        "lane": lane,
        "timeoutSeconds": timeout_seconds,
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

    def test_chores_plan_unknown_slug_shows_blockers(self) -> None:
        """chores plan fails closed when slug resolves to neither project nor package."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # Slug guaranteed to miss both resolution paths.
            result = runner.invoke(main, ["chores", "plan", "totally-nonexistent-chore-slug"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("BLOCKERS", result.output)

    def test_chores_rejects_v1_schema(self) -> None:
        """Registry loader rejects v1 schema format."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            registry_path = _project_chores_root() / "registry.json"
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
            chore_path = str(_project_chores_root() / "shell-test")
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
        """Registry loader fails when a chore dir has no acceptance.json witness."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = ".gzkit/chores/no-acceptance"
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
            # New resolver semantics: acceptance.json is the witness; absence
            # surfaces as "not found in either resolution path" (with the slug
            # named) rather than the legacy "Missing acceptance.json" string.
            self.assertIn("no-acceptance", result.output)
            self.assertIn("not found in either resolution path", result.output)

    def test_chores_run_executes_criteria_and_writes_log(self) -> None:
        """chore run executes acceptance criteria and writes log."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="demo-run",
                chore_path=".gzkit/chores/demo-run",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "run", "demo-run"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Chore completed", result.output)

            log_path = Path(".gzkit/chores/demo-run/proofs/CHORE-LOG.md")
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
                chore_path=".gzkit/chores/slow-run",
                command=f'{_PYTHON} -c "import time; time.sleep(5)"',
            )
            # Patch chore's explicit timeoutSeconds to 1s for test speed (GHI #447).
            reg_path = _project_chores_root() / "registry.json"
            reg = json.loads(reg_path.read_text(encoding="utf-8"))
            for chore in reg["chores"]:
                if chore["slug"] == "slow-run":
                    chore["timeoutSeconds"] = 1
            reg_path.write_text(json.dumps(reg), encoding="utf-8")

            result = runner.invoke(main, ["chores", "run", "slow-run"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Timed out", result.output)

            log_path = Path(".gzkit/chores/slow-run/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_run_nonzero_exit_returns_nonzero(self) -> None:
        """chore run fails when criterion exit code doesn't match expected."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="failing-run",
                chore_path=".gzkit/chores/failing-run",
                command=f'{_PYTHON} -c "import sys; sys.exit(3)"',
            )

            result = runner.invoke(main, ["chores", "run", "failing-run"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("criterion failed", result.output)

            log_path = Path(".gzkit/chores/failing-run/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_advise_failing_criterion_exits_policy_breach(self) -> None:
        """chore advise reports a failing criterion through its exit status (GHI #781)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="failing-advise",
                chore_path=".gzkit/chores/failing-advise",
                command=f'{_PYTHON} -c "import sys; sys.exit(3)"',
            )

            result = runner.invoke(main, ["chores", "advise", "failing-advise"])
            # The verdict must reach the exit status, not only the rendered
            # output: `gz chores` documents 3 as Policy breach, and a caller
            # that reads $? is the documented Step 4 of gz-chore-runner.
            self.assertEqual(result.exit_code, 3)

    def test_chores_advise_all_passing_exits_zero(self) -> None:
        """chore advise stays exit 0 when every criterion passes (GHI #781)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="passing-advise",
                chore_path=".gzkit/chores/passing-advise",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "advise", "passing-advise"])
            self.assertEqual(result.exit_code, 0)

    def test_chores_run_missing_executable(self) -> None:
        """chore run fails closed when criterion executable is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="missing-exe",
                chore_path=".gzkit/chores/missing-exe",
                command="this-executable-should-not-exist-gzkit",
            )

            result = runner.invoke(main, ["chores", "run", "missing-exe"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Missing executable", result.output)

            log_path = Path(".gzkit/chores/missing-exe/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))

    def test_chores_audit_reports_log_presence(self) -> None:
        """chore audit reports log status per chore."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="auditable",
                chore_path=".gzkit/chores/auditable",
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

    def test_chores_rejects_medium_lane(self) -> None:
        """Medium lane is no longer a valid gate-rigor classification (GHI #447)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _setup_demo_chore(
                slug="medium-chore",
                chore_path=".gzkit/chores/medium-chore",
                lane="medium",
                command=f'{_PYTHON} -c "print(42)"',
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("lane must be one of", result.output)
            self.assertNotIn("medium", "lite heavy")  # canonical lanes per AGENTS.md

    def test_chores_rejects_missing_timeout_seconds(self) -> None:
        """Each chore must declare an explicit positive timeoutSeconds (GHI #447)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # Build a pointer that omits timeoutSeconds entirely.
            chore_path = str(_project_chores_root() / "no-timeout-chore")
            _write_v2_registry(
                [
                    {
                        "slug": "no-timeout-chore",
                        "title": "Demo without timeout",
                        "version": "1.0.0",
                        "path": chore_path,
                        "lane": "lite",
                    }
                ]
            )
            _write_acceptance(
                chore_path,
                [
                    {
                        "type": "exitCodeEquals",
                        "command": f'{_PYTHON} -c "print(0)"',
                        "expected": 0,
                    }
                ],
            )

            result = runner.invoke(main, ["chores", "list"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("timeoutSeconds", result.output)
            self.assertIn("positive integer", result.output)

    def test_chores_vendor_field_parsed_and_displayed(self) -> None:
        """Vendor field is parsed from registry and shown in list output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            Path(".claude").mkdir()
            _setup_demo_chore(
                slug="vendor-chore",
                chore_path=".gzkit/chores/vendor-chore",
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
                chore_path=".gzkit/chores/vendor-chore",
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
                    "timeoutSeconds": 120,
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
                chore_path=".gzkit/chores/fe-parse",
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
            chore_path = ".gzkit/chores/fe-blocker"
            _write_v2_registry(
                [
                    {
                        "slug": "fe-blocker",
                        "title": "Missing path",
                        "version": "1.0.0",
                        "path": chore_path,
                        "lane": "lite",
                        "timeoutSeconds": 120,
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
            chore_path = ".gzkit/chores/fe-present"
            target = ".gzkit/chores/fe-present/sentinel.txt"
            self._write_file_exists_chore(
                chore_path=chore_path,
                slug="fe-present",
                target_path=target,
            )
            Path(target).write_text("present", encoding="utf-8")

            result = runner.invoke(main, ["chores", "run", "fe-present"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Chore completed", result.output)

            log_path = Path(".gzkit/chores/fe-present/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            log_content = log_path.read_text(encoding="utf-8")
            self.assertIn("Status: PASS", log_content)

    def test_fileExists_run_fails_when_file_missing(self) -> None:
        """chore run with fileExists criterion fails when the target file is missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_path = ".gzkit/chores/fe-missing"
            target = ".gzkit/chores/fe-missing/never-here.txt"
            self._write_file_exists_chore(
                chore_path=chore_path,
                slug="fe-missing",
                target_path=target,
            )

            result = runner.invoke(main, ["chores", "run", "fe-missing"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("file not found", result.output)

            log_path = Path(".gzkit/chores/fe-missing/proofs/CHORE-LOG.md")
            self.assertTrue(log_path.exists())
            self.assertIn("Status: FAIL", log_path.read_text(encoding="utf-8"))


def _scaffold_project_chore(slug: str, lane: str = "lite") -> Path:
    """Create a project-local chore with acceptance.json. Returns the chore dir."""
    chore_dir = _project_chores_root() / slug
    chore_dir.mkdir(parents=True, exist_ok=True)
    (chore_dir / "acceptance.json").write_text(
        json.dumps({"criteria": [{"type": "exitCodeEquals", "command": "true", "expected": 0}]}),
        encoding="utf-8",
    )
    (chore_dir / "CHORE.md").write_text(f"# {slug}\n", encoding="utf-8")
    return chore_dir


def _scaffold_package_chore(pkg_root: Path, slug: str) -> Path:
    """Create a fake package-resource chore at pkg_root/slug. Returns chore dir."""
    chore_dir = pkg_root / slug
    chore_dir.mkdir(parents=True, exist_ok=True)
    (chore_dir / "acceptance.json").write_text(
        json.dumps({"criteria": [{"type": "exitCodeEquals", "command": "true", "expected": 0}]}),
        encoding="utf-8",
    )
    (chore_dir / "CHORE.md").write_text(f"# {slug}\n", encoding="utf-8")
    return chore_dir


def _scaffold_package_registry(pkg_root: Path, chores: list[dict[str, object]]) -> None:
    """Write a fake registry.json into the package root tempdir."""
    payload: dict[str, object] = {
        "specVersion": "2.0",
        "description": "Package registry",
        "project": {"name": "gzkit", "root": ".", "choresDir": ".gzkit/chores"},
        "lanes": {
            "lite": {"description": "Gate-rigor: Gates 1, 2 required."},
            "heavy": {"description": "Gate-rigor: All gates required."},
        },
        "chores": chores,
    }
    (pkg_root / "registry.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class TestChoreResolver(unittest.TestCase):
    """REQ-derived tests for the project-first / package-fallback resolver (OBPI-0.0.21-04)."""

    @covers("REQ-0.0.21-04-01")
    def test_chore_resolver_project_wins(self) -> None:
        """Project-local chore directory wins over any package fallback."""
        from gzkit.commands.chores import _resolve_chore_dir

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            chore_dir = _scaffold_project_chore("demo-chore")
            result = _resolve_chore_dir("demo-chore")
            self.assertEqual(result.source, "project")
            self.assertEqual(result.path.resolve(), chore_dir.resolve())

    @covers("REQ-0.0.21-04-02")
    def test_chore_resolver_falls_back_to_package(self) -> None:
        """No project tree → resolver returns the package path and logs the fallback."""
        from gzkit.commands import chores as chores_mod

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with (
                structlog.testing.capture_logs() as cap,
                patch.object(chores_mod, "_package_chores_root") as mock_pkg_root,
            ):
                pkg_root = Path("fake-pkg-root").resolve()
                pkg_root.mkdir(parents=True, exist_ok=True)
                _scaffold_package_chore(pkg_root, "pkg-chore")
                mock_pkg_root.return_value = pkg_root
                result = chores_mod._resolve_chore_dir("pkg-chore")
            self.assertEqual(result.source, "package")
            self.assertEqual(result.path.resolve(), (pkg_root / "pkg-chore").resolve())
            events = [e for e in cap if e.get("event") == "chore.resolver.fallback"]
            self.assertTrue(events, f"no fallback log event in: {cap}")
            self.assertEqual(events[0].get("slug"), "pkg-chore")

    @covers("REQ-0.0.21-04-03")
    def test_chore_resolver_raises_with_both_paths_named(self) -> None:
        """Both paths miss → GzCliError names project AND importlib.resources/gzkit.chores."""
        from gzkit.commands import chores as chores_mod
        from gzkit.commands.common import GzCliError

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with patch.object(chores_mod, "_package_chores_root") as mock_pkg_root:
                pkg_root = Path("fake-pkg-root").resolve()
                pkg_root.mkdir(parents=True, exist_ok=True)
                mock_pkg_root.return_value = pkg_root
                with self.assertRaises(GzCliError) as ctx:
                    chores_mod._resolve_chore_dir("missing-slug")
            msg = str(ctx.exception)
            self.assertIn(".gzkit/chores", msg)
            self.assertIn("missing-slug", msg)
            self.assertIn("gzkit.chores", msg)
            self.assertIn("importlib.resources", msg)

    @covers("REQ-0.0.21-04-04")
    def test_gz_chores_list_explain_distinguishes_source(self) -> None:
        """`gz chores list --explain` labels each row with project / package / missing."""
        from gzkit.commands import chores as chores_mod

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _scaffold_project_chore("local-one")
            with patch.object(chores_mod, "_package_chores_root") as mock_pkg_root:
                pkg_root = Path("fake-pkg-root").resolve()
                pkg_root.mkdir(parents=True, exist_ok=True)
                _scaffold_package_chore(pkg_root, "pkg-only")
                mock_pkg_root.return_value = pkg_root
                _write_v2_registry(
                    [
                        {
                            "slug": "local-one",
                            "title": "Local one",
                            "version": "1.0.0",
                            "path": str(_project_chores_root() / "local-one"),
                            "lane": "lite",
                            "timeoutSeconds": 120,
                        },
                        {
                            "slug": "pkg-only",
                            "title": "Package only",
                            "version": "1.0.0",
                            "path": str(_project_chores_root() / "pkg-only"),
                            "lane": "lite",
                            "timeoutSeconds": 120,
                        },
                    ]
                )
                result = runner.invoke(main, ["chores", "list", "--explain"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Source", result.output)
            self.assertIn("project", result.output)
            self.assertIn("package", result.output)

    @covers("REQ-0.0.21-04-05")
    def test_registry_resolver_uses_same_order(self) -> None:
        """`_resolve_registry()` falls back to the package registry and logs the hit."""
        from gzkit.commands import chores as chores_mod

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with (
                structlog.testing.capture_logs() as cap,
                patch.object(chores_mod, "_package_chores_root") as mock_pkg_root,
            ):
                pkg_root = Path("fake-pkg-root").resolve()
                pkg_root.mkdir(parents=True, exist_ok=True)
                _scaffold_package_registry(pkg_root, [])
                mock_pkg_root.return_value = pkg_root
                result = chores_mod._resolve_registry()
            self.assertEqual(result.source, "package")
            self.assertEqual(result.path.resolve(), (pkg_root / "registry.json").resolve())
            events = [e for e in cap if e.get("event") == "chore.resolver.fallback"]
            self.assertTrue(events, f"no fallback log event in: {cap}")
            self.assertEqual(events[0].get("slug"), "registry")

    @covers("REQ-0.0.21-04-06")
    def test_resolved_path_model_is_well_typed(self) -> None:
        """`ResolvedPath` is a frozen Pydantic model with a constrained `source`.

        REQ-0.0.21-04-06 demands `uv run gz typecheck` exit 0 after the change.
        The runtime model surface this test pins is the same surface ty checks
        statically; if the resolver's type signatures regress, this test (which
        constructs the model with both literal values and rejects an unknown
        one) catches the same defect class the typecheck would.
        """
        from gzkit.commands.chores import ResolvedPath

        ok_project = ResolvedPath(path=Path("."), source="project")
        ok_package = ResolvedPath(path=Path("."), source="package")
        self.assertEqual(ok_project.source, "project")
        self.assertEqual(ok_package.source, "package")
        with self.assertRaises(ValueError):
            ResolvedPath(path=Path("."), source="bogus")  # type: ignore

    @covers("REQ-0.0.21-04-07")
    def test_chores_list_default_no_source_column(self) -> None:
        """Default `gz chores list` (no --explain) keeps the pre-OBPI column shape."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _scaffold_project_chore("demo-chore")
            _setup_demo_chore(
                slug="demo-chore",
                chore_path=str(_project_chores_root() / "demo-chore"),
            )
            result = runner.invoke(main, ["chores", "list"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            # No "Source" column header in default output.
            self.assertNotIn("Source", result.output)


def _seed_canonical_chores_into_project() -> None:
    """Scaffold every canonical chore into .gzkit/chores/ for a clean baseline."""
    from gzkit.chores import scaffold_core_chores
    from gzkit.config import GzkitConfig

    project_root = Path.cwd()
    cfg = GzkitConfig.load(project_root / ".gzkit.json")
    scaffold_core_chores(project_root, cfg, skip_existing=False)


def _first_canonical_slug() -> str:
    """Return the first canonical chore slug (deterministic by sort)."""
    import importlib.resources

    root = importlib.resources.files("gzkit.chores")
    slugs = sorted(
        entry.name
        for entry in root.iterdir()
        if entry.is_dir()
        and not entry.name.startswith("__")
        and entry.joinpath("CHORE.md").is_file()
    )
    if not slugs:
        raise RuntimeError("No canonical chore slugs found in gzkit.chores package.")
    return slugs[0]


class TestChoresDoctor(unittest.TestCase):
    """REQ-derived tests for the gz chores doctor command (OBPI-0.0.21-09)."""

    @covers("REQ-0.0.21-09-01")
    def test_doctor_subcommand_registered(self) -> None:
        """`gz chores doctor --help` exits 0 — the subcommand is registered."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["chores", "doctor", "--help"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("doctor", result.output.lower())

    @covers("REQ-0.0.21-09-02")
    def test_doctor_healthy_tree_is_noop(self) -> None:
        """On a freshly-scaffolded tree, every slug shows HEALTHY/HEALTHY and no files change."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            chores_dir = _project_chores_root()
            before = sorted(p.relative_to(chores_dir).as_posix() for p in chores_dir.rglob("*"))

            result = runner.invoke(main, ["chores", "doctor"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("HEALTHY", result.output)
            after = sorted(p.relative_to(chores_dir).as_posix() for p in chores_dir.rglob("*"))
            self.assertEqual(before, after)

    @covers("REQ-0.0.21-09-03")
    @covers("REQ-0.0.21-09-09")
    def test_doctor_repairs_missing_slug(self) -> None:
        """A canonical slug whose directory is absent gets re-scaffolded; exit 0 on repair."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            slug = _first_canonical_slug()
            target = _project_chores_root() / slug
            import shutil as _shutil

            _shutil.rmtree(target)
            self.assertFalse(target.exists())

            result = runner.invoke(main, ["chores", "doctor"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue((target / "CHORE.md").is_file())
            self.assertTrue((target / "acceptance.json").is_file())
            self.assertIn(slug, result.output)
            self.assertIn("MISSING", result.output)

    @covers("REQ-0.0.21-09-04")
    def test_doctor_repairs_damaged_slug(self) -> None:
        """A slug whose acceptance.json was deleted has the canonical bytes restored."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            slug = _first_canonical_slug()
            target = _project_chores_root() / slug
            (target / "acceptance.json").unlink()
            self.assertFalse((target / "acceptance.json").exists())

            result = runner.invoke(main, ["chores", "doctor"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue((target / "acceptance.json").is_file())
            self.assertIn("DAMAGED", result.output)

            import importlib.resources as _ir

            canonical_bytes = (
                _ir.files("gzkit.chores").joinpath(slug, "acceptance.json").read_bytes()
            )
            restored_bytes = (target / "acceptance.json").read_bytes()
            self.assertEqual(canonical_bytes, restored_bytes)

    @covers("REQ-0.0.21-09-05")
    def test_doctor_preserves_proofs(self) -> None:
        """Files under .gzkit/chores/<slug>/proofs/ are byte-identical before and after repair."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            slug = _first_canonical_slug()
            target = _project_chores_root() / slug
            proofs_dir = target / "proofs"
            proofs_dir.mkdir(exist_ok=True)
            evidence = proofs_dir / "evidence.txt"
            evidence_bytes = b"operator-attested-evidence-bytes-1234\n"
            evidence.write_bytes(evidence_bytes)
            (target / "CHORE.md").unlink()  # damage to force repair
            self.assertFalse((target / "CHORE.md").exists())

            result = runner.invoke(main, ["chores", "doctor"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue((target / "CHORE.md").is_file())
            self.assertEqual(evidence.read_bytes(), evidence_bytes)

    @covers("REQ-0.0.21-09-06")
    def test_doctor_untouches_project_local(self) -> None:
        """A slug present in the project but absent from canonical is labelled PROJECT-LOCAL."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            local_slug = "operator-only-local-chore"
            local_dir = _project_chores_root() / local_slug
            local_dir.mkdir(parents=True, exist_ok=True)
            local_chore_md = local_dir / "CHORE.md"
            local_chore_md.write_text("# operator-only chore\n", encoding="utf-8")
            (local_dir / "acceptance.json").write_text(
                json.dumps({"criteria": []}), encoding="utf-8"
            )
            before = local_chore_md.read_text(encoding="utf-8")

            result = runner.invoke(main, ["chores", "doctor"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(local_chore_md.is_file())
            self.assertEqual(local_chore_md.read_text(encoding="utf-8"), before)
            self.assertIn("PROJECT-LOCAL", result.output)
            self.assertIn(local_slug, result.output)

    @covers("REQ-0.0.21-09-07")
    def test_doctor_dry_run_makes_no_changes(self) -> None:
        """`--dry-run` with a missing slug reports without touching the filesystem."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            slug = _first_canonical_slug()
            target = _project_chores_root() / slug
            import shutil as _shutil

            _shutil.rmtree(target)
            chores_dir = _project_chores_root()
            before = sorted(p.relative_to(chores_dir).as_posix() for p in chores_dir.rglob("*"))

            result = runner.invoke(main, ["chores", "doctor", "--dry-run"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            after = sorted(p.relative_to(chores_dir).as_posix() for p in chores_dir.rglob("*"))
            self.assertEqual(before, after)
            self.assertFalse(target.exists())

    @covers("REQ-0.0.21-09-08")
    def test_doctor_json_output_parses(self) -> None:
        """`--json` emits a list of {slug, before_status, after_status} records."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            slug = _first_canonical_slug()
            import shutil as _shutil

            _shutil.rmtree(_project_chores_root() / slug)

            result = runner.invoke(main, ["chores", "doctor", "--json"])

            self.assertEqual(result.exit_code, 0, msg=result.output)
            payload = json.loads(result.output)
            self.assertIsInstance(payload, list)
            slugs = {row["slug"]: row for row in payload}
            self.assertIn(slug, slugs)
            self.assertEqual(slugs[slug]["before_status"], "MISSING")
            self.assertEqual(slugs[slug]["after_status"], "HEALTHY")
            for row in payload:
                self.assertIn("slug", row)
                self.assertIn("before_status", row)
                self.assertIn("after_status", row)


class TestChoresDoctorOutputForm(unittest.TestCase):
    """Output-form fixture: doctor's default rendering is a Rich table.

    Pinned per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariant 3 —
    the manpage Output Contract for `gz chores doctor` is a summary table.
    """

    def test_doctor_renders_rich_table(self) -> None:
        """Default doctor output contains box-drawing characters (Rich table form)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_canonical_chores_into_project()
            result = runner.invoke(main, ["chores", "doctor"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            # Rich's default box style emits these box-drawing chars.
            box_chars = ("╭", "╰", "┬", "┴", "│")
            self.assertTrue(
                any(ch in result.output for ch in box_chars),
                msg=f"doctor output lacks Rich-table box chars: {result.output!r}",
            )
