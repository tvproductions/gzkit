"""Tests for ``gz constitute`` — scaffolder must round-trip through validator.

GHI #216 / GZKIT-BOOTSTRAP-008 — same class of failure as GHI #186 (PRD):
the scaffolder and `gz validate --documents` must agree on id format and
schema registration. A fresh `gz constitute X` followed by
`gz validate --documents` must return zero errors.
"""

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.validate_pkg.document import validate_document
from tests.commands.common import CliRunner, _quick_init


class TestConstituteCommand(unittest.TestCase):
    """Basic scaffolder behavior."""

    def test_constitute_creates_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["constitute", "TEST-1.0.0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(Path("design/constitutions/CONSTITUTION-TEST-1.0.0.md").exists())

    def test_constitute_records_event(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["constitute", "TEST-1.0.0"])
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("constitution_created", ledger_content)


class TestConstituteIdCanonicalization(unittest.TestCase):
    """GHI #216 — scaffolder must emit ids its own validator accepts.

    The validator schema at src/gzkit/schemas/constitution.json requires
    ``^CONSTITUTION-[A-Z0-9]+-[0-9]+\\.[0-9]+\\.[0-9]+$``.
    """

    def test_kebab_slug_normalizes_to_canonical_id(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["constitute", "rhea-kernel"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            expected = Path("design/constitutions/CONSTITUTION-RHEAKERNEL-1.0.0.md")
            seen = list(Path("design/constitutions").glob("*.md"))
            self.assertTrue(expected.exists(), msg=f"missing {expected}; saw {seen}")
            frontmatter = expected.read_text(encoding="utf-8")[:200]
            self.assertIn("id: CONSTITUTION-RHEAKERNEL-1.0.0", frontmatter)

    def test_trailing_semver_is_preserved(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["constitute", "rhea-core-2.1.0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            expected = Path("design/constitutions/CONSTITUTION-RHEACORE-2.1.0.md")
            self.assertTrue(expected.exists())
            frontmatter = expected.read_text(encoding="utf-8")[:200]
            self.assertIn("id: CONSTITUTION-RHEACORE-2.1.0", frontmatter)
            self.assertIn("semver: 2.1.0", frontmatter)

    def test_already_canonical_id_is_preserved(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["constitute", "CONSTITUTION-TEST-1.0.0"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(Path("design/constitutions/CONSTITUTION-TEST-1.0.0.md").exists())

    def test_scaffolder_validator_roundtrip(self) -> None:
        """Scaffolded constitution must pass validate_document against the constitution schema."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["constitute", "repro-constitution", "--title", "Repro"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            scaffolded = Path("design/constitutions/CONSTITUTION-REPROCONSTITUTION-1.0.0.md")
            self.assertTrue(scaffolded.exists())
            errors = validate_document(scaffolded, "constitution")
            self.assertEqual(
                [e.message for e in errors],
                [],
                msg="validator rejected freshly-scaffolded constitution",
            )
