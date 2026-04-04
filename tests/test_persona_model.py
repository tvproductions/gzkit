"""Tests for gzkit.models.persona — persona frontmatter model and helpers."""

import tempfile
import unittest
from pathlib import Path

from gzkit.models.persona import (
    PersonaFrontmatter,
    discover_persona_files,
    load_persona,
    parse_persona_file,
)
from gzkit.traceability import covers

_VALID_PERSONA = """\
---
name: tester
traits:
  - methodical
  - thorough
anti-traits:
  - shallow-compliance
grounding: I verify every claim with evidence.
---

# Tester Persona

Behavioral identity for verification work.
"""


class TestPersonaFrontmatter(unittest.TestCase):
    """PersonaFrontmatter model validation."""

    @covers("REQ-0.0.11-02-01")
    def test_valid_persona_parses(self) -> None:
        fm = PersonaFrontmatter(
            name="tester",
            traits=["methodical"],
            anti_traits=["shallow-compliance"],
            grounding="Evidence-first.",
        )
        self.assertEqual(fm.name, "tester")
        self.assertEqual(fm.traits, ["methodical"])
        self.assertEqual(fm.anti_traits, ["shallow-compliance"])

    @covers("REQ-0.0.11-02-01")
    def test_anti_traits_alias(self) -> None:
        data = {
            "name": "x",
            "traits": ["a"],
            "anti-traits": ["b"],
            "grounding": "g",
        }
        fm = PersonaFrontmatter(**data)
        self.assertEqual(fm.anti_traits, ["b"])

    @covers("REQ-0.0.11-02-01")
    def test_missing_required_field_raises(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            PersonaFrontmatter(name="x", traits=["a"])  # type: ignore[call-arg]

    @covers("REQ-0.0.11-02-01")
    def test_extra_field_rejected(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            PersonaFrontmatter(
                name="x",
                traits=["a"],
                anti_traits=["b"],
                grounding="g",
                unknown="bad",  # type: ignore[call-arg]
            )


class TestParsePersonaFile(unittest.TestCase):
    """parse_persona_file() tests."""

    @covers("REQ-0.0.11-02-01")
    def test_parse_valid_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "tester.md"
            p.write_text(_VALID_PERSONA, encoding="utf-8")
            fm, body = parse_persona_file(p)
            self.assertEqual(fm.name, "tester")
            self.assertIn("Tester Persona", body)

    @covers("REQ-0.0.11-02-01")
    def test_missing_frontmatter_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.md"
            p.write_text("# No frontmatter\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_persona_file(p)

    @covers("REQ-0.0.11-02-01")
    def test_incomplete_frontmatter_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.md"
            p.write_text("---\nname: x\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_persona_file(p)


class TestDiscoverPersonaFiles(unittest.TestCase):
    """discover_persona_files() tests."""

    @covers("REQ-0.0.11-02-02")
    def test_empty_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(discover_persona_files(Path(tmpdir)), [])

    @covers("REQ-0.0.11-02-02")
    def test_ignores_non_md_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "notes.txt").write_text("hi", encoding="utf-8")
            self.assertEqual(discover_persona_files(Path(tmpdir)), [])

    @covers("REQ-0.0.11-02-02")
    def test_returns_sorted_md_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "beta.md").write_text("b", encoding="utf-8")
            (d / "alpha.md").write_text("a", encoding="utf-8")
            result = discover_persona_files(d)
            self.assertEqual([p.name for p in result], ["alpha.md", "beta.md"])

    @covers("REQ-0.0.11-02-02")
    def test_missing_dir_returns_empty(self) -> None:
        self.assertEqual(discover_persona_files(Path("/nonexistent")), [])


class TestLoadPersona(unittest.TestCase):
    """load_persona() tests."""

    @covers("REQ-0.0.11-02-03")
    def test_load_existing_persona(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            (pdir / "tester.md").write_text(_VALID_PERSONA, encoding="utf-8")
            body = load_persona(root, "tester")
            self.assertIsNotNone(body)
            self.assertIn("Tester Persona", body)

    @covers("REQ-0.0.11-02-03")
    def test_load_missing_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertIsNone(load_persona(Path(tmpdir), "nonexistent"))

    @covers("REQ-0.0.11-02-03")
    def test_load_invalid_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            (pdir / "bad.md").write_text("no frontmatter", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_persona(root, "bad")


class TestExemplarFile(unittest.TestCase):
    """Verify the shipped exemplar persona file parses correctly."""

    @covers("REQ-0.0.11-02-04")
    def test_exemplar_implementer_parses(self) -> None:
        exemplar = Path(".gzkit/personas/implementer.md")
        if not exemplar.is_file():
            self.skipTest("exemplar not yet created")
        fm, body = parse_persona_file(exemplar)
        self.assertEqual(fm.name, "implementer")
        self.assertGreater(len(fm.traits), 0)
        self.assertGreater(len(fm.anti_traits), 0)
        self.assertGreater(len(body), 0)

    @covers("REQ-0.0.12-01-01")
    def test_main_session_parses(self) -> None:
        """OBPI-0.0.12-01: main-session persona parses correctly."""
        path = Path(".gzkit/personas/main-session.md")
        if not path.is_file():
            self.skipTest("main-session persona not yet created")
        fm, body = parse_persona_file(path)
        self.assertEqual(fm.name, "main-session")
        self.assertGreater(len(fm.traits), 0)
        self.assertGreater(len(fm.anti_traits), 0)
        self.assertGreater(len(body), 0)

    @covers("REQ-0.0.12-03-01")
    def test_spec_reviewer_parses(self) -> None:
        """OBPI-0.0.12-03: spec-reviewer persona parses correctly."""
        path = Path(".gzkit/personas/spec-reviewer.md")
        if not path.is_file():
            self.skipTest("spec-reviewer persona not yet created")
        fm, body = parse_persona_file(path)
        self.assertEqual(fm.name, "spec-reviewer")
        self.assertGreater(len(fm.traits), 0)
        self.assertGreater(len(fm.anti_traits), 0)
        self.assertGreater(len(body), 0)

    @covers("REQ-0.0.12-03-01")
    def test_quality_reviewer_parses(self) -> None:
        """OBPI-0.0.12-03: quality-reviewer persona parses correctly."""
        path = Path(".gzkit/personas/quality-reviewer.md")
        if not path.is_file():
            self.skipTest("quality-reviewer persona not yet created")
        fm, body = parse_persona_file(path)
        self.assertEqual(fm.name, "quality-reviewer")
        self.assertGreater(len(fm.traits), 0)
        self.assertGreater(len(fm.anti_traits), 0)
        self.assertGreater(len(body), 0)
