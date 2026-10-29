import importlib.metadata
import inspect
import json
import re
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands.common import GzCliError
from gzkit.commands.init_cmd import (
    PROJECT_TYPES,
    ProjectSkeleton,
    _normalize_package_name,
    scaffold_project_skeleton,
)
from gzkit.config import GzkitConfig
from gzkit.governance.trust_audits.astral_discipline import (
    BASELINE_RELPATH,
    find_violations,
    seed_discipline_baseline,
)
from gzkit.traceability import covers
from gzkit.validate_pkg.sync_parity import check_sync_parity
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)


def setUpModule() -> None:
    """Stub the init subprocess boundaries (uv sync + ruff format)."""
    start_init_subprocess_patches()


def tearDownModule() -> None:
    stop_init_subprocess_patches()


class TestInitCommand(unittest.TestCase):
    """Tests for gz init command."""

    def test_init_creates_codex_config_baseline(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--no-skeleton"])

            self.assertEqual(result.exit_code, 0, result.output)
            config_path = Path(".codex/config.toml")
            self.assertTrue(config_path.is_file(), "gz init must create Codex config")
            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["sandbox_mode"], "workspace-write")
            self.assertIs(config["sandbox_workspace_write"]["network_access"], True)
            self.assertIs(config["features"]["hooks"], True)

    def test_init_creates_gzkit_dir(self) -> None:
        """init creates .gzkit directory."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit").exists())

    def test_init_creates_ledger(self) -> None:
        """init creates ledger file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit/ledger.jsonl").exists())

    def test_init_creates_manifest(self) -> None:
        """init creates manifest file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit/manifest.json").exists())

    def test_init_creates_design_directories(self) -> None:
        """init creates design directories."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/prd").exists())
            self.assertTrue(Path("design/constitutions").exists())
            self.assertTrue(Path("design/adr").exists())

    def test_init_rerun_repairs_instead_of_failing(self) -> None:
        """Re-running init without --force repairs missing artifacts."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            # Delete a skeleton file to simulate missing artifact
            pyproject = Path("pyproject.toml")
            pyproject.unlink()
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Repairing", result.output)
            self.assertTrue(pyproject.exists())

    def test_init_rerun_reports_nothing_to_repair(self) -> None:
        """Re-running init when everything exists reports nothing to repair."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Nothing to repair", result.output)

    def test_init_repair_preserves_operator_codex_config(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            first = runner.invoke(main, ["init", "--no-skeleton"])
            self.assertEqual(first.exit_code, 0, first.output)
            config_path = Path(".codex/config.toml")
            operator_config = b'model = "gpt-5.4"\napproval_policy = "on-request"\n'
            config_path.write_bytes(operator_config)

            repaired = runner.invoke(main, ["init", "--no-skeleton"])

            self.assertEqual(repaired.exit_code, 0, repaired.output)
            self.assertEqual(config_path.read_bytes(), operator_config)

    def test_init_with_force(self) -> None:
        """init --force reinitializes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["init", "--force"])
            self.assertEqual(result.exit_code, 0)


class TestInitProjectSkeleton(unittest.TestCase):
    """Tests for project skeleton scaffolding during gz init."""

    def test_init_creates_pyproject_toml(self) -> None:
        """init creates pyproject.toml."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            pyproject = Path("pyproject.toml")
            self.assertTrue(pyproject.exists())
            content = pyproject.read_text(encoding="utf-8")
            self.assertIn("[project]", content)
            floor = importlib.metadata.metadata("py-gzkit")["Requires-Python"]
            self.assertIn(f'requires-python = "{floor}"', content)

    def test_init_creates_src_package(self) -> None:
        """init creates src/<project>/__init__.py."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            # The directory name becomes the package name -- assert that, rather
            # than trusting iterdir() order. src/ also carries the generated
            # nested AGENTS.md now that init leaves a synced tree (GHI #908), and
            # which entry comes back first is the filesystem's choice.
            package_dir = Path("src") / _normalize_package_name(Path.cwd().name)
            present = sorted(entry.name for entry in Path("src").iterdir())
            self.assertTrue(
                (package_dir / "__init__.py").exists(),
                f"expected a package at {package_dir}; src/ holds {present}",
            )

    def test_init_creates_tests_init(self) -> None:
        """init creates tests/__init__.py."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("tests/__init__.py").exists())

    def test_init_no_skeleton_skips_project_files(self) -> None:
        """init --no-skeleton does not create project skeleton."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--no-skeleton"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(Path("pyproject.toml").exists())
            self.assertFalse(Path("tests/__init__.py").exists())

    def test_init_does_not_overwrite_existing_pyproject(self) -> None:
        """init preserves an existing pyproject.toml."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            custom = '[project]\nname = "my-custom"\nversion = "9.9.9"\n'
            Path("pyproject.toml").write_text(custom, encoding="utf-8")
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            content = Path("pyproject.toml").read_text(encoding="utf-8")
            self.assertIn("9.9.9", content)

    def test_init_pyproject_uses_project_name(self) -> None:
        """pyproject.toml contains the detected project name."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            content = Path("pyproject.toml").read_text(encoding="utf-8")
            # The directory name is the project name (from tempdir)
            self.assertIn('name = "', content)

    def test_repair_creates_missing_skeleton(self) -> None:
        """Re-running init repairs missing skeleton files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            # Delete skeleton files
            Path("pyproject.toml").unlink()
            import shutil

            shutil.rmtree("tests")
            # Re-run should repair
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("pyproject.toml").exists())
            self.assertTrue(Path("tests/__init__.py").exists())

    def test_repair_partial_skeleton_fills_gaps(self) -> None:
        """Repair with partial skeleton only creates what's missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            # Keep pyproject.toml, delete only tests/
            original_pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
            import shutil

            shutil.rmtree("tests")
            # Re-run should repair tests/ but leave pyproject.toml untouched
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("tests/__init__.py").exists())
            self.assertEqual(
                Path("pyproject.toml").read_text(encoding="utf-8"),
                original_pyproject,
            )
            # Only tests/ repair should appear, not pyproject.toml
            self.assertNotIn("pyproject.toml", result.output)


def _dev_group_names(project: dict) -> set[str]:
    """Return the distribution names in a manifest's dev dependency group.

    Returns:
        The lower-cased names, without version specifiers or markers.

    """
    return {
        re.split(r"[<>=!~;\[\s]", spec, maxsplit=1)[0].lower()
        for spec in project.get("dependency-groups", {}).get("dev", [])
    }


class TestInitBuildsTheProjectThroughUv(unittest.TestCase):
    """RO-9 tranche 7: `gz init` builds a new project with uv init and uv add."""

    def _init(self, *args: str) -> tuple[dict, Path]:
        result = CliRunner().invoke(main, ["init", *args])
        self.assertEqual(result.exit_code, 0, result.output)
        manifest = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        return manifest, Path("src") / _normalize_package_name(Path.cwd().name)

    def test_each_project_type_builds_its_uv_shape(self) -> None:
        for project_type in PROJECT_TYPES:
            with self.subTest(project_type=project_type), CliRunner().isolated_filesystem():
                manifest, package = self._init("--project-type", project_type)
                self.assertEqual(manifest["build-system"]["build-backend"], "uv_build")
                self.assertTrue((package / "__init__.py").is_file())
                # A library ships typing information and no entry point; a package or
                # an app is something one runs, so uv declares its script.
                self.assertEqual(project_type == "lib", (package / "py.typed").is_file())
                self.assertEqual(project_type != "lib", "scripts" in manifest["project"])

    def test_default_project_type_is_lib(self) -> None:
        with CliRunner().isolated_filesystem():
            manifest, package = self._init()
            self.assertTrue((package / "py.typed").is_file())
            self.assertNotIn("scripts", manifest["project"])

    def test_no_author_identity_lands_in_the_manifest(self) -> None:
        with CliRunner().isolated_filesystem():
            manifest, _ = self._init()
            self.assertNotIn("authors", manifest["project"])

    def test_dev_group_locks_ruff_and_ty(self) -> None:
        with CliRunner().isolated_filesystem():
            manifest, _ = self._init()
            self.assertEqual(_dev_group_names(manifest), {"ruff", "ty"})
            self.assertNotIn("optional-dependencies", manifest["project"])

    def test_ruff_config_bans_the_pep_563_import(self) -> None:
        with CliRunner().isolated_filesystem():
            manifest, _ = self._init()
            banned = manifest["tool"]["ruff"]["lint"]["flake8-tidy-imports"]["banned-api"]
            self.assertIn("__future__.annotations", banned)

    def test_ci_workflow_runs_uv_with_the_lock_checked(self) -> None:
        with CliRunner().isolated_filesystem():
            self._init()
            ci = Path(".github/workflows/ci.yml")
            self.assertTrue(ci.is_file(), "gz init wrote no CI workflow")
            workflow = ci.read_text(encoding="utf-8")
            steps = [line.strip().removeprefix("- ") for line in workflow.splitlines()]
            setup_uv = [step for step in steps if "astral-sh/setup-uv@" in step]
            self.assertEqual(len(setup_uv), 1, workflow)
            # The action is pinned to a commit, never a movable tag.
            self.assertRegex(setup_uv[0], r"setup-uv@[0-9a-f]{40}\b")
            self.assertIn("run: uv sync --locked", steps)
            self.assertNotIn("actions/setup-python", workflow)

    def test_fresh_scaffold_carries_no_astral_discipline_violation(self) -> None:
        with CliRunner().isolated_filesystem():
            self._init()
            self.assertEqual(find_violations(Path.cwd()), [])
            seeded = json.loads(Path(BASELINE_RELPATH).read_text(encoding="utf-8"))
            self.assertEqual(seeded["violations"], [])

    def test_adopting_project_seeds_its_existing_debt(self) -> None:
        with CliRunner().isolated_filesystem():
            Path("pyproject.toml").write_text(
                '[project]\nname = "adopter"\nversion = "1.0.0"\n', encoding="utf-8"
            )
            Path("requirements.txt").write_text("requests\n", encoding="utf-8")
            result = CliRunner().invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0, result.output)
            rows = json.loads(Path(BASELINE_RELPATH).read_text(encoding="utf-8"))["violations"]
            held = {(row["rule"], row["file"]) for row in rows}
            self.assertIn(("pip-in-project", "requirements.txt"), held)
            # What the baseline holds is exactly what the scan finds: it starts exact.
            self.assertEqual(sum(row["count"] for row in rows), len(find_violations(Path.cwd())))

    def test_existing_baseline_is_never_reseeded(self) -> None:
        with CliRunner().isolated_filesystem():
            Path("data").mkdir()
            prior = '{"violations": []}\n'
            Path(BASELINE_RELPATH).write_text(prior, encoding="utf-8")
            Path("requirements.txt").write_text("requests\n", encoding="utf-8")
            self._init()
            self.assertEqual(Path(BASELINE_RELPATH).read_text(encoding="utf-8"), prior)

    def test_non_src_source_root_moves_the_package_and_tells_uv_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scaffold_project_skeleton(
                root, ProjectSkeleton(name="demo-proj", source_root="lib", tests_root="tests")
            )
            manifest = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
            self.assertTrue((root / "lib" / "demo_proj" / "__init__.py").is_file())
            self.assertFalse((root / "src").exists())
            self.assertEqual(manifest["tool"]["uv"]["build-backend"]["module-root"], "lib")
            self.assertEqual(manifest["tool"]["ruff"]["src"], ["lib", "tests"])

    def test_readme_points_at_the_agent_contract(self) -> None:
        # uv writes a README of its own; gzkit replaces it with the governance one.
        with CliRunner().isolated_filesystem():
            self._init()
            self.assertIn("AGENTS.md", Path("README.md").read_text(encoding="utf-8"))

    def test_unknown_project_type_is_a_usage_error(self) -> None:
        with CliRunner().isolated_filesystem():
            result = CliRunner().invoke(main, ["init", "--project-type", "script"])
            self.assertEqual(result.exit_code, 2, result.output)
            self.assertFalse(Path("pyproject.toml").exists())


class TestUvSkeletonFailsWithRecovery(unittest.TestCase):
    """When uv cannot build the project, init stops and names the recovery."""

    def _scaffold_fails(self, root: Path) -> str:
        with self.assertRaises(GzCliError) as caught:
            scaffold_project_skeleton(root, ProjectSkeleton(name="demo-proj"))
        self.assertFalse((root / "pyproject.toml").exists())
        self.assertFalse((root / ".github").exists())
        return str(caught.exception)

    def test_missing_uv_names_the_install_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "no-such-uv")
            with patch("gzkit.commands.init_cmd.resolve_executable", return_value=missing):
                message = self._scaffold_fails(Path(tmp))
            self.assertIn("uv is not on PATH", message)
            self.assertIn("re-run `gz init`", message)

    def test_failing_uv_command_names_the_command_and_stops(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # The interpreter given uv's argv exits non-zero with its own stderr: a real
            # failing process, on every platform.
            with patch("gzkit.commands.init_cmd.resolve_executable", return_value=sys.executable):
                message = self._scaffold_fails(Path(tmp))
            self.assertIn("`uv init --lib", message)
            self.assertIn("re-run `gz init`", message)

    def test_missing_python_floor_refuses_to_pin_one(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch(
                "gzkit.commands.init_cmd.importlib.metadata.metadata",
                return_value={"Requires-Python": "~=3.14"},
            ),
        ):
            message = self._scaffold_fails(Path(tmp))
        self.assertIn("no Python floor", message)


class TestInitRepairBuildsAndSeeds(unittest.TestCase):
    """The repair flow (an initialized project) honours the same tranche 7 contract."""

    def test_repair_builds_the_requested_project_type(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            result = runner.invoke(main, ["init", "--project-type", "package"])
            self.assertEqual(result.exit_code, 0, result.output)
            manifest = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
            self.assertIn("scripts", manifest["project"])

    def test_repair_seeds_a_missing_baseline(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init"]).exit_code, 0)
            Path(BASELINE_RELPATH).unlink()
            Path("requirements.txt").write_text("requests\n", encoding="utf-8")
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(Path(BASELINE_RELPATH).is_file(), result.output)
            rows = json.loads(Path(BASELINE_RELPATH).read_text(encoding="utf-8"))["violations"]
            self.assertIn(
                ("pip-in-project", "requirements.txt"), {(r["rule"], r["file"]) for r in rows}
            )

    def test_repair_dry_run_plans_the_seed_without_writing_it(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init"]).exit_code, 0)
            Path(BASELINE_RELPATH).unlink()
            result = runner.invoke(main, ["init", "--dry-run"])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertFalse(Path(BASELINE_RELPATH).exists())
            # output-contract: the dry-run plan is the command's named output.
            self.assertIn(f"Would seed {BASELINE_RELPATH}", result.output)


class TestSeedDisciplineBaseline(unittest.TestCase):
    """seed_discipline_baseline writes once, exactly, and reports what it wrote."""

    def test_returns_the_number_of_rows_it_wrote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "requirements.txt").write_text("requests\n", encoding="utf-8")
            written = seed_discipline_baseline(root)
            rows = json.loads((root / BASELINE_RELPATH).read_text(encoding="utf-8"))
            self.assertTrue(rows["violations"])
            self.assertEqual(written, len(rows["violations"]))

    def test_existing_baseline_is_left_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "requirements.txt").write_text("requests\n", encoding="utf-8")
            (root / "data").mkdir()
            prior = '{"violations": []}\n'
            (root / BASELINE_RELPATH).write_text(prior, encoding="utf-8")
            self.assertIsNone(seed_discipline_baseline(root))
            self.assertEqual((root / BASELINE_RELPATH).read_text(encoding="utf-8"), prior)


class TestInitPersonaScaffolding(unittest.TestCase):
    """Integration tests for persona scaffolding during gz init."""

    def test_init_creates_personas_directory(self) -> None:
        """init creates .gzkit/personas/ directory."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit/personas").is_dir())

    def test_init_creates_default_persona_files(self) -> None:
        """init creates at least one default persona file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            personas = list(Path(".gzkit/personas").glob("*.md"))
            self.assertGreaterEqual(len(personas), 1)

    def test_init_does_not_overwrite_existing_personas(self) -> None:
        """init --force preserves existing persona files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            persona_file = Path(".gzkit/personas/main-session.md")
            custom = (
                "---\nname: main-session\ntraits:\n  - custom\n"
                "anti-traits:\n  - x\ngrounding: custom\n---\n"
            )
            persona_file.write_text(custom, encoding="utf-8")
            runner.invoke(main, ["init", "--force"])
            content = persona_file.read_text(encoding="utf-8")
            self.assertIn("custom", content)


class TestInitGitignore(unittest.TestCase):
    """Tests for .gitignore scaffolding during gz init."""

    def test_init_creates_gitignore(self) -> None:
        """init creates .gitignore with Python defaults."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            gitignore = Path(".gitignore")
            self.assertTrue(gitignore.exists())
            content = gitignore.read_text(encoding="utf-8")
            self.assertIn(".venv/", content)
            self.assertIn("__pycache__/", content)
            self.assertIn("settings.local.json", content)

    def test_init_does_not_overwrite_existing_gitignore(self) -> None:
        """init preserves an existing .gitignore."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            custom = "my-custom-ignore\n"
            Path(".gitignore").write_text(custom, encoding="utf-8")
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            content = Path(".gitignore").read_text(encoding="utf-8")
            self.assertEqual(content, custom)

    def test_repair_creates_missing_gitignore(self) -> None:
        """Re-running init creates .gitignore if missing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            Path(".gitignore").unlink()
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gitignore").exists())

    def test_no_skeleton_still_creates_gitignore(self) -> None:
        """--no-skeleton still creates .gitignore (it's not a skeleton file)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--no-skeleton"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gitignore").exists())


class TestNormalizePackageName(unittest.TestCase):
    """Tests for _normalize_package_name."""

    _CASES = [
        ("my-project", "my_project"),
        ("My Project", "my_project"),
        ("rhea", "rhea"),
        ("RHEA", "rhea"),
        ("my--double--hyphen", "my_double_hyphen"),
        ("project.name", "projectname"),
        ("123start", "123start"),
        ("", "app"),
        ("---", "app"),
    ]

    def test_normalize_cases(self) -> None:
        """Package name normalization produces valid Python identifiers."""
        for input_name, expected in self._CASES:
            with self.subTest(input_name=input_name):
                self.assertEqual(_normalize_package_name(input_name), expected)


class TestScaffoldCoreChores(unittest.TestCase):
    """Tests for gzkit.chores.scaffold_core_chores (REQ-0.0.21-05-01..03,06,07)."""

    def test_scaffold_core_chores_creates_canonical_slugs(self) -> None:
        """REQ-05-01: empty project → at least 3 representative slugs land."""
        from gzkit.chores import scaffold_core_chores  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            scaffold_core_chores(project_root, config)
            chores_dir = project_root / config.paths.chores
            for slug in ("coverage-40pct", "quality-check", "dependency-currency"):
                slug_dir = chores_dir / slug
                self.assertTrue(
                    (slug_dir / "CHORE.md").exists(),
                    f"missing CHORE.md for {slug}",
                )
                self.assertTrue(
                    (slug_dir / "acceptance.json").exists(),
                    f"missing acceptance.json for {slug}",
                )
                self.assertTrue(
                    (slug_dir / "README.md").exists(),
                    f"missing README.md for {slug}",
                )

    def test_scaffold_core_chores_skip_existing_preserves_operator_edits(self) -> None:
        """REQ-05-02: skip_existing=True leaves a pre-existing slug untouched."""
        from gzkit.chores import scaffold_core_chores  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            chores_dir = project_root / config.paths.chores
            slug_dir = chores_dir / "coverage-40pct"
            slug_dir.mkdir(parents=True)
            custom = "OPERATOR EDIT — do not clobber\n"
            (slug_dir / "CHORE.md").write_text(custom, encoding="utf-8")
            scaffold_core_chores(project_root, config, skip_existing=True)
            self.assertEqual(
                (slug_dir / "CHORE.md").read_text(encoding="utf-8"),
                custom,
            )

    def test_scaffold_core_chores_does_not_copy_proofs(self) -> None:
        """REQ-05-03a: canonical proofs/ subdirs are never copied to destination."""
        from gzkit.chores import scaffold_core_chores  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            scaffold_core_chores(project_root, config)
            chores_dir = project_root / config.paths.chores
            stray_proofs = list(chores_dir.glob("*/proofs"))
            self.assertEqual(stray_proofs, [], f"unexpected proofs dirs: {stray_proofs}")

    def test_scaffold_core_chores_preserves_existing_proofs(self) -> None:
        """REQ-05-03b/REQ-07: pre-existing proofs/ at destination survive a run."""
        from gzkit.chores import scaffold_core_chores  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            chores_dir = project_root / config.paths.chores
            proofs_dir = chores_dir / "coverage-40pct" / "proofs"
            proofs_dir.mkdir(parents=True)
            evidence = proofs_dir / "evidence.txt"
            evidence_content = "operator-captured proof artifact\n"
            evidence.write_text(evidence_content, encoding="utf-8")
            scaffold_core_chores(project_root, config, skip_existing=False)
            self.assertTrue(evidence.exists())
            self.assertEqual(evidence.read_text(encoding="utf-8"), evidence_content)

    def test_scaffold_core_chores_signature_matches_brief(self) -> None:
        """REQ-05-06: signature matches scaffold_core_skills exactly."""
        from gzkit.chores import scaffold_core_chores  # noqa: PLC0415

        sig = inspect.signature(scaffold_core_chores)
        params = list(sig.parameters.values())
        self.assertEqual(params[0].name, "project_root")
        self.assertEqual(params[0].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        self.assertEqual(params[1].name, "config")
        self.assertEqual(params[1].default, None)
        self.assertEqual(params[2].name, "skip_existing")
        self.assertEqual(params[2].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertEqual(params[2].default, False)

    def test_scaffold_core_chores_returns_one_path_per_scaffolded_slug(self) -> None:
        """REQ-05-07: returned list has one CHORE.md path per scaffolded slug."""
        from gzkit.chores import scaffold_core_chores  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            created = scaffold_core_chores(project_root, config)
            self.assertGreater(len(created), 0)
            for path in created:
                self.assertEqual(path.name, "CHORE.md")
                self.assertTrue(path.exists())


class TestMergeChoresRegistry(unittest.TestCase):
    """Tests for gzkit.chores.merge_chores_registry (REQ-0.0.21-05-04)."""

    def setUp(self) -> None:
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        self._stdout_redirect = contextlib.redirect_stdout(io.StringIO())
        self._stdout_redirect.__enter__()

    def tearDown(self) -> None:
        self._stdout_redirect.__exit__(None, None, None)

    def _seed_local_registry(
        self,
        project_root: Path,
        config: GzkitConfig,
        slugs: list[str],
    ) -> Path:
        chores_dir = project_root / config.paths.chores
        chores_dir.mkdir(parents=True, exist_ok=True)
        registry_path = chores_dir / "registry.json"
        payload = {
            "specVersion": "2.0",
            "chores": [
                {
                    "slug": s,
                    "title": s,
                    "version": "0.0.0",
                    "path": "x",
                    "lane": "lite",
                }
                for s in slugs
            ],
        }
        registry_path.write_text(json.dumps(payload), encoding="utf-8")
        return registry_path

    def test_merge_chores_registry_reports_diff_on_canonical_addition(self) -> None:
        """REQ-05-04: merge surfaces canonical-only slugs in `added`."""
        from gzkit.chores import merge_chores_registry  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            self._seed_local_registry(project_root, config, slugs=["only-local-slug"])
            report = merge_chores_registry(project_root, config, auto_yes=True)
            self.assertGreater(len(report.added), 0)
            self.assertIn("only-local-slug", report.unchanged_local)
            self.assertTrue(report.wrote)

    def test_merge_chores_registry_yes_skips_prompt(self) -> None:
        """REQ-05-04(e): auto_yes=True bypasses the _confirm prompt."""
        from gzkit.chores import merge_chores_registry  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            self._seed_local_registry(project_root, config, slugs=["only-local"])
            with patch("gzkit.chores._confirm") as mock_confirm:
                merge_chores_registry(project_root, config, auto_yes=True)
                mock_confirm.assert_not_called()

    def test_merge_chores_registry_dry_run_never_writes(self) -> None:
        """REQ-05-04: dry_run=True leaves the local registry byte-identical."""
        from gzkit.chores import merge_chores_registry  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig()
            registry_path = self._seed_local_registry(project_root, config, slugs=["only-local"])
            before = registry_path.read_bytes()
            merge_chores_registry(project_root, config, dry_run=True, auto_yes=True)
            after = registry_path.read_bytes()
            self.assertEqual(before, after)


class TestInitChoresIntegration(unittest.TestCase):
    """Tests for gz init wiring of scaffold_core_chores (REQ-0.0.21-05-05)."""

    def test_gz_init_invokes_scaffold_core_chores_main_path(self) -> None:
        """REQ-05-05: main init path calls scaffold_core_chores once."""
        from gzkit.chores import scaffold_core_chores as real_scaffold  # noqa: PLC0415

        runner = CliRunner()
        with (
            runner.isolated_filesystem(),
            patch(
                "gzkit.commands.init_cmd.scaffold_core_chores",
                wraps=real_scaffold,
            ) as mock_scaffold,
        ):
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertGreaterEqual(mock_scaffold.call_count, 1)
            first_call = mock_scaffold.call_args_list[0]
            self.assertNotIn("skip_existing", first_call.kwargs)

    def test_gz_init_repair_invokes_scaffold_core_chores_with_skip_existing(self) -> None:
        """REQ-05-05: repair path calls scaffold_core_chores with skip_existing=True."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            with patch(
                "gzkit.commands.init_cmd.scaffold_core_chores",
                return_value=[],
            ) as mock_scaffold:
                result = runner.invoke(main, ["init"])
                self.assertEqual(result.exit_code, 0)
                self.assertTrue(
                    any(
                        c.kwargs.get("skip_existing") is True for c in mock_scaffold.call_args_list
                    ),
                    "no repair-path call with skip_existing=True",
                )


class TestInitRulesIntegration(unittest.TestCase):
    """Integration tests for gz init wiring of scaffold_core_rules (REQ-0.0.32-04-04)."""

    @covers("REQ-0.0.32-04-04")
    @covers("REQ-0.0.32-04-07")
    def test_gz_init_invokes_scaffold_core_rules_main_path(self) -> None:
        """REQ-04-04/07: main init path calls scaffold_core_rules and populates .gzkit/rules/."""
        from gzkit.rules import scaffold_core_rules as real_scaffold  # noqa: PLC0415

        runner = CliRunner()
        with (
            runner.isolated_filesystem(),
            patch(
                "gzkit.commands.init_cmd.scaffold_core_rules",
                wraps=real_scaffold,
            ) as mock_scaffold,
        ):
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertGreaterEqual(mock_scaffold.call_count, 1)
            rules_dir = Path(".gzkit") / "rules"
            self.assertTrue(rules_dir.exists(), ".gzkit/rules/ was not created by init")
            rule_files = list(rules_dir.glob("*.md"))
            self.assertGreater(len(rule_files), 0, ".gzkit/rules/ contains no .md files")

    @covers("REQ-0.0.32-04-05")
    def test_gz_init_repair_invokes_scaffold_core_rules_with_skip_existing(self) -> None:
        """REQ-04-05: repair path calls scaffold_core_rules with skip_existing=True."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            with patch(
                "gzkit.commands.init_cmd.scaffold_core_rules",
                return_value=[],
            ) as mock_scaffold:
                result = runner.invoke(main, ["init"])
                self.assertEqual(result.exit_code, 0)
                self.assertTrue(
                    any(
                        c.kwargs.get("skip_existing") is True for c in mock_scaffold.call_args_list
                    ),
                    "no repair-path call with skip_existing=True",
                )

    @covers("REQ-0.0.32-04-08")
    def test_init_manpage_mentions_rules(self) -> None:
        """REQ-04-08: docs/user/manpages/init.md mentions rule scaffolding."""
        manpage = Path("docs/user/manpages/init.md")
        self.assertTrue(manpage.exists(), "docs/user/manpages/init.md not found")
        content = manpage.read_text(encoding="utf-8").lower()
        self.assertIn("rule", content, "init.md does not mention rules")

    @covers("REQ-0.0.32-04-08")
    def test_skill_surface_sync_rule_has_gz_init_bootstrap_note(self) -> None:
        """REQ-04-08: .gzkit/rules/skill-surface-sync.md documents gz init bootstrap."""
        rule_file = Path(".gzkit/rules/skill-surface-sync.md")
        self.assertTrue(rule_file.exists(), ".gzkit/rules/skill-surface-sync.md not found")
        content = rule_file.read_text(encoding="utf-8").lower()
        self.assertIn("gz init", content, "skill-surface-sync.md does not document gz init")
        self.assertIn("rules", content, "skill-surface-sync.md does not mention rules surface")

    @covers("REQ-0.0.32-04-09")
    def test_core_rules_check_passes(self) -> None:
        """REQ-04-09: CORE_RULES registry is consistent (gz check prerequisite)."""
        from gzkit.rules import CORE_RULES, _iter_canonical_rule_slugs  # noqa: PLC0415

        iter_slugs = sorted(e.name[:-3] for e in _iter_canonical_rule_slugs())
        self.assertEqual(
            CORE_RULES,
            iter_slugs,
            "CORE_RULES does not match _iter_canonical_rule_slugs output",
        )


class TestInitPersonasScaffoldingObpi10(unittest.TestCase):
    """Integration tests for scaffold_core_personas wired into gz init (OBPI-0.0.32-10)."""

    @covers("REQ-0.0.32-10-04")
    @covers("REQ-0.0.32-10-07")
    def test_fresh_init_produces_7_canonical_persona_files(self) -> None:
        """A fresh gz init produces 7 canonical persona files at .gzkit/personas/."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            personas_dir = Path(".gzkit/personas")
            self.assertTrue(personas_dir.is_dir())
            persona_files = list(personas_dir.glob("*.md"))
            self.assertEqual(
                len(persona_files),
                7,
                f"Expected 7 canonical persona files, got {len(persona_files)}: "
                f"{[f.name for f in persona_files]}",
            )
            expected_slugs = {
                "flight-test-engineer",
                "implementer",
                "main-session",
                "narrator",
                "pipeline-orchestrator",
                "quality-reviewer",
                "spec-reviewer",
            }
            actual_slugs = {f.stem for f in persona_files}
            self.assertEqual(actual_slugs, expected_slugs)

    @covers("REQ-0.0.32-10-05")
    def test_repair_adds_missing_canonical_personas(self) -> None:
        """gz init repair adds any missing canonical personas without overwriting existing."""
        import tempfile  # noqa: PLC0415

        from gzkit.personas import scaffold_core_personas  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # Simulate partial scaffolding: only 1 persona file present
            personas_dir = project_root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "main-session.md").write_bytes(b"existing content")
            # scaffold_core_personas(skip_existing=True) must add the missing 6
            created = scaffold_core_personas(project_root, skip_existing=True)
            self.assertEqual(len(created), 6)
            # The pre-existing main-session.md must be preserved
            self.assertEqual((personas_dir / "main-session.md").read_bytes(), b"existing content")


class TestInitTemplatesScaffolding(unittest.TestCase):
    """REQ-0.0.32-12-04, 05, 07: init cmd templates scaffolding integration."""

    @covers("REQ-0.0.32-12-07")
    def test_init_creates_templates_directory(self) -> None:
        """gz init creates .gzkit/templates/ directory."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(".gzkit/templates").is_dir())

    @covers("REQ-0.0.32-12-04")
    @covers("REQ-0.0.32-12-07")
    def test_init_creates_template_files(self) -> None:
        """gz init scaffolds canonical template .md files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            templates = list(Path(".gzkit/templates").glob("*.md"))
            self.assertGreaterEqual(len(templates), 11)

    @covers("REQ-0.0.32-12-05")
    def test_repair_adds_missing_templates(self) -> None:
        """Re-running init (repair mode) scaffolds missing templates."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            # Delete a template to simulate missing artifact
            template_file = Path(".gzkit/templates/adr.md")
            template_file.unlink()
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(template_file.exists(), "Repair must restore missing templates")

    @covers("REQ-0.0.32-12-08")
    def test_repair_preserves_operator_edited_templates(self) -> None:
        """Repair mode does not overwrite operator-edited templates."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            template_file = Path(".gzkit/templates/adr.md")
            template_file.write_text("OPERATOR-EDIT", encoding="utf-8")
            runner.invoke(main, ["init"])  # repair mode
            self.assertEqual(template_file.read_text(encoding="utf-8"), "OPERATOR-EDIT")


class TestInitLeavesASyncedTree(unittest.TestCase):
    """The scaffolder must satisfy the gate it ships (GHI #908).

    ``gz init`` ran its only ``sync_all`` BEFORE ``scaffold_core_rules``, so the
    vendor mirrors were rendered from a ``.gzkit/rules/`` directory that did not
    exist yet and nothing re-rendered them afterwards. Measured 2026-08-28 at
    ``1fd8d6ec`` on an empty directory: ``gz init --yes`` exited 0 and then
    ``gz validate --surfaces`` exited 1 with 58 missing surfaces -- 25
    ``.claude/rules/``, 25 ``.github/instructions/`` and 8 nested ``AGENTS.md``.
    A brand-new project failed its own surface gate, and the repair was a
    command the operator had no reason to know they needed.

    The ordering discipline already existed one function over: the repair path
    re-syncs LAST, after every scaffolder, under the comment "Always re-sync
    control surfaces (idempotent, not counted as repairs)". Only the fresh-init
    path was missing it.

    This asserts the property rather than the ordering, because the ordering is
    one way to satisfy it and the property is what the operator experiences: the
    tree ``gz init`` produces is already synced.
    """

    def test_init_leaves_no_sync_parity_drift(self) -> None:
        """A freshly initialized tree passes the surface gate with no repair."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0, result.output)

            errors = check_sync_parity(Path.cwd())

        self.assertEqual(
            sorted(error.artifact for error in errors),
            [],
            "gz init scaffolded a tree its own surface gate rejects",
        )


class TestScaffoldedManifestIsSelfConsistent(unittest.TestCase):
    """The scaffolder must not name a file it does not create (GHI #910).

    `gz init` wrote `readme = "README.md"` into the pyproject and never created
    the file, so the tree it produced could not be built. Measured 2026-08-28 at
    `515c95dc` on an empty directory:

        $ uv run gz init --yes          -> exit 0
        $ uv run python -c "print(1)"   -> exit 1
          OSError: Readme file does not exist: README.md

    Every `uv run` in a freshly scaffolded project failed that way — including
    `uv run gz <anything>`, which is the invocation form init's own closing
    output tells the operator to use.

    The class is a generated manifest naming a peer by path: a readme, a
    license, a packaging include. Such a manifest is syntactically valid, so
    every static check accepts it; only an actual build reads the reference, and
    `gz init` never performs one. `test_scaffolded_pyproject_names_no_missing_file`
    is written against the class rather than the readme instance for that
    reason — it is the cheaper assertion and it catches the next one too.
    """

    @staticmethod
    def _declared_file_references(pyproject: dict) -> list[str]:
        """Return every path in the manifest that must exist on disk.

        The PEP 621 file-valued fields plus uv_build's module root, the backend
        the scaffold builds with since RO-9 tranche 7. `readme` and `license`
        each accept a bare string or a `{file = ...}` table, and both spellings
        name a file the tree has to carry.

        Returns:
            The declared paths, relative to the project root.

        """
        project = pyproject.get("project", {})
        declared: list[str] = []

        for key in ("readme", "license"):
            value = project.get(key)
            if isinstance(value, str) and key == "readme":
                declared.append(value)
            elif isinstance(value, dict) and "file" in value:
                declared.append(value["file"])

        declared.extend(project.get("license-files", []))
        backend = pyproject.get("tool", {}).get("uv", {}).get("build-backend", {})
        if "module-root" in backend:
            declared.append(backend["module-root"])
        return declared

    def test_init_creates_the_readme_its_manifest_names(self) -> None:
        """The instance: `readme = "README.md"` and no README.md."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0, result.output)

            self.assertTrue(Path("README.md").is_file(), "manifest names a README init never wrote")

    def test_scaffolded_pyproject_names_no_missing_file(self) -> None:
        """The class: every path the manifest declares exists in the tree."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0, result.output)

            pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
            declared = self._declared_file_references(pyproject)
            self.assertTrue(declared, "no file references found; the extractor lost its subject")
            missing = sorted(ref for ref in declared if not Path(ref).exists())

        self.assertEqual(
            missing,
            [],
            "the scaffolded manifest references paths the scaffolder did not create",
        )

    def test_a_pre_existing_readme_is_left_alone(self) -> None:
        """Idempotent, on the same terms as every other skeleton artifact."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("README.md").write_text("# Operator's own README\n", encoding="utf-8")

            result = runner.invoke(main, ["init"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(
                Path("README.md").read_text(encoding="utf-8"), "# Operator's own README\n"
            )
