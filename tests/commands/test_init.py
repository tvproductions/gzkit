import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands.init_cmd import _normalize_package_name
from gzkit.config import GzkitConfig
from gzkit.traceability import covers
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
