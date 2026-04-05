import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner


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

    def test_init_fails_if_already_initialized(self) -> None:
        """init fails if already initialized."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["init"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("already initialized", result.output)

    def test_init_with_force(self) -> None:
        """init --force reinitializes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["init", "--force"])
            self.assertEqual(result.exit_code, 0)


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
