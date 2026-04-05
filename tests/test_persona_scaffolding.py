"""Tests for persona scaffolding — OBPI-0.0.13-02.

Verifies that scaffold_default_personas() creates valid, project-agnostic
default persona files and respects idempotency.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.models.persona import parse_persona_file, validate_persona_structure
from gzkit.personas import DEFAULT_PERSONAS, scaffold_default_personas

# Terms that MUST NOT appear in project-agnostic default personas.
_GZKIT_TERMS = [
    "gzkit",
    "obpi",
    " adr",
    "prd",
    "pipeline",
    "pep 8",
    "pep8",
    "python",
    "ruff",
    "gz init",
    "gz agent",
    ".gzkit",
]


class TestDefaultPersonaContent(unittest.TestCase):
    """Default persona content validates against the portable schema."""

    def test_at_least_one_default_persona(self) -> None:
        self.assertGreaterEqual(len(DEFAULT_PERSONAS), 1)

    def test_each_default_validates_against_schema(self) -> None:
        for name, content in DEFAULT_PERSONAS.items():
            with self.subTest(persona=name), tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / f"{name}.md"
                p.write_text(content, encoding="utf-8")
                errors = validate_persona_structure(p)
                self.assertEqual(errors, [], f"{name}: {errors}")

    def test_each_default_parses_with_pydantic(self) -> None:
        for name, content in DEFAULT_PERSONAS.items():
            with self.subTest(persona=name), tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / f"{name}.md"
                p.write_text(content, encoding="utf-8")
                fm, _body = parse_persona_file(p)
                self.assertEqual(fm.name, name)
                self.assertGreater(len(fm.traits), 0)
                self.assertGreater(len(fm.anti_traits), 0)
                self.assertGreater(len(fm.grounding.strip()), 0)

    def test_defaults_contain_no_project_specific_content(self) -> None:
        for name, content in DEFAULT_PERSONAS.items():
            with self.subTest(persona=name):
                lower = content.lower()
                for term in _GZKIT_TERMS:
                    self.assertNotIn(
                        term,
                        lower,
                        f"Default persona '{name}' contains project-specific term '{term}'",
                    )

    def test_name_matches_filename_stem(self) -> None:
        for name, content in DEFAULT_PERSONAS.items():
            with self.subTest(persona=name), tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / f"{name}.md"
                p.write_text(content, encoding="utf-8")
                fm, _ = parse_persona_file(p)
                self.assertEqual(fm.name, p.stem)


class TestScaffoldDefaultPersonas(unittest.TestCase):
    """scaffold_default_personas() function behavior."""

    def test_creates_personas_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            self.assertTrue((root / ".gzkit" / "personas").is_dir())

    def test_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = scaffold_default_personas(root)
            self.assertEqual(len(created), len(DEFAULT_PERSONAS))
            for p in created:
                self.assertTrue(p.exists())
                self.assertEqual(p.suffix, ".md")

    def test_returns_empty_when_all_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            scaffold_default_personas(root)
            second = scaffold_default_personas(root)
            self.assertEqual(second, [])

    def test_does_not_overwrite_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            first_name = next(iter(DEFAULT_PERSONAS))
            sentinel = (
                f"---\nname: {first_name}\ntraits:\n  - custom\n"
                "anti-traits:\n  - x\ngrounding: sentinel\n---\n"
            )
            (personas_dir / f"{first_name}.md").write_text(sentinel, encoding="utf-8")
            scaffold_default_personas(root)
            content = (personas_dir / f"{first_name}.md").read_text(encoding="utf-8")
            self.assertIn("sentinel", content)

    def test_creates_missing_files_when_some_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            names = list(DEFAULT_PERSONAS.keys())
            # Pre-create only the first one
            first = names[0]
            (personas_dir / f"{first}.md").write_text(DEFAULT_PERSONAS[first], encoding="utf-8")
            created = scaffold_default_personas(root)
            self.assertEqual(len(created), len(names) - 1)

    def test_idempotent_directory_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit" / "personas").mkdir(parents=True)
            # Should not raise
            scaffold_default_personas(root)


if __name__ == "__main__":
    unittest.main()
