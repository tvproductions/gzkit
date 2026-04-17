import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands.init_cmd import _normalize_package_name
from tests.commands.common import CliRunner

_uv_sync_patcher = patch("gzkit.commands.init_cmd._run_uv_sync", return_value=None)


def setUpModule() -> None:
    """Stub subprocess calls to ``uv sync`` — each real invocation costs ~1s."""
    _uv_sync_patcher.start()


def tearDownModule() -> None:
    _uv_sync_patcher.stop()


class TestInitCommand(unittest.TestCase):
    """Tests for gz init command."""

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
            self.assertIn('requires-python = ">=3.13"', content)

    def test_init_creates_src_package(self) -> None:
        """init creates src/<project>/__init__.py."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            self.assertEqual(result.exit_code, 0)
            # Directory name becomes the package name
            src_dirs = list(Path("src").iterdir())
            self.assertGreaterEqual(len(src_dirs), 1)
            package_dir = src_dirs[0]
            self.assertTrue((package_dir / "__init__.py").exists())

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
            persona_file = Path(".gzkit/personas/default-agent.md")
            custom = (
                "---\nname: default-agent\ntraits:\n  - custom\n"
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
