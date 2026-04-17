import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.validate_pkg.document import validate_document
from tests.commands.common import CliRunner, _quick_init


class TestPrdCommand(unittest.TestCase):
    """Tests for gz prd command."""

    def test_prd_creates_file(self) -> None:
        """prd creates PRD file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["prd", "TEST-1.0.0"])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("design/prd/PRD-TEST-1.0.0.md").exists())

    def test_prd_records_event(self) -> None:
        """prd records event in ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["prd", "TEST-1.0.0"])
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("prd_created", ledger_content)


class TestPrdIdCanonicalization(unittest.TestCase):
    """GHI #186 — scaffolder must emit ids that its own validator accepts.

    The validator schema at src/gzkit/schemas/prd.json requires
    ``^PRD-[A-Z0-9]+-[0-9]+\\.[0-9]+\\.[0-9]+$``. Every slug the scaffolder
    accepts must normalize to that canonical shape.
    """

    def test_kebab_slug_normalizes_to_canonical_id(self) -> None:
        """bug-repro -> PRD-BUGREPRO-1.0.0 (uppercase, hyphens stripped, semver embedded)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["prd", "bug-repro"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            expected = Path("design/prd/PRD-BUGREPRO-1.0.0.md")
            seen = list(Path("design/prd").glob("*.md"))
            self.assertTrue(expected.exists(), msg=f"missing {expected}; saw {seen}")
            frontmatter = expected.read_text(encoding="utf-8")[:200]
            self.assertIn("id: PRD-BUGREPRO-1.0.0", frontmatter)

    def test_trailing_semver_is_preserved(self) -> None:
        """rhea-core-2.1.0 -> PRD-RHEACORE-2.1.0 (trailing semver consumed, slug clean)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["prd", "rhea-core-2.1.0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            expected = Path("design/prd/PRD-RHEACORE-2.1.0.md")
            self.assertTrue(expected.exists())
            frontmatter = expected.read_text(encoding="utf-8")[:200]
            self.assertIn("id: PRD-RHEACORE-2.1.0", frontmatter)
            self.assertIn("semver: 2.1.0", frontmatter)

    def test_already_canonical_id_is_preserved(self) -> None:
        """PRD-TEST-1.0.0 -> PRD-TEST-1.0.0 (idempotent for well-formed input)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["prd", "PRD-TEST-1.0.0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(Path("design/prd/PRD-TEST-1.0.0.md").exists())

    def test_scaffolder_validator_roundtrip(self) -> None:
        """Scaffolded PRD must pass validate_document against the prd schema (GHI #186)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["prd", "bug-repro", "--title", "Repro"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            scaffolded = Path("design/prd/PRD-BUGREPRO-1.0.0.md")
            self.assertTrue(scaffolded.exists())
            errors = validate_document(scaffolded, "prd")
            self.assertEqual(
                errors,
                [],
                msg=f"validator rejected freshly-scaffolded PRD: {[e.message for e in errors]}",
            )
